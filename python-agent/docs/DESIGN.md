# BOM Agent Service - Design Document

## Overview

BOM Agent Service is a multi-agent system for processing Bills of Materials (BOMs) using CrewAI. The system separates **data enrichment** from **decisioning**, with specialized agents operating on structured data stores. All operations are exposed via FastAPI with a Rich CLI for interaction.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              INTAKE LAYER                                   │
│  CLI: uv run sourcing process <bom.csv>                                     │
│  API: POST /projects/upload-and-process                                     │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ENRICHMENT LAYER                                  │
│  Fetches supplier offers for each line item (mock data currently)          │
│  Populates OffersStore with pricing, stock, and lead time data             │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DECISIONING LAYER                                 │
│  CrewAI Flow: Engineering → Sourcing → Finance                             │
│  Each agent reviews line items and makes decisions with reasoning          │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            OUTPUT LAYER                                     │
│  Project with decisions, execution trace, and recommendations              │
│  CLI: uv run sourcing status <project_id>                                   │
│  API: GET /projects/{id}                                                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Data Stores

| Store | Scope | Persistence | Location |
|-------|-------|-------------|----------|
| **OffersStore** | Per-project | Ephemeral (TTL 24h) | SQLite (`data/offers.db`) |
| **OrgKnowledgeStore** | Organization | Persistent | SQLite (`data/org_knowledge.db`) |
| **ProjectStore** | Per-project | Persistent | SQLite (`data/projects.db`) |

### OrgKnowledgeStore

Stores organizational knowledge that persists across projects:
- **Parts Knowledge**: Banned parts, approved alternates, usage history, failure rates
- **Supplier Knowledge**: Trust levels, on-time rates, quality rates, notes

### OffersStore

Stores supplier offers for parts with TTL expiration:
- Unit price, MOQ, stock levels
- Lead time, supplier info
- Timestamps for cache invalidation

### ProjectStore

Stores project state and execution history:
- Project context (requirements, constraints, compliance)
- BOM line items with decisions
- Execution trace for auditability

## Agent Architecture

### CrewAI Flow

The system uses CrewAI Flows for orchestration:

```python
class BOMProcessingFlow(Flow[BOMFlowState]):
    @start()
    def intake(self): ...          # Parse BOM + intake YAML

    @listen(intake)
    def enrich(self): ...          # Fetch supplier offers

    @listen(enrich)
    def engineering_review(self): ... # Technical evaluation

    @listen(engineering_review)
    def sourcing_review(self): ...    # Supply chain analysis

    @listen(sourcing_review)
    def finance_review(self): ...     # Budget approval
```

### Agent Definitions

| Agent | Role | Uses Context For |
|-------|------|------------------|
| **EngineeringAgent** | Technical Reviewer | Compliance checks, preferred manufacturers, critical parts, engineering notes |
| **SourcingAgent** | Supply Analyst | Broker policy, preferred distributors, lead time limits, single-source requirements |
| **FinanceAgent** | Budget Approver | Budget total, quantity for price break analysis |

### CrewAI Memory & Knowledge

Agents use CrewAI's built-in memory and knowledge systems:

- **Long-term Memory**: SQLite-backed storage for agent learning across sessions
- **Knowledge Sources**: RAG-style retrieval for policies and org knowledge
- **Policy Documents**: Engineering and sourcing policies as StringKnowledgeSources

## API Design

### Projects API (`/projects`)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/projects` | GET | List all projects |
| `/projects/{id}` | GET | Get project details |
| `/projects/{id}/trace` | GET | Get execution trace |
| `/projects` | POST | Create project from BOM upload |
| `/projects/upload-and-process` | POST | Upload BOM and run full flow |
| `/projects/{id}` | DELETE | Delete project |

