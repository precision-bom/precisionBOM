"""Finance review agent with batch processing."""

import json
from crewai import Agent, Task, Crew

from ..models import (
    BOMLineItem,
    ProjectContext,
    AgentDecision,
    DecisionStatus,
)
from ..stores import OffersStore
from .memory_config import (
    get_llm,
    build_project_knowledge_source,
    FINANCE_POLICIES,
)


class FinanceAgent:
    """
    Evaluates cost and budget fit.
    Processes all parts in a single LLM call for efficiency.
    """

    def __init__(self):
        """Initialize agent with LLM and cached policy knowledge."""
        self._llm = get_llm()

        self.agent = Agent(
            role="Procurement Finance Analyst",
            goal="Evaluate costs and ensure budget compliance",
            backstory="""You are a procurement finance specialist with expertise in:
            - Cost analysis and budget management
            - Price break optimization
            - Total cost of ownership calculations
            - Volume consolidation opportunities
            - Payment terms and cash flow impact

            Your job is to review the sourcing recommendations and ensure they fit
            within the project budget while identifying cost optimization opportunities.""",
            llm=self._llm,
            verbose=False,
            allow_delegation=False,
        )

        # Cache static knowledge sources
        self._policy_knowledge = FINANCE_POLICIES

    def evaluate_batch(
        self,
        line_items: list[BOMLineItem],
        project_context: ProjectContext,
        offers_store: OffersStore,
    ) -> dict[str, AgentDecision]:
        """Evaluate finance for all line items in a single LLM call.

        Returns a dict mapping MPN to AgentDecision.
        """
        if not line_items:
            return {}

        # Filter to items that have sourcing decisions
        items_to_evaluate = [
            item for item in line_items
            if item.sourcing_decision and item.sourcing_decision.status == DecisionStatus.APPROVED
        ]

        if not items_to_evaluate:
            # Return rejections for all items without sourcing
            return {
                item.mpn: AgentDecision(
                    agent_name="FinanceAgent",
                    status=DecisionStatus.REJECTED,
                    reasoning="No approved sourcing decision",
                    output_data={},
                    references=[],
                )
                for item in line_items
            }

        # Build context for all parts
        parts_context = []
        running_total = 0.0
        for item in items_to_evaluate:
            part_ctx, line_cost = self._build_part_context(item, project_context, offers_store, running_total)
            parts_context.append(part_ctx)
            running_total += line_cost

        all_parts_text = "\n\n---\n\n".join(parts_context)

        task = Task(
            description=f"""Review the financial aspects of ALL the following procurement items.

## Budget Overview
- Total budget: ${project_context.budget_total:,.2f}
- Number of items: {len(items_to_evaluate)}
- Estimated total spend: ${running_total:,.2f}

---

## LINE ITEMS TO REVIEW

{all_parts_text}

---

For EACH part, evaluate:
1. Does the line cost fit within remaining budget?
2. Should we adjust quantity to hit a better price break?
3. What's the MOQ impact?
4. Are there any cash flow concerns?

Respond with a JSON array containing one object per part:
```json
[
  {{
    "mpn": "PART-NUMBER-1",
    "decision": "APPROVED" or "REJECTED",
    "approved_qty": 100,
    "approved_spend": 0.00,
    "unit_price": 0.00,
    "reasoning": "brief explanation"
  }},
  ...
]
```

Return ONLY the JSON array, no other text.""",
            expected_output="JSON array with finance decision for each part",
            agent=self.agent,
        )

        # Build knowledge sources
        project_knowledge = build_project_knowledge_source(project_context)
        knowledge_sources = [self._policy_knowledge, project_knowledge]

        crew = Crew(
            agents=[self.agent],
            tasks=[task],
            verbose=False,
            knowledge_sources=knowledge_sources,
        )

        result = crew.kickoff()

        # Parse and build results
        decisions = self._parse_batch_result(result.raw, items_to_evaluate)

        # Add rejections for items without sourcing
        for item in line_items:
            if item.mpn not in decisions:
                decisions[item.mpn] = AgentDecision(
                    agent_name="FinanceAgent",
                    status=DecisionStatus.REJECTED,
                    reasoning="No approved sourcing decision",
                    output_data={},
                    references=[],
                )

        return decisions

    def _build_part_context(
        self,
        line_item: BOMLineItem,
        project_context: ProjectContext,
        offers_store: OffersStore,
        running_total: float,
    ) -> tuple[str, float]:
        """Build context string for a single part. Returns (context, line_cost)."""
        sourcing = line_item.sourcing_decision
        unit_price = sourcing.output_data.get("unit_price", 0.0)
        selected_mpn = sourcing.output_data.get("selected_mpn", line_item.mpn)

        # Get MOQ from offer
        moq = 1
        part_offers = offers_store.get_offers(selected_mpn)
        if part_offers:
            selected_supplier = sourcing.output_data.get("selected_supplier")
            for offer in part_offers.offers:
                if offer.supplier_id == selected_supplier:
                    moq = offer.moq
                    break

        order_qty = max(line_item.quantity, moq)
        line_cost = unit_price * order_qty
        remaining_budget = project_context.budget_total - running_total

        lines = [
            f"### Part: {line_item.mpn}",
            f"- Quantity needed: {line_item.quantity}",
            f"- Unit price: ${unit_price:.4f}",
            f"- MOQ: {moq}",
            f"- Order quantity: {order_qty}",
            f"- Line cost: ${line_cost:.2f}",
            f"- Remaining budget before: ${remaining_budget:,.2f}",
            f"- Remaining budget after: ${remaining_budget - line_cost:,.2f}",
        ]

        return "\n".join(lines), line_cost

    def _parse_batch_result(self, raw_result: str, line_items: list[BOMLineItem]) -> dict[str, AgentDecision]:
        """Parse batch result into dict of decisions."""
        decisions = {}

        try:
            start = raw_result.find("[")
            end = raw_result.rfind("]") + 1
            if start >= 0 and end > start:
                data = json.loads(raw_result[start:end])

                for item_data in data:
                    mpn = item_data.get("mpn", "")
                    decision_str = item_data.get("decision", "APPROVED").upper()
                    status = DecisionStatus.APPROVED if decision_str == "APPROVED" else DecisionStatus.REJECTED

                    decisions[mpn] = AgentDecision(
                        agent_name="FinanceAgent",
                        status=status,
                        reasoning=item_data.get("reasoning", ""),
                        output_data={
                            "approved_qty": item_data.get("approved_qty", 0),
                            "approved_spend": item_data.get("approved_spend", 0.0),
                            "unit_price": item_data.get("unit_price", 0.0),
                        },
                        references=[],
                    )
        except json.JSONDecodeError:
            pass

        # Fill in any missing MPNs with defaults based on sourcing data
        for item in line_items:
            if item.mpn not in decisions:
                sourcing = item.sourcing_decision
                unit_price = sourcing.output_data.get("unit_price", 0.0) if sourcing else 0.0
                decisions[item.mpn] = AgentDecision(
                    agent_name="FinanceAgent",
                    status=DecisionStatus.APPROVED,
                    reasoning="Auto-approved (not in batch response)",
                    output_data={
                        "approved_qty": item.quantity,
                        "approved_spend": unit_price * item.quantity,
                        "unit_price": unit_price,
                    },
                    references=[],
                )

        return decisions
