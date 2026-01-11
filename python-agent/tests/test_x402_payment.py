"""End-to-end tests for x402 payment authentication flow.

Test Cases:
x402 Payment Flow:
- X402_1: Request without auth returns 402 Payment Required when x402 enabled
- X402_2: 402 response includes payment requirements header
- X402_3: Valid x402 payment creates project and returns access_token
- X402_4: Access token grants access to the created project
- X402_5: Access token cannot access other projects
- X402_7: Project-scoped token can access project trace
- X402_8: Project-scoped token can delete project
- X402_9: API key auth still works when x402 is enabled
- X402_10: Invalid payment returns 402

Identity Model:
- X402_IDN1: AuthMethod.X402 is a valid auth method
- X402_IDN2: Identity with X402 auth has wallet_address
"""

import base64
import json
from contextlib import asynccontextmanager
from decimal import Decimal
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
import httpx


# =============================================================================
# Fixtures for x402 Testing
# =============================================================================

@pytest.fixture
def mock_facilitator_verify_success():
    """Mock successful payment verification from facilitator."""
    return {
        "valid": True,
        "payer": "0x1234567890abcdef1234567890abcdef12345678",
        "amount": "0.10",
        "network": "base-sepolia",
    }


@pytest.fixture
def mock_facilitator_settle_success():
    """Mock successful payment settlement from facilitator."""
    return {
        "success": True,
        "txHash": "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
        "status": "settled",
    }


@pytest.fixture
def valid_payment_header():
    """Create a valid-looking x402 payment header (payload will be mocked)."""
    payload = {
        "payer": "0x1234567890abcdef1234567890abcdef12345678",
        "amount": "0.10",
        "recipient": "0x0000000000000000000000000000000000000000",
        "network": "base-sepolia",
        "signature": "0xmockedsignature",
    }
    return base64.b64encode(json.dumps(payload).encode()).decode()


@pytest.fixture
def x402_enabled_config():
    """Auth config with x402 enabled."""
    from bom_agent_service.auth.config import AuthConfig
    return AuthConfig(
        api_key_auth_enabled=True,
        jwt_auth_enabled=False,
        x402_enabled=True,
        x402_network="base-sepolia",
        x402_pay_to_address="0x0000000000000000000000000000000000000000",
        x402_base_price=Decimal("0.05"),
        x402_per_item_price=Decimal("0.005"),
    )


@pytest.fixture
def x402_app(x402_enabled_config):
    """Create FastAPI app with x402 enabled."""
    from bom_agent_service.main import app
    from bom_agent_service.auth.dependencies import reset_auth_config
    import bom_agent_service.auth.dependencies as deps_module

    # Reset and set new config
    reset_auth_config()
    deps_module._config = x402_enabled_config

    yield app

    # Reset after test
    reset_auth_config()


@pytest_asyncio.fixture
async def x402_unauthenticated_client(x402_app):
    """Client without any authentication for x402 tests."""
    transport = httpx.ASGITransport(app=x402_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@asynccontextmanager
async def mock_x402_payment(verify_result, settle_result):
    """Context manager to mock x402 payment verification and settlement."""
    with patch(
        "bom_agent_service.auth.providers.x402.X402Provider._verify_payment",
        new_callable=AsyncMock,
        return_value=verify_result
    ), patch(
        "bom_agent_service.auth.providers.x402.X402Provider._settle_payment",
        new_callable=AsyncMock,
        return_value=settle_result
    ):
        yield


# =============================================================================
# x402 Payment Flow Tests
# =============================================================================

@pytest.mark.asyncio
async def test_x402_1_request_without_auth_returns_402(
    x402_app, x402_unauthenticated_client
):
    """X402_1: Request without auth returns 402 Payment Required when x402 enabled."""
    response = await x402_unauthenticated_client.get("/projects")

    assert response.status_code == 402
    assert "Payment required" in response.json().get("detail", "")


@pytest.mark.asyncio
async def test_x402_2_402_response_includes_payment_requirements(
    x402_app, x402_unauthenticated_client
):
    """X402_2: 402 response includes X-Payment-Required header with payment details."""
    response = await x402_unauthenticated_client.get("/projects")

    assert response.status_code == 402
    assert "X-Payment-Required" in response.headers or "x-payment-required" in response.headers

    # Decode and verify payment requirements
    payment_header = response.headers.get("X-Payment-Required") or response.headers.get("x-payment-required")
    requirements = json.loads(base64.b64decode(payment_header))

    assert "price" in requirements or "basePrice" in requirements
    assert "network" in requirements
    assert "recipient" in requirements


@pytest.mark.asyncio
async def test_x402_3_valid_payment_creates_project_with_access_token(
    x402_app,
    valid_payment_header,
    mock_facilitator_verify_success,
    mock_facilitator_settle_success,
    sample_bom_csv,
):
    """X402_3: Valid x402 payment creates project and returns access_token."""

    async with mock_x402_payment(mock_facilitator_verify_success, mock_facilitator_settle_success):
        transport = httpx.ASGITransport(app=x402_app)
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://test",
            headers={"X-Payment": valid_payment_header}
        ) as client:
            files = {"bom_file": ("test_bom.csv", sample_bom_csv, "text/csv")}
            data = {"project_name": "X402 Test Project"}

            response = await client.post("/projects", files=files, data=data)

    assert response.status_code == 200
    result = response.json()

    # Should have access_token for x402 payments
    assert "access_token" in result
    assert result["access_token"] is not None
    assert result["access_token"].startswith("pbom_sk_")

    # Should have wallet address
    assert "wallet_address" in result
    assert result["wallet_address"] == "0x1234567890abcdef1234567890abcdef12345678"

    # Should have project details
    assert "project_id" in result
    assert result["project_name"] == "X402 Test Project"


