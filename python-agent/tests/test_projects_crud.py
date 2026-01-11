"""Tests for projects CRUD operations.

Test Cases:
- P1: Create project with BOM upload
- P2: List all projects
- P3: List projects with limit
- P4: Get project by ID
- P5: Get project trace
- P6: Delete project
- P7: Get deleted project returns 404
"""

import pytest


@pytest.mark.asyncio
async def test_p1_create_project_with_bom_upload(client, sample_bom_csv, test_state):
    """P1: Create project with BOM upload returns project summary with ID."""
    files = {"bom_file": ("test_bom.csv", sample_bom_csv, "text/csv")}
    data = {
        "project_name": "Test Project P1",
        "owner": "test@example.com",
        "product_type": "consumer",
        "quantity": "100",
    }

    response = await client.post("/projects", files=files, data=data)

    assert response.status_code == 200
    result = response.json()

    assert "project_id" in result
    assert result["project_name"] == "Test Project P1"
    assert "status" in result
    assert "line_item_count" in result
    assert result["line_item_count"] == 3  # 3 items in sample_bom_csv
    assert "created_at" in result
    assert "updated_at" in result

    # Store for later tests
    test_state.created_project_ids.append(result["project_id"])


@pytest.mark.asyncio
async def test_p2_list_all_projects(client, sample_bom_csv, test_state):
    """P2: List all projects returns list of project summaries."""
    # Create a project first
    files = {"bom_file": ("test_bom.csv", sample_bom_csv, "text/csv")}
    data = {"project_name": "Test Project P2"}
    create_response = await client.post("/projects", files=files, data=data)
    project_id = create_response.json()["project_id"]
    test_state.created_project_ids.append(project_id)

    # List projects
    response = await client.get("/projects")

    assert response.status_code == 200
    projects = response.json()

    assert isinstance(projects, list)
    assert len(projects) >= 1

    # Check structure of each project summary
    for project in projects:
        assert "project_id" in project
        assert "status" in project
        assert "line_item_count" in project
        assert "created_at" in project
        assert "updated_at" in project


@pytest.mark.asyncio
async def test_p3_list_projects_with_limit(client, sample_bom_csv, test_state):
    """P3: List projects with limit returns at most N projects."""
    # Create multiple projects
    for i in range(3):
        files = {"bom_file": ("test_bom.csv", sample_bom_csv, "text/csv")}
        data = {"project_name": f"Test Project P3-{i}"}
        create_response = await client.post("/projects", files=files, data=data)
        test_state.created_project_ids.append(create_response.json()["project_id"])

    # List with limit
    response = await client.get("/projects", params={"limit": 2})

    assert response.status_code == 200
    projects = response.json()

    assert len(projects) <= 2


@pytest.mark.asyncio
async def test_p4_get_project_by_id(client, sample_bom_csv, test_state):
    """P4: Get project by ID returns full project details."""
    # Create a project first
    files = {"bom_file": ("test_bom.csv", sample_bom_csv, "text/csv")}
    data = {"project_name": "Test Project P4"}
    create_response = await client.post("/projects", files=files, data=data)
    project_id = create_response.json()["project_id"]
    test_state.created_project_ids.append(project_id)

    # Get project by ID
    response = await client.get(f"/projects/{project_id}")

    assert response.status_code == 200
    project = response.json()

    assert project["project_id"] == project_id
    assert "context" in project
    assert "line_items" in project
    assert "status" in project
    assert "created_at" in project
    assert "updated_at" in project
    assert "trace" in project

    # Check line items
    assert len(project["line_items"]) == 3


@pytest.mark.asyncio
async def test_p5_get_project_trace(client, sample_bom_csv, test_state):
    """P5: Get project trace returns execution trace steps."""
    # Create a project first
    files = {"bom_file": ("test_bom.csv", sample_bom_csv, "text/csv")}
    data = {"project_name": "Test Project P5"}
    create_response = await client.post("/projects", files=files, data=data)
    project_id = create_response.json()["project_id"]
    test_state.created_project_ids.append(project_id)

    # Get trace
    response = await client.get(f"/projects/{project_id}/trace")

    assert response.status_code == 200
    trace = response.json()

    assert isinstance(trace, list)
    # Newly created project may have empty trace
    # Trace entries (if any) should have required fields


@pytest.mark.asyncio
async def test_p6_delete_project(client, sample_bom_csv):
    """P6: Delete project returns deleted project ID."""
    # Create a project first
    files = {"bom_file": ("test_bom.csv", sample_bom_csv, "text/csv")}
    data = {"project_name": "Test Project P6 - To Delete"}
    create_response = await client.post("/projects", files=files, data=data)
    project_id = create_response.json()["project_id"]

    # Delete the project
    response = await client.delete(f"/projects/{project_id}")

    assert response.status_code == 200
    result = response.json()
    assert result["deleted"] == project_id


@pytest.mark.asyncio
async def test_p7_get_deleted_project_returns_404(client, sample_bom_csv):
    """P7: Get deleted project returns 404 Not Found."""
    # Create a project
    files = {"bom_file": ("test_bom.csv", sample_bom_csv, "text/csv")}
    data = {"project_name": "Test Project P7 - To Delete"}
    create_response = await client.post("/projects", files=files, data=data)
    project_id = create_response.json()["project_id"]

    # Delete the project
    await client.delete(f"/projects/{project_id}")

    # Try to get the deleted project
    response = await client.get(f"/projects/{project_id}")

    assert response.status_code == 404
