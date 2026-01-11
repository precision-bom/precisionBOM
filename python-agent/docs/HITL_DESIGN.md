# Human-in-the-Loop (HITL) System Design

## Overview

Add approval gates after each agent step, configurable escalation triggers, and seamless interaction via Web UI and CLI. The system pauses at checkpoints, allows human review/approval, then resumes processing.

## Architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│                           AGENT FLOW                                     │
│  intake → enrich → [ENG] → [SRC] → [FIN] → complete                     │
│                       │       │       │                                  │
│                       ▼       ▼       ▼                                  │
│               ┌───────────────────────────────┐                          │
│               │     HITL CHECKPOINT GATE      │                          │
│               │  - Evaluate escalation rules  │                          │
│               │  - Create approval requests   │                          │
│               │  - PAUSE flow execution       │                          │
│               └───────────────────────────────┘                          │
│                       │                                                  │
└───────────────────────│──────────────────────────────────────────────────┘
                        ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                    APPROVAL LAYER                                        │
│  ┌────────────┐  ┌────────────┐  ┌─────────────────┐                    │
│  │  Web UI    │  │    CLI     │  │  Email/Webhook  │                    │
│  │  Dashboard │  │  Interactive│  │  Notifications  │                    │
│  └─────┬──────┘  └─────┬──────┘  └────────┬────────┘                    │
│        │               │                   │                             │
│        └───────────────┼───────────────────┘                             │
│                        ▼                                                 │
│               ┌───────────────────────────────┐                          │
│               │     APPROVAL API              │                          │
│               │  POST /approvals/{id}/submit  │                          │
│               │  POST /approvals/batch        │                          │
│               └───────────────────────────────┘                          │
│                        │                                                 │
└────────────────────────│─────────────────────────────────────────────────┘
                        ▼
              ┌─────────────────────┐
              │   RESUME FLOW       │
              │   Next agent step   │
              └─────────────────────┘
```

---

## State Machine

### Line Item States (additions to `LineItemStatus`)

```python
# Add to models/enums.py
class LineItemStatus(str, Enum):
    # ... existing states ...

    # HITL States
    AWAITING_ENGINEERING_APPROVAL = "awaiting_engineering_approval"
    AWAITING_SOURCING_APPROVAL = "awaiting_sourcing_approval"
    AWAITING_FINANCE_APPROVAL = "awaiting_finance_approval"
    ESCALATED_ENGINEERING = "escalated_engineering"
    ESCALATED_SOURCING = "escalated_sourcing"
    ESCALATED_FINANCE = "escalated_finance"
```

### Project Status (additions)

```python
class ProjectStatus(str, Enum):
    # ... existing states ...
    AWAITING_ENGINEERING_APPROVAL = "awaiting_engineering_approval"
    AWAITING_SOURCING_APPROVAL = "awaiting_sourcing_approval"
    AWAITING_FINANCE_APPROVAL = "awaiting_finance_approval"
```

### State Diagram

```
                                    ┌──────────────┐
                                    │   CREATED    │
                                    └──────┬───────┘
                                           │
                                           ▼
                                    ┌──────────────┐
                                    │  ENRICHING   │
                                    └──────┬───────┘
                                           │
                                           ▼
┌────────────────────────────────────────────────────────────────────┐
│                     ENGINEERING CHECKPOINT                         │
│   ┌───────────────────┐       ┌───────────────────────┐           │
│   │ AWAITING_ENG_     │◄──────│   ENGINEERING_REVIEW  │           │
│   │   APPROVAL        │       └───────────────────────┘           │
│   └────────┬──────────┘                                           │
│            │                                                       │
│    ┌───────┴───────┐                                              │
│    ▼               ▼                                              │
│ APPROVED    ESCALATED_ENG ────► Manual review required            │
│    │               │                                              │
│    └───────────────┴──────────► SOURCING_REVIEW                   │
└────────────────────────────────────────────────────────────────────┘
                                           │
                                           ▼
                        (Same pattern for SOURCING and FINANCE)
                                           │
                                           ▼
                                    ┌──────────────┐
                                    │   COMPLETE   │
                                    └──────────────┘
```

---

## Data Models

### File: `models/approvals.py` (NEW)

```python
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field
import uuid


class ApprovalCheckpoint(str, Enum):
    """Checkpoints where approval is required."""
    POST_ENGINEERING = "post_engineering"
    POST_SOURCING = "post_sourcing"
    POST_FINANCE = "post_finance"