@pytest.mark.asyncio
async def test_x402_4_access_token_grants_project_access(
    x402_app,
    valid_payment_header,
    mock_facilitator_verify_success,
    mock_facilitator_settle_success,
    sample_bom_csv,
):
    """X402_4: Access token returned from x402 payment grants access to the project."""
    transport = httpx.ASGITransport(app=x402_app)

    # First create a project via x402 payment
    async with mock_x402_payment(mock_facilitator_verify_success, mock_facilitator_settle_success):
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://test",
            headers={"X-Payment": valid_payment_header}
        ) as client:
            files = {"bom_file": ("test_bom.csv", sample_bom_csv, "text/csv")}
            data = {"project_name": "X402 Access Test Project"}

            create_response = await client.post("/projects", files=files, data=data)

    assert create_response.status_code == 200
    result = create_response.json()
    access_token = result["access_token"]
    project_id = result["project_id"]

    # Now use the access token to get the project
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://test",
        headers={"X-API-Key": access_token}
    ) as client:
        get_response = await client.get(f"/projects/{project_id}")

    assert get_response.status_code == 200
    project = get_response.json()
    assert project["project_id"] == project_id
    assert project["context"]["project_name"] == "X402 Access Test Project"


@pytest.mark.asyncio
async def test_x402_5_access_token_cannot_access_other_projects(
    x402_app,
    valid_payment_header,
    mock_facilitator_verify_success,
    mock_facilitator_settle_success,
    sample_bom_csv,
    api_key,  # Regular API key for creating other project
):
    """X402_5: Project-scoped access token cannot access other projects."""
    transport = httpx.ASGITransport(app=x402_app)

    # Create a project via regular API key
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://test",
        headers={"X-API-Key": api_key}
    ) as client:
        files = {"bom_file": ("test_bom.csv", sample_bom_csv, "text/csv")}
        data = {"project_name": "Other Client Project"}
        other_response = await client.post("/projects", files=files, data=data)

    other_project_id = other_response.json()["project_id"]

    # Create a project via x402 payment to get a scoped token
    async with mock_x402_payment(mock_facilitator_verify_success, mock_facilitator_settle_success):
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://test",
            headers={"X-Payment": valid_payment_header}
        ) as client:
            files = {"bom_file": ("test_bom.csv", sample_bom_csv, "text/csv")}
            data = {"project_name": "X402 Scoped Project"}

            x402_response = await client.post("/projects", files=files, data=data)

    x402_access_token = x402_response.json()["access_token"]

    # Try to access other project with x402 token - should fail
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://test",
        headers={"X-API-Key": x402_access_token}
    ) as client:
        forbidden_response = await client.get(f"/projects/{other_project_id}")

    # Should be 403 Forbidden or 404 Not Found (depending on implementation)
    assert forbidden_response.status_code in [403, 404]

    # Cleanup
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://test",
        headers={"X-API-Key": api_key}
    ) as client:
        await client.delete(f"/projects/{other_project_id}")


