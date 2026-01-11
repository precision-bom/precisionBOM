"""Tests for multi-tenant authentication and authorization.

Test Cases:
Authentication:
- AUTH1: Request without API key returns 401
- AUTH2: Request with invalid API key returns 401
- AUTH3: Request with valid API key succeeds
- AUTH4: Request with revoked API key returns 401

Client Isolation:
- ISO1: Client A cannot see Client B's projects
- ISO2: Client A cannot access Client B's project by ID
- ISO3: Client A cannot delete Client B's project
- ISO4: Client B cannot see Client A's projects

Admin Access:
- ADM1: Admin can list all projects across all clients
- ADM2: Admin can access any project by ID
- ADM3: Admin can delete any project
- ADM4: Admin can filter projects by client_id

Identity Model:
- IDN1: Identity.is_admin returns True for admin scope
- IDN2: Identity.is_admin returns False without admin scope
- IDN3: Identity.effective_client_id returns None for admin
- IDN4: Identity.effective_client_id returns client_id for regular user
- IDN5: Identity.can_access_client returns True for admin accessing other client
"""

import pytest


# =============================================================================
# Authentication Tests
# =============================================================================

@pytest.mark.asyncio
async def test_auth1_request_without_api_key_returns_401(unauthenticated_client):
    """AUTH1: Request without API key returns 401 Unauthorized."""
    response = await unauthenticated_client.get("/projects")
    assert response.status_code == 401
    assert "detail" in response.json()


@pytest.mark.asyncio
async def test_auth2_request_with_invalid_api_key_returns_401(app):
    """AUTH2: Request with invalid API key returns 401 Unauthorized."""
    import httpx
    transport = httpx.ASGITransport(app=app)
    headers = {"X-API-Key": "pbom_sk_invalid_key_12345"}
    async with httpx.AsyncClient(transport=transport, base_url="http://test", headers=headers) as client:
        response = await client.get("/projects")
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_auth3_request_with_valid_api_key_succeeds(client):
    """AUTH3: Request with valid API key succeeds."""
    response = await client.get("/projects")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_auth4_request_with_revoked_api_key_returns_401(app, test_client_id):
    """AUTH4: Request with revoked API key returns 401 Unauthorized."""
    import httpx
    from bom_agent_service.stores import ApiKeyStore

    # Create and immediately revoke a key
    store = ApiKeyStore()
    api_key, raw_key = store.create_key(
        client_id=test_client_id,
        name="pytest-revoked-key",
        scopes=["all"],
    )
    store.revoke_key(api_key.key_id)

    # Try to use the revoked key
    transport = httpx.ASGITransport(app=app)
    headers = {"X-API-Key": raw_key}
    async with httpx.AsyncClient(transport=transport, base_url="http://test", headers=headers) as client:
        response = await client.get("/projects")
        assert response.status_code == 401


# =============================================================================
# Client Isolation Tests
# =============================================================================

@pytest.mark.asyncio
async def test_iso1_client_a_cannot_see_client_b_projects(client, client_b, sample_bom_csv):
    """ISO1: Client A cannot see Client B's projects in list."""
    # Client B creates a project
    files = {"bom_file": ("test_bom.csv", sample_bom_csv, "text/csv")}
    data = {"project_name": "Client B Secret Project"}
    create_response = await client_b.post("/projects", files=files, data=data)
    assert create_response.status_code == 200
    client_b_project_id = create_response.json()["project_id"]

    # Client A lists projects - should NOT see Client B's project
    response = await client.get("/projects")
    assert response.status_code == 200
    projects = response.json()

    project_ids = [p["project_id"] for p in projects]
    assert client_b_project_id not in project_ids

    # Cleanup: delete Client B's project
    await client_b.delete(f"/projects/{client_b_project_id}")


