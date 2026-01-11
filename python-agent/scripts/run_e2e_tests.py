#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pytest>=8.0.0",
#     "pytest-asyncio>=0.24.0",
#     "asgi-lifespan>=2.1.0",
#     "python-dotenv>=1.0.0",
#     "rich>=13.0.0",
#     "httpx>=0.27.0",
# ]
# ///
"""
E2E Test Runner for BOM Agent Service

This script provides a friendly wrapper around the e2e test suite with:
- Clear phase-by-phase output
- Visual progress indicators
- Timing information
- Categorized test results

Usage:
    uv run scripts/run_e2e_tests.py           # Run all tests
    uv run scripts/run_e2e_tests.py --quick   # Run only fast tests (skip LLM)
    uv run scripts/run_e2e_tests.py --module health  # Run specific module
"""

import argparse
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.table import Table
from rich.text import Text

# Load environment variables from .env file
load_dotenv(Path(__file__).parent.parent / ".env")

console = Console()

# Test categories with descriptions
TEST_CATEGORIES = {
    "health": {
        "file": "test_health.py",
        "name": "Health & Utility Endpoints",
        "description": "Basic health check, root endpoint, and models listing",
        "involves_llm": False,
    },
    "projects": {
        "file": "test_projects_crud.py",
        "name": "Projects CRUD",
        "description": "Create, read, update, delete operations for BOM projects",
        "involves_llm": False,
    },
    "upload": {
        "file": "test_upload_and_process.py",
        "name": "Upload & Processing Flow",
        "description": "BOM upload, intake processing, and agent execution",
        "involves_llm": True,
    },
    "parts": {
        "file": "test_knowledge_parts.py",
        "name": "Knowledge Base - Parts",
        "description": "Part banning, alternates, and knowledge queries",
        "involves_llm": False,
    },
    "suppliers": {
        "file": "test_knowledge_suppliers.py",
        "name": "Knowledge Base - Suppliers",
        "description": "Supplier management and trust level operations",
        "involves_llm": False,
    },
    "chat": {
        "file": "test_chat_completions.py",
        "name": "Chat Completions",
        "description": "OpenAI-compatible chat API endpoint tests",
        "involves_llm": True,
    },
    "errors": {
        "file": "test_error_handling.py",
        "name": "Error Handling",
        "description": "Validation errors, 404s, and edge case handling",
        "involves_llm": False,
    },
    "auth": {
        "file": "test_auth.py",
        "name": "Authentication",
        "description": "API key authentication and authorization tests",
        "involves_llm": False,
    },
    "payment": {
        "file": "test_x402_payment.py",
        "name": "X402 Payment",
        "description": "Payment protocol integration tests",
        "involves_llm": False,
    },
}


@dataclass
class TestResult:
    """Result of running a test category."""
    category: str
    passed: int
    failed: int
    skipped: int
    duration: float
    success: bool
    output: str


def print_banner():
    """Print the test runner banner."""
    console.print(Panel(
        Text.from_markup("[bold cyan]BOM Agent Service[/bold cyan]\n[dim]End-to-End Test Runner[/dim]"),
        box=box.DOUBLE,
        padding=(1, 4),
    ))


def check_prerequisites():
    """Check that all prerequisites are met."""
    console.print("\n[bold]Checking prerequisites...[/bold]\n")

    checks = []

    # Check OPENAI_API_KEY
    has_openai_key = bool(os.environ.get("OPENAI_API_KEY"))
    checks.append(("OPENAI_API_KEY environment variable", has_openai_key))

    # Check tests directory exists
    tests_dir = Path(__file__).parent.parent / "tests"
    has_tests_dir = tests_dir.exists()
    checks.append(("Tests directory exists", has_tests_dir))

    # Check .env file exists
    env_file = Path(__file__).parent.parent / ".env"
    has_env_file = env_file.exists()
    checks.append((".env file exists", has_env_file))

    # Display checks
    for check_name, passed in checks:
        status = "[green]✓[/green]" if passed else "[red]✗[/red]"
        console.print(f"  {status} {check_name}")

    # Fail if critical checks fail
    if not has_openai_key:
        console.print("\n[red bold]Error:[/red bold] OPENAI_API_KEY is required.")
        console.print("Set it in your .env file or environment.")
        return False

    if not has_tests_dir:
        console.print("\n[red bold]Error:[/red bold] Tests directory not found.")
        return False

    console.print("\n[green]All prerequisites met![/green]\n")
    return True


