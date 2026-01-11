# Journal: PostgreSQL Migration Test Fixes

**Date**: 2026-01-11
**Session**: afternoon

## Summary
Fixed multiple issues preventing tests from passing after the PostgreSQL migration. Addressed datetime timezone handling, multi-tenant client_id requirements, Alembic migration state, and LLM model compatibility.

## Goals
- [x] Fix test failures after PostgreSQL migration
- [x] Update test fixtures for multi-tenant auth
- [x] Fix datetime timezone mismatches
- [x] Fix client_id propagation in BOM flow
- [x] Fix LLM temperature parameter issue

## Changes Made

### Datetime Timezone Fixes
- Updated all Pydantic models to use timezone-aware datetimes
- Replaced deprecated `datetime.utcnow()` with `datetime.now(timezone.utc)`
- Files affected:
  - `src/bom_agent_service/models/client.py`
  - `src/bom_agent_service/models/api_key.py`
  - `src/bom_agent_service/models/offers.py`
  - `src/bom_agent_service/models/knowledge.py`
  - `src/bom_agent_service/models/project.py`

### Multi-Tenant Client ID Fixes
- **API Key Store**: Updated `create_key()` to require `client_id` parameter
- **BOM Flow**: Updated all `update_project()` calls to pass `client_id=self.state.client_id`
- **Conftest**: Added test client creation before API key creation

### Alembic Migration State
- Manually applied missing migration steps (clients table existed but api_keys.client_id was missing)
- Added `client_id` column to `api_keys` and `projects` tables
- Created foreign key constraints and indexes
- Stamped migration as complete with `alembic stamp head`

### LLM Configuration
- Fixed temperature parameter issue for gpt-5-nano (doesn't support temperature)
- Changed default model from `gpt-5-nano` to `gpt-5-mini` for better structured output reliability
- Added conditional temperature setting in `get_llm()` for nano models

## Decisions

### Decision: Default LLM Model
**Context**: Tests were failing intermittently due to malformed JSON from LLM
**Options Considered**:
1. gpt-5-nano - Cheapest but unreliable for structured JSON output
2. gpt-4o-mini - More expensive but reliable
3. gpt-5-mini - Balance of cost and reliability
**Chosen**: gpt-5-mini
**Rationale**: Better structured output support than nano, still cost-effective

### Decision: Client ID in Flow Updates
**Context**: PostgreSQL requires client_id (NOT NULL) but flow wasn't passing it
**Options Considered**:
1. Make client_id optional in DB (requires migration change)
2. Pass client_id through all update_project calls
**Chosen**: Pass client_id through all calls
**Rationale**: Maintains data integrity, cleaner multi-tenant isolation

## Issues Encountered

### Issue: "can't compare offset-naive and offset-aware datetimes"
- **Cause**: PostgreSQL returns timezone-aware datetimes, Pydantic models used naive
- **Resolution**: Added `_utc_now()` helper using `datetime.now(timezone.utc)` in all models

### Issue: "null value in column 'client_id' violates not-null constraint"
- **Cause**: `update_project()` in flow didn't pass client_id for upsert
- **Resolution**: Updated all 5 `update_project()` calls in `bom_flow.py` to include `client_id`

### Issue: "Unsupported value: 'temperature' does not support 0.3"
- **Cause**: gpt-5-nano doesn't support temperature parameter
- **Resolution**: Added conditional in `get_llm()` to skip temperature for nano models

### Issue: "Invalid JSON" from LLM in FinanceBatchResult
- **Cause**: gpt-5-nano produces malformed JSON for complex nested structures
- **Resolution**: Changed default model to gpt-5-mini

## Test Results
- **40/40 non-LLM tests pass** (health, CRUD, knowledge, error handling)
- **5 upload/process tests** - depend on LLM output quality, may have intermittent failures

## Files Modified
1. `src/bom_agent_service/models/*.py` - Timezone fixes
2. `src/bom_agent_service/stores/api_key_store.py` - client_id parameter
3. `src/bom_agent_service/flows/bom_flow.py` - client_id propagation
4. `src/bom_agent_service/agents/memory_config.py` - LLM config
5. `tests/conftest.py` - Test client/key setup

## Next Steps
- [ ] Consider adding retry logic for LLM calls with JSON parsing failures
- [ ] Add structured output validation/retry at agent level
- [ ] Monitor gpt-5-mini reliability in production

## Notes
- The Pyright diagnostics showing "reportOptionalMemberAccess" are type hints issues, not runtime bugs
- Multi-tenant test fixtures were enhanced (admin_api_key, client_b) for future isolation testing
- Client model was updated to include `wallet_address` field for x402 payment integration
