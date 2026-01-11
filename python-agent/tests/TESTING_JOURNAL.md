# Testing Journal: BOM Agent Service E2E Tests

**Date:** January 10, 2026
**Author:** Development Team
**Project:** BOM Agent Service - Python Agent

---

## Objective

Implement comprehensive black-box end-to-end (E2E) test scenarios for the BOM Agent Service API, execute the tests, and document the results.

---

## Phase 1: Discovery & Planning

### Initial Exploration

We began by exploring the codebase to understand the API structure and functionality:

- **Framework**: FastAPI with CrewAI for multi-agent orchestration
- **Database**: SQLite for persistence (projects, org knowledge, offers)
- **Agents**: Engineering, Sourcing, and Finance agents for BOM review
- **Existing Tests**: None - this was a greenfield testing situation

### API Endpoints Identified

| Category | Endpoints |
|----------|-----------|
| Health/Utility | `GET /health`, `GET /`, `GET /v1/models` |
| Projects | `GET/POST /projects`, `GET/DELETE /projects/{id}`, `POST /projects/upload-and-process` |
| Knowledge Parts | `GET /knowledge/parts`, `POST /knowledge/parts/{mpn}/ban`, alternates management |
| Knowledge Suppliers | `GET/POST /knowledge/suppliers`, trust level management |
| Chat | `POST /v1/chat/completions` (OpenAI-compatible) |

### Test Strategy Decisions

After analysis, we made the following configuration choices:

1. **Server Startup**: Auto-start using pytest fixtures with ASGI test client (httpx)
2. **Database Isolation**: Separate test database directory (`data/test/`) cleaned each run
3. **API Key Requirement**: Tests fail if `OPENAI_API_KEY` not set (loaded from `.env`)

---

## Phase 2: Implementation

### Test Framework Setup

Added dependencies to `pyproject.toml`:
```toml
[dependency-groups]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.24.0",
    "asgi-lifespan>=2.1.0",
    "python-dotenv>=1.0.0",
]
```

Configured pytest for async support:
```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "function"
```

### Test Files Created

| File | Test Count | Purpose |
|------|------------|---------|
| `conftest.py` | - | Fixtures, test client, sample data, env loading |
| `test_health.py` | 3 | Health and utility endpoints |
| `test_projects_crud.py` | 7 | Project CRUD operations |
| `test_upload_and_process.py` | 6 | BOM upload and agent processing flow |
| `test_knowledge_parts.py` | 9 | Parts knowledge base API |
| `test_knowledge_suppliers.py` | 7 | Suppliers knowledge base API |
| `test_chat_completions.py` | 4 | OpenAI-compatible chat API |
| `test_error_handling.py` | 10 | Error cases and validation |
| `TEST_CASES.md` | - | Comprehensive test documentation |

### Key Fixtures

```python
# Auto-load environment variables
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

# Async HTTP client with ASGI transport
@pytest_asyncio.fixture
async def client(app):
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

# Sample test data
@pytest.fixture
def sample_bom_csv() -> bytes:
    # 3-line BOM with resistor, capacitor, and microcontroller
    ...
```

---

## Phase 3: Bug Discovery & Resolution

### Issue: Async CrewAI Flow Not Awaited

**Symptom**: Upload-and-process tests failed with 500 errors and warning:
```
RuntimeWarning: coroutine 'Flow.kickoff.<locals>._run_flow' was never awaited
```

**Root Cause**: The `run_flow()` function called `flow.kickoff()` synchronously, but CrewAI Flows use async execution internally. When called from an async FastAPI endpoint, the coroutine was never awaited.

**Solution**:

1. Created async version of `run_flow`:
```python
async def run_flow_async(...) -> Project:
    """Run the BOM processing flow asynchronously."""
    flow = BOMProcessingFlow(...)
    await flow.kickoff_async()  # Use async kickoff
    return project_store.get_project(flow.state.project_id)

def run_flow(...) -> Project:
    """Synchronous wrapper for CLI usage."""
    import asyncio
    return asyncio.run(run_flow_async(...))
```

2. Updated API endpoint:
```python
@router.post("/upload-and-process")
async def upload_and_process(...):
    project = await run_flow_async(...)  # Now properly awaited
```

