"""API key store with SQLite persistence."""

import hashlib
import secrets
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

from ..models import ApiKey


def _hash_key(raw_key: str) -> str:
    """Hash a raw API key using SHA-256."""
    return hashlib.sha256(raw_key.encode()).hexdigest()


def _generate_key() -> str:
    """Generate a new API key with pbom_sk_ prefix."""
    return f"pbom_sk_{secrets.token_urlsafe(32)}"


class ApiKeyStore:
    """Store for API keys with SQLite persistence."""

    def __init__(self, db_path: str = "data/api_keys.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        """Initialize the database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS api_keys (
                    key_id TEXT PRIMARY KEY,
                    hashed_key TEXT NOT NULL UNIQUE,
                    client_id TEXT,
                    name TEXT NOT NULL,
                    scopes TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    last_used TEXT,
                    is_active INTEGER DEFAULT 1
                )
            """)
            # Add client_id column if it doesn't exist (migration)
            try:
                conn.execute("ALTER TABLE api_keys ADD COLUMN client_id TEXT")
            except sqlite3.OperationalError:
                pass  # Column already exists
            conn.commit()

    def create_key(self, name: str, scopes: list[str] | None = None, client_id: str | None = None) -> tuple[ApiKey, str]:
        """
        Create a new API key.

        Args:
            name: Human-readable name for the key
            scopes: List of permission scopes (defaults to ["all"])
            client_id: Optional client ID this key belongs to

        Returns:
            Tuple of (ApiKey model, raw key string).
            The raw key is only returned once and should be shown to the user.
        """
        if scopes is None:
            scopes = ["all"]

        raw_key = _generate_key()
        hashed_key = _hash_key(raw_key)

        api_key = ApiKey(
            hashed_key=hashed_key,
            name=name,
            scopes=scopes,
            client_id=client_id,
        )

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO api_keys (key_id, hashed_key, client_id, name, scopes, created_at, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    api_key.key_id,
                    api_key.hashed_key,
                    api_key.client_id,
                    api_key.name,
                    ",".join(api_key.scopes),
                    api_key.created_at.isoformat(),
                    1,
                ),
            )
            conn.commit()

        return api_key, raw_key

    def validate_key(self, raw_key: str) -> Optional[ApiKey]:
        """
        Validate a raw API key.

        If valid, updates last_used timestamp and returns the ApiKey.
        If invalid or inactive, returns None.
        """
        hashed_key = _hash_key(raw_key)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT key_id, hashed_key, client_id, name, scopes, created_at, last_used, is_active
                FROM api_keys
                WHERE hashed_key = ? AND is_active = 1
                """,
                (hashed_key,),
            )
            row = cursor.fetchone()

            if not row:
                return None

            # Update last_used
            now = datetime.utcnow()
            conn.execute(
                "UPDATE api_keys SET last_used = ? WHERE key_id = ?",
                (now.isoformat(), row[0]),
            )
            conn.commit()

            return ApiKey(
                key_id=row[0],
                hashed_key=row[1],
                client_id=row[2],
                name=row[3],
                scopes=row[4].split(",") if row[4] else ["all"],
                created_at=datetime.fromisoformat(row[5]),
                last_used=now,
                is_active=bool(row[7]),
            )

    def revoke_key(self, key_id: str) -> bool:
        """
        Revoke an API key by setting is_active to False.

        Returns True if the key was found and revoked, False otherwise.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "UPDATE api_keys SET is_active = 0 WHERE key_id = ?",
                (key_id,),
            )
            conn.commit()
            return cursor.rowcount > 0

    def list_keys(self, client_id: str | None = None) -> list[ApiKey]:
        """
        List API keys, optionally filtered by client_id.

        Note: Returns ApiKey objects with hashed_key field (not the raw key).
        """
        with sqlite3.connect(self.db_path) as conn:
            if client_id:
                cursor = conn.execute(
                    """
                    SELECT key_id, hashed_key, client_id, name, scopes, created_at, last_used, is_active
                    FROM api_keys
                    WHERE client_id = ?
                    ORDER BY created_at DESC
                    """,
                    (client_id,),
                )
            else:
                cursor = conn.execute(
                    """
                    SELECT key_id, hashed_key, client_id, name, scopes, created_at, last_used, is_active
                    FROM api_keys
                    ORDER BY created_at DESC
                    """
                )

            keys = []
            for row in cursor.fetchall():
                keys.append(
                    ApiKey(
                        key_id=row[0],
                        hashed_key=row[1],
                        client_id=row[2],
                        name=row[3],
                        scopes=row[4].split(",") if row[4] else ["all"],
                        created_at=datetime.fromisoformat(row[5]),
                        last_used=datetime.fromisoformat(row[6]) if row[6] else None,
                        is_active=bool(row[7]),
                    )
                )
            return keys

    def get_key(self, key_id: str) -> Optional[ApiKey]:
        """Get a specific API key by its ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT key_id, hashed_key, client_id, name, scopes, created_at, last_used, is_active
                FROM api_keys
                WHERE key_id = ?
                """,
                (key_id,),
            )
            row = cursor.fetchone()

            if not row:
                return None

            return ApiKey(
                key_id=row[0],
                hashed_key=row[1],
                client_id=row[2],
                name=row[3],
                scopes=row[4].split(",") if row[4] else ["all"],
                created_at=datetime.fromisoformat(row[5]),
                last_used=datetime.fromisoformat(row[6]) if row[6] else None,
                is_active=bool(row[7]),
            )
