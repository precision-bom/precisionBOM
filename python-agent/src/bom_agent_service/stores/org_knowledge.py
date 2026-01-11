"""Organization knowledge store with SQLite persistence."""

import sqlite3
from datetime import date, datetime
from pathlib import Path
from typing import Optional

from ..models import (
    PartKnowledge,
    SupplierKnowledge,
    CategoryKnowledge,
    StoreUpdate,
    SupplierType,
    TrustLevel,
)


class OrgKnowledgeStore:
    """
    Persistent organization-wide knowledge store.
    Updated by agents (via requests) and manual tooling.
    """

    def __init__(self, db_path: str = "data/org_knowledge.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        """Initialize the database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS parts (
                    mpn TEXT PRIMARY KEY,
                    data JSON NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS suppliers (
                    supplier_id TEXT PRIMARY KEY,
                    data JSON NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    category TEXT PRIMARY KEY,
                    data JSON NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS update_log (
                    update_id TEXT PRIMARY KEY,
                    data JSON NOT NULL,
                    timestamp TEXT NOT NULL
                )
            """)
            conn.commit()

    # -------------------------------------------------------------------------
    # Part Knowledge
    # -------------------------------------------------------------------------

    def get_part(self, mpn: str) -> Optional[PartKnowledge]:
        """Get knowledge about a part."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT data FROM parts WHERE mpn = ?", (mpn,))
            row = cursor.fetchone()
            if row:
                return PartKnowledge.model_validate_json(row[0])
            return None

    def get_or_create_part(self, mpn: str) -> PartKnowledge:
        """Get or create part knowledge."""
        part = self.get_part(mpn)
        if not part:
            part = PartKnowledge(mpn=mpn)
            self._save_part(part)
        return part

    def _save_part(self, part: PartKnowledge) -> None:
        """Save part knowledge."""
        part.updated_at = datetime.utcnow()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO parts (mpn, data, updated_at) VALUES (?, ?, ?)",
                (part.mpn, part.model_dump_json(), part.updated_at.isoformat())
            )
            conn.commit()

    def is_part_banned(self, mpn: str) -> tuple[bool, str]:
        """Check if a part is banned."""
        part = self.get_part(mpn)
        if part and part.banned:
            return True, part.ban_reason
        return False, ""

    def get_approved_alternates(self, mpn: str) -> list[str]:
        """Get approved alternates for a part."""
        part = self.get_part(mpn)
        return part.approved_alternates if part else []

    def list_parts(self, limit: int = 100) -> list[PartKnowledge]:
        """List all parts."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT data FROM parts ORDER BY mpn LIMIT ?", (limit,))
            return [PartKnowledge.model_validate_json(row[0]) for row in cursor.fetchall()]

    # -------------------------------------------------------------------------
    # Supplier Knowledge
    # -------------------------------------------------------------------------

    def get_supplier(self, supplier_id: str) -> Optional[SupplierKnowledge]:
        """Get knowledge about a supplier."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT data FROM suppliers WHERE supplier_id = ?", (supplier_id,))
            row = cursor.fetchone()
            if row:
                return SupplierKnowledge.model_validate_json(row[0])
            return None

    def get_or_create_supplier(self, supplier_id: str, name: str) -> SupplierKnowledge:
        """Get or create supplier knowledge."""
        supplier = self.get_supplier(supplier_id)
        if not supplier:
            supplier = SupplierKnowledge(supplier_id=supplier_id, name=name)
            self._save_supplier(supplier)
        return supplier

    def _save_supplier(self, supplier: SupplierKnowledge) -> None:
        """Save supplier knowledge."""
        supplier.updated_at = datetime.utcnow()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO suppliers (supplier_id, data, updated_at) VALUES (?, ?, ?)",
                (supplier.supplier_id, supplier.model_dump_json(), supplier.updated_at.isoformat())
            )
            conn.commit()

    def get_supplier_trust(self, supplier_id: str) -> TrustLevel:
        """Get supplier trust level."""
        supplier = self.get_supplier(supplier_id)
        return supplier.trust_level if supplier else TrustLevel.LOW

    def list_suppliers(self, limit: int = 100) -> list[SupplierKnowledge]:
        """List all suppliers."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT data FROM suppliers ORDER BY supplier_id LIMIT ?", (limit,))
            return [SupplierKnowledge.model_validate_json(row[0]) for row in cursor.fetchall()]

    # -------------------------------------------------------------------------
    # Manual Updates
    # -------------------------------------------------------------------------

    def ban_part(self, mpn: str, reason: str, user: str) -> None:
        """Ban a part."""
        part = self.get_or_create_part(mpn)
        part.banned = True
        part.ban_reason = reason
        self._save_part(part)
        self._log_update(StoreUpdate(
            source=f"manual:{user}",
            update_type="update",
            entity_type="part",
            entity_id=mpn,
            field="banned",
            value=True,
            reason=reason,
        ))

    def unban_part(self, mpn: str, user: str) -> None:
        """Unban a part."""
        part = self.get_part(mpn)
        if part:
            part.banned = False
            part.ban_reason = ""
            self._save_part(part)
            self._log_update(StoreUpdate(
                source=f"manual:{user}",
                update_type="update",
                entity_type="part",
                entity_id=mpn,
                field="banned",
                value=False,
                reason="Unbanned",
            ))

    def add_alternate(self, mpn: str, alternate_mpn: str, user: str, reason: str) -> None:
        """Add an approved alternate for a part."""
        part = self.get_or_create_part(mpn)
        if alternate_mpn not in part.approved_alternates:
            part.approved_alternates.append(alternate_mpn)
            self._save_part(part)
            self._log_update(StoreUpdate(
                source=f"manual:{user}",
                update_type="append",
                entity_type="part",
                entity_id=mpn,
                field="approved_alternates",
                value=alternate_mpn,
                reason=reason,
            ))

    def add_part_note(self, mpn: str, note: str, user: str) -> None:
        """Add a note to a part."""
        part = self.get_or_create_part(mpn)
        dated_note = f"[{user} {date.today()}] {note}"
        part.notes.append(dated_note)
        self._save_part(part)

    def set_supplier_trust(self, supplier_id: str, trust: TrustLevel, user: str, reason: str) -> None:
        """Set supplier trust level."""
        supplier = self.get_supplier(supplier_id)
        if supplier:
            supplier.trust_level = trust
            self._save_supplier(supplier)
            self._log_update(StoreUpdate(
                source=f"manual:{user}",
                update_type="update",
                entity_type="supplier",
                entity_id=supplier_id,
                field="trust_level",
                value=trust.value,
                reason=reason,
            ))

    def add_supplier_note(self, supplier_id: str, note: str, user: str) -> None:
        """Add a note to a supplier."""
        supplier = self.get_supplier(supplier_id)
        if supplier:
            dated_note = f"[{user} {date.today()}] {note}"
            supplier.notes.append(dated_note)
            self._save_supplier(supplier)

    # -------------------------------------------------------------------------
    # Update Logging
    # -------------------------------------------------------------------------

    def _log_update(self, update: StoreUpdate) -> None:
        """Log an update for audit trail."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO update_log (update_id, data, timestamp) VALUES (?, ?, ?)",
                (update.update_id, update.model_dump_json(), update.timestamp.isoformat())
            )
            conn.commit()

    def apply_update(self, update: StoreUpdate) -> bool:
        """Apply a store update request from an agent."""
        try:
            if update.entity_type == "part":
                part = self.get_or_create_part(update.entity_id)
                if update.update_type == "update":
                    setattr(part, update.field, update.value)
                elif update.update_type == "append":
                    current = getattr(part, update.field)
                    if isinstance(current, list):
                        current.append(update.value)
                self._save_part(part)

            elif update.entity_type == "supplier":
                supplier = self.get_supplier(update.entity_id)
                if supplier:
                    if update.update_type == "update":
                        setattr(supplier, update.field, update.value)
                    elif update.update_type == "append":
                        current = getattr(supplier, update.field)
                        if isinstance(current, list):
                            current.append(update.value)
                    self._save_supplier(supplier)

            self._log_update(update)
            return True

        except Exception as e:
            print(f"Failed to apply update: {e}")
            return False


def seed_default_suppliers(store: OrgKnowledgeStore) -> None:
    """Seed default supplier knowledge."""
    suppliers = [
        SupplierKnowledge(
            supplier_id="digikey",
            name="Digi-Key",
            supplier_type=SupplierType.AUTHORIZED,
            trust_level=TrustLevel.HIGH,
            on_time_rate=0.95,
            quality_rate=0.99,
        ),
        SupplierKnowledge(
            supplier_id="mouser",
            name="Mouser",
            supplier_type=SupplierType.AUTHORIZED,
            trust_level=TrustLevel.HIGH,
            on_time_rate=0.92,
            quality_rate=0.98,
        ),
        SupplierKnowledge(
            supplier_id="newark",
            name="Newark",
            supplier_type=SupplierType.AUTHORIZED,
            trust_level=TrustLevel.HIGH,
            on_time_rate=0.90,
            quality_rate=0.97,
        ),
    ]
    for supplier in suppliers:
        if not store.get_supplier(supplier.supplier_id):
            store._save_supplier(supplier)