**Files Modified**:
- `src/bom_agent_service/flows/bom_flow.py` - Added `run_flow_async()`
- `src/bom_agent_service/flows/__init__.py` - Exported new function
- `src/bom_agent_service/api/projects.py` - Use async version in endpoint

---

## Phase 4: Test Execution

### Final Test Run

```bash
uv run pytest tests/ -v
```

### Results

```
======================== 46 passed in 572.74s (0:09:32) ========================
```

| Category | Passed | Failed | Skipped |
|----------|--------|--------|---------|
| Chat Completions | 4 | 0 | 0 |
| Error Handling | 10 | 0 | 0 |
| Health | 3 | 0 | 0 |
| Knowledge Parts | 9 | 0 | 0 |
| Knowledge Suppliers | 7 | 0 | 0 |
| Projects CRUD | 7 | 0 | 0 |
| Upload & Process | 6 | 0 | 0 |
| **Total** | **46** | **0** | **0** |

### Performance Notes

- Fast tests (health, CRUD, knowledge): ~1 second each
- LLM-dependent tests (chat, upload-and-process): 10-90 seconds each
- Total suite time: ~9.5 minutes (dominated by agent execution)

---

## Test Coverage by Endpoint

### Fully Tested
- `GET /health` - Health check
- `GET /` - Service info
- `GET /v1/models` - Model listing
- `GET /projects` - List projects (with pagination)
- `POST /projects` - Create project with BOM upload
- `GET /projects/{id}` - Get project details
- `GET /projects/{id}/trace` - Get execution trace
- `DELETE /projects/{id}` - Delete project
- `POST /projects/upload-and-process` - Full agent processing
- `POST /projects/{id}/process` - Re-process existing project
- `GET /knowledge/parts` - List parts
- `GET /knowledge/parts/{mpn}` - Get part details
- `POST /knowledge/parts/{mpn}/ban` - Ban part
- `POST /knowledge/parts/{mpn}/unban` - Unban part
- `POST /knowledge/parts/{mpn}/alternates` - Add alternate
- `GET /knowledge/parts/{mpn}/alternates` - Get alternates
- `GET /knowledge/suppliers` - List suppliers
- `GET /knowledge/suppliers/{id}` - Get supplier details
- `POST /knowledge/suppliers` - Create supplier
- `POST /knowledge/suppliers/{id}/trust` - Set trust level
- `POST /v1/chat/completions` - Chat completion

### Error Cases Tested
- Invalid project ID format (404)
- Non-existent project (404)
- Missing required file upload (422)
- Malformed CSV (lenient parsing behavior documented)
- Empty CSV (400)
- Invalid ban request body (422)
- Duplicate supplier creation (400)
- Invalid trust level (400)
- Invalid supplier type (400)

---

## Lessons Learned

1. **Async/Sync Boundary**: When mixing FastAPI (async) with libraries that have internal async code (CrewAI), ensure proper async propagation through the call stack.

2. **CrewAI Flow Execution**: CrewAI Flows have both `kickoff()` and `kickoff_async()` methods. Use the async version when calling from async contexts.

3. **Environment Loading**: Using `python-dotenv` in conftest.py provides seamless environment variable loading without manual exports.

4. **Test Database Isolation**: Patching module-level `DATA_DIR` constants before app import effectively isolates test data.

5. **Black-Box Testing Value**: These tests uncovered a real bug in the async flow execution that would have caused production issues.

---

## Running the Tests

```bash
# Install dependencies
uv sync --group dev

# Run all tests
uv run pytest tests/ -v

# Run specific test file
uv run pytest tests/test_health.py -v

# Run with output visible
uv run pytest tests/ -v -s
```

**Prerequisites**:
- `OPENAI_API_KEY` in `.env` file
- Python 3.11+

---

## Future Improvements

1. **Parallel Test Execution**: Consider `pytest-xdist` for parallel runs (though LLM tests may have rate limits)
2. **Mock LLM Responses**: Add option to mock agent responses for faster CI runs
3. **Performance Benchmarks**: Track agent execution times across test runs
4. **Integration with CI/CD**: Add GitHub Actions workflow for automated testing

---

## Conclusion

Successfully implemented 46 E2E tests covering all API endpoints. The testing process uncovered and helped fix a critical async bug in the CrewAI Flow integration. The test suite now serves as both a regression safety net and living documentation of API behavior.