### Knowledge API (`/knowledge`)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/knowledge/parts` | GET | List all parts |
| `/knowledge/parts/{mpn}` | GET | Get part details |
| `/knowledge/parts/{mpn}/ban` | POST | Ban a part |
| `/knowledge/parts/{mpn}/unban` | POST | Remove ban |
| `/knowledge/parts/{mpn}/alternates` | GET/POST | Manage alternates |
| `/knowledge/suppliers` | GET | List suppliers |
| `/knowledge/suppliers/{id}` | GET | Get supplier details |
| `/knowledge/suppliers/{id}/trust` | POST | Set trust level |

## CLI Design

The CLI uses the API for all operations (no direct store access):

```bash
# Process BOM
uv run sourcing process sample_bom.csv --intake project_intake.yaml

# View projects
uv run sourcing status                    # List all
uv run sourcing status <project_id>       # Get details
uv run sourcing trace <project_id>        # View execution trace

# Knowledge management
uv run sourcing kb parts list
uv run sourcing kb parts show <mpn>
uv run sourcing kb parts ban <mpn> --reason "..."
uv run sourcing kb suppliers list
uv run sourcing kb suppliers trust <id> high --reason "..."

# Interactive chat
uv run sourcing chat
```

## Project Context Schema

Projects include rich context that feeds into agent decisions:

```yaml
project:
  name: "IoT Sensor Board v1"
  owner: "jdoe@company.com"

requirements:
  product_type: "consumer"  # consumer | industrial | medical | automotive
  quantity: 100
  deadline: "2025-03-01"
  budget_total: 5000.00

compliance:
  standards: ["RoHS", "CE"]
  quality_class: "IPC Class 2"

sourcing_constraints:
  allow_brokers: false
  allow_alternates: true
  preferred_distributors: ["digikey", "mouser"]
  max_lead_time_days: 30

engineering_context:
  notes: "Temperature sensitive design..."
  critical_parts: ["U1", "U2"]
  preferred_manufacturers:
    capacitors: ["Murata", "Samsung"]
```

## File Structure

```
python-agent/
├── src/bom_agent_service/
│   ├── main.py              # FastAPI app with CORS
│   ├── cli.py               # Rich CLI using API
│   │
│   ├── api/                 # FastAPI routers
│   │   ├── projects.py      # /projects endpoints
│   │   └── knowledge.py     # /knowledge endpoints
│   │
│   ├── models/              # Pydantic models
│   │   ├── enums.py         # DecisionStatus, RiskLevel, etc.
│   │   ├── project.py       # ProjectContext, BOMLineItem
│   │   ├── offers.py        # SupplierOffer, PartOffers
│   │   └── knowledge.py     # PartKnowledge, SupplierKnowledge
│   │
│   ├── stores/              # SQLite data stores
│   │   ├── offers_store.py
│   │   ├── org_knowledge.py
│   │   └── project_store.py
│   │
│   ├── agents/              # CrewAI agents
│   │   ├── memory_config.py # Memory and knowledge config
│   │   ├── engineering.py
│   │   ├── sourcing.py
│   │   └── finance.py
│   │
│   └── flows/               # CrewAI flows
│       └── bom_flow.py
│
├── docs/                    # Documentation
├── data/                    # SQLite databases (gitignored)
├── sample_bom.csv           # Example BOM
└── project_intake.yaml      # Example project context
```

## Technology Stack

- **Framework**: FastAPI with CORS middleware
- **Agent Framework**: CrewAI with Flows
- **LLM**: Claude (via Anthropic API)
- **Database**: SQLite for all stores
- **CLI**: Click + Rich for beautiful output
- **HTTP Client**: httpx for CLI-to-API communication

## Future Enhancements

1. **Real API Integration**: Replace mock enrichment with Octopart, Mouser, DigiKey APIs
2. **Human-in-the-Loop**: Add approval workflows for high-value decisions
3. **Purchasing Agent**: Generate PO recommendations
4. **Quality Feedback**: Record delivery outcomes to improve supplier ratings
5. **Alternate Suggestions**: Proactive part substitution recommendations
