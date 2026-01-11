#!/usr/bin/env python3
"""CLI tool for BOM Agent Service - uses API endpoints."""

import sys
from pathlib import Path

import click
import httpx
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich import box

console = Console()
DEFAULT_API_URL = "http://localhost:8000"


class APIClient:
    """HTTP client for BOM Agent Service API."""

    def __init__(self, base_url: str = DEFAULT_API_URL):
        self.base_url = base_url.rstrip("/")
        self.client = httpx.Client(timeout=300.0)  # Long timeout for processing

    def health_check(self) -> bool:
        """Check if API is healthy."""
        try:
            resp = self.client.get(f"{self.base_url}/health")
            return resp.status_code == 200
        except Exception:
            return False

    # Projects API
    def list_projects(self) -> list[dict]:
        resp = self.client.get(f"{self.base_url}/projects")
        resp.raise_for_status()
        return resp.json()

    def get_project(self, project_id: str) -> dict:
        resp = self.client.get(f"{self.base_url}/projects/{project_id}")
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.json()

    def get_trace(self, project_id: str) -> list[dict]:
        resp = self.client.get(f"{self.base_url}/projects/{project_id}/trace")
        resp.raise_for_status()
        return resp.json()

    def upload_and_process(self, bom_path: str, intake_path: str = None) -> dict:
        files = {"bom_file": open(bom_path, "rb")}
        if intake_path:
            files["intake_file"] = open(intake_path, "rb")

        try:
            resp = self.client.post(
                f"{self.base_url}/projects/upload-and-process",
                files=files,
            )
            resp.raise_for_status()
            return resp.json()
        finally:
            for f in files.values():
                f.close()

    # Knowledge API - Parts
    def list_parts(self) -> list[dict]:
        resp = self.client.get(f"{self.base_url}/knowledge/parts")
        resp.raise_for_status()
        return resp.json()

    def get_part(self, mpn: str) -> dict:
        resp = self.client.get(f"{self.base_url}/knowledge/parts/{mpn}")
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.json()

    def ban_part(self, mpn: str, reason: str) -> dict:
        resp = self.client.post(
            f"{self.base_url}/knowledge/parts/{mpn}/ban",
            json={"reason": reason, "user": "cli"},
        )
        resp.raise_for_status()
        return resp.json()

    def unban_part(self, mpn: str) -> dict:
        resp = self.client.post(
            f"{self.base_url}/knowledge/parts/{mpn}/unban",
            params={"user": "cli"},
        )
        resp.raise_for_status()
        return resp.json()

    def add_alternate(self, mpn: str, alt_mpn: str, reason: str) -> dict:
        resp = self.client.post(
            f"{self.base_url}/knowledge/parts/{mpn}/alternates",
            json={"alternate_mpn": alt_mpn, "reason": reason, "user": "cli"},
        )
        resp.raise_for_status()
        return resp.json()

    def get_alternates(self, mpn: str) -> list[str]:
        resp = self.client.get(f"{self.base_url}/knowledge/parts/{mpn}/alternates")
        resp.raise_for_status()
        return resp.json()

    # Knowledge API - Suppliers
    def list_suppliers(self) -> list[dict]:
        resp = self.client.get(f"{self.base_url}/knowledge/suppliers")
        resp.raise_for_status()
        return resp.json()

    def get_supplier(self, supplier_id: str) -> dict:
        resp = self.client.get(f"{self.base_url}/knowledge/suppliers/{supplier_id}")
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.json()

    def set_supplier_trust(self, supplier_id: str, level: str, reason: str) -> dict:
        resp = self.client.post(
            f"{self.base_url}/knowledge/suppliers/{supplier_id}/trust",
            json={"trust_level": level, "reason": reason, "user": "cli"},
        )
        resp.raise_for_status()
        return resp.json()


def get_client(url: str) -> APIClient:
    """Get API client, checking health first."""
    client = APIClient(url)
    if not client.health_check():
        console.print(f"[red]API not available at {url}[/]")
        console.print("[dim]Start the service with: uv run uvicorn bom_agent_service.main:app --reload[/]")
        sys.exit(1)
    return client


@click.group()
@click.option("--api-url", envvar="BOM_API_URL", default=DEFAULT_API_URL, help="API base URL")
@click.version_option(version="0.1.0")
@click.pass_context
def main(ctx, api_url: str):
    """BOM Agent Service CLI - Process BOMs through multi-agent review."""
    ctx.ensure_object(dict)
    ctx.obj["api_url"] = api_url


