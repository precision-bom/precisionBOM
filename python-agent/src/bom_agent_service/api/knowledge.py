"""Knowledge base API router."""

from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..models import TrustLevel
from ..stores import OrgKnowledgeStore
from ..stores.org_knowledge import seed_default_suppliers

router = APIRouter(prefix="/knowledge", tags=["knowledge"])

DATA_DIR = "data"


def get_org_store() -> OrgKnowledgeStore:
    store = OrgKnowledgeStore(f"{DATA_DIR}/org_knowledge.db")
    seed_default_suppliers(store)
    return store


# =============================================================================
# Parts API
# =============================================================================

class PartKnowledgeResponse(BaseModel):
    """Part knowledge response."""
    mpn: str
    notes: list[str]
    approved_alternates: list[str]
    banned: bool
    ban_reason: str
    preferred: bool
    times_used: int
    failure_count: int


class PartBanRequest(BaseModel):
    """Request to ban a part."""
    reason: str
    user: str = "api"


class PartAlternateRequest(BaseModel):
    """Request to add an alternate."""
    alternate_mpn: str
    reason: str = ""
    user: str = "api"


@router.get("/parts", response_model=list[PartKnowledgeResponse])
async def list_parts(limit: int = 100):
    """List all parts in knowledge base."""
    store = get_org_store()
    parts = store.list_parts(limit=limit)

    return [
        PartKnowledgeResponse(
            mpn=p.mpn,
            notes=p.notes,
            approved_alternates=p.approved_alternates,
            banned=p.banned,
            ban_reason=p.ban_reason,
            preferred=p.preferred,
            times_used=p.times_used,
            failure_count=p.failure_count,
        )
        for p in parts
    ]


@router.get("/parts/{mpn}", response_model=PartKnowledgeResponse)
async def get_part(mpn: str):
    """Get knowledge for a specific part."""
    store = get_org_store()
    part = store.get_part(mpn)

    if not part:
        raise HTTPException(status_code=404, detail=f"Part not found: {mpn}")

    return PartKnowledgeResponse(
        mpn=part.mpn,
        notes=part.notes,
        approved_alternates=part.approved_alternates,
        banned=part.banned,
        ban_reason=part.ban_reason,
        preferred=part.preferred,
        times_used=part.times_used,
        failure_count=part.failure_count,
    )


@router.post("/parts/{mpn}/ban")
async def ban_part(mpn: str, request: PartBanRequest):
    """Ban a part from use."""
    store = get_org_store()
    store.ban_part(mpn, request.reason, request.user)

    return {"status": "banned", "mpn": mpn, "reason": request.reason}


@router.post("/parts/{mpn}/unban")
async def unban_part(mpn: str, user: str = "api"):
    """Remove ban from a part."""
    store = get_org_store()
    store.unban_part(mpn, user)

    return {"status": "unbanned", "mpn": mpn}


@router.post("/parts/{mpn}/alternates")
async def add_alternate(mpn: str, request: PartAlternateRequest):
    """Add an approved alternate for a part."""
    store = get_org_store()
    store.add_alternate(mpn, request.alternate_mpn, request.user, request.reason)

    return {
        "status": "added",
        "mpn": mpn,
        "alternate_mpn": request.alternate_mpn,
    }


@router.get("/parts/{mpn}/alternates", response_model=list[str])
async def get_alternates(mpn: str):
    """Get approved alternates for a part."""
    store = get_org_store()
    return store.get_approved_alternates(mpn)


# =============================================================================
# Suppliers API
# =============================================================================

class SupplierKnowledgeResponse(BaseModel):
    """Supplier knowledge response."""
    supplier_id: str
    name: str
    supplier_type: str
    trust_level: str
    on_time_rate: float
    quality_rate: float
    order_count_ytd: int
    notes: list[str]


class SupplierTrustRequest(BaseModel):
    """Request to set supplier trust level."""
    trust_level: str  # high, medium, low, blocked
    reason: str = ""
    user: str = "api"


class SupplierCreateRequest(BaseModel):
    """Request to create a supplier."""
    supplier_id: str
    name: str
    supplier_type: str = "authorized"
    trust_level: str = "medium"


@router.get("/suppliers", response_model=list[SupplierKnowledgeResponse])
async def list_suppliers(limit: int = 100):
    """List all suppliers in knowledge base."""
    store = get_org_store()
    suppliers = store.list_suppliers(limit=limit)

    return [
        SupplierKnowledgeResponse(
            supplier_id=s.supplier_id,
            name=s.name,
            supplier_type=s.supplier_type.value,
            trust_level=s.trust_level.value,
            on_time_rate=s.on_time_rate,
            quality_rate=s.quality_rate,
            order_count_ytd=s.order_count_ytd,
            notes=s.notes,
        )
        for s in suppliers
    ]


@router.get("/suppliers/{supplier_id}", response_model=SupplierKnowledgeResponse)
async def get_supplier(supplier_id: str):
    """Get knowledge for a specific supplier."""
    store = get_org_store()
    supplier = store.get_supplier(supplier_id)

    if not supplier:
        raise HTTPException(status_code=404, detail=f"Supplier not found: {supplier_id}")

    return SupplierKnowledgeResponse(
        supplier_id=supplier.supplier_id,
        name=supplier.name,
        supplier_type=supplier.supplier_type.value,
        trust_level=supplier.trust_level.value,
        on_time_rate=supplier.on_time_rate,
        quality_rate=supplier.quality_rate,
        order_count_ytd=supplier.order_count_ytd,
        notes=supplier.notes,
    )


@router.post("/suppliers/{supplier_id}/trust")
async def set_supplier_trust(supplier_id: str, request: SupplierTrustRequest):
    """Set supplier trust level."""
    store = get_org_store()

    # Validate trust level
    try:
        trust = TrustLevel(request.trust_level.lower())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid trust level. Use: high, medium, low, blocked"
        )

    supplier = store.get_supplier(supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail=f"Supplier not found: {supplier_id}")

    store.set_supplier_trust(supplier_id, trust, request.user, request.reason)

    return {
        "status": "updated",
        "supplier_id": supplier_id,
        "trust_level": trust.value,
    }


@router.post("/suppliers")
async def create_supplier(request: SupplierCreateRequest):
    """Create a new supplier."""
    from ..models import SupplierType

    store = get_org_store()

    # Check if already exists
    if store.get_supplier(request.supplier_id):
        raise HTTPException(
            status_code=400,
            detail=f"Supplier already exists: {request.supplier_id}"
        )

    try:
        supplier_type = SupplierType(request.supplier_type.lower())
        trust_level = TrustLevel(request.trust_level.lower())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    supplier = store.get_or_create_supplier(request.supplier_id, request.name)
    supplier.supplier_type = supplier_type
    supplier.trust_level = trust_level
    store._save_supplier(supplier)

    return {
        "status": "created",
        "supplier_id": request.supplier_id,
        "name": request.name,
    }
