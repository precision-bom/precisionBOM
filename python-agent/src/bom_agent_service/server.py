"""Server entry point for running with uv run."""

import uvicorn


def main():
    """Run the BOM Agent Service API server."""
    uvicorn.run(
        "bom_agent_service.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )


if __name__ == "__main__":
    main()
