"""Unified identity model for authentication."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel


class AuthMethod(str, Enum):
    """Authentication method used to establish identity."""

    API_KEY = "api_key"
    JWT = "jwt"
    X402 = "x402"
    ANONYMOUS = "anonymous"


class Identity(BaseModel):
    """
    Unified identity context from any authentication method.

    This is the core abstraction that endpoints receive, regardless of
    whether the user authenticated via API key or JWT token.
    """

    client_id: str
    client_name: str
    auth_method: AuthMethod
    scopes: list[str]

    # API Key specific fields
    api_key_id: Optional[str] = None
    api_key_name: Optional[str] = None

    # JWT specific fields
    subject: Optional[str] = None  # OIDC 'sub' claim (user ID)
    email: Optional[str] = None
    issuer: Optional[str] = None

    # x402 specific fields
    wallet_address: Optional[str] = None  # Ethereum address from payment

    def has_scope(self, scope: str) -> bool:
        """Check if identity has a specific scope."""
        return "all" in self.scopes or scope in self.scopes

    @property
    def is_admin(self) -> bool:
        """Check if identity has admin privileges (can access all clients)."""
        return "admin" in self.scopes

    def can_access_client(self, target_client_id: str) -> bool:
        """Check if identity can access resources for a given client."""
        return self.is_admin or self.client_id == target_client_id

    def effective_client_id(self, requested_client_id: str | None = None) -> str | None:
        """
        Get effective client_id for filtering.

        For admins: returns requested_client_id (or None for all clients)
        For regular users: always returns their own client_id

        Args:
            requested_client_id: Optional client to filter by (admin only)

        Returns:
            Client ID for filtering, or None for no filter (admin viewing all)
        """
        if self.is_admin:
            return requested_client_id  # Admin can filter by any client or None for all
        return self.client_id  # Regular users always scoped to their client
