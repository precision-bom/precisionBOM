"""Server entry point for running with uv run."""

import logging
import os
import sys
from pathlib import Path

import uvicorn

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    env_file = Path(__file__).parent.parent.parent.parent / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        print(f"Loaded environment from {env_file}")
except ImportError:
    pass  # dotenv not installed, rely on system env vars


def setup_logging():
    """Configure logging to file and console."""
    # Create logs directory (python-agent/logs/)
    log_dir = Path(__file__).parent.parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / "server.log"

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # File handler - all logs
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        "%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)

    # Console handler - INFO and above
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter("%(asctime)s [%(name)s] %(levelname)s: %(message)s", datefmt="%H:%M:%S")
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # Also capture httpx logs for LLM calls
    logging.getLogger("httpx").setLevel(logging.INFO)

    print(f"Logging to: {log_file}")
    return log_file


def main():
    """Run the BOM Agent Service API server."""
    log_file = setup_logging()
    print("Starting BOM Agent Service...")
    print(f"Logs: {log_file}")
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "bom_agent_service.main:app",
        host="0.0.0.0",
        port=port,
    )


if __name__ == "__main__":
    main()