class ApprovalAction(str, Enum):
    """Human approval action."""
    APPROVE = "approve"
    REJECT = "reject"
    ESCALATE = "escalate"
    REQUEST_INFO = "request_info"
    MODIFY = "modify"


class EscalationReason(str, Enum):
    """Reasons for escalation."""
    HIGH_VALUE = "high_value"           # Line cost > threshold
    AGENT_REJECTED = "agent_rejected"   # Agent said no
    CRITICAL_PART = "critical_part"     # In critical parts list
    HIGH_RISK_SUPPLIER = "high_risk"    # Risk level = high
    BUDGET_THRESHOLD = "budget"         # % of total budget
    LIFECYCLE_CONCERN = "lifecycle"     # NRND/EOL
    COMPLIANCE_FLAG = "compliance"      # Compliance issues
    LEAD_TIME_EXCEEDED = "lead_time"    # > max days
    NO_STOCK = "no_stock"
    MANUAL_ESCALATION = "manual"


class ApprovalRequest(BaseModel):
    """A pending approval request."""
    request_id: str = Field(default_factory=lambda: f"APR-{uuid.uuid4().hex[:8].upper()}")
    project_id: str
    line_item_id: str
    checkpoint: ApprovalCheckpoint

    # What needs approval
    agent_decision: dict                # The AgentDecision that triggered this
    agent_name: str

    # Context for approver
    escalation_reasons: list[EscalationReason] = Field(default_factory=list)
    escalation_score: float = 0.0       # 0-100, higher = more urgent
    context_summary: str = ""           # Human-readable summary

    # Offer/pricing context
    selected_offer: Optional[dict] = None
    alternative_offers: list[dict] = Field(default_factory=list)

    # Timing
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None

    # Assignment
    assigned_to: Optional[str] = None


class ApprovalResponse(BaseModel):
    """Human response to an approval request."""
    response_id: str = Field(default_factory=lambda: f"RSP-{uuid.uuid4().hex[:8].upper()}")
    request_id: str

    # Decision
    action: ApprovalAction
    approver: str                       # user ID or email
    approved_at: datetime = Field(default_factory=datetime.utcnow)

    # Details
    comments: str = ""
    modified_values: Optional[dict] = None  # For MODIFY action

    # For partial approvals
    approved_quantity: Optional[int] = None
    approved_supplier: Optional[str] = None


class EscalationConfig(BaseModel):
    """Configuration for escalation triggers."""
    # Value thresholds
    high_value_threshold: float = 1000.0
    budget_warning_percent: float = 20.0

    # Risk thresholds
    escalate_on_agent_reject: bool = True
    escalate_on_high_risk: bool = True
    escalate_critical_parts: bool = True

    # Lead time
    lead_time_threshold_days: int = 45

    # Lifecycle
    escalate_nrnd: bool = True
    escalate_eol: bool = True

    # Timeout settings
    approval_timeout_hours: int = 48
    auto_escalate_on_timeout: bool = True
```

---

## Escalation Rules Engine

### File: `hitl/escalation.py` (NEW)

Evaluates each item after agent decision to determine if HITL is needed:

```python
from dataclasses import dataclass

@dataclass
class EscalationResult:
    """Result of escalation evaluation."""
    should_escalate: bool
    reasons: list[EscalationReason]
    score: float  # 0-100 urgency score
    summary: str