# =============================================================================
# Process Command
# =============================================================================

@main.command()
@click.argument("bom", type=click.Path(exists=True))
@click.option("--intake", "-i", type=click.Path(exists=True), help="Project intake YAML file")
@click.option("--verbose", "-v", is_flag=True, help="Show detailed output")
@click.pass_context
def process(ctx, bom: str, intake: str | None, verbose: bool):
    """Process a BOM through the full agent flow.

    BOM is the path to a CSV file containing the bill of materials.
    """
    console.print(Panel.fit(
        "[bold cyan]BOM Processing Flow[/]",
        border_style="cyan",
    ))

    client = get_client(ctx.obj["api_url"])

    console.print(f"\n[bold]BOM:[/] {bom}")
    if intake:
        console.print(f"[bold]Intake:[/] {intake}")
    console.print()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task("[cyan]Processing BOM (this may take a while)...", total=None)

        try:
            result = client.upload_and_process(bom, intake)
        except httpx.HTTPStatusError as e:
            console.print(f"\n[red]Error: {e.response.text}[/]")
            sys.exit(1)
        except Exception as e:
            console.print(f"\n[red]Error: {e}[/]")
            sys.exit(1)

    # Display results
    console.print()
    console.print(Panel.fit(
        f"[bold green]Project Complete[/]\n"
        f"ID: {result['project_id']}\n"
        f"Status: {result['status']}\n"
        f"Message: {result['message']}",
        border_style="green",
    ))

    # Fetch full project details
    project = client.get_project(result["project_id"])
    if project:
        table = Table(title="Line Item Summary", box=box.ROUNDED)
        table.add_column("MPN", style="cyan")
        table.add_column("Qty", justify="right")
        table.add_column("Status", style="yellow")

        for item in project.get("line_items", []):
            table.add_row(
                item.get("mpn", "-"),
                str(item.get("quantity", 0)),
                item.get("status", "-"),
            )

        console.print(table)


# =============================================================================
# Status Command
# =============================================================================

@main.command()
@click.argument("project_id", required=False)
@click.pass_context
def status(ctx, project_id: str | None):
    """Show project status.

    If PROJECT_ID is omitted, lists all projects.
    """
    client = get_client(ctx.obj["api_url"])

    if project_id:
        project = client.get_project(project_id)
        if not project:
            console.print(f"[red]Project not found: {project_id}[/]")
            sys.exit(1)

        ctx_data = project.get("context", {})
        console.print(Panel.fit(
            f"[bold]Project:[/] {project['project_id']}\n"
            f"[bold]Name:[/] {ctx_data.get('project_name') or 'N/A'}\n"
            f"[bold]Status:[/] {project['status']}\n"
            f"[bold]Created:[/] {project['created_at']}\n"
            f"[bold]Items:[/] {len(project.get('line_items', []))}",
            title="Project Details",
            border_style="cyan",
        ))

        table = Table(title="Line Items", box=box.ROUNDED)
        table.add_column("MPN", style="cyan")
        table.add_column("Manufacturer")
        table.add_column("Qty", justify="right")
        table.add_column("Status", style="yellow")

        for item in project.get("line_items", []):
            table.add_row(
                item.get("mpn", "-"),
                item.get("manufacturer") or "-",
                str(item.get("quantity", 0)),
                item.get("status", "-"),
            )

        console.print(table)
    else:
        projects = client.list_projects()
        if not projects:
            console.print("[dim]No projects found.[/]")
            return

        table = Table(title="Projects", box=box.ROUNDED)
        table.add_column("Project ID", style="cyan")
        table.add_column("Name")
        table.add_column("Status", style="yellow")
        table.add_column("Items", justify="right")
        table.add_column("Created")

        for p in projects:
            table.add_row(
                p["project_id"],
                p.get("project_name") or "-",
                p["status"],
                str(p["line_item_count"]),
                p["created_at"][:19],
            )

        console.print(table)


# =============================================================================
# Trace Command
# =============================================================================