def get_test_files_to_run(args) -> list[tuple[str, dict]]:
    """Determine which test files to run based on arguments."""
    if args.module:
        # Run specific module
        if args.module in TEST_CATEGORIES:
            return [(args.module, TEST_CATEGORIES[args.module])]
        else:
            console.print(f"[red]Unknown module: {args.module}[/red]")
            console.print(f"Available modules: {', '.join(TEST_CATEGORIES.keys())}")
            sys.exit(1)

    if args.quick:
        # Skip LLM tests
        return [(k, v) for k, v in TEST_CATEGORIES.items() if not v["involves_llm"]]

    # Run all tests
    return list(TEST_CATEGORIES.items())


def run_test_category(category: str, info: dict, verbose: bool = True) -> TestResult:
    """Run tests for a specific category."""
    tests_dir = Path(__file__).parent.parent / "tests"
    test_file = tests_dir / info["file"]

    if not test_file.exists():
        return TestResult(
            category=category,
            passed=0,
            failed=0,
            skipped=1,
            duration=0,
            success=False,
            output=f"Test file not found: {test_file}",
        )

    # Build pytest command using uv run to use project environment
    cmd = [
        "uv", "run", "--group", "dev", "pytest",
        str(test_file),
        "-v",
        "--tb=short",
    ]

    if verbose:
        cmd.append("-s")

    start_time = time.time()

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(Path(__file__).parent.parent),
    )

    duration = time.time() - start_time

    # Parse output for pass/fail counts
    output = result.stdout + result.stderr
    passed = output.count(" PASSED")
    failed = output.count(" FAILED")
    errors = output.count(" ERROR")
    skipped = output.count(" SKIPPED")

    # Count errors as failures
    failed = failed + errors

    return TestResult(
        category=category,
        passed=passed,
        failed=failed,
        skipped=skipped,
        duration=duration,
        success=result.returncode == 0,
        output=output,
    )


def print_category_header(info: dict):
    """Print a header for a test category."""
    llm_badge = "[yellow](LLM)[/yellow] " if info["involves_llm"] else ""
    console.print(Panel(
        f"[bold]{info['name']}[/bold]\n{llm_badge}[dim]{info['description']}[/dim]",
        title=f"[cyan]Running: {info['file']}[/cyan]",
        border_style="blue",
    ))


def print_category_result(result: TestResult, show_output: bool = False):
    """Print the result of a test category."""
    if result.success:
        status = "[green bold]PASSED[/green bold]"
    else:
        status = "[red bold]FAILED[/red bold]"

    console.print(f"\n  Result: {status}")
    console.print(f"  [green]{result.passed} passed[/green], [red]{result.failed} failed[/red], [yellow]{result.skipped} skipped[/yellow]")
    console.print(f"  [dim]Duration: {result.duration:.2f}s[/dim]\n")

    if show_output and (result.failed > 0 or not result.success):
        console.print("[dim]─" * 60 + "[/dim]")
        console.print(result.output)
        console.print("[dim]─" * 60 + "[/dim]")


