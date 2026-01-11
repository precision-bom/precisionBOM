"""Data stores for BOM processing."""

from .project_store import ProjectStore
from .offers_store import OffersStore
from .org_knowledge import OrgKnowledgeStore
from .api_key_store import ApiKeyStore
from .market_intel_store import MarketIntelStore
from .client_store import ClientStore

# Singleton instances
_project_store: ProjectStore | None = None
_offers_store: OffersStore | None = None
_org_knowledge_store: OrgKnowledgeStore | None = None
_api_key_store: ApiKeyStore | None = None
_market_intel_store: MarketIntelStore | None = None
_client_store: ClientStore | None = None


def get_project_store() -> ProjectStore:
    """Get or create singleton ProjectStore instance."""
    global _project_store
    if _project_store is None:
        _project_store = ProjectStore()
    return _project_store


def get_offers_store() -> OffersStore:
    """Get or create singleton OffersStore instance."""
    global _offers_store
    if _offers_store is None:
        _offers_store = OffersStore()
    return _offers_store


def get_org_knowledge_store() -> OrgKnowledgeStore:
    """Get or create singleton OrgKnowledgeStore instance."""
    global _org_knowledge_store
    if _org_knowledge_store is None:
        _org_knowledge_store = OrgKnowledgeStore()
    return _org_knowledge_store


def get_api_key_store() -> ApiKeyStore:
    """Get or create singleton ApiKeyStore instance."""
    global _api_key_store
    if _api_key_store is None:
        _api_key_store = ApiKeyStore()
    return _api_key_store


def get_market_intel_store() -> MarketIntelStore:
    """Get or create singleton MarketIntelStore instance."""
    global _market_intel_store
    if _market_intel_store is None:
        _market_intel_store = MarketIntelStore()
    return _market_intel_store


def get_client_store() -> ClientStore:
    """Get or create singleton ClientStore instance."""
    global _client_store
    if _client_store is None:
        _client_store = ClientStore()
    return _client_store


__all__ = [
    "ProjectStore",
    "OffersStore",
    "OrgKnowledgeStore",
    "ApiKeyStore",
    "MarketIntelStore",
    "ClientStore",
    "get_project_store",
    "get_offers_store",
    "get_org_knowledge_store",
    "get_api_key_store",
    "get_market_intel_store",
    "get_client_store",
]
