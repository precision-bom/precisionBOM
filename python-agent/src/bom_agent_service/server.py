"""Server entry point for running with uv run."""

import os

import uvicorn


def main():
    """Run the BOM Agent Service API server."""
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "bom_agent_service.main:app",
        host="0.0.0.0",
        port=port,
    )


if __name__ == "__main__":
    main()
