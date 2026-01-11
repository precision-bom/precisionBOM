"""BOM Processing Flow using CrewAI with batch processing."""

import csv
from datetime import datetime
from pathlib import Path
from typing import Optional, Callable
import yaml

from crewai.flow.flow import Flow, listen, start
from pydantic import BaseModel

from ..models import (
    ProjectContext,
    BOMLineItem,
    Project,
    FlowTraceStep,
    LineItemStatus,
    DecisionStatus,
    ComplianceRequirements,
    SourcingConstraints,
    EngineeringContext,
    PreferredManufacturers,
    ProductType,
)
from ..stores import ProjectStore, OffersStore, OrgKnowledgeStore
from ..stores.offers_store import create_mock_offers
from ..stores.org_knowledge import seed_default_suppliers
from ..agents import EngineeringAgent, SourcingAgent, FinanceAgent


class BOMFlowState(BaseModel):
    """State maintained throughout the flow."""
    project_id: str = ""
    bom_path: str = ""
    intake_path: str = ""
    error: Optional[str] = None


class BOMProcessingFlow(Flow[BOMFlowState]):
    """Flow for processing a BOM through all stages with batch processing."""

    def __init__(
        self,
        project_store: ProjectStore,
        org_store: OrgKnowledgeStore,
        engineering_agent: EngineeringAgent,
        sourcing_agent: SourcingAgent,
        finance_agent: FinanceAgent,
        on_step: Optional[Callable[[FlowTraceStep], None]] = None,
    ):
        super().__init__()
        self.project_store = project_store
        self.org_store = org_store
        self.on_step = on_step
        self.offers_store: Optional[OffersStore] = None
        self._project: Optional[Project] = None

        # Use pre-initialized agents
        self._engineering_agent = engineering_agent
        self._sourcing_agent = sourcing_agent
        self._finance_agent = finance_agent

    def _log_step(self, step: str, message: str, agent: str = None, reasoning: str = None, references: list[str] = None):
        """Log a step and notify callback."""
        trace_step = FlowTraceStep(
            step=step,
            agent=agent,
            message=message,
            reasoning=reasoning,
            references=references or [],
        )
        if self._project:
            self._project.trace.append(trace_step)
            self.project_store.update_project(self._project)
        if self.on_step:
            self.on_step(trace_step)

    @start()
    def intake(self):
        """Parse BOM and create project."""
        self._log_step("intake", f"Starting intake from {self.state.bom_path}")

        try:
            context = self._parse_intake(self.state.intake_path) if self.state.intake_path else ProjectContext()
            line_items = self._parse_bom(self.state.bom_path)

            self._project = self.project_store.create_project(context, line_items)
            self.state.project_id = self._project.project_id

            self.offers_store = OffersStore(self._project.project_id)

            self._log_step(
                "intake",
                f"Created project {self._project.project_id} with {len(line_items)} line items"
            )

            return self.state

        except Exception as e:
            self.state.error = str(e)
            self._log_step("intake", f"ERROR: {e}")
            return self.state

    @listen(intake)
    def enrich(self):
        """Enrich line items with supplier offers."""
        if self.state.error:
            return self.state

        self._log_step("enrich", "Starting enrichment")

        self._project = self.project_store.get_project(self.state.project_id)
        self._project.status = "enriching"

        enriched = 0
        for item in self._project.line_items:
            mock = create_mock_offers(item.mpn, item.manufacturer, item.description)
            self.offers_store.set_offers(item.mpn, mock)
            item.status = LineItemStatus.ENRICHED
            enriched += 1

        self.project_store.update_project(self._project)
        self._log_step("enrich", f"Enriched {enriched}/{len(self._project.line_items)} items with mock data")

        return self.state

    @listen(enrich)
    def engineering_review(self):
        """Run engineering review on all line items in a single batch."""
        if self.state.error:
            return self.state

        self._log_step("engineering", "Starting engineering review (batch)")

        self._project = self.project_store.get_project(self.state.project_id)
        self._project.status = "engineering_review"

        # Get items to evaluate
        items_to_evaluate = [
            item for item in self._project.line_items
            if item.status == LineItemStatus.ENRICHED
        ]

        if not items_to_evaluate:
            self._log_step("engineering", "No items to evaluate")
            return self.state

        # Batch evaluate all items in a single LLM call
        decisions = self._engineering_agent.evaluate_batch(
            items_to_evaluate,
            self._project.context,
            self.offers_store,
        )

        # Apply decisions to items
        approved = 0
        for item in items_to_evaluate:
            decision = decisions.get(item.mpn)
            if decision:
                item.engineering_decision = decision
                if decision.status == DecisionStatus.APPROVED:
                    item.approved_alternates = decision.output_data.get("approved_alternates", [])
                    item.status = LineItemStatus.PENDING_SOURCING
                    approved += 1
                else:
                    item.status = LineItemStatus.FAILED

                self._log_step(
                    "engineering",
                    f"{item.mpn}: {decision.status.value}",
                    agent="EngineeringAgent",
                    reasoning=decision.reasoning[:200] if decision.reasoning else None,
                )

        self.project_store.update_project(self._project)
        self._log_step("engineering", f"Engineering review complete: {approved}/{len(items_to_evaluate)} approved")

        return self.state

    @listen(engineering_review)
    def sourcing_review(self):
        """Run sourcing review on approved items in a single batch."""
        if self.state.error:
            return self.state

        self._log_step("sourcing", "Starting sourcing review (batch)")

        self._project = self.project_store.get_project(self.state.project_id)
        self._project.status = "sourcing_review"

        # Get items to evaluate
        items_to_evaluate = [
            item for item in self._project.line_items
            if item.status == LineItemStatus.PENDING_SOURCING
        ]

        if not items_to_evaluate:
            self._log_step("sourcing", "No items to evaluate")
            return self.state

        # Batch evaluate all items in a single LLM call
        decisions = self._sourcing_agent.evaluate_batch(
            items_to_evaluate,
            self._project.context,
            self.offers_store,
        )

        # Apply decisions to items
        approved = 0
        for item in items_to_evaluate:
            decision = decisions.get(item.mpn)
            if decision:
                item.sourcing_decision = decision
                if decision.status == DecisionStatus.APPROVED:
                    item.selected_mpn = decision.output_data.get("selected_mpn", item.mpn)
                    item.selected_supplier = decision.output_data.get("selected_supplier")
                    item.status = LineItemStatus.PENDING_FINANCE
                    approved += 1
                else:
                    item.status = LineItemStatus.FAILED

                self._log_step(
                    "sourcing",
                    f"{item.mpn}: {decision.status.value} - {decision.output_data.get('selected_supplier_name', 'N/A')}",
                    agent="SourcingAgent",
                    reasoning=decision.reasoning[:200] if decision.reasoning else None,
                )

        self.project_store.update_project(self._project)
        self._log_step("sourcing", f"Sourcing review complete: {approved} suppliers selected")

        return self.state

    @listen(sourcing_review)
    def finance_review(self):
        """Run finance review on sourced items in a single batch."""
        if self.state.error:
            return self.state

        self._log_step("finance", "Starting finance review (batch)")

        self._project = self.project_store.get_project(self.state.project_id)
        self._project.status = "finance_review"

        # Get items to evaluate
        items_to_evaluate = [
            item for item in self._project.line_items
            if item.status == LineItemStatus.PENDING_FINANCE
        ]

        if not items_to_evaluate:
            self._log_step("finance", "No items to evaluate")
            return self.state

        # Batch evaluate all items in a single LLM call
        decisions = self._finance_agent.evaluate_batch(
            items_to_evaluate,
            self._project.context,
            self.offers_store,
        )

        # Apply decisions to items
        approved = 0
        total_spend = 0.0
        for item in items_to_evaluate:
            decision = decisions.get(item.mpn)
            if decision:
                item.finance_decision = decision
                if decision.status == DecisionStatus.APPROVED:
                    item.status = LineItemStatus.PENDING_PURCHASE
                    total_spend += decision.output_data.get("approved_spend", 0.0)
                    approved += 1
                else:
                    item.status = LineItemStatus.FAILED

                self._log_step(
                    "finance",
                    f"{item.mpn}: {decision.status.value} - ${decision.output_data.get('approved_spend', 0):.2f}",
                    agent="FinanceAgent",
                    reasoning=decision.reasoning[:200] if decision.reasoning else None,
                )

        self.project_store.update_project(self._project)
        self._log_step("finance", f"Finance review complete: ${total_spend:.2f} total approved")

        return self.state

    @listen(finance_review)
    def complete(self):
        """Mark project as complete."""
        if self.state.error:
            return self.state

        self._project = self.project_store.get_project(self.state.project_id)
        self._project.status = "complete"
        self.project_store.update_project(self._project)

        self._log_step("complete", f"Project {self._project.project_id} processing complete")

        return self.state

    def _parse_bom(self, bom_path: str) -> list[BOMLineItem]:
        """Parse a BOM CSV file."""
        items = []
        with open(bom_path, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                ref_des = row.get("Reference Designators", row.get("Ref Des", row.get("Part Number", "")))
                items.append(BOMLineItem(
                    reference_designators=[ref_des] if ref_des else [],
                    quantity=int(row.get("Quantity", row.get("Qty", 1))),
                    mpn=row.get("MPN", row.get("Part Number", "")),
                    manufacturer=row.get("Manufacturer", ""),
                    description=row.get("Description", ""),
                    package=row.get("Package", ""),
                    value=row.get("Value", ""),
                ))
        return items

    def _parse_intake(self, intake_path: str) -> ProjectContext:
        """Parse a project intake YAML file."""
        with open(intake_path) as f:
            data = yaml.safe_load(f)

        project = data.get("project", {})
        requirements = data.get("requirements", {})
        compliance = data.get("compliance", {})
        sourcing = data.get("sourcing_constraints", {})
        engineering = data.get("engineering_context", {})

        pref_mfg_data = engineering.get("preferred_manufacturers", {})
        pref_mfg = PreferredManufacturers(
            capacitors=pref_mfg_data.get("capacitors", []),
            resistors=pref_mfg_data.get("resistors", []),
            mcu=pref_mfg_data.get("mcu", []),
            connectors=pref_mfg_data.get("connectors", []),
        )

        return ProjectContext(
            project_id=project.get("id", ""),
            project_name=project.get("name", ""),
            owner=project.get("owner", ""),
            engineering_contact=project.get("engineering_contact", ""),
            product_type=ProductType(requirements.get("product_type", "consumer")),
            quantity=requirements.get("quantity", 1),
            deadline=requirements.get("deadline"),
            budget_total=requirements.get("budget_total", 0.0),
            compliance=ComplianceRequirements(
                standards=compliance.get("standards", []),
                quality_class=compliance.get("quality_class", "IPC Class 2"),
                country_of_origin_restrictions=compliance.get("country_of_origin_restrictions", []),
            ),
            sourcing_constraints=SourcingConstraints(
                allow_brokers=sourcing.get("allow_brokers", False),
                allow_alternates=sourcing.get("allow_alternates", True),
                single_source_ok=sourcing.get("single_source_ok", False),
                preferred_distributors=sourcing.get("preferred_distributors", []),
                max_lead_time_days=sourcing.get("max_lead_time_days", 30),
            ),
            engineering_context=EngineeringContext(
                notes=engineering.get("notes", ""),
                critical_parts=engineering.get("critical_parts", []),
                preferred_manufacturers=pref_mfg,
            ),
        )


# Global agent instances - initialized at startup
_engineering_agent: Optional[EngineeringAgent] = None
_sourcing_agent: Optional[SourcingAgent] = None
_finance_agent: Optional[FinanceAgent] = None
_org_store: Optional[OrgKnowledgeStore] = None


def initialize_agents(data_dir: str = "data"):
    """Initialize agents at startup. Call this once when server starts."""
    global _engineering_agent, _sourcing_agent, _finance_agent, _org_store

    print("Initializing BOM processing agents...")

    _org_store = OrgKnowledgeStore(f"{data_dir}/org_knowledge.db")
    seed_default_suppliers(_org_store)

    _engineering_agent = EngineeringAgent(_org_store)
    _sourcing_agent = SourcingAgent(_org_store)
    _finance_agent = FinanceAgent()

    print(f"Agents initialized with model: {_engineering_agent._llm.model}")


def get_agents():
    """Get initialized agents. Returns (engineering, sourcing, finance, org_store)."""
    if _engineering_agent is None:
        raise RuntimeError("Agents not initialized. Call initialize_agents() first.")
    return _engineering_agent, _sourcing_agent, _finance_agent, _org_store


async def run_flow_async(
    bom_path: str,
    intake_path: Optional[str] = None,
    data_dir: str = "data",
    on_step: Optional[Callable[[FlowTraceStep], None]] = None,
) -> Project:
    """Run the BOM processing flow asynchronously."""
    global _engineering_agent, _sourcing_agent, _finance_agent, _org_store

    if _engineering_agent is None:
        initialize_agents(data_dir)

    project_store = ProjectStore(f"{data_dir}/projects.db")

    flow = BOMProcessingFlow(
        project_store,
        _org_store,
        _engineering_agent,
        _sourcing_agent,
        _finance_agent,
        on_step=on_step,
    )
    flow.state.bom_path = bom_path
    flow.state.intake_path = intake_path or ""

    await flow.kickoff_async()

    return project_store.get_project(flow.state.project_id)


def run_flow(
    bom_path: str,
    intake_path: Optional[str] = None,
    data_dir: str = "data",
    on_step: Optional[Callable[[FlowTraceStep], None]] = None,
) -> Project:
    """Run the BOM processing flow synchronously (for CLI usage)."""
    import asyncio
    return asyncio.run(run_flow_async(bom_path, intake_path, data_dir, on_step))
