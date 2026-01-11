"""Authentication configuration."""

import os
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class OIDCProviderConfig(BaseModel):
    """Configuration for a specific OIDC provider."""

    name: str  # e.g., "auth0", "okta", "keycloak"
    issuer: str  # e.g., "https://your-tenant.us.auth0.com/"
    audience: Optional[str] = None  # Expected audience claim
    client_id: Optional[str] = None  # For client credentials flow


class AuthConfig(BaseSettings):
    """Authentication configuration from environment."""

    # Enable/disable auth methods
    api_key_auth_enabled: bool = True
    jwt_auth_enabled: bool = False
    x402_enabled: bool = False

    # For development: allow unauthenticated access
    allow_anonymous: bool = False

    # x402 payment settings
    x402_network: str = "base-sepolia"  # or "base" for mainnet
    x402_pay_to_address: str = ""  # Wallet address to receive payments
    x402_facilitator_url: str = "https://x402.org/facilitator"
    x402_base_price: Decimal = Decimal("0.05")  # USD base price per project
    x402_per_item_price: Decimal = Decimal("0.005")  # USD per BOM line item

    # JWT settings
    default_audience: str = "bom-agent-api"

    # OIDC provider configs (populated from env)
    oidc_providers: list[OIDCProviderConfig] = Field(default_factory=list)

    model_config = {
        "env_prefix": "AUTH_",
        "env_file": ".env",
        "extra": "ignore",
    }

    @property
    def allowed_issuers(self) -> list[str]:
        """Get list of allowed OIDC issuers."""
        return [p.issuer for p in self.oidc_providers]

    @classmethod
    def from_env(cls) -> "AuthConfig":
        """Load auth config from environment variables."""
        config = cls()

        # Parse OIDC providers from env
        # Format: AUTH_OIDC_PROVIDER_<N>_ISSUER, AUTH_OIDC_PROVIDER_<N>_AUDIENCE
        providers = []
        for i in range(10):  # Support up to 10 providers
            issuer = os.getenv(f"AUTH_OIDC_PROVIDER_{i}_ISSUER")
            if issuer:
                providers.append(
                    OIDCProviderConfig(
                        name=os.getenv(f"AUTH_OIDC_PROVIDER_{i}_NAME", f"provider_{i}"),
                        issuer=issuer,
                        audience=os.getenv(f"AUTH_OIDC_PROVIDER_{i}_AUDIENCE"),
                        client_id=os.getenv(f"AUTH_OIDC_PROVIDER_{i}_CLIENT_ID"),
                    )
                )

        config.oidc_providers = providers
        return config
