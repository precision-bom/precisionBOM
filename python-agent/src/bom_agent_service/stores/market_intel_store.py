"""Store for market intelligence data with SQLite persistence."""

import json
import sqlite3
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from ..models.market_intel import (
    MarketIntelItem,
    MarketIntelReport,
    IntelCategory,
    IntelSentiment,
)


class MarketIntelStore:
    """
    Store for market intelligence data.
    Caches scraped intel with TTL expiration.
    """

    def __init__(self, db_path: str = "data/market_intel.db", ttl_hours: int = 24):
        """Initialize the store with SQLite persistence."""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.ttl_hours = ttl_hours
        self._init_db()

    def _init_db(self) -> None:
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS intel_items (
                    intel_id TEXT PRIMARY KEY,
                    source_url TEXT NOT NULL,
                    title TEXT,
                    summary TEXT,
                    full_text TEXT,
                    category TEXT,
                    sentiment TEXT,
                    relevance_score REAL,
                    related_mpns JSON,
                    related_manufacturers JSON,
                    keywords JSON,
                    scraped_at TEXT,
                    expires_at TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS intel_reports (
                    report_id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    generated_at TEXT,
                    data JSON NOT NULL
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_intel_items_mpn
                ON intel_items (related_mpns)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_reports_project
                ON intel_reports (project_id)
            """)
            conn.commit()

    def store_intel_item(self, item: MarketIntelItem) -> None:
        """Store a single intel item."""
        if not item.intel_id:
            item.intel_id = str(uuid.uuid4())

        if not item.expires_at:
            item.expires_at = datetime.utcnow() + timedelta(hours=self.ttl_hours)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO intel_items
                (intel_id, source_url, title, summary, full_text, category, sentiment,
                 relevance_score, related_mpns, related_manufacturers, keywords,
                 scraped_at, expires_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item.intel_id,
                item.source_url,
                item.title,
                item.summary,
                item.full_text,
                item.category.value,
                item.sentiment.value,
                item.relevance_score,
                json.dumps(item.related_mpns),
                json.dumps(item.related_manufacturers),
                json.dumps(item.keywords),
                item.scraped_at.isoformat(),
                item.expires_at.isoformat() if item.expires_at else None,
            ))
            conn.commit()

    def store_intel_items(self, items: list[MarketIntelItem]) -> None:
        """Store multiple intel items."""
        for item in items:
            self.store_intel_item(item)

    def get_intel_item(self, intel_id: str) -> Optional[MarketIntelItem]:
        """Get a single intel item by ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT * FROM intel_items WHERE intel_id = ? AND (expires_at IS NULL OR expires_at > ?)",
                (intel_id, datetime.utcnow().isoformat())
            )
            row = cursor.fetchone()
            if row:
                return self._row_to_item(row)
        return None

    def get_intel_for_mpn(self, mpn: str) -> list[MarketIntelItem]:
        """Get all intel items related to a specific MPN."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT * FROM intel_items
                WHERE related_mpns LIKE ?
                AND (expires_at IS NULL OR expires_at > ?)
                ORDER BY relevance_score DESC, scraped_at DESC
            """, (f'%"{mpn}"%', datetime.utcnow().isoformat()))
            return [self._row_to_item(row) for row in cursor.fetchall()]

    def get_intel_for_manufacturer(self, manufacturer: str) -> list[MarketIntelItem]:
        """Get all intel items related to a manufacturer."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT * FROM intel_items
                WHERE LOWER(related_manufacturers) LIKE LOWER(?)
                AND (expires_at IS NULL OR expires_at > ?)
                ORDER BY relevance_score DESC, scraped_at DESC
            """, (f'%{manufacturer}%', datetime.utcnow().isoformat()))
            return [self._row_to_item(row) for row in cursor.fetchall()]

    def get_recent_intel(
        self,
        limit: int = 50,
        category: Optional[IntelCategory] = None,
        min_relevance: float = 0.0,
    ) -> list[MarketIntelItem]:
        """Get recent intel items with optional filtering."""
        query = """
            SELECT * FROM intel_items
            WHERE (expires_at IS NULL OR expires_at > ?)
            AND relevance_score >= ?
        """
        params = [datetime.utcnow().isoformat(), min_relevance]

        if category:
            query += " AND category = ?"
            params.append(category.value)

        query += " ORDER BY scraped_at DESC LIMIT ?"
        params.append(limit)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(query, params)
            return [self._row_to_item(row) for row in cursor.fetchall()]

    def get_shortage_alerts(self) -> list[MarketIntelItem]:
        """Get intel items categorized as component shortages."""
        return self.get_recent_intel(
            limit=100,
            category=IntelCategory.COMPONENT_SHORTAGE,
            min_relevance=0.5,
        )

    def store_report(self, report: MarketIntelReport) -> None:
        """Store a market intelligence report."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO intel_reports (report_id, project_id, generated_at, data)
                VALUES (?, ?, ?, ?)
            """, (
                report.report_id,
                report.project_id,
                report.generated_at.isoformat(),
                report.model_dump_json(),
            ))
            conn.commit()

    def get_report(self, report_id: str) -> Optional[MarketIntelReport]:
        """Get a report by ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT data FROM intel_reports WHERE report_id = ?",
                (report_id,)
            )
            row = cursor.fetchone()
            if row:
                return MarketIntelReport.model_validate_json(row[0])
        return None

    def get_reports_for_project(self, project_id: str) -> list[MarketIntelReport]:
        """Get all reports for a project."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT data FROM intel_reports WHERE project_id = ? ORDER BY generated_at DESC",
                (project_id,)
            )
            return [MarketIntelReport.model_validate_json(row[0]) for row in cursor.fetchall()]

    def cleanup_expired(self) -> int:
        """Remove expired intel items. Returns count of removed items."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "DELETE FROM intel_items WHERE expires_at IS NOT NULL AND expires_at < ?",
                (datetime.utcnow().isoformat(),)
            )
            conn.commit()
            return cursor.rowcount

    def _row_to_item(self, row: tuple) -> MarketIntelItem:
        """Convert a database row to MarketIntelItem."""
        return MarketIntelItem(
            intel_id=row[0],
            source_url=row[1],
            title=row[2] or "",
            summary=row[3] or "",
            full_text=row[4] or "",
            category=IntelCategory(row[5]) if row[5] else IntelCategory.GENERAL,
            sentiment=IntelSentiment(row[6]) if row[6] else IntelSentiment.NEUTRAL,
            relevance_score=row[7] or 0.5,
            related_mpns=json.loads(row[8]) if row[8] else [],
            related_manufacturers=json.loads(row[9]) if row[9] else [],
            keywords=json.loads(row[10]) if row[10] else [],
            scraped_at=datetime.fromisoformat(row[11]) if row[11] else datetime.utcnow(),
            expires_at=datetime.fromisoformat(row[12]) if row[12] else None,
        )