def print_summary(results: list[TestResult], total_duration: float):
    """Print a summary of all test results."""
    console.print("\n")
    console.print(Panel("[bold]Test Summary[/bold]", box=box.DOUBLE))

    # Create summary table
    table = Table(box=box.ROUNDED)
    table.add_column("Category", style="cyan")
    table.add_column("Passed", justify="right", style="green")
    table.add_column("Failed", justify="right", style="red")
    table.add_column("Skipped", justify="right", style="yellow")
    table.add_column("Duration", justify="right")
    table.add_column("Status", justify="center")

    total_passed = 0
    total_failed = 0
    total_skipped = 0

    for result in results:
        total_passed += result.passed
        total_failed += result.failed
        total_skipped += result.skipped

        status = "[green]✓[/green]" if result.success else "[red]✗[/red]"
        table.add_row(
            TEST_CATEGORIES[result.category]["name"],
            str(result.passed),
            str(result.failed),
            str(result.skipped),
            f"{result.duration:.2f}s",
            status,
        )

    # Add totals row
    table.add_section()
    table.add_row(
        "[bold]TOTAL[/bold]",
        f"[bold]{total_passed}[/bold]",
        f"[bold]{total_failed}[/bold]",
        f"[bold]{total_skipped}[/bold]",
        f"[bold]{total_duration:.2f}s[/bold]",
        "",
    )

    console.print(table)

    # Final status
    console.print()
    if total_failed == 0:
        console.print(Panel(
            "[green bold]All tests passed![/green bold]",
            border_style="green",
        ))
    else:
        console.print(Panel(
            f"[red bold]{total_failed} tests failed[/red bold]",
            border_style="red",
        ))

    return total_failed == 0


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run E2E tests for BOM Agent Service",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  uv run scripts/run_e2e_tests.py              # Run all tests
  uv run scripts/run_e2e_tests.py --quick      # Skip LLM-dependent tests
  uv run scripts/run_e2e_tests.py -m health    # Run only health tests
  uv run scripts/run_e2e_tests.py --show-output # Show pytest output for failures

Available modules:
  health     - Health & utility endpoints
  projects   - Projects CRUD operations
  upload     - Upload & processing flow (LLM)
  parts      - Knowledge base - parts
  suppliers  - Knowledge base - suppliers
  chat       - Chat completions (LLM)
  errors     - Error handling
  auth       - Authentication
  payment    - X402 payment protocol
        """,
    )
    parser.add_argument(
        "--quick", "-q",
        action="store_true",
        help="Run only fast tests (skip LLM-dependent tests)",
    )
    parser.add_argument(
        "--module", "-m",
        type=str,
        help="Run only a specific test module",
    )
    parser.add_argument(
        "--show-output", "-o",
        action="store_true",
        help="Show full pytest output for failed tests",
    )
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List available test modules and exit",
    )

    args = parser.parse_args()

    # List modules and exit
    if args.list:
        console.print("\n[bold]Available test modules:[/bold]\n")
        for key, info in TEST_CATEGORIES.items():
            llm = "[yellow](LLM)[/yellow]" if info["involves_llm"] else ""
            console.print(f"  [cyan]{key:12}[/cyan] {info['name']} {llm}")
            console.print(f"               [dim]{info['description']}[/dim]")
        console.print()
        return 0

    print_banner()

    # Check prerequisites
    if not check_prerequisites():
        return 1

    # Get tests to run
    tests_to_run = get_test_files_to_run(args)

    console.print(f"[bold]Running {len(tests_to_run)} test categories...[/bold]\n")

    if args.quick:
        console.print("[yellow]Quick mode: Skipping LLM-dependent tests[/yellow]\n")

    results = []
    total_start_time = time.time()

    # Run each category
    for i, (category, info) in enumerate(tests_to_run, 1):
        console.print(f"[dim]({i}/{len(tests_to_run)})[/dim]")
        print_category_header(info)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeElapsedColumn(),
            console=console,
            transient=True,
        ) as progress:
            task = progress.add_task(f"Running {info['file']}...", total=None)
            result = run_test_category(category, info, verbose=True)
            progress.update(task, completed=True)

        results.append(result)
        print_category_result(result, show_output=args.show_output)

    total_duration = time.time() - total_start_time

    # Print summary
    success = print_summary(results, total_duration)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