@pytest.mark.asyncio
async def test_x402_7_project_scoped_token_can_access_trace(
    x402_app,
    valid_payment_header,
    mock_facilitator_verify_success,
    mock_facilitator_settle_success,
    sample_bom_csv,
):
    """X402_7: Project-scoped token can access project trace."""
    transport = httpx.ASGITransport(app=x402_app)

    # Create project via x402
    async with mock_x402_payment(mock_facilitator_verify_success, mock_facilitator_settle_success):
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://test",
            headers={"X-Payment": valid_payment_header}
        ) as client:
            files = {"bom_file": ("test_bom.csv", sample_bom_csv, "text/csv")}
            data = {"project_name": "X402 Trace Test"}

            create_response = await client.post("/projects", files=files, data=data)

    result = create_response.json()
    access_token = result["access_token"]
    project_id = result["project_id"]

    # Access trace with the token
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://test",
        headers={"X-API-Key": access_token}
    ) as client:
        trace_response = await client.get(f"/projects/{project_id}/trace")

    assert trace_response.status_code == 200
    assert isinstance(trace_response.json(), list)


@pytest.mark.asyncio
async def test_x402_8_project_scoped_token_can_delete_project(
    x402_app,
    valid_payment_header,
    mock_facilitator_verify_success,
    mock_facilitator_settle_success,
    sample_bom_csv,
):
    """X402_8: Project-scoped token can delete the project."""
    transport = httpx.ASGITransport(app=x402_app)

    # Create project via x402
    async with mock_x402_payment(mock_facilitator_verify_success, mock_facilitator_settle_success):
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://test",
            headers={"X-Payment": valid_payment_header}
        ) as client:
            files = {"bom_file": ("test_bom.csv", sample_bom_csv, "text/csv")}
            data = {"project_name": "X402 Delete Test"}

            create_response = await client.post("/projects", files=files, data=data)

    result = create_response.json()
    access_token = result["access_token"]
    project_id = result["project_id"]

    # Delete with the token
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://test",
        headers={"X-API-Key": access_token}
    ) as client:
        delete_response = await client.delete(f"/projects/{project_id}")

    assert delete_response.status_code == 200
    assert delete_response.json()["deleted"] == project_id


@pytest.mark.asyncio
async def test_x402_9_api_key_auth_still_works(x402_app, api_key, sample_bom_csv):
    """X402_9: Regular API key authentication still works when x402 is enabled."""
    transport = httpx.ASGITransport(app=x402_app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://test",
        headers={"X-API-Key": api_key}
    ) as client:
        # List projects should work with API key
        list_response = await client.get("/projects")
        assert list_response.status_code == 200

        # Create project should work with API key
        files = {"bom_file": ("test_bom.csv", sample_bom_csv, "text/csv")}
        data = {"project_name": "API Key Test With X402 Enabled"}
        create_response = await client.post("/projects", files=files, data=data)

        assert create_response.status_code == 200
        result = create_response.json()

        # API key auth should NOT return access_token (only x402 does)
        assert result.get("access_token") is None

        # Cleanup
        await client.delete(f"/projects/{result['project_id']}")


@pytest.mark.asyncio
async def test_x402_10_invalid_payment_returns_402(
    x402_app,
    valid_payment_header,
    sample_bom_csv,
):
    """X402_10: Invalid payment (verification fails) returns 402."""
    transport = httpx.ASGITransport(app=x402_app)

    # Mock failed verification
    failed_verify = {"valid": False, "error": "Insufficient funds"}
    async with mock_x402_payment(failed_verify, {}):
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://test",
            headers={"X-Payment": valid_payment_header}
        ) as client:
            files = {"bom_file": ("test_bom.csv", sample_bom_csv, "text/csv")}
            data = {"project_name": "Should Fail"}

            response = await client.post("/projects", files=files, data=data)

    assert response.status_code == 402
    assert "verification failed" in response.json().get("detail", "").lower()


# =============================================================================
# Identity Model Tests for x402
# =============================================================================

def test_x402_idn1_authmethod_x402_is_valid():
    """X402_IDN1: AuthMethod.X402 is a valid authentication method."""
    from bom_agent_service.auth.identity import AuthMethod

    assert hasattr(AuthMethod, "X402")
    assert AuthMethod.X402.value == "x402"


