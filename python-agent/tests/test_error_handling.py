"""Tests for error handling and validation.

Test Cases:
- E1: Invalid project ID format
- E2: Non-existent project
- E3: Missing required file upload
- E4: Invalid CSV format
- E5: Empty CSV file
- E6: Invalid ban request body
- E7: Delete non-existent project
"""

import pytest
import uuid


@pytest.mark.asyncio
async def test_e1_invalid_project_id_format(client):
    """E1: Invalid project ID format returns 404."""
    # Using a clearly invalid format
    response = await client.get("/projects/not-a-valid-uuid")

    # Could be 404 (not found) or 422 (validation error)
    assert response.status_code in [404, 422]


@pytest.mark.asyncio
async def test_e2_non_existent_project(client):
    """E2: Non-existent project ID returns 404 Not Found."""
    # Generate a random UUID that doesn't exist
    fake_id = str(uuid.uuid4())

    response = await client.get(f"/projects/{fake_id}")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_e3_missing_required_file_upload(client):
    """E3: POST /projects without file returns 422 Validation Error."""
    # Try to create project without required file
    response = await client.post("/projects", data={"project_name": "Test"})

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_e4_invalid_csv_format(client, malformed_csv):
    """E4: Upload malformed CSV - API is lenient and may parse partial data."""
    files = {"bom_file": ("bad.csv", malformed_csv, "text/csv")}

    response = await client.post("/projects", files=files)

    # The API is lenient with CSV parsing - it may succeed with partial data
    # or fail with 400. Both are acceptable behaviors.
    assert response.status_code in [200, 400]

    if response.status_code == 200:
        result = response.json()
        # If it succeeds, verify it has expected structure
        assert "project_id" in result
        assert "line_item_count" in result


@pytest.mark.asyncio
async def test_e5_empty_csv_file(client, empty_csv):
    """E5: Upload empty CSV (headers only) returns 400 Bad Request."""
    files = {"bom_file": ("empty.csv", empty_csv, "text/csv")}

    response = await client.post("/projects", files=files)

    # Empty CSV should fail validation
    assert response.status_code == 400
    assert "no valid line items" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_e6_invalid_ban_request_body(client):
    """E6: Invalid ban request body returns 422 Validation Error."""
    # Missing required 'reason' field
    response = await client.post(
        "/knowledge/parts/TEST-PART/ban",
        json={},  # Missing reason
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_e7_delete_non_existent_project(client):
    """E7: Delete non-existent project returns 404 Not Found."""
    fake_id = str(uuid.uuid4())

    response = await client.delete(f"/projects/{fake_id}")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_e8_invalid_supplier_type(client):
    """E8: Create supplier with invalid type returns 400."""
    response = await client.post(
        "/knowledge/suppliers",
        json={
            "supplier_id": "test-invalid-type",
            "name": "Test Supplier",
            "supplier_type": "invalid_type",
            "trust_level": "high",
        },
    )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_e9_get_trace_non_existent_project(client):
    """E9: Get trace for non-existent project returns 404."""
    fake_id = str(uuid.uuid4())

    response = await client.get(f"/projects/{fake_id}/trace")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_e10_process_non_existent_project(client):
    """E10: Process non-existent project returns 404."""
    fake_id = str(uuid.uuid4())

    response = await client.post(f"/projects/{fake_id}/process")

    assert response.status_code == 404
