"""Tests for knowledge base suppliers API.

Test Cases:
- KS1: List all suppliers
- KS2: Get supplier by ID
- KS3: Get unknown supplier returns 404
- KS4: Create new supplier
- KS5: Create duplicate supplier fails
- KS6: Set supplier trust level
- KS7: Invalid trust level fails
"""

import pytest
import uuid


@pytest.mark.asyncio
async def test_ks1_list_all_suppliers(client):
    """KS1: List all suppliers returns supplier list."""
    response = await client.get("/knowledge/suppliers")

    assert response.status_code == 200
    suppliers = response.json()

    assert isinstance(suppliers, list)
    # Default suppliers may be seeded
    if len(suppliers) > 0:
        supplier = suppliers[0]
        assert "supplier_id" in supplier
        assert "name" in supplier
        assert "supplier_type" in supplier
        assert "trust_level" in supplier


@pytest.mark.asyncio
async def test_ks2_get_supplier_by_id(client, test_state):
    """KS2: Get supplier by ID returns supplier details."""
    # Create a supplier first
    supplier_id = f"TEST-SUPPLIER-{uuid.uuid4().hex[:8]}"
    await client.post(
        "/knowledge/suppliers",
        json={
            "supplier_id": supplier_id,
            "name": "Test Supplier KS2",
            "supplier_type": "authorized",
            "trust_level": "high",
        },
    )
    test_state.created_supplier_ids.append(supplier_id)

    # Get the supplier
    response = await client.get(f"/knowledge/suppliers/{supplier_id}")

    assert response.status_code == 200
    supplier = response.json()

    assert supplier["supplier_id"] == supplier_id
    assert supplier["name"] == "Test Supplier KS2"
    assert "supplier_type" in supplier
    assert "trust_level" in supplier
    assert "on_time_rate" in supplier
    assert "quality_rate" in supplier
    assert "order_count_ytd" in supplier
    assert "notes" in supplier


@pytest.mark.asyncio
async def test_ks3_get_unknown_supplier_returns_404(client):
    """KS3: Get unknown supplier returns 404 Not Found."""
    response = await client.get("/knowledge/suppliers/UNKNOWN-NONEXISTENT-SUPPLIER")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_ks4_create_new_supplier(client, test_state):
    """KS4: Create new supplier returns created status."""
    supplier_id = f"TEST-SUPPLIER-{uuid.uuid4().hex[:8]}"

    response = await client.post(
        "/knowledge/suppliers",
        json={
            "supplier_id": supplier_id,
            "name": "New Test Supplier",
            "supplier_type": "broker",
            "trust_level": "medium",
        },
    )

    assert response.status_code == 200
    result = response.json()

    assert result["status"] == "created"
    assert result["supplier_id"] == supplier_id
    assert result["name"] == "New Test Supplier"

    test_state.created_supplier_ids.append(supplier_id)


@pytest.mark.asyncio
async def test_ks5_create_duplicate_supplier_fails(client, test_state):
    """KS5: Create duplicate supplier returns 400 Bad Request."""
    supplier_id = f"TEST-SUPPLIER-DUP-{uuid.uuid4().hex[:8]}"

    # Create first supplier
    await client.post(
        "/knowledge/suppliers",
        json={
            "supplier_id": supplier_id,
            "name": "First Supplier",
            "supplier_type": "authorized",
            "trust_level": "high",
        },
    )
    test_state.created_supplier_ids.append(supplier_id)

    # Try to create duplicate
    response = await client.post(
        "/knowledge/suppliers",
        json={
            "supplier_id": supplier_id,
            "name": "Duplicate Supplier",
            "supplier_type": "authorized",
            "trust_level": "high",
        },
    )

    assert response.status_code == 400
    assert "already exists" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_ks6_set_supplier_trust_level(client, test_state):
    """KS6: Set supplier trust level updates the trust level."""
    supplier_id = f"TEST-SUPPLIER-TRUST-{uuid.uuid4().hex[:8]}"

    # Create supplier with initial trust level
    await client.post(
        "/knowledge/suppliers",
        json={
            "supplier_id": supplier_id,
            "name": "Trust Test Supplier",
            "supplier_type": "authorized",
            "trust_level": "medium",
        },
    )
    test_state.created_supplier_ids.append(supplier_id)

    # Update trust level
    response = await client.post(
        f"/knowledge/suppliers/{supplier_id}/trust",
        json={
            "trust_level": "high",
            "reason": "Excellent performance",
            "user": "test_user",
        },
    )

    assert response.status_code == 200
    result = response.json()

    assert result["status"] == "updated"
    assert result["supplier_id"] == supplier_id
    assert result["trust_level"] == "high"

    # Verify the change
    get_response = await client.get(f"/knowledge/suppliers/{supplier_id}")
    supplier = get_response.json()
    assert supplier["trust_level"] == "high"


@pytest.mark.asyncio
async def test_ks7_invalid_trust_level_fails(client, test_state):
    """KS7: Invalid trust level returns 400 Bad Request."""
    supplier_id = f"TEST-SUPPLIER-INVALID-{uuid.uuid4().hex[:8]}"

    # Create supplier
    await client.post(
        "/knowledge/suppliers",
        json={
            "supplier_id": supplier_id,
            "name": "Invalid Trust Supplier",
            "supplier_type": "authorized",
            "trust_level": "medium",
        },
    )
    test_state.created_supplier_ids.append(supplier_id)

    # Try to set invalid trust level
    response = await client.post(
        f"/knowledge/suppliers/{supplier_id}/trust",
        json={
            "trust_level": "invalid_level",
            "reason": "Testing",
            "user": "test",
        },
    )

    assert response.status_code == 400
    assert "invalid trust level" in response.json()["detail"].lower()
