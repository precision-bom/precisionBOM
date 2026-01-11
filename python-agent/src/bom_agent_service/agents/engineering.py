"""Engineering review agent with batch processing."""

import json
from crewai import Agent, Task, Crew

from ..models import (
    BOMLineItem,
    ProjectContext,
    AgentDecision,
    DecisionStatus,
    PartOffers,
)
from ..stores import OrgKnowledgeStore, OffersStore
from .memory_config import (
    get_llm,
    build_org_knowledge_source,
    build_project_knowledge_source,
    ENGINEERING_POLICIES,
)


class EngineeringAgent:
    """
    Evaluates technical acceptability of parts.
    Processes all parts in a single LLM call for efficiency.
    """

    def __init__(self, org_store: OrgKnowledgeStore):
        """Initialize agent with LLM and cached knowledge sources."""
        self.org_store = org_store
        self._llm = get_llm()

        self.agent = Agent(
            role="Electronics Engineering Expert",
            goal="Evaluate technical acceptability of BOM parts and ensure compliance",
            backstory="""You are a senior electronics engineer with 20+ years of experience
            in component selection and qualification. You have deep knowledge of:
            - Component lifecycle management (active, NRND, EOL, obsolete)
            - Compliance requirements (RoHS, REACH, UL, CE, FDA)
            - Quality standards (IPC classes, automotive AEC-Q)
            - Counterfeit detection and authorized sourcing
            - Form-fit-function alternates and second sourcing

            Your job is to review each BOM line item and determine if it's technically
            acceptable for the project requirements. Flag any concerns and suggest
            approved alternates when available.""",
            llm=self._llm,
            verbose=False,
            allow_delegation=False,
        )

        # Cache static knowledge sources
        self._policy_knowledge = ENGINEERING_POLICIES
        self._org_knowledge = build_org_knowledge_source(org_store)

    def evaluate_batch(
        self,
        line_items: list[BOMLineItem],
        project_context: ProjectContext,
        offers_store: OffersStore,
    ) -> dict[str, AgentDecision]:
        """Evaluate all line items in a single LLM call.

        Returns a dict mapping MPN to AgentDecision.
        """
        if not line_items:
            return {}

        # Build context for all parts
        parts_context = []
        for item in line_items:
            part_offers = offers_store.get_offers(item.mpn)
            is_banned, ban_reason = self.org_store.is_part_banned(item.mpn)
            approved_alternates = self.org_store.get_approved_alternates(item.mpn)
            part_knowledge = self.org_store.get_part(item.mpn)

            parts_context.append(self._build_part_context(
                item, project_context, part_offers, is_banned, ban_reason,
                approved_alternates, part_knowledge
            ))

        all_parts_text = "\n\n---\n\n".join(parts_context)

        task = Task(
            description=f"""Review ALL of the following BOM line items for technical acceptability.

## Project Requirements
- Product type: {project_context.product_type.value}
- Compliance standards: {', '.join(project_context.compliance.standards)}
- Quality class: {project_context.compliance.quality_class}

## Engineering Notes
{project_context.engineering_context.notes or 'None'}

## Critical Parts (require extra scrutiny)
{', '.join(project_context.engineering_context.critical_parts) or 'None'}

---

## LINE ITEMS TO EVALUATE

{all_parts_text}

---

For EACH part, evaluate:
1. Is the part banned in org knowledge? If so, REJECT.
2. Does the part meet compliance requirements?
3. Is the part lifecycle acceptable (active or NRND)?
4. Is this a critical part needing extra scrutiny?
5. Are there approved alternates available?

Respond with a JSON array containing one object per part, in the same order as listed above:
```json
[
  {{
    "mpn": "PART-NUMBER-1",
    "decision": "APPROVED" or "REJECTED",
    "reasoning": "brief explanation",
    "concerns": ["list of concerns if any"],
    "approved_alternates": ["alternates if any"]
  }},
  ...
]
```

Return ONLY the JSON array, no other text.""",
            expected_output="JSON array with decision for each part",
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

        # Parse batch result
        return self._parse_batch_result(result.raw, [item.mpn for item in line_items])

    def _build_part_context(
        self,
        line_item: BOMLineItem,
        project_context: ProjectContext,
        part_offers: PartOffers | None,
        is_banned: bool,
        ban_reason: str,
        approved_alternates: list[str],
        part_knowledge,
    ) -> str:
        """Build context string for a single part."""
        lines = [
            f"### Part: {line_item.mpn}",
            f"- Manufacturer: {line_item.manufacturer}",
            f"- Description: {line_item.description}",
            f"- Quantity: {line_item.quantity}",
            f"- Reference designators: {', '.join(line_item.reference_designators)}",
            f"- Banned: {is_banned}" + (f" (reason: {ban_reason})" if is_banned else ""),
            f"- Approved alternates: {', '.join(approved_alternates) if approved_alternates else 'None'}",
        ]

        if part_knowledge:
            lines.extend([
                f"- Times used: {part_knowledge.times_used}",
                f"- Failure count: {part_knowledge.failure_count}",
            ])

        if part_offers:
            lines.extend([
                f"- Lifecycle: {part_offers.lifecycle_status.value}",
                f"- RoHS compliant: {part_offers.rohs_compliant}",
            ])

        is_critical = any(
            ref in project_context.engineering_context.critical_parts
            for ref in line_item.reference_designators
        )
        if is_critical:
            lines.append("- **CRITICAL PART**")

        return "\n".join(lines)

    def _parse_batch_result(self, raw_result: str, mpns: list[str]) -> dict[str, AgentDecision]:
        """Parse batch result into dict of decisions."""
        decisions = {}

        try:
            # Extract JSON array from result
            start = raw_result.find("[")
            end = raw_result.rfind("]") + 1
            if start >= 0 and end > start:
                data = json.loads(raw_result[start:end])

                for item in data:
                    mpn = item.get("mpn", "")
                    decision_str = item.get("decision", "APPROVED").upper()
                    status = DecisionStatus.APPROVED if decision_str == "APPROVED" else DecisionStatus.REJECTED

                    decisions[mpn] = AgentDecision(
                        agent_name="EngineeringAgent",
                        status=status,
                        reasoning=item.get("reasoning", ""),
                        output_data={
                            "concerns": item.get("concerns", []),
                            "approved_alternates": item.get("approved_alternates", []),
                        },
                        references=[],
                    )
        except json.JSONDecodeError:
            pass

        # Fill in any missing MPNs with default approval
        for mpn in mpns:
            if mpn not in decisions:
                decisions[mpn] = AgentDecision(
                    agent_name="EngineeringAgent",
                    status=DecisionStatus.APPROVED,
                    reasoning="Auto-approved (not in batch response)",
                    output_data={},
                    references=[],
                )

        return decisions
