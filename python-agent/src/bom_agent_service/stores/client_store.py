"""Client (organization/tenant) store with PostgreSQL persistence."""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from ..db import get_session
from ..db.tables import ClientTable
from ..models import Client


class ClientStore:
    """Store for clients (tenants) with PostgreSQL persistence."""

    def __init__(self, session: Optional[Session] = None):
        """
        Initialize store.

        Args:
            session: Optional SQLAlchemy session. If not provided,
                     will create new sessions per operation.
        """
        self._session = session

    def _get_session(self) -> Session:
        """Get session - either injected or create new one."""
        if self._session:
            return self._session
        return next(get_session())

    def _close_session(self, session: Session) -> None:
        """Close session if it was created by this store."""
        if session is not self._session:
            session.close()

    def _row_to_client(self, row: ClientTable) -> Client:
        """Convert database row to Client model."""
        return Client(
            client_id=row.client_id,
            name=row.name,
            slug=row.slug,
            is_active=row.is_active,
            oidc_issuer=row.oidc_issuer,
            oidc_audience=row.oidc_audience,
            wallet_address=row.wallet_address,
            settings=row.settings or {},
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

    def create_client(
        self,
        name: str,
        slug: str,
        oidc_issuer: Optional[str] = None,
        oidc_audience: Optional[str] = None,
        wallet_address: Optional[str] = None,
        settings: Optional[dict] = None,
    ) -> Client:
        """Create a new client."""
        client = Client(
            name=name,
            slug=slug,
            oidc_issuer=oidc_issuer,
            oidc_audience=oidc_audience,
            wallet_address=wallet_address,
            settings=settings or {},
        )

        session = self._get_session()
        try:
            row = ClientTable(
                client_id=client.client_id,
                name=client.name,
                slug=client.slug,
                is_active=client.is_active,
                oidc_issuer=client.oidc_issuer,
                oidc_audience=client.oidc_audience,
                wallet_address=client.wallet_address,
                settings=client.settings,
            )
            session.add(row)
            session.commit()
            session.refresh(row)
            return self._row_to_client(row)
        finally:
            self._close_session(session)

    def get_client(self, client_id: str) -> Optional[Client]:
        """Get client by ID."""
        session = self._get_session()
        try:
            stmt = select(ClientTable).where(ClientTable.client_id == client_id)
            row = session.execute(stmt).scalar_one_or_none()
            if row:
                return self._row_to_client(row)
            return None
        finally:
            self._close_session(session)

    def get_client_by_slug(self, slug: str) -> Optional[Client]:
        """Get client by slug."""
        session = self._get_session()
        try:
            stmt = select(ClientTable).where(ClientTable.slug == slug)
            row = session.execute(stmt).scalar_one_or_none()
            if row:
                return self._row_to_client(row)
            return None
        finally:
            self._close_session(session)

    def get_client_by_oidc_issuer(self, issuer: str) -> Optional[Client]:
        """Get client by OIDC issuer URL."""
        session = self._get_session()
        try:
            stmt = select(ClientTable).where(
                ClientTable.oidc_issuer == issuer,
                ClientTable.is_active == True,  # noqa: E712
            )
            row = session.execute(stmt).scalar_one_or_none()
            if row:
                return self._row_to_client(row)
            return None
        finally:
            self._close_session(session)

    def get_client_by_oidc_audience(self, audience: str) -> Optional[Client]:
        """Get client by OIDC audience."""
        session = self._get_session()
        try:
            stmt = select(ClientTable).where(
                ClientTable.oidc_audience == audience,
                ClientTable.is_active == True,  # noqa: E712
            )
            row = session.execute(stmt).scalar_one_or_none()
            if row:
                return self._row_to_client(row)
            return None
        finally:
            self._close_session(session)

    def get_client_by_wallet(self, wallet_address: str) -> Optional[Client]:
        """Get client by x402 wallet address."""
        session = self._get_session()
        try:
            # Normalize to lowercase for comparison
            normalized = wallet_address.lower()
            stmt = select(ClientTable).where(
                ClientTable.wallet_address == normalized,
                ClientTable.is_active == True,  # noqa: E712
            )
            row = session.execute(stmt).scalar_one_or_none()
            if row:
                return self._row_to_client(row)
            return None
        finally:
            self._close_session(session)

    def list_clients(self, include_inactive: bool = False) -> list[Client]:
        """List all clients."""
        session = self._get_session()
        try:
            stmt = select(ClientTable).order_by(ClientTable.created_at.desc())
            if not include_inactive:
                stmt = stmt.where(ClientTable.is_active == True)  # noqa: E712
            rows = session.execute(stmt).scalars().all()
            return [self._row_to_client(row) for row in rows]
        finally:
            self._close_session(session)

    def update_client(
        self,
        client_id: str,
        name: Optional[str] = None,
        is_active: Optional[bool] = None,
        oidc_issuer: Optional[str] = None,
        oidc_audience: Optional[str] = None,
        settings: Optional[dict] = None,
    ) -> Optional[Client]:
        """Update a client. Returns updated client or None if not found."""
        session = self._get_session()
        try:
            values = {"updated_at": datetime.now(timezone.utc)}
            if name is not None:
                values["name"] = name
            if is_active is not None:
                values["is_active"] = is_active
            if oidc_issuer is not None:
                values["oidc_issuer"] = oidc_issuer
            if oidc_audience is not None:
                values["oidc_audience"] = oidc_audience
            if settings is not None:
                values["settings"] = settings

            stmt = (
                update(ClientTable)
                .where(ClientTable.client_id == client_id)
                .values(**values)
            )
            result = session.execute(stmt)
            session.commit()

            if result.rowcount == 0:
                return None

            return self.get_client(client_id)
        finally:
            self._close_session(session)

    def deactivate_client(self, client_id: str) -> bool:
        """Deactivate a client. Returns True if found and deactivated."""
        session = self._get_session()
        try:
            stmt = (
                update(ClientTable)
                .where(ClientTable.client_id == client_id)
                .values(is_active=False, updated_at=datetime.now(timezone.utc))
            )
            result = session.execute(stmt)
            session.commit()
            return result.rowcount > 0
        finally:
            self._close_session(session)
