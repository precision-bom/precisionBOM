"""Authentication chain - tries providers in order."""

from typing import Optional

from fastapi import HTTPException, Request

from .config import AuthConfig
from .identity import Identity, AuthMethod
from .providers.base import AuthProvider
from .providers.x402 import encode_payment_requirements


class AuthChain:
    """
    Chain of authentication providers.

    Tries each provider in order until one succeeds.
    """

    def __init__(self, config: AuthConfig):
        self._config = config
        self._providers: list[AuthProvider] = []

    def add_provider(self, provider: AuthProvider) -> "AuthChain":
        """Add a provider to the chain."""
        self._providers.append(provider)
        return self

    async def authenticate(self, request: Request) -> Identity:
        """
        Authenticate request using registered providers.

        Returns Identity on success, raises HTTPException on failure.
        """
        if self._config.allow_anonymous:
            # Return a default anonymous identity for development
            return Identity(
                client_id="anonymous",
                client_name="Anonymous",
                auth_method=AuthMethod.ANONYMOUS,
                scopes=["all"],
            )

        errors: list[tuple[str, HTTPException]] = []

        for provider in self._providers:
            if provider.can_handle(request):
                try:
                    identity = await provider.authenticate(request)
                    if identity:
                        return identity
                except HTTPException as e:
                    errors.append((provider.name, e))

        # No provider succeeded
        if errors:
            # Return the last error (most relevant)
            _, last_error = errors[-1]
            raise last_error

        # If x402 is enabled, return 402 Payment Required with payment options
        if self._config.x402_enabled:
            raise HTTPException(
                status_code=402,
                detail="Payment required. Provide API key, JWT, or x402 payment.",
                headers={
                    "WWW-Authenticate": "Bearer, ApiKey, X402",
                    "X-Payment-Required": encode_payment_requirements(self._config),
                },
            )

        raise HTTPException(
            status_code=401,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer, ApiKey"},
        )

    def get_provider(self, name: str) -> Optional[AuthProvider]:
        """Get a provider by name."""
        for provider in self._providers:
            if provider.name == name:
                return provider
        return None