class EscalationEvaluator:
    """Evaluates whether items should be escalated."""

    def __init__(self, config: EscalationConfig):
        self.config = config

    def evaluate(
        self,
        line_item: BOMLineItem,
        project_context: ProjectContext,
        agent_decision: AgentDecision,
        running_budget_total: float = 0.0,
    ) -> EscalationResult:
        """Evaluate if this item should be escalated."""
        reasons = []
        score = 0.0

        # 1. Agent rejected → always escalate
        if self.config.escalate_on_agent_reject and agent_decision.status == DecisionStatus.REJECTED:
            reasons.append(EscalationReason.AGENT_REJECTED)
            score += 30

        # 2. High value item
        unit_price = agent_decision.output_data.get("unit_price", 0)
        line_cost = unit_price * line_item.quantity
        if line_cost >= self.config.high_value_threshold:
            reasons.append(EscalationReason.HIGH_VALUE)
            score += 20

        # 3. Budget threshold
        if project_context.budget_total > 0:
            budget_percent = (line_cost / project_context.budget_total) * 100
            if budget_percent >= self.config.budget_warning_percent:
                reasons.append(EscalationReason.BUDGET_THRESHOLD)
                score += 25

        # 4. Critical part
        is_critical = any(
            ref in project_context.engineering_context.critical_parts
            for ref in line_item.reference_designators
        )
        if self.config.escalate_critical_parts and is_critical:
            reasons.append(EscalationReason.CRITICAL_PART)
            score += 15

        # 5. High risk supplier
        risk_level = agent_decision.output_data.get("risk_level", "low")
        if self.config.escalate_on_high_risk and risk_level == "high":
            reasons.append(EscalationReason.HIGH_RISK_SUPPLIER)
            score += 20

        # 6. Lead time exceeded
        lead_time = agent_decision.output_data.get("lead_time_days", 0)
        if lead_time > self.config.lead_time_threshold_days:
            reasons.append(EscalationReason.LEAD_TIME_EXCEEDED)
            score += 15

        # 7. Lifecycle concerns
        concerns = agent_decision.output_data.get("concerns", [])
        if self.config.escalate_nrnd and any("NRND" in c for c in concerns):
            reasons.append(EscalationReason.LIFECYCLE_CONCERN)
            score += 10
        if self.config.escalate_eol and any("EOL" in c for c in concerns):
            reasons.append(EscalationReason.LIFECYCLE_CONCERN)
            score += 20

        # Cap score at 100
        score = min(score, 100.0)

        return EscalationResult(
            should_escalate=len(reasons) > 0,
            reasons=reasons,
            score=score,
            summary=self._build_summary(line_item, reasons, line_cost),
        )

    def _build_summary(self, line_item, reasons, line_cost) -> str:
        if not reasons:
            return f"MPN {line_item.mpn}: No escalation triggers"

        reason_texts = {
            EscalationReason.HIGH_VALUE: f"High value (${line_cost:.2f})",
            EscalationReason.AGENT_REJECTED: "Agent rejected",
            EscalationReason.CRITICAL_PART: "Critical part",
            EscalationReason.HIGH_RISK_SUPPLIER: "High risk supplier",
            EscalationReason.BUDGET_THRESHOLD: "Significant budget impact",
            EscalationReason.LIFECYCLE_CONCERN: "Lifecycle concern",
            EscalationReason.LEAD_TIME_EXCEEDED: "Long lead time",
        }

        triggers = [reason_texts.get(r, r.value) for r in reasons]
        return f"MPN {line_item.mpn}: {', '.join(triggers)}"
```

---

## Approval Store

### File: `stores/approval_store.py` (NEW)

```python
class ApprovalStore:
    """SQLite store for approval workflow data."""

    def __init__(self, db_path: str = "data/approvals.db"):
        self.db_path = Path(db_path)
        self._init_db()

    def _init_db(self) -> None:
        """Initialize database schema."""
        # Tables:
        # - approval_requests: Pending approval items
        # - approval_responses: Human decisions
        # - approval_audit: Full audit trail

    def create_request(self, request: ApprovalRequest) -> ApprovalRequest:
        """Create a new approval request."""

    def get_request(self, request_id: str) -> Optional[ApprovalRequest]:
        """Get a specific approval request."""

    def get_pending_requests(
        self,
        project_id: Optional[str] = None,
        checkpoint: Optional[ApprovalCheckpoint] = None,
        limit: int = 100,
    ) -> list[ApprovalRequest]:
        """Get pending approval requests."""

    def submit_response(self, response: ApprovalResponse) -> None:
        """Submit a response to an approval request."""

    def get_response_for_item(
        self,
        line_item_id: str,
        checkpoint: ApprovalCheckpoint
    ) -> Optional[ApprovalResponse]:
        """Get response for a line item at checkpoint."""
```

---

## API Endpoints

### File: `api/approvals.py` (NEW)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/approvals/pending` | GET | List pending approvals (filter by project, checkpoint, escalated) |
| `/approvals/projects/{id}/summary` | GET | Approval summary for project |
| `/approvals/{request_id}` | GET | Full approval request with context |
| `/approvals/{request_id}/submit` | POST | Submit approval/rejection |
| `/approvals/batch` | POST | Batch approve multiple items |
| `/approvals/projects/{id}/approve-all` | POST | Approve all non-escalated |
| `/approvals/ws/{project_id}` | WS | Real-time updates (WebSocket) |

### Request/Response Examples

