"""API Key authentication provider."""

from typing import Optional

from fastapi import HTTPException, Request

from ...stores import ApiKeyStore, ClientStore
from ..identity import Identity, AuthMethod
from .base import AuthProvider


class ApiKeyProvider(AuthProvider):
    """API Key authentication provider using X-API-Key header."""

    def __init__(
        self,
        api_key_store: ApiKeyStore,
        client_store: ClientStore,
    ):
        self._api_key_store = api_key_store
        self._client_store = client_store

    @property
    def name(self) -> str:
        return "api_key"

    def can_handle(self, request: Request) -> bool:
        """Check if request has X-API-Key header."""
        return "x-api-key" in request.headers

    async def authenticate(self, request: Request) -> Optional[Identity]:
        """
        Authenticate using API key.

        Validates the X-API-Key header and returns Identity on success.
        """
        api_key = request.headers.get("x-api-key")
        if not api_key:
            return None

        validated = self._api_key_store.validate_key(api_key)
        if not validated:
            raise HTTPException(
                status_code=401,
                detail="Invalid API key",
                headers={"WWW-Authenticate": "ApiKey"},
            )

        # Get client info
        client = self._client_store.get_client(validated.client_id)
        if not client or not client.is_active:
            raise HTTPException(
                status_code=401,
                detail="Client inactive or not found",
            )

        return Identity(
            client_id=validated.client_id,
            client_name=client.name,
            auth_method=AuthMethod.API_KEY,
            scopes=validated.scopes,
            api_key_id=validated.key_id,
            api_key_name=validated.name,
        )
