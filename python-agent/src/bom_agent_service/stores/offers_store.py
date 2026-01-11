"""Ephemeral offers store with optional SQLite persistence."""

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from ..models import PartOffers, SupplierOffer, PriceBreak, LifecycleStatus


class OffersStore:
    """
    Ephemeral store for supplier offers.
    Scoped to a project, expires after TTL.
    """

    def __init__(self, project_id: str, ttl_hours: int = 24, db_path: Optional[str] = None):
        self.project_id = project_id
        self.ttl_hours = ttl_hours
        self._offers: dict[str, PartOffers] = {}

        # Optional SQLite persistence
        self.db_path = Path(db_path) if db_path else None
        if self.db_path:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            self._init_db()
            self._load_from_db()

    def _init_db(self) -> None:
        """Initialize the database schema."""
        if not self.db_path:
            return
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS offers (
                    project_id TEXT NOT NULL,
                    mpn TEXT NOT NULL,
                    data JSON NOT NULL,
                    expires_at TEXT NOT NULL,
                    PRIMARY KEY (project_id, mpn)
                )
            """)
            conn.commit()

    def _load_from_db(self) -> None:
        """Load non-expired offers from database."""
        if not self.db_path:
            return
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT mpn, data FROM offers WHERE project_id = ? AND expires_at > ?",
                (self.project_id, datetime.utcnow().isoformat())
            )
            for row in cursor.fetchall():
                self._offers[row[0]] = PartOffers.model_validate_json(row[1])

    def get_offers(self, mpn: str) -> Optional[PartOffers]:
        """Get all offers for an MPN."""
        part_offers = self._offers.get(mpn)
        if part_offers and self._is_expired(part_offers):
            del self._offers[mpn]
            return None
        return part_offers

    def set_offers(self, mpn: str, offers: PartOffers) -> None:
        """Store offers for an MPN."""
        self._offers[mpn] = offers

        if self.db_path:
            expires_at = datetime.utcnow() + timedelta(hours=self.ttl_hours)
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO offers (project_id, mpn, data, expires_at)
                    VALUES (?, ?, ?, ?)
                """, (self.project_id, mpn, offers.model_dump_json(), expires_at.isoformat()))
                conn.commit()

    def get_all_mpns(self) -> list[str]:
        """Get all MPNs with offers."""
        return list(self._offers.keys())

    def get_best_offer(
        self,
        mpn: str,
        qty_needed: int,
        authorized_only: bool = False
    ) -> Optional[SupplierOffer]:
        """Get best offer based on qty and constraints."""
        part_offers = self.get_offers(mpn)
        if not part_offers:
            return None
        return part_offers.get_best_offer(qty_needed, authorized_only)

    def _is_expired(self, part_offers: PartOffers) -> bool:
        """Check if offers have expired."""
        return datetime.utcnow() > part_offers.last_updated + timedelta(hours=self.ttl_hours)

    def clear(self) -> None:
        """Clear all offers."""
        self._offers.clear()
        if self.db_path:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM offers WHERE project_id = ?", (self.project_id,))
                conn.commit()


def create_mock_offers(mpn: str, manufacturer: str = "", description: str = "") -> PartOffers:
    """Create mock offers for testing."""
    return PartOffers(
        mpn=mpn,
        manufacturer=manufacturer,
        description=description,
        lifecycle_status=LifecycleStatus.ACTIVE,
        rohs_compliant=True,
        offers=[
            SupplierOffer(
                mpn=mpn,
                supplier_id="digikey",
                supplier_name="Digi-Key",
                price_breaks=[
                    PriceBreak(qty=1, price=1.50),
                    PriceBreak(qty=10, price=1.20),
                    PriceBreak(qty=100, price=0.80),
                    PriceBreak(qty=1000, price=0.50),
                ],
                stock_qty=5000,
                lead_time_days=2,
                is_authorized=True,
                packaging="cut tape",
                moq=1,
            ),
            SupplierOffer(
                mpn=mpn,
                supplier_id="mouser",
                supplier_name="Mouser",
                price_breaks=[
                    PriceBreak(qty=1, price=1.55),
                    PriceBreak(qty=10, price=1.25),
                    PriceBreak(qty=100, price=0.85),
                ],
                stock_qty=3000,
                lead_time_days=3,
                is_authorized=True,
                packaging="cut tape",
                moq=1,
            ),
        ]
    )
