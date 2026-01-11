"""JWT/OIDC authentication provider."""

from typing import Optional

import httpx
from fastapi import HTTPException, Request
from jose import jwt, JWTError
from jose.exceptions import ExpiredSignatureError

from ...stores import ClientStore
from ..config import AuthConfig
from ..identity import Identity, AuthMethod
from .base import AuthProvider


class JWTProvider(AuthProvider):
    """JWT/OIDC authentication provider supporting multiple issuers."""

    def __init__(self, config: AuthConfig, client_store: ClientStore):
        self._config = config
        self._client_store = client_store
        self._jwks_cache: dict[str, dict] = {}

    @property
    def name(self) -> str:
        return "jwt"

    def can_handle(self, request: Request) -> bool:
        """Check if request has Bearer token in Authorization header."""
        auth = request.headers.get("authorization", "")
        return auth.lower().startswith("bearer ")

    async def authenticate(self, request: Request) -> Optional[Identity]:
        """
        Authenticate using JWT token.

        Validates the Bearer token, fetches JWKS from issuer, and returns Identity.
        """
        auth = request.headers.get("authorization", "")
        if not auth.lower().startswith("bearer "):
            return None

        token = auth[7:]  # Strip "Bearer "

        try:
            # Decode without verification first to get issuer
            unverified = jwt.get_unverified_claims(token)
            issuer = unverified.get("iss")

            if not issuer:
                raise HTTPException(status_code=401, detail="Token missing issuer")

            # Find client by OIDC issuer
            client = self._client_store.get_client_by_oidc_issuer(issuer)
            if not client:
                # Check if issuer is in global allowed issuers
                if issuer not in self._config.allowed_issuers:
                    raise HTTPException(
                        status_code=401, detail=f"Unknown token issuer: {issuer}"
                    )
                # For global issuers, find client by audience
                audience = unverified.get("aud")
                if isinstance(audience, list):
                    audience = audience[0] if audience else None
                if audience:
                    client = self._client_store.get_client_by_oidc_audience(audience)

            if not client or not client.is_active:
                raise HTTPException(
                    status_code=401, detail="Client not found or inactive"
                )

            # Get JWKS and verify token
            jwks = await self._get_jwks(issuer)

            # Verify token
            claims = jwt.decode(
                token,
                jwks,
                algorithms=["RS256", "RS384", "RS512"],
                audience=client.oidc_audience or self._config.default_audience,
                issuer=issuer,
            )

            # Extract scopes from token
            scopes = self._extract_scopes(claims)

            return Identity(
                client_id=client.client_id,
                client_name=client.name,
                auth_method=AuthMethod.JWT,
                scopes=scopes,
                subject=claims.get("sub"),
                email=claims.get("email"),
                issuer=issuer,
            )

        except ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except JWTError as e:
            raise HTTPException(status_code=401, detail=f"Invalid token: {e}")

    def _extract_scopes(self, claims: dict) -> list[str]:
        """Extract scopes from JWT claims (handles various formats)."""
        # Auth0 style: space-separated "scope" claim
        if "scope" in claims:
            return claims["scope"].split()
        # Keycloak style: "realm_access.roles" array
        if "realm_access" in claims:
            return claims["realm_access"].get("roles", [])
        # Custom claim: "scopes" as list or string
        if "scopes" in claims:
            scopes = claims["scopes"]
            if isinstance(scopes, list):
                return scopes
            return scopes.split()
        # Default: full access
        return ["all"]

    async def _get_jwks(self, issuer: str) -> dict:
        """Get JWKS for issuer with caching."""
        if issuer in self._jwks_cache:
            return self._jwks_cache[issuer]

        # Fetch OIDC discovery document
        discovery_url = f"{issuer.rstrip('/')}/.well-known/openid-configuration"
        async with httpx.AsyncClient() as client:
            resp = await client.get(discovery_url)
            resp.raise_for_status()
            config = resp.json()

            jwks_url = config["jwks_uri"]
            resp = await client.get(jwks_url)
            resp.raise_for_status()
            jwks = resp.json()

        self._jwks_cache[issuer] = jwks
        return jwks