def test_x402_idn2_identity_with_x402_has_wallet_address():
    """X402_IDN2: Identity created with X402 auth has wallet_address field."""
    from bom_agent_service.auth.identity import Identity, AuthMethod

    identity = Identity(
        client_id="cli_ephemeral",
        client_name="X402 Wallet 0x1234...5678",
        auth_method=AuthMethod.X402,
        scopes=["all"],
        wallet_address="0x1234567890abcdef1234567890abcdef12345678",
    )

    assert identity.auth_method == AuthMethod.X402
    assert identity.wallet_address == "0x1234567890abcdef1234567890abcdef12345678"


def test_x402_idn3_identity_has_scope_checks_project_scope():
    """X402_IDN3: Identity.has_scope correctly checks project-specific scopes."""
    from bom_agent_service.auth.identity import Identity, AuthMethod

    identity = Identity(
        client_id="cli_ephemeral",
        client_name="X402 Wallet",
        auth_method=AuthMethod.X402,
        scopes=["project:proj_abc123"],
        wallet_address="0x1234567890abcdef1234567890abcdef12345678",
    )

    # Should have access to specific project
    assert identity.has_scope("project:proj_abc123") is True

    # Should NOT have access to other projects
    assert identity.has_scope("project:proj_other") is False

    # Should NOT have "all" scope
    assert identity.has_scope("all") is False


# =============================================================================
# X402Provider Unit Tests
# =============================================================================

def test_x402_provider_can_handle():
    """Test X402Provider.can_handle correctly identifies x402 requests."""
    from bom_agent_service.auth.providers.x402 import X402Provider
    from bom_agent_service.auth.config import AuthConfig
    from bom_agent_service.stores import ClientStore
    from unittest.mock import MagicMock

    config = AuthConfig(x402_enabled=True)
    client_store = ClientStore()
    provider = X402Provider(config, client_store)

    # Request with X-Payment header
    request_with_payment = MagicMock()
    request_with_payment.headers = {"x-payment": "somebase64payload"}
    assert provider.can_handle(request_with_payment) is True

    # Request without X-Payment header
    request_without_payment = MagicMock()
    request_without_payment.headers = {"x-api-key": "somekey"}
    assert provider.can_handle(request_without_payment) is False


def test_x402_encode_payment_requirements():
    """Test encode_payment_requirements produces valid output."""
    from bom_agent_service.auth.providers.x402 import encode_payment_requirements
    from bom_agent_service.auth.config import AuthConfig
    from decimal import Decimal

    config = AuthConfig(
        x402_enabled=True,
        x402_network="base-sepolia",
        x402_pay_to_address="0xtest",
        x402_base_price=Decimal("0.05"),
        x402_per_item_price=Decimal("0.01"),
    )

    # With 10 items: 0.05 + 0.01 * 10 = 0.15
    encoded = encode_payment_requirements(config, item_count=10)

    decoded = json.loads(base64.b64decode(encoded))
    assert decoded["price"] == "0.15"
    assert decoded["network"] == "base-sepolia"
    assert decoded["recipient"] == "0xtest"
    assert decoded["asset"] == "USDC"


# =============================================================================
# Client Store Wallet Tests
# =============================================================================

def test_client_store_get_by_wallet():
    """Test ClientStore.get_client_by_wallet."""
    from bom_agent_service.stores import ClientStore
    import uuid

    store = ClientStore()

    # Create client with unique wallet address
    unique_id = uuid.uuid4().hex[:32]
    unique_slug = f"test-wallet-{unique_id[:8]}"
    wallet = f"0x{unique_id}abcdef12"  # Unique wallet per test run

    client = store.create_client(
        name="Wallet Test Client",
        slug=unique_slug,
        wallet_address=wallet,
    )

    # Should find by wallet
    found = store.get_client_by_wallet(wallet)
    assert found is not None
    assert found.client_id == client.client_id
    assert found.wallet_address == wallet

    # Case-insensitive lookup
    found_upper = store.get_client_by_wallet(wallet.upper())
    assert found_upper is not None
    assert found_upper.client_id == client.client_id


def test_client_store_wallet_not_found():
    """Test ClientStore.get_client_by_wallet returns None for unknown wallet."""
    from bom_agent_service.stores import ClientStore

    store = ClientStore()
    result = store.get_client_by_wallet("0xunknown0000000000000000000000000000000")
    assert result is None