**List pending:**
```http
GET /approvals/pending?project_id=PRJ-001&escalated_only=true

Response:
{
  "total": 3,
  "items": [
    {
      "request_id": "APR-A1B2C3D4",
      "project_id": "PRJ-001",
      "line_item_id": "LI-001",
      "checkpoint": "post_engineering",
      "escalation_score": 45,
      "escalation_reasons": ["agent_rejected", "critical_part"],
      "context_summary": "MPN RC0805FR-0710KL: Agent rejected, Critical part"
    }
  ],
  "checkpoint_counts": {
    "post_engineering": 3
  }
}
```

**Submit approval:**
```http
POST /approvals/APR-12345678/submit
{
  "action": "approve",
  "approver": "jdoe@company.com",
  "comments": "Verified with engineering team"
}

Response:
{
  "status": "submitted",
  "response_id": "RSP-X1Y2Z3W4"
}
```

**Batch approve:**
```http
POST /approvals/batch
{
  "approver": "jdoe@company.com",
  "decisions": [
    {"request_id": "APR-001", "action": "approve"},
    {"request_id": "APR-002", "action": "reject", "comments": "Use alternate"}
  ]
}

Response:
{
  "results": [
    {"request_id": "APR-001", "status": "submitted"},
    {"request_id": "APR-002", "status": "submitted"}
  ]
}
```

---

## Flow Integration

### Modified: `flows/bom_flow.py`

Add HITL checkpoints after each review step:

```python
class BOMProcessingFlow(Flow[BOMFlowState]):
    def __init__(
        self,
        project_store: ProjectStore,
        org_store: OrgKnowledgeStore,
        approval_store: ApprovalStore,      # NEW
        escalation_config: EscalationConfig, # NEW
        hitl_enabled: bool = True,           # NEW
        on_step: Optional[Callable] = None,
        data_dir: str = "data",
    ):
        super().__init__()
        self.approval_store = approval_store
        self.hitl_enabled = hitl_enabled
        self.escalation_evaluator = EscalationEvaluator(escalation_config)
        # ... rest of init

    @listen(engineering_review)
    def post_engineering_checkpoint(self):
        """HITL gate after engineering review."""
        if self.state.error or not self.hitl_enabled:
            return self.state  # Skip directly to sourcing

        self._project = self.project_store.get_project(self.state.project_id)

        for item in self._project.line_items:
            if item.engineering_decision is None:
                continue

            # Evaluate escalation
            result = self.escalation_evaluator.evaluate(
                item, self._project.context, item.engineering_decision
            )

            # Create approval request
            request = ApprovalRequest(
                project_id=self._project.project_id,
                line_item_id=item.line_id,
                checkpoint=ApprovalCheckpoint.POST_ENGINEERING,
                agent_decision=item.engineering_decision.model_dump(),
                agent_name="EngineeringAgent",
                escalation_reasons=result.reasons if result.should_escalate else [],
                escalation_score=result.score,
                context_summary=result.summary,
            )
            self.approval_store.create_request(request)

            # Update item status
            if result.should_escalate:
                item.status = LineItemStatus.ESCALATED_ENGINEERING
            else:
                item.status = LineItemStatus.AWAITING_ENGINEERING_APPROVAL

        # Update project status - FLOW PAUSES HERE
        self._project.status = "awaiting_engineering_approval"
        self.project_store.update_project(self._project)

        self._log_step("checkpoint", f"Awaiting approval at engineering checkpoint")
        return self.state  # Flow pauses - resumed via API

    # Similar checkpoints for post_sourcing and post_finance

    async def resume_from_checkpoint(self, checkpoint: ApprovalCheckpoint):
        """Called by API after all items approved."""
        self._project = self.project_store.get_project(self.state.project_id)

        # Apply approval decisions to items
        for item in self._project.line_items:
            response = self.approval_store.get_response_for_item(
                item.line_id, checkpoint
            )
            if response is None:
                continue

            if response.action == ApprovalAction.APPROVE:
                # Progress to next stage
                if checkpoint == ApprovalCheckpoint.POST_ENGINEERING:
                    item.status = LineItemStatus.PENDING_SOURCING
                elif checkpoint == ApprovalCheckpoint.POST_SOURCING:
                    item.status = LineItemStatus.PENDING_FINANCE
                elif checkpoint == ApprovalCheckpoint.POST_FINANCE:
                    item.status = LineItemStatus.PENDING_PURCHASE
            elif response.action == ApprovalAction.REJECT:
                item.status = LineItemStatus.FAILED

        self.project_store.update_project(self._project)

        # Continue to next step
        if checkpoint == ApprovalCheckpoint.POST_ENGINEERING:
            return self.sourcing_review()
        elif checkpoint == ApprovalCheckpoint.POST_SOURCING:
            return self.finance_review()
        elif checkpoint == ApprovalCheckpoint.POST_FINANCE:
            return self.complete()
```

