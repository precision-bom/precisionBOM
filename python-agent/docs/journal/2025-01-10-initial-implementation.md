# Journal: Initial Multi-Agent BOM System Implementation

**Date**: 2026-01-10
**Session**: Full day

## Summary

Built out the complete multi-agent BOM processing system using CrewAI Flows. Implemented three specialized agents (Engineering, Sourcing, Finance), SQLite-backed data stores, FastAPI endpoints, and a Rich CLI. Integrated CrewAI's memory and knowledge primitives for agent learning and policy retrieval.

## Goals
- [x] Design multi-agent architecture for BOM processing
- [x] Implement data stores (Project, Offers, OrgKnowledge)
- [x] Create CrewAI agents with specialized roles
- [x] Build CrewAI Flow for orchestration
- [x] Add FastAPI endpoints for all operations
- [x] Update CLI to use API (not direct store access)
- [x] Integrate CrewAI memory and knowledge systems
- [x] Test full integration

## Changes Made

### Data Models (`models/`)
- Created comprehensive Pydantic models for:
  - `ProjectContext`, `BOMLineItem`, `Project`, `FlowTraceStep`
  - `SupplierOffer`, `PartOffers`
  - `PartKnowledge`, `SupplierKnowledge`
  - Enums: `DecisionStatus`, `RiskLevel`, `TrustLevel`, `SupplierType`, `ProductType`

### Data Stores (`stores/`)
- **ProjectStore**: SQLite persistence for projects with JSON serialization
- **OffersStore**: Ephemeral offer storage with TTL support
- **OrgKnowledgeStore**: Persistent org knowledge (parts, suppliers)
- Added `seed_default_suppliers()` for DigiKey, Mouser, Newark defaults

### CrewAI Agents (`agents/`)
- **EngineeringAgent**: Reviews compliance, preferred manufacturers, critical parts
- **SourcingAgent**: Analyzes supply chain, broker policy, lead times
- **FinanceAgent**: Budget approval, price break analysis
- **memory_config.py**: Centralized CrewAI memory and knowledge configuration
  - Long-term SQLite memory for agent learning
  - `build_org_knowledge_source()`: Converts structured data to RAG text
  - `build_project_knowledge_source()`: Project context as knowledge
  - Policy documents as `StringKnowledgeSource`

### CrewAI Flow (`flows/bom_flow.py`)
- `BOMProcessingFlow` with stages:
  1. `intake()` - Parse BOM CSV and project context
  2. `enrich()` - Fetch supplier offers (mock data)
  3. `engineering_review()` - Technical evaluation
  4. `sourcing_review()` - Supply chain analysis
  5. `finance_review()` - Budget approval
- Full execution trace with timestamps, reasoning, references

### FastAPI API (`api/`)
- **projects.py**: `/projects` endpoints
  - `GET /projects` - List projects
  - `GET /projects/{id}` - Get project
  - `GET /projects/{id}/trace` - Execution trace
  - `POST /projects` - Create from BOM upload
  - `POST /projects/upload-and-process` - Upload and process
  - `DELETE /projects/{id}` - Delete
- **knowledge.py**: `/knowledge` endpoints
  - Parts CRUD, ban/unban, alternates
  - Suppliers CRUD, trust level management

### CLI (`cli.py`)
- Complete rewrite to use API via httpx
- `APIClient` class for all HTTP operations
- Commands: `process`, `status`, `trace`, `kb parts`, `kb suppliers`, `chat`
- Rich formatting with tables and panels

### Main App (`main.py`)
- Added CORS middleware
- Included projects and knowledge routers
- Kept OpenAI-compatible `/v1/chat/completions` for backward compatibility

## Decisions

### Decision: Use CrewAI Memory + Custom Stores (Hybrid Approach)
**Context**: Question of whether to use CrewAI's built-in memory/knowledge or custom SQLite stores
**Options Considered**:
1. CrewAI primitives only - simpler but less control over structured data
2. Custom stores only - full control but miss agent learning benefits
3. Hybrid - structured stores for business data, CrewAI memory for agent learning
**Chosen**: Option 3 (Hybrid)
**Rationale**: Business data (parts, suppliers, projects) needs structured queries and explicit management. Agent learning and policy retrieval benefits from CrewAI's RAG-style knowledge sources.

### Decision: CLI Uses API (Not Direct Store Access)
**Context**: Whether CLI should access stores directly or go through API
**Options Considered**:
1. Direct store access - simpler, no server needed
2. API-first - consistent interface, supports remote usage
**Chosen**: Option 2 (API-first)
**Rationale**: Ensures single source of truth, enables future remote CLI usage, and validates API design through CLI testing.

### Decision: SQLite for All Stores
**Context**: Which database to use for persistence
**Options Considered**:
1. In-memory with JSON files - simple but not concurrent
2. SQLite - robust, concurrent, no external dependencies
3. PostgreSQL - overkill for hackathon scope
**Chosen**: Option 2 (SQLite)
**Rationale**: Perfect balance of simplicity and robustness. Supports concurrent access, no external setup required.

## Issues Encountered

- **Issue**: SQL error `no such column: name` in supplier queries
  - **Cause**: Used `ORDER BY name` but column is `supplier_id`
  - **Resolution**: Changed to `ORDER BY supplier_id`

- **Issue**: Missing model exports causing ImportError
  - **Cause**: New models not added to `models/__init__.py`
  - **Resolution**: Added all model exports (FlowTraceStep, ProductType, etc.)

- **Issue**: CLI method signature mismatches
  - **Cause**: CLI called store methods with wrong arguments
  - **Resolution**: Rewrote CLI to use API, eliminating direct store access

## Test Results

All integration tests passed:
```
✓ API health check
✓ List suppliers via CLI
✓ Show supplier details
✓ Update supplier trust level
✓ List parts
✓ List projects
✓ View project trace
✓ Direct API endpoint access
```

## Next Steps
- [ ] Replace mock enrichment with real Octopart/Mouser/DigiKey APIs
- [ ] Add human-in-the-loop approval workflows
- [ ] Implement PurchasingAgent for PO generation
- [ ] Add quality feedback loop for delivery outcomes
- [ ] Improve agent prompts based on test results

## Notes

- The engineering agent rejects parts that don't meet automotive-grade requirements from the project notes, even when parts are technically compliant. This is expected behavior based on the intake YAML.
- Mock enrichment provides 2 offers per part (DigiKey and Mouser) with reasonable pricing.
- Agent reasoning is captured in trace and includes references to data sources used.
- CrewAI memory stores persist in `data/agent_memory/` directory.
