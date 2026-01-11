"""Pytest configuration and fixtures for E2E tests."""

import os
import shutil
from pathlib import Path

import pytest
import pytest_asyncio
import httpx
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(Path(__file__).parent.parent / ".env")

# Test data directory (isolated from production)
TEST_DATA_DIR = Path(__file__).parent.parent / "data" / "test"


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test environment before any tests run."""
    # Ensure OPENAI_API_KEY is set
    if not os.environ.get("OPENAI_API_KEY"):
        pytest.fail("OPENAI_API_KEY environment variable is required for tests (check .env file)")

    # Clean and create test data directory
    if TEST_DATA_DIR.exists():
        shutil.rmtree(TEST_DATA_DIR)
    TEST_DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Patch DATA_DIR in the API modules before importing the app
    import bom_agent_service.api.projects as projects_module
    import bom_agent_service.api.knowledge as knowledge_module

    projects_module.DATA_DIR = str(TEST_DATA_DIR)
    knowledge_module.DATA_DIR = str(TEST_DATA_DIR)

    yield

    # Cleanup after all tests
    if TEST_DATA_DIR.exists():
        shutil.rmtree(TEST_DATA_DIR)


@pytest.fixture(scope="session")
def app():
    """Get the FastAPI application."""
    from bom_agent_service.main import app
    return app


@pytest_asyncio.fixture
async def client(app):
    """Async HTTP client for testing the API."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def sample_bom_csv() -> bytes:
    """Sample BOM CSV content for testing."""
    content = """Part Number,Description,Quantity,Manufacturer,MPN
R1,10K Resistor 0805 1%,100,Yageo,RC0805FR-0710KL
C1,100uF Electrolytic 25V,50,Panasonic,ECA-1EM101
U1,ATmega328P Microcontroller,10,Microchip,ATMEGA328P-PU
"""
    return content.encode("utf-8")


@pytest.fixture
def sample_intake_yaml() -> bytes:
    """Sample project intake YAML content for testing."""
    content = """project:
  name: "Test Project"
  id: "TEST-001"
  owner: "test@example.com"

requirements:
  product_type: "consumer"
  quantity: 100
  deadline: "2025-06-01"
  budget_total: 5000.00

compliance:
  standards:
    - "RoHS"
  quality_class: "IPC Class 2"

sourcing_constraints:
  allow_brokers: false
  allow_alternates: true
  preferred_distributors:
    - "digikey"
    - "mouser"
  max_lead_time_days: 30

engineering_context:
  notes: "Test notes for E2E testing"
  critical_parts:
    - "U1"
"""
    return content.encode("utf-8")


@pytest.fixture
def minimal_bom_csv() -> bytes:
    """Minimal single-line BOM CSV for testing."""
    content = """Part Number,Description,Quantity,Manufacturer,MPN
R1,Test Resistor,10,Yageo,TEST-PART-001
"""
    return content.encode("utf-8")


@pytest.fixture
def malformed_csv() -> bytes:
    """Malformed CSV content for error testing."""
    return b"this is not,valid csv\nwith broken,lines"


@pytest.fixture
def empty_csv() -> bytes:
    """Empty CSV with only headers for error testing."""
    return b"Part Number,Description,Quantity,Manufacturer,MPN\n"


# Shared state for tests that need to pass data between tests
class TestState:
    """Shared state for test scenarios that need project IDs."""

    def __init__(self):
        self.created_project_ids: list[str] = []
        self.created_supplier_ids: list[str] = []
        self.banned_parts: list[str] = []


@pytest.fixture(scope="session")
def test_state():
    """Shared test state across test session."""
    return TestState()