---

## CLI Commands

### Added to `cli.py`

```bash
# List pending approvals
uv run sourcing approvals list
uv run sourcing approvals list --project PRJ-001 --escalated

# Interactive review of single item
uv run sourcing approvals review APR-12345678

# Batch approve all for a project
uv run sourcing approvals approve-all PRJ-001 --approver jdoe@email.com

# Interactive mode - review one by one
uv run sourcing approvals interactive --project PRJ-001
```

### Interactive Review Flow

```
╭─ Approval Request ─────────────────────────────────────────────────╮
│ Request: APR-12345678                                              │
│ Project: PRJ-2026-001                                              │
│ Line Item: R1                                                      │
│ Checkpoint: post_engineering                                       │
│ Agent: EngineeringAgent                                            │
╰────────────────────────────────────────────────────────────────────╯

Agent Decision:
  Status: rejected
  Reasoning: Part does not meet automotive-grade requirements
             specified in engineering notes. The RC0805FR-0710KL
             is a standard commercial grade resistor...

Output Data:
  unit_price: 0.02
  lifecycle: active
  concerns: ["Not automotive-grade", "Consider AEC-Q200 qualified"]

ESCALATION TRIGGERS:
  - Agent rejected
  - Critical part (U1)
  Score: 45/100

Actions:
  [a] Approve  [r] Reject  [e] Escalate  [m] Modify  [q] Quit

Select action: a
Comments (optional): Acceptable for prototype run
Your name/email: jdoe@company.com

Submitted: APPROVED
```

### CLI Implementation

```python
@main.group()
def approvals():
    """Manage HITL approvals."""
    pass


@approvals.command("list")
@click.option("--project", "-p", help="Filter by project ID")
@click.option("--checkpoint", "-c",
              type=click.Choice(["post_engineering", "post_sourcing", "post_finance"]))
@click.option("--escalated", is_flag=True, help="Show only escalated items")
@click.pass_context
def approvals_list(ctx, project, checkpoint, escalated):
    """List pending approval requests."""
    # Display Rich table with pending approvals


@approvals.command("review")
@click.argument("request_id")
@click.pass_context
def approvals_review(ctx, request_id):
    """Review a specific approval request interactively."""
    # Fetch full context, display, prompt for action


@approvals.command("approve-all")
@click.argument("project_id")
@click.option("--approver", "-a", required=True)
@click.option("--force", is_flag=True, help="Include escalated items")
@click.pass_context
def approvals_approve_all(ctx, project_id, approver, force):
    """Approve all pending items for a project."""


@approvals.command("interactive")
@click.option("--project", "-p", help="Filter by project ID")
@click.pass_context
def approvals_interactive(ctx, project):
    """Interactive approval mode - review items one by one."""
    # Loop through pending items, calling review for each
```

---

## Web UI Contract

### Polling Approach (Simple)

```typescript
// Poll every 5 seconds for updates
const pollApprovals = async (projectId: string) => {
  const response = await fetch(`/api/approvals/projects/${projectId}/summary`);
  return response.json();
};

// Response shape
interface ApprovalSummary {
  project_id: string;
  status: string;
  current_checkpoint: string | null;
  pending_count: number;
  escalated_count: number;
  items: ApprovalItem[];
}
```

### WebSocket Approach (Real-time)

```typescript
const ws = new WebSocket(`ws://api/approvals/ws/${projectId}`);

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  switch (data.event) {
    case 'new_approval':
      // New item needs approval
      addApprovalToQueue(data.request);
      break;
    case 'checkpoint_complete':
      // All items at checkpoint approved
      showCheckpointComplete(data.checkpoint);
      break;
    case 'flow_resumed':
      // Flow continued to next step
      updateProjectStatus(data.status);
      break;
  }
};
```

### Frontend Components Needed

1. **Approval Queue Dashboard**
   - List of pending approvals grouped by checkpoint
   - Filter by project, escalation status
   - Bulk selection for batch operations
   - Sort by urgency score

2. **Approval Detail View**
   - Full agent decision with reasoning
   - Offer comparison (for sourcing checkpoint)
   - Escalation triggers highlighted in red
   - Action buttons: Approve, Reject, Escalate, Modify

3. **Project Progress Indicator**
   - Visual flow diagram showing current checkpoint
   - Items count at each stage (approved/pending/failed)
   - Progress percentage

4. **Notification System**
   - Toast notifications for new approvals
   - Email integration for high-priority escalations
   - Sound alerts for urgent items

### API Contract for Frontend

```typescript
interface ApprovalRequest {
  request_id: string;
  project_id: string;
  line_item_id: string;
  checkpoint: 'post_engineering' | 'post_sourcing' | 'post_finance';
  agent_decision: {
    agent_name: string;
    status: string;
    reasoning: string;
    output_data: Record<string, any>;
    references: string[];
  };
  escalation_reasons: string[];
  escalation_score: number;
  context_summary: string;
  selected_offer?: OfferDetails;
  alternative_offers?: OfferDetails[];
  created_at: string;
  expires_at?: string;
}