@pytest.mark.asyncio
async def test_iso2_client_a_cannot_access_client_b_project_by_id(client, client_b, sample_bom_csv):
    """ISO2: Client A cannot access Client B's project by ID."""
    # Client B creates a project
    files = {"bom_file": ("test_bom.csv", sample_bom_csv, "text/csv")}
    data = {"project_name": "Client B Private Project"}
    create_response = await client_b.post("/projects", files=files, data=data)
    assert create_response.status_code == 200
    client_b_project_id = create_response.json()["project_id"]

    # Client A tries to access Client B's project - should get 404
    response = await client.get(f"/projects/{client_b_project_id}")
    assert response.status_code == 404

    # Cleanup
    await client_b.delete(f"/projects/{client_b_project_id}")


@pytest.mark.asyncio
async def test_iso3_client_a_cannot_delete_client_b_project(client, client_b, sample_bom_csv):
    """ISO3: Client A cannot delete Client B's project."""
    # Client B creates a project
    files = {"bom_file": ("test_bom.csv", sample_bom_csv, "text/csv")}
    data = {"project_name": "Client B Protected Project"}
    create_response = await client_b.post("/projects", files=files, data=data)
    assert create_response.status_code == 200
    client_b_project_id = create_response.json()["project_id"]

    # Client A tries to delete Client B's project - should get 404
    response = await client.delete(f"/projects/{client_b_project_id}")
    assert response.status_code == 404

    # Verify project still exists for Client B
    verify_response = await client_b.get(f"/projects/{client_b_project_id}")
    assert verify_response.status_code == 200

    # Cleanup
    await client_b.delete(f"/projects/{client_b_project_id}")


@pytest.mark.asyncio
async def test_iso4_client_b_cannot_see_client_a_projects(client, client_b, sample_bom_csv):
    """ISO4: Client B cannot see Client A's projects."""
    # Client A creates a project
    files = {"bom_file": ("test_bom.csv", sample_bom_csv, "text/csv")}
    data = {"project_name": "Client A Confidential Project"}
    create_response = await client.post("/projects", files=files, data=data)
    assert create_response.status_code == 200
    client_a_project_id = create_response.json()["project_id"]

    # Client B lists projects - should NOT see Client A's project
    response = await client_b.get("/projects")
    assert response.status_code == 200
    projects = response.json()

    project_ids = [p["project_id"] for p in projects]
    assert client_a_project_id not in project_ids

    # Cleanup
    await client.delete(f"/projects/{client_a_project_id}")


# =============================================================================
# Admin Access Tests
# =============================================================================

@pytest.mark.asyncio
async def test_adm1_admin_can_list_all_projects(admin_client, client, client_b, sample_bom_csv):
    """ADM1: Admin can list all projects across all clients."""
    # Create projects for both clients
    files_a = {"bom_file": ("test_bom.csv", sample_bom_csv, "text/csv")}
    data_a = {"project_name": "Admin Test - Client A Project"}
    response_a = await client.post("/projects", files=files_a, data=data_a)
    project_a_id = response_a.json()["project_id"]

    files_b = {"bom_file": ("test_bom.csv", sample_bom_csv, "text/csv")}
    data_b = {"project_name": "Admin Test - Client B Project"}
    response_b = await client_b.post("/projects", files=files_b, data=data_b)
    project_b_id = response_b.json()["project_id"]

    # Admin lists all projects - should see both
    response = await admin_client.get("/projects")
    assert response.status_code == 200
    projects = response.json()

    project_ids = [p["project_id"] for p in projects]
    assert project_a_id in project_ids
    assert project_b_id in project_ids

    # Cleanup
    await client.delete(f"/projects/{project_a_id}")
    await client_b.delete(f"/projects/{project_b_id}")


