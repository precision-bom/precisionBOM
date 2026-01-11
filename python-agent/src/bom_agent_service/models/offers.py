"""Supplier offer models."""

from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel, Field
import uuid

from .enums import LifecycleStatus


class PriceBreak(BaseModel):
    """A price break tier."""
    qty: int
    price: float


class SupplierOffer(BaseModel):
    """A single offer from a supplier for a part."""
    offer_id: str = Field(default_factory=lambda: f"OFF-{uuid.uuid4().hex[:8].upper()}")
    mpn: str
    supplier_id: str
    supplier_name: str

    # Pricing
    price_breaks: list[PriceBreak] = Field(default_factory=list)
    currency: str = "USD"

    # Availability
    stock_qty: int = 0
    lead_time_days: int = 0

    # Metadata
    is_authorized: bool = True
    packaging: str = ""  # "cut tape", "reel", "tray"
    moq: int = 1

    # Timestamps
    fetched_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime = Field(default_factory=lambda: datetime.utcnow() + timedelta(hours=24))

    def get_price_at_qty(self, qty: int) -> float:
        """Get unit price at a given quantity."""
        if not self.price_breaks:
            return 0.0
        applicable = [pb for pb in self.price_breaks if pb.qty <= qty]
        if applicable:
            return max(applicable, key=lambda x: x.qty).price
        return self.price_breaks[0].price


class PartOffers(BaseModel):
    """All offers for a single MPN."""
    mpn: str
    offers: list[SupplierOffer] = Field(default_factory=list)

    # Enriched part data
    lifecycle_status: LifecycleStatus = LifecycleStatus.ACTIVE
    rohs_compliant: bool = True
    datasheet_url: str = ""
    manufacturer: str = ""
    description: str = ""

    last_updated: datetime = Field(default_factory=datetime.utcnow)

    def get_best_offer(
        self,
        qty_needed: int,
        authorized_only: bool = False
    ) -> Optional[SupplierOffer]:
        """Get best offer based on qty and constraints."""
        valid_offers = [
            o for o in self.offers
            if o.stock_qty >= qty_needed
            and (not authorized_only or o.is_authorized)
        ]

        if not valid_offers:
            return None

        return min(valid_offers, key=lambda o: o.get_price_at_qty(qty_needed))