@main.command()
@click.argument("project_id")
@click.pass_context
def trace(ctx, project_id: str):
    """Show project execution trace."""
    client = get_client(ctx.obj["api_url"])

    try:
        trace_data = client.get_trace(project_id)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            console.print(f"[red]Project not found: {project_id}[/]")
        else:
            console.print(f"[red]Error: {e.response.text}[/]")
        sys.exit(1)

    console.print(Panel.fit(
        f"[bold]Execution Trace[/] for {project_id}",
        border_style="cyan",
    ))

    if not trace_data:
        console.print("[dim]No trace entries.[/]")
        return

    for i, step in enumerate(trace_data, 1):
        agent_str = f" [yellow]({step.get('agent')})[/]" if step.get("agent") else ""
        console.print(f"\n[bold]{i}. [{step.get('step')}][/]{agent_str}")
        console.print(f"   {step.get('message')}")
        if step.get("reasoning"):
            console.print(f"   [dim]Reasoning: {step.get('reasoning')}[/]")
        if step.get("references"):
            console.print(f"   [dim]References: {', '.join(step.get('references'))}[/]")
        console.print(f"   [dim]{step.get('timestamp')}[/]")


# =============================================================================
# Knowledge Base Commands
# =============================================================================

@main.group()
def kb():
    """Knowledge base management."""
    pass


# -----------------------------------------------------------------------------
# KB Parts
# -----------------------------------------------------------------------------

@kb.group()
def parts():
    """Manage parts knowledge."""
    pass


@parts.command("list")
@click.pass_context
def parts_list(ctx):
    """List all parts in knowledge base."""
    client = get_client(ctx.obj["api_url"])
    parts_data = client.list_parts()

    if not parts_data:
        console.print("[dim]No parts in knowledge base.[/]")
        return

    table = Table(title="Parts Knowledge", box=box.ROUNDED)
    table.add_column("MPN", style="cyan")
    table.add_column("Times Used", justify="right")
    table.add_column("Failures", justify="right", style="red")
    table.add_column("Banned?", style="yellow")
    table.add_column("Notes")

    for part in parts_data:
        banned = "Yes" if part.get("banned") else "No"
        notes = part.get("notes", [])
        notes_str = "; ".join(notes) if notes else "-"
        notes_str = notes_str[:30] + "..." if len(notes_str) > 30 else notes_str
        table.add_row(
            part["mpn"],
            str(part.get("times_used", 0)),
            str(part.get("failure_count", 0)),
            banned,
            notes_str,
        )

    console.print(table)


@parts.command("show")
@click.argument("mpn")
@click.pass_context
def parts_show(ctx, mpn: str):
    """Show details for a specific part."""
    client = get_client(ctx.obj["api_url"])
    part = client.get_part(mpn)

    if not part:
        console.print(f"[dim]No knowledge for MPN: {mpn}[/]")
        return

    notes = part.get("notes", [])
    notes_str = "; ".join(notes) if notes else "None"
    console.print(Panel.fit(
        f"[bold]MPN:[/] {part['mpn']}\n"
        f"[bold]Times Used:[/] {part.get('times_used', 0)}\n"
        f"[bold]Failures:[/] {part.get('failure_count', 0)}\n"
        f"[bold]Banned:[/] {'Yes - ' + part.get('ban_reason', '') if part.get('banned') else 'No'}\n"
        f"[bold]Notes:[/] {notes_str}",
        title="Part Knowledge",
        border_style="cyan",
    ))

    alternates = client.get_alternates(mpn)
    if alternates:
        console.print(f"\n[bold]Approved Alternates:[/] {', '.join(alternates)}")


@parts.command("ban")
@click.argument("mpn")
@click.option("--reason", "-r", required=True, help="Reason for banning")
@click.pass_context
def parts_ban(ctx, mpn: str, reason: str):
    """Ban a part from use."""
    client = get_client(ctx.obj["api_url"])
    client.ban_part(mpn, reason)
    console.print(f"[green]Banned part: {mpn}[/]")


@parts.command("unban")
@click.argument("mpn")
@click.pass_context
def parts_unban(ctx, mpn: str):
    """Remove ban from a part."""
    client = get_client(ctx.obj["api_url"])
    client.unban_part(mpn)
    console.print(f"[green]Unbanned part: {mpn}[/]")


@parts.command("alternate")
@click.argument("mpn")
@click.argument("alt_mpn")
@click.option("--reason", "-r", default="Added via CLI", help="Reason for adding alternate")
@click.pass_context
def parts_alternate(ctx, mpn: str, alt_mpn: str, reason: str):
    """Add an approved alternate for a part."""
    client = get_client(ctx.obj["api_url"])
    client.add_alternate(mpn, alt_mpn, reason)
    console.print(f"[green]Added alternate {alt_mpn} for {mpn}[/]")