@pytest.mark.asyncio
async def test_adm2_admin_can_access_any_project_by_id(admin_client, client_b, sample_bom_csv):
    """ADM2: Admin can access any project by ID regardless of owner."""
    # Client B creates a project
    files = {"bom_file": ("test_bom.csv", sample_bom_csv, "text/csv")}
    data = {"project_name": "Admin Access Test Project"}
    create_response = await client_b.post("/projects", files=files, data=data)
    assert create_response.status_code == 200
    project_id = create_response.json()["project_id"]

    # Admin can access it
    response = await admin_client.get(f"/projects/{project_id}")
    assert response.status_code == 200
    assert response.json()["project_id"] == project_id

    # Cleanup
    await client_b.delete(f"/projects/{project_id}")


@pytest.mark.asyncio
async def test_adm3_admin_can_delete_any_project(admin_client, client_b, sample_bom_csv):
    """ADM3: Admin can delete any project regardless of owner."""
    # Client B creates a project
    files = {"bom_file": ("test_bom.csv", sample_bom_csv, "text/csv")}
    data = {"project_name": "Admin Delete Test Project"}
    create_response = await client_b.post("/projects", files=files, data=data)
    assert create_response.status_code == 200
    project_id = create_response.json()["project_id"]

    # Admin deletes it
    response = await admin_client.delete(f"/projects/{project_id}")
    assert response.status_code == 200
    assert response.json()["deleted"] == project_id

    # Verify it's gone
    verify_response = await client_b.get(f"/projects/{project_id}")
    assert verify_response.status_code == 404


@pytest.mark.asyncio
async def test_adm4_admin_can_filter_projects_by_client_id(
    admin_client, client, client_b, sample_bom_csv, client_b_id
):
    """ADM4: Admin can filter projects by client_id parameter."""
    # Create projects for both clients
    files_a = {"bom_file": ("test_bom.csv", sample_bom_csv, "text/csv")}
    data_a = {"project_name": "Admin Filter Test - Client A"}
    response_a = await client.post("/projects", files=files_a, data=data_a)
    project_a_id = response_a.json()["project_id"]

    files_b = {"bom_file": ("test_bom.csv", sample_bom_csv, "text/csv")}
    data_b = {"project_name": "Admin Filter Test - Client B"}
    response_b = await client_b.post("/projects", files=files_b, data=data_b)
    project_b_id = response_b.json()["project_id"]

    # Admin filters by Client B's ID
    response = await admin_client.get("/projects", params={"client_id": client_b_id})
    assert response.status_code == 200
    projects = response.json()

    project_ids = [p["project_id"] for p in projects]
    # Should see Client B's project but not Client A's
    assert project_b_id in project_ids
    assert project_a_id not in project_ids

    # Cleanup
    await client.delete(f"/projects/{project_a_id}")
    await client_b.delete(f"/projects/{project_b_id}")


# =============================================================================
# Identity Model Unit Tests
# =============================================================================

def test_idn1_identity_is_admin_returns_true_for_admin_scope():
    """IDN1: Identity.is_admin returns True when 'admin' in scopes."""
    from bom_agent_service.auth.identity import Identity, AuthMethod

    identity = Identity(
        client_id="cli_test",
        client_name="Test Client",
        auth_method=AuthMethod.API_KEY,
        scopes=["all", "admin"],
    )
    assert identity.is_admin is True


def test_idn2_identity_is_admin_returns_false_without_admin_scope():
    """IDN2: Identity.is_admin returns False without 'admin' scope."""
    from bom_agent_service.auth.identity import Identity, AuthMethod

    identity = Identity(
        client_id="cli_test",
        client_name="Test Client",
        auth_method=AuthMethod.API_KEY,
        scopes=["all"],
    )
    assert identity.is_admin is False


def test_idn3_identity_effective_client_id_returns_none_for_admin():
    """IDN3: Identity.effective_client_id() returns None for admin (no filter)."""
    from bom_agent_service.auth.identity import Identity, AuthMethod

    identity = Identity(
        client_id="cli_admin",
        client_name="Admin Client",
        auth_method=AuthMethod.API_KEY,
        scopes=["all", "admin"],
    )
    # Without argument, admin gets None (sees all)
    assert identity.effective_client_id() is None
    # With argument, admin can filter to specific client
    assert identity.effective_client_id("cli_other") == "cli_other"


