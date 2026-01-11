"""Organization knowledge models."""

from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field
import uuid

from .enums import SupplierType, TrustLevel


class PartKnowledge(BaseModel):
    """Organizational knowledge about a specific part."""
    mpn: str

    # Internal notes
    notes: list[str] = Field(default_factory=list)

    # Alternates
    approved_alternates: list[str] = Field(default_factory=list)

    # Status
    banned: bool = False
    ban_reason: str = ""
    preferred: bool = False

    # Usage history
    last_used_date: Optional[date] = None
    projects_used_in: list[str] = Field(default_factory=list)

    # Quality history
    times_used: int = 0
    failure_count: int = 0
    quality_notes: list[str] = Field(default_factory=list)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class SupplierKnowledge(BaseModel):
    """Organizational knowledge about a supplier."""
    supplier_id: str
    name: str
    supplier_type: SupplierType = SupplierType.AUTHORIZED
    trust_level: TrustLevel = TrustLevel.MEDIUM

    # Performance metrics
    on_time_rate: float = 1.0
    quality_rate: float = 1.0
    lead_time_accuracy: float = 1.0

    # Relationship
    account_rep: str = ""
    account_rep_email: str = ""
    payment_terms: str = "Net 30"
    credit_limit: float = 0.0

    # Notes
    notes: list[str] = Field(default_factory=list)

    # Activity
    last_order_date: Optional[date] = None
    total_spend_ytd: float = 0.0
    order_count_ytd: int = 0

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class CategoryKnowledge(BaseModel):
    """Knowledge about a part category."""
    category: str  # "0603 MLCC", "STM32F4", etc.
    preferred_manufacturers: list[str] = Field(default_factory=list)
    avoid_manufacturers: list[str] = Field(default_factory=list)
    typical_lead_time_days: int = 7
    notes: str = ""

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class PriceObservation(BaseModel):
    """Historical price observation."""
    mpn: str
    supplier_id: str
    observed_date: date
    qty: int
    unit_price: float


class StoreUpdate(BaseModel):
    """Request to update the org knowledge store."""
    update_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: str  # agent name or "manual:username"

    update_type: str  # "add", "update", "append", "delete"
    entity_type: str  # "part", "supplier", "category"
    entity_id: str    # MPN or supplier_id
    field: str        # field name to update
    value: str | int | float | bool | list | dict  # new value (JSON serializable)
    reason: str       # audit trail
