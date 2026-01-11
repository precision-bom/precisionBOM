"""FastAPI routers for BOM Agent Service."""

from .projects import router as projects_router
from .knowledge import router as knowledge_router
from .search import router as search_router
from .api_keys import router as api_keys_router
from .clients import router as clients_router
from .admin import router as admin_router

__all__ = [
    "projects_router",
    "knowledge_router",
    "search_router",
    "api_keys_router",
    "clients_router",
    "admin_router",
]
