"""x402 payment authentication provider."""

import base64
import hashlib
import json
from typing import Optional

import httpx
from fastapi import HTTPException, Request

from ...models import Client
from ...stores import ClientStore
from ..config import AuthConfig
from ..identity import Identity, AuthMethod
from .base import AuthProvider


class X402Provider(AuthProvider):
    """
    x402 payment authentication provider.

    Authenticates requests by verifying x402 payment signatures via a facilitator.
    Creates ephemeral clients for wallet addresses to enable project access.
    """

    def __init__(
        self,
        config: AuthConfig,
        client_store: ClientStore,
    ):
        self._config = config
        self._client_store = client_store
        self._http = httpx.AsyncClient(timeout=30.0)

    @property
    def name(self) -> str:
        return "x402"

    def can_handle(self, request: Request) -> bool:
        """Check if request has X-Payment header."""
        return "x-payment" in request.headers

    async def authenticate(self, request: Request) -> Optional[Identity]:
        """
        Authenticate using x402 payment.

        1. Extract and decode payment payload from X-Payment header
        2. Verify payment with facilitator
        3. Settle payment
        4. Create/find ephemeral client for wallet
        5. Return Identity
        """
        payment_header = request.headers.get("x-payment")
        if not payment_header:
            return None

        # Decode payment payload
        try:
            payload = self._decode_payment(payment_header)
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid payment payload: {e}",
            )

        # Verify payment with facilitator
        verification = await self._verify_payment(payload)
        if not verification.get("valid"):
            raise HTTPException(
                status_code=402,
                detail=f"Payment verification failed: {verification.get('error', 'Unknown error')}",
                headers=self._payment_required_headers(),
            )

        # Settle payment
        settlement = await self._settle_payment(payload)
        if not settlement.get("success"):
            raise HTTPException(
                status_code=402,
                detail=f"Payment settlement failed: {settlement.get('error', 'Unknown error')}",
                headers=self._payment_required_headers(),
            )

        # Extract payer wallet address
        wallet_address = verification.get("payer") or payload.get("payer")
        if not wallet_address:
            raise HTTPException(
                status_code=400,
                detail="Could not determine payer wallet address",
            )

        # Normalize wallet address (lowercase)
        wallet_address = wallet_address.lower()

        # Get or create ephemeral client for this wallet
        client = self._get_or_create_ephemeral_client(wallet_address)

        return Identity(
            client_id=client.client_id,
            client_name=client.name,
            auth_method=AuthMethod.X402,
            scopes=["all"],  # Full access to their own resources
            wallet_address=wallet_address,
        )

    def _decode_payment(self, payment_header: str) -> dict:
        """Decode base64-encoded payment payload."""
        try:
            decoded = base64.b64decode(payment_header)
            return json.loads(decoded)
        except Exception:
            # Try as raw JSON if not base64
            return json.loads(payment_header)

    async def _verify_payment(self, payload: dict) -> dict:
        """Verify payment with facilitator."""
        try:
            response = await self._http.post(
                f"{self._config.x402_facilitator_url}/verify",
                json={
                    "payload": payload,
                    "requirements": {
                        "network": self._config.x402_network,
                        "recipient": self._config.x402_pay_to_address,
                    },
                },
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            return {"valid": False, "error": str(e)}

    async def _settle_payment(self, payload: dict) -> dict:
        """Settle payment with facilitator."""
        try:
            response = await self._http.post(
                f"{self._config.x402_facilitator_url}/settle",
                json={"payload": payload},
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            return {"success": False, "error": str(e)}

    def _get_or_create_ephemeral_client(self, wallet_address: str) -> Client:
        """
        Get or create an ephemeral client for a wallet address.

        Uses wallet_address field for lookup, with deterministic slug as fallback.
        """
        # Try to find by wallet address first
        client = self._client_store.get_client_by_wallet(wallet_address)
        if client:
            return client

        # Fallback: try by deterministic slug (for backwards compatibility)
        wallet_hash = hashlib.sha256(wallet_address.encode()).hexdigest()[:12]
        slug = f"x402-{wallet_hash}"
        client = self._client_store.get_client_by_slug(slug)
        if client:
            return client

        # Create new ephemeral client
        short_addr = f"{wallet_address[:6]}...{wallet_address[-4:]}"
        return self._client_store.create_client(
            name=f"x402 Wallet {short_addr}",
            slug=slug,
            wallet_address=wallet_address,
            settings={"ephemeral": True},
        )

    def _payment_required_headers(self) -> dict[str, str]:
        """Generate headers for 402 Payment Required response."""
        requirements = {
            "network": self._config.x402_network,
            "recipient": self._config.x402_pay_to_address,
            "asset": "USDC",
            "basePrice": str(self._config.x402_base_price),
            "perItemPrice": str(self._config.x402_per_item_price),
        }
        encoded = base64.b64encode(json.dumps(requirements).encode()).decode()
        return {
            "X-Payment-Required": encoded,
            "WWW-Authenticate": "X402",
        }


def encode_payment_requirements(
    config: AuthConfig,
    item_count: int = 0,
) -> str:
    """
    Encode payment requirements for 402 response header.

    Args:
        config: Auth config with x402 settings
        item_count: Number of BOM line items (for dynamic pricing)

    Returns:
        Base64-encoded payment requirements JSON
    """
    total_price = config.x402_base_price + (config.x402_per_item_price * item_count)

    requirements = {
        "price": str(total_price),
        "network": config.x402_network,
        "recipient": config.x402_pay_to_address,
        "asset": "USDC",
        "description": f"BOM Analysis ({item_count} items)" if item_count else "BOM Analysis",
    }
    return base64.b64encode(json.dumps(requirements).encode()).decode()