def test_idn4_identity_effective_client_id_returns_own_client_id_for_regular_user():
    """IDN4: Identity.effective_client_id() returns own client_id for regular user."""
    from bom_agent_service.auth.identity import Identity, AuthMethod

    identity = Identity(
        client_id="cli_user",
        client_name="User Client",
        auth_method=AuthMethod.API_KEY,
        scopes=["all"],
    )
    # Regular user always gets their own client_id
    assert identity.effective_client_id() == "cli_user"
    # Even if they try to pass another client_id
    assert identity.effective_client_id("cli_other") == "cli_user"


def test_idn5_identity_can_access_client_returns_true_for_admin():
    """IDN5: Identity.can_access_client returns True for admin accessing any client."""
    from bom_agent_service.auth.identity import Identity, AuthMethod

    identity = Identity(
        client_id="cli_admin",
        client_name="Admin Client",
        auth_method=AuthMethod.API_KEY,
        scopes=["all", "admin"],
    )
    # Admin can access any client
    assert identity.can_access_client("cli_admin") is True
    assert identity.can_access_client("cli_other") is True
    assert identity.can_access_client("cli_random") is True


def test_idn6_identity_can_access_client_returns_false_for_regular_user_other_client():
    """IDN6: Identity.can_access_client returns False for regular user accessing other client."""
    from bom_agent_service.auth.identity import Identity, AuthMethod

    identity = Identity(
        client_id="cli_user",
        client_name="User Client",
        auth_method=AuthMethod.API_KEY,
        scopes=["all"],
    )
    # Regular user can only access their own client
    assert identity.can_access_client("cli_user") is True
    assert identity.can_access_client("cli_other") is False


# =============================================================================
# Client Store Tests
# =============================================================================

def test_client_store_create_and_get():
    """Test ClientStore.create_client and get_client."""
    from bom_agent_service.stores import ClientStore

    store = ClientStore()

    # Create a unique client
    import uuid
    unique_slug = f"test-client-{uuid.uuid4().hex[:8]}"

    client = store.create_client(
        name="Test Store Client",
        slug=unique_slug,
    )

    assert client.client_id.startswith("cli_")
    assert client.name == "Test Store Client"
    assert client.slug == unique_slug
    assert client.is_active is True

    # Get by ID
    retrieved = store.get_client(client.client_id)
    assert retrieved is not None
    assert retrieved.client_id == client.client_id

    # Get by slug
    by_slug = store.get_client_by_slug(unique_slug)
    assert by_slug is not None
    assert by_slug.client_id == client.client_id


def test_client_store_deactivate():
    """Test ClientStore.deactivate_client."""
    from bom_agent_service.stores import ClientStore

    store = ClientStore()

    import uuid
    unique_slug = f"test-deactivate-{uuid.uuid4().hex[:8]}"

    client = store.create_client(
        name="Deactivate Test Client",
        slug=unique_slug,
    )

    assert client.is_active is True

    # Deactivate
    result = store.deactivate_client(client.client_id)
    assert result is True

    # Verify deactivated
    retrieved = store.get_client(client.client_id)
    assert retrieved.is_active is False


def test_client_store_list_clients():
    """Test ClientStore.list_clients."""
    from bom_agent_service.stores import ClientStore

    store = ClientStore()
    clients = store.list_clients()

    # Should have at least the test clients created in conftest
    assert len(clients) >= 2
    assert all(c.is_active for c in clients)


# =============================================================================
# API Key Store Tests
# =============================================================================

def test_api_key_store_create_and_validate():
    """Test ApiKeyStore.create_key and validate_key."""
    from bom_agent_service.stores import ApiKeyStore

    store = ApiKeyStore()

    # Use existing test client
    api_key, raw_key = store.create_key(
        client_id="cli_pytest_test",
        name="store-test-key",
        scopes=["read", "write"],
    )

    assert api_key.key_id.startswith("key_")
    assert api_key.client_id == "cli_pytest_test"
    assert api_key.name == "store-test-key"
    assert api_key.scopes == ["read", "write"]
    assert raw_key.startswith("pbom_sk_")

    # Validate the raw key
    validated = store.validate_key(raw_key)
    assert validated is not None
    assert validated.key_id == api_key.key_id
    assert validated.client_id == "cli_pytest_test"


