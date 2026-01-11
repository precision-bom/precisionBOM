"""SQLAlchemy ORM table definitions."""

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin


class ClientTable(Base, TimestampMixin):
    """Clients (organizations/tenants) table."""

    __tablename__ = "clients"

    client_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # OIDC configuration
    oidc_issuer: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    oidc_audience: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # x402 wallet address (for ephemeral clients created via payment)
    wallet_address: Mapped[Optional[str]] = mapped_column(String(42), nullable=True)

    # Flexible settings as JSONB
    settings: Mapped[dict[str, Any]] = mapped_column(JSONB, default={}, nullable=False)

    __table_args__ = (
        Index("ix_clients_slug", "slug"),
        Index("ix_clients_oidc_issuer", "oidc_issuer"),
        Index("ix_clients_wallet_address", "wallet_address"),
    )


class ProjectTable(Base, TimestampMixin):
    """Projects table - stores full project state as JSONB."""

    __tablename__ = "projects"

    project_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    client_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("clients.client_id"),
        nullable=False,
    )
    data: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)

    __table_args__ = (
        Index("ix_projects_created_at", "created_at"),
        Index("ix_projects_client_id", "client_id"),
    )


class ApiKeyTable(Base):
    """API keys table for authentication."""

    __tablename__ = "api_keys"

    key_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    client_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("clients.client_id"),
        nullable=False,
    )
    hashed_key: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    scopes: Mapped[str] = mapped_column(Text, nullable=False)  # Comma-separated
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    last_used: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    __table_args__ = (
        Index("ix_api_keys_hashed_key", "hashed_key"),
        Index("ix_api_keys_client_id", "client_id"),
    )


class PartTable(Base, TimestampMixin):
    """Parts knowledge table."""

    __tablename__ = "parts"

    mpn: Mapped[str] = mapped_column(String(255), primary_key=True)
    data: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    # Raw API metadata from external providers (DigiKey, Mouser, etc.)
    api_metadata: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)


class SupplierTable(Base, TimestampMixin):
    """Suppliers knowledge table."""

    __tablename__ = "suppliers"

    supplier_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    data: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)


class CategoryTable(Base, TimestampMixin):
    """Category knowledge table."""

    __tablename__ = "categories"

    category: Mapped[str] = mapped_column(String(255), primary_key=True)
    data: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)


class UpdateLogTable(Base):
    """Audit log for knowledge store updates."""

    __tablename__ = "update_log"

    update_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    data: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (Index("ix_update_log_timestamp", "timestamp"),)


class OfferTable(Base):
    """Ephemeral offers cache table."""

    __tablename__ = "offers"

    project_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    mpn: Mapped[str] = mapped_column(String(255), primary_key=True)
    data: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    __table_args__ = (Index("ix_offers_expires_at", "expires_at"),)
