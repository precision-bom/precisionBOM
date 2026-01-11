"""Tests for health and utility endpoints.

Test Cases:
- H1: Health check returns 200
- H2: Root endpoint returns service info
- H3: Models endpoint lists available models
"""

import pytest


@pytest.mark.asyncio
async def test_h1_health_check_returns_200(client):
    """H1: Health check endpoint returns 200 with healthy status."""
    response = await client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_h2_root_endpoint_returns_service_info(client):
    """H2: Root endpoint returns service name, version, and endpoints."""
    response = await client.get("/")

    assert response.status_code == 200
    data = response.json()

    assert "service" in data
    assert data["service"] == "BOM Agent Service"
    assert "version" in data
    assert data["version"] == "0.1.0"
    assert "endpoints" in data
    assert "projects" in data["endpoints"]
    assert "knowledge" in data["endpoints"]
    assert "chat" in data["endpoints"]
    assert "health" in data["endpoints"]


@pytest.mark.asyncio
async def test_h3_models_endpoint_lists_available_models(client):
    """H3: Models endpoint returns list with bom-agent model."""
    response = await client.get("/v1/models")

    assert response.status_code == 200
    data = response.json()

    assert "object" in data
    assert data["object"] == "list"
    assert "data" in data
    assert len(data["data"]) >= 1

    # Find bom-agent model
    model_ids = [m["id"] for m in data["data"]]
    assert "bom-agent" in model_ids

    # Check model structure
    bom_agent = next(m for m in data["data"] if m["id"] == "bom-agent")
    assert bom_agent["object"] == "model"
    assert "created" in bom_agent
    assert bom_agent["owned_by"] == "bom-agent-service"