interface SubmitApprovalRequest {
  action: 'approve' | 'reject' | 'escalate' | 'modify';
  approver: string;
  comments?: string;
  modified_values?: Record<string, any>;
}

interface BatchApprovalRequest {
  approver: string;
  decisions: Array<{
    request_id: string;
    action: string;
    comments?: string;
  }>;
}
```

---

## Implementation Plan

### Phase 1: Core Models & Store
1. Create `models/approvals.py` with approval models
2. Create `stores/approval_store.py` with SQLite persistence
3. Add new statuses to `models/enums.py`

### Phase 2: Escalation Engine
1. Create `hitl/__init__.py`
2. Create `hitl/escalation.py` with rule evaluator
3. Make rules configurable via `EscalationConfig`

### Phase 3: Flow Integration
1. Add checkpoint methods to `flows/bom_flow.py`
2. Add `resume_from_checkpoint()` method
3. Wire approval store into flow initialization
4. Update `run_flow()` to support HITL mode

### Phase 4: API Layer
1. Create `api/approvals.py` router
2. Add WebSocket endpoint for real-time updates
3. Register in `main.py`
4. Add endpoint to trigger flow resume

### Phase 5: CLI
1. Add `approvals` command group to `cli.py`
2. Implement `list`, `review`, `approve-all`, `interactive`
3. Update `process` command to handle HITL pause

### Phase 6: Testing
1. Unit tests for escalation rules
2. Integration tests for approval flow
3. End-to-end test with CLI

---

## Files to Create/Modify

| File | Action | Purpose |
|------|--------|---------|
| `models/approvals.py` | CREATE | Approval data models |
| `models/enums.py` | MODIFY | Add HITL status enums |
| `models/__init__.py` | MODIFY | Export new models |
| `stores/approval_store.py` | CREATE | SQLite approval persistence |
| `stores/__init__.py` | MODIFY | Export ApprovalStore |
| `hitl/__init__.py` | CREATE | HITL module |
| `hitl/escalation.py` | CREATE | Escalation rules engine |
| `flows/bom_flow.py` | MODIFY | Add checkpoint methods |
| `flows/__init__.py` | MODIFY | Export updated flow |
| `api/approvals.py` | CREATE | REST endpoints + WebSocket |
| `api/__init__.py` | MODIFY | Export approvals_router |
| `main.py` | MODIFY | Include approvals router |
| `cli.py` | MODIFY | Add approvals commands |

---

## Verification

```bash
# Start API
uv run uvicorn bom_agent_service.main:app --reload

# Process a BOM (will pause at checkpoints with HITL enabled)
uv run sourcing process sample_bom.csv --intake project_intake.yaml

# Check pending approvals
uv run sourcing approvals list

# Review escalated items
uv run sourcing approvals list --escalated

# Interactive review
uv run sourcing approvals interactive

# Or batch approve all non-escalated
uv run sourcing approvals approve-all PRJ-xxx --approver jdoe@email.com

# Verify flow resumed
uv run sourcing status PRJ-xxx
uv run sourcing trace PRJ-xxx
```

---

## Configuration

### Default Escalation Config

Can be set via environment or intake YAML:

```yaml
# project_intake.yaml
hitl:
  enabled: true
  escalation:
    high_value_threshold: 1000.0
    budget_warning_percent: 20.0
    escalate_on_agent_reject: true
    escalate_critical_parts: true
    lead_time_threshold_days: 45
    approval_timeout_hours: 48
```

### Environment Variables

```bash
HITL_ENABLED=true
HITL_HIGH_VALUE_THRESHOLD=1000
HITL_APPROVAL_TIMEOUT_HOURS=48
```