# -----------------------------------------------------------------------------
# KB Suppliers
# -----------------------------------------------------------------------------

@kb.group()
def suppliers():
    """Manage supplier knowledge."""
    pass


@suppliers.command("list")
@click.pass_context
def suppliers_list(ctx):
    """List all suppliers in knowledge base."""
    client = get_client(ctx.obj["api_url"])
    suppliers_data = client.list_suppliers()

    if not suppliers_data:
        console.print("[dim]No suppliers in knowledge base.[/]")
        return

    table = Table(title="Supplier Knowledge", box=box.ROUNDED)
    table.add_column("ID", style="cyan")
    table.add_column("Name")
    table.add_column("Trust", style="yellow")
    table.add_column("On-Time", justify="right", style="green")
    table.add_column("Quality", justify="right", style="blue")
    table.add_column("Orders", justify="right")

    for s in suppliers_data:
        table.add_row(
            s["supplier_id"],
            s["name"],
            s["trust_level"],
            f"{s['on_time_rate']:.0%}",
            f"{s['quality_rate']:.0%}",
            str(s.get("order_count_ytd", 0)),
        )

    console.print(table)


@suppliers.command("show")
@click.argument("supplier_id")
@click.pass_context
def suppliers_show(ctx, supplier_id: str):
    """Show details for a specific supplier."""
    client = get_client(ctx.obj["api_url"])
    supplier = client.get_supplier(supplier_id)

    if not supplier:
        console.print(f"[dim]No knowledge for supplier: {supplier_id}[/]")
        return

    notes = supplier.get("notes", [])
    notes_str = "; ".join(notes) if notes else "None"
    console.print(Panel.fit(
        f"[bold]ID:[/] {supplier['supplier_id']}\n"
        f"[bold]Name:[/] {supplier['name']}\n"
        f"[bold]Trust Level:[/] {supplier['trust_level']}\n"
        f"[bold]On-Time Rate:[/] {supplier['on_time_rate']:.0%}\n"
        f"[bold]Quality Rate:[/] {supplier['quality_rate']:.0%}\n"
        f"[bold]Orders YTD:[/] {supplier.get('order_count_ytd', 0)}\n"
        f"[bold]Notes:[/] {notes_str}",
        title="Supplier Knowledge",
        border_style="cyan",
    ))


@suppliers.command("trust")
@click.argument("supplier_id")
@click.argument("level", type=click.Choice(["high", "medium", "low", "blocked"]))
@click.option("--reason", "-r", default="Updated via CLI", help="Reason for change")
@click.pass_context
def suppliers_trust(ctx, supplier_id: str, level: str, reason: str):
    """Set supplier trust level."""
    client = get_client(ctx.obj["api_url"])
    client.set_supplier_trust(supplier_id, level, reason)
    console.print(f"[green]Set trust level for {supplier_id} to {level}[/]")


# =============================================================================
# Chat Command
# =============================================================================

@main.command()
@click.pass_context
def chat(ctx):
    """Interactive chat mode."""
    api_url = ctx.obj["api_url"]
    client = get_client(api_url)

    console.print(Panel.fit(
        "[bold cyan]BOM Agent CLI[/] - Chat Mode\n[dim]Type 'quit' to exit[/]",
        border_style="cyan",
    ))

    console.print(f"[green]Connected to {api_url}[/]")

    system_prompt = """You are an electronics parts sourcing expert. You help users identify parts,
find alternatives, and optimize their Bill of Materials for cost, availability, and reliability.
Be concise and practical in your responses."""

    while True:
        console.print()
        try:
            user_input = console.input("[bold cyan]You:[/] ")
        except (KeyboardInterrupt, EOFError):
            break

        if user_input.lower() in ("quit", "exit", "q"):
            break

        if not user_input.strip():
            continue

        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                progress.add_task("[cyan]Thinking...", total=None)

                resp = client.client.post(
                    f"{api_url}/v1/chat/completions",
                    json={
                        "model": "bom-agent",
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_input},
                        ],
                    },
                )

            if resp.status_code == 200:
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                console.print()
                console.print(Panel(content, title="[bold green]Agent[/]", border_style="green"))
            else:
                console.print(f"[red]Error: {resp.text}[/]")

        except Exception as e:
            console.print(f"[red]Error: {e}[/]")

    console.print("\n[dim]Goodbye![/]")


if __name__ == "__main__":
    main()
