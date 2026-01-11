"""Client (organization/tenant) model."""

import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import BaseModel, Field


def _utc_now() -> datetime:
    """Get current UTC time as timezone-aware datetime."""
    return datetime.now(timezone.utc)


class Client(BaseModel):
    """A client organization (tenant) in the system."""

    client_id: str = Field(default_factory=lambda: f"cli_{uuid.uuid4().hex[:12]}")
    name: str  # Human-readable name (e.g., "Acme Corp")
    slug: str  # URL-safe identifier (e.g., "acme-corp")
    is_active: bool = True
    created_at: datetime = Field(default_factory=_utc_now)
    updated_at: datetime = Field(default_factory=_utc_now)

    # OIDC configuration for JWT authentication
    oidc_issuer: Optional[str] = None  # e.g., "https://acme.us.auth0.com/"
    oidc_audience: Optional[str] = None  # Expected audience claim

    # x402 wallet address (for ephemeral clients created via payment)
    wallet_address: Optional[str] = None  # Ethereum address, e.g., "0x..."

    # Flexible settings
    settings: dict[str, Any] = Field(default_factory=dict)
