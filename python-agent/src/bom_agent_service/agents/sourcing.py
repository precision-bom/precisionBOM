"""Sourcing review agent with batch processing."""

import json
from crewai import Agent, Task, Crew

from ..models import (
    BOMLineItem,
    ProjectContext,
    AgentDecision,
    DecisionStatus,
    RiskLevel,
)
from ..stores import OrgKnowledgeStore, OffersStore
from .memory_config import (
    get_llm,
    build_org_knowledge_source,
    build_project_knowledge_source,
    SOURCING_POLICIES,
)


class SourcingAgent:
    """
    Evaluates supply availability and risk.
    Processes all parts in a single LLM call for efficiency.
    """

    def __init__(self, org_store: OrgKnowledgeStore):
        """Initialize agent with LLM and cached knowledge sources."""
        self.org_store = org_store
        self._llm = get_llm()

        self.agent = Agent(
            role="Supply Chain Analyst",
            goal="Evaluate supply risk and select optimal suppliers",
            backstory="""You are an experienced supply chain analyst specializing in
            electronics procurement. You have expertise in:
            - Supplier evaluation and risk assessment
            - Price negotiation and cost optimization
            - Lead time analysis and delivery planning
            - Multi-sourcing strategies
            - Authorized vs broker sourcing decisions

            Your job is to analyze available offers for each BOM item and recommend
            the best sourcing option considering price, availability, risk, and
            project constraints.""",
            llm=self._llm,
            verbose=False,
            allow_delegation=False,
        )

        # Cache static knowledge sources
        self._policy_knowledge = SOURCING_POLICIES
        self._org_knowledge = build_org_knowledge_source(org_store)

    def evaluate_batch(
        self,
        line_items: list[BOMLineItem],
        project_context: ProjectContext,
        offers_store: OffersStore,
    ) -> dict[str, AgentDecision]:
        """Evaluate sourcing for all line items in a single LLM call.

        Returns a dict mapping MPN to AgentDecision.
        """
        if not line_items:
            return {}

        # Build context for all parts
        parts_context = []
        for item in line_items:
            parts_context.append(self._build_part_context(item, project_context, offers_store))

        all_parts_text = "\n\n---\n\n".join(parts_context)

        task = Task(
            description=f"""Analyze sourcing options for ALL of the following BOM line items.

## Project Constraints
- Deadline: {project_context.deadline or 'Not specified'}
- Allow brokers: {project_context.sourcing_constraints.allow_brokers}
- Max lead time: {project_context.sourcing_constraints.max_lead_time_days} days
- Preferred distributors: {', '.join(project_context.sourcing_constraints.preferred_distributors) or 'None'}
- Single source OK: {project_context.sourcing_constraints.single_source_ok}

---

## LINE ITEMS TO SOURCE

{all_parts_text}

---

For EACH part, evaluate:
1. Stock availability vs quantity needed
2. Lead time vs project deadline
3. Price (consider price breaks)
4. Supplier trust level and performance
5. Authorized vs broker sourcing

Select the best offer for each part.

Respond with a JSON array containing one object per part:
```json
[
  {{
    "mpn": "PART-NUMBER-1",
    "decision": "APPROVED" or "REJECTED",
    "selected_supplier": "supplier_id",
    "selected_supplier_name": "supplier name",
    "unit_price": 0.00,
    "lead_time_days": 0,
    "risk_level": "low" or "medium" or "high",
    "reasoning": "brief explanation"
  }},
  ...
]
```

Return ONLY the JSON array, no other text.""",
            expected_output="JSON array with sourcing decision for each part",
            agent=self.agent,
        )

        # Build knowledge sources
        project_knowledge = build_project_knowledge_source(project_context)
        knowledge_sources = [self._policy_knowledge, project_knowledge]
        if self._org_knowledge:
            knowledge_sources.append(self._org_knowledge)

        crew = Crew(
            agents=[self.agent],
            tasks=[task],
            verbose=False,
            knowledge_sources=knowledge_sources,
        )

        result = crew.kickoff()

        return self._parse_batch_result(result.raw, [item.mpn for item in line_items])

    def _build_part_context(
        self,
        line_item: BOMLineItem,
        project_context: ProjectContext,
        offers_store: OffersStore,
    ) -> str:
        """Build context string for a single part including offers."""
        # Get all MPNs to consider (primary + approved alternates)
        mpns_to_consider = [line_item.mpn] + line_item.approved_alternates

        lines = [
            f"### Part: {line_item.mpn}",
            f"- Quantity needed: {line_item.quantity}",
            f"- Approved alternates: {', '.join(line_item.approved_alternates) if line_item.approved_alternates else 'None'}",
            "",
            "**Available Offers:**",
        ]

        offer_num = 1
        for mpn in mpns_to_consider:
            part_offers = offers_store.get_offers(mpn)
            if part_offers:
                for offer in part_offers.offers:
                    supplier = self.org_store.get_supplier(offer.supplier_id)
                    price_at_qty = offer.get_price_at_qty(line_item.quantity)
                    lines.append(
                        f"  {offer_num}. {offer.supplier_name} (ID: {offer.supplier_id}): "
                        f"${price_at_qty:.4f}/unit, stock: {offer.stock_qty}, "
                        f"lead: {offer.lead_time_days}d, "
                        f"authorized: {offer.is_authorized}, "
                        f"trust: {supplier.trust_level.value if supplier else 'unknown'}"
                    )
                    offer_num += 1

        if offer_num == 1:
            lines.append("  NO OFFERS AVAILABLE")

        return "\n".join(lines)

    def _parse_batch_result(self, raw_result: str, mpns: list[str]) -> dict[str, AgentDecision]:
        """Parse batch result into dict of decisions."""
        decisions = {}

        try:
            start = raw_result.find("[")
            end = raw_result.rfind("]") + 1
            if start >= 0 and end > start:
                data = json.loads(raw_result[start:end])

                for item in data:
                    mpn = item.get("mpn", "")
                    decision_str = item.get("decision", "APPROVED").upper()
                    status = DecisionStatus.APPROVED if decision_str == "APPROVED" else DecisionStatus.REJECTED

                    risk_str = item.get("risk_level", "medium").lower()
                    risk_level = RiskLevel(risk_str) if risk_str in ["low", "medium", "high"] else RiskLevel.MEDIUM

                    decisions[mpn] = AgentDecision(
                        agent_name="SourcingAgent",
                        status=status,
                        reasoning=item.get("reasoning", ""),
                        output_data={
                            "selected_mpn": mpn,
                            "selected_supplier": item.get("selected_supplier"),
                            "selected_supplier_name": item.get("selected_supplier_name"),
                            "unit_price": item.get("unit_price", 0.0),
                            "lead_time_days": item.get("lead_time_days", 0),
                            "risk_level": risk_level.value,
                        },
                        references=[],
                    )
        except json.JSONDecodeError:
            pass

        # Fill in any missing MPNs with rejection
        for mpn in mpns:
            if mpn not in decisions:
                decisions[mpn] = AgentDecision(
                    agent_name="SourcingAgent",
                    status=DecisionStatus.REJECTED,
                    reasoning="Could not parse sourcing result",
                    output_data={},
                    references=[],
                )

        return decisions
