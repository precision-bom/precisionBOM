"""FastAPI routers for BOM Agent Service."""

from .projects import router as projects_router
from .knowledge import router as knowledge_router

__all__ = ["projects_router", "knowledge_router"]