def test_api_key_store_validate_invalid_key():
    """Test ApiKeyStore.validate_key returns None for invalid key."""
    from bom_agent_service.stores import ApiKeyStore

    store = ApiKeyStore()
    result = store.validate_key("pbom_sk_totally_invalid_key")
    assert result is None


def test_api_key_store_revoke():
    """Test ApiKeyStore.revoke_key."""
    from bom_agent_service.stores import ApiKeyStore

    store = ApiKeyStore()

    api_key, raw_key = store.create_key(
        client_id="cli_pytest_test",
        name="revoke-test-key",
        scopes=["all"],
    )

    # Revoke
    result = store.revoke_key(api_key.key_id)
    assert result is True

    # Validate should now fail
    validated = store.validate_key(raw_key)
    assert validated is None


def test_api_key_store_list_keys_by_client():
    """Test ApiKeyStore.list_keys filters by client_id."""
    from bom_agent_service.stores import ApiKeyStore

    store = ApiKeyStore()

    # List keys for test client
    keys = store.list_keys(client_id="cli_pytest_test")
    assert len(keys) >= 1
    assert all(k.client_id == "cli_pytest_test" for k in keys)


# =============================================================================
# Project Store Client Scoping Tests
# =============================================================================

def test_project_store_create_with_client_id():
    """Test ProjectStore.create_project includes client_id."""
    from bom_agent_service.stores import ProjectStore
    from bom_agent_service.models import ProjectContext, BOMLineItem

    store = ProjectStore()

    context = ProjectContext(project_name="Client Scoping Test")
    line_items = [
        BOMLineItem(mpn="TEST-001", quantity=10, description="Test Part")
    ]

    project = store.create_project(context, line_items, client_id="cli_pytest_test")

    assert project.project_id is not None

    # Get without client_id filter (admin mode)
    retrieved = store.get_project(project.project_id)
    assert retrieved is not None

    # Get with correct client_id
    retrieved_filtered = store.get_project(project.project_id, client_id="cli_pytest_test")
    assert retrieved_filtered is not None

    # Get with wrong client_id should return None
    wrong_client = store.get_project(project.project_id, client_id="cli_wrong_client")
    assert wrong_client is None

    # Cleanup
    store.delete_project(project.project_id)


def test_project_store_list_projects_by_client():
    """Test ProjectStore.list_projects filters by client_id."""
    from bom_agent_service.stores import ProjectStore
    from bom_agent_service.models import ProjectContext, BOMLineItem

    store = ProjectStore()

    # Create project for Client A
    context_a = ProjectContext(project_name="List Test - Client A")
    line_items = [BOMLineItem(mpn="TEST-A", quantity=1, description="Test")]
    project_a = store.create_project(context_a, line_items, client_id="cli_pytest_test")

    # Create project for Client B
    context_b = ProjectContext(project_name="List Test - Client B")
    project_b = store.create_project(context_b, line_items, client_id="cli_pytest_client_b")

    # List for Client A only
    client_a_projects = store.list_projects(client_id="cli_pytest_test")
    client_a_ids = [p.project_id for p in client_a_projects]
    assert project_a.project_id in client_a_ids
    assert project_b.project_id not in client_a_ids

    # List for Client B only
    client_b_projects = store.list_projects(client_id="cli_pytest_client_b")
    client_b_ids = [p.project_id for p in client_b_projects]
    assert project_b.project_id in client_b_ids
    assert project_a.project_id not in client_b_ids

    # Cleanup
    store.delete_project(project_a.project_id)
    store.delete_project(project_b.project_id)
