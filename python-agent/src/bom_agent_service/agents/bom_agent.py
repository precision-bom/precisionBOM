"""CrewAI agent for BOM analysis and optimization."""

from crewai import Agent, Task, Crew


class BomAnalysisCrew:
    """CrewAI crew for analyzing and optimizing Bill of Materials."""

    def __init__(self):
        self.analyst = Agent(
            role="Electronics Parts Sourcing Expert",
            goal="Analyze BOM items and provide optimal sourcing recommendations",
            backstory="""You are an expert electronics parts sourcing specialist with deep
            knowledge of electronic components, manufacturers, and distributors. You help
            engineers identify parts, find alternatives, and optimize their Bill of Materials
            for cost, availability, and reliability.""",
            verbose=True,
            allow_delegation=False,
        )

    def analyze_bom(self, bom_content: str) -> str:
        """Analyze BOM items for ambiguity and suggest search terms.

        Args:
            bom_content: JSON string containing BOM items to analyze

        Returns:
            JSON string with analysis results
        """
        task = Task(
            description=f"""Analyze the following BOM items and for each item:
1. Determine if the part specification is ambiguous or needs clarification
2. Suggest optimal search terms for distributor APIs
3. Note any concerns (obsolete parts, unclear specs, etc.)

BOM Items:
{bom_content}

Respond in JSON format:
{{
  "analysis": [
    {{
      "bomItemId": "id",
      "query": "best search query for this part",
      "isAmbiguous": true/false,
      "suggestedSearchTerms": ["term1", "term2"],
      "notes": "any concerns or suggestions"
    }}
  ],
  "overallNotes": "any BOM-level observations"
}}""",
            expected_output="A JSON object containing analysis for each BOM item with search terms and notes",
            agent=self.analyst,
        )

        crew = Crew(
            agents=[self.analyst],
            tasks=[task],
            verbose=True,
        )

        result = crew.kickoff()
        return result.raw

    def generate_optimization_strategies(self, bom_with_offers: str) -> str:
        """Generate optimization strategies for BOM with available offers.

        Args:
            bom_with_offers: JSON string containing BOM items with their available offers

        Returns:
            JSON string with optimization strategies
        """
        task = Task(
            description=f"""You are a BOM optimization expert. Given a BOM with offers from
multiple distributors, generate 2-4 optimal sourcing strategies.

Consider these factors for JOINT optimization:
1. **Distributor Consolidation**: Fewer distributors = lower shipping costs
2. **Volume Pricing**: Some distributors offer better prices at higher quantities
3. **Stock Availability**: Prefer in-stock items for faster delivery
4. **Total Cost**: Balance individual part prices with shipping consolidation
5. **Minimum Order Quantities**: Some offers require minimum quantities

Generate strategies that represent different trade-offs (e.g., lowest cost vs fastest delivery vs single distributor).

BOM with Offers:
{bom_with_offers}

Respond in JSON format:
{{
  "strategies": [
    {{
      "name": "Strategy Name",
      "description": "Brief description of this strategy's trade-offs",
      "selections": {{"bomItemId1": 0, "bomItemId2": 1}},
      "reasoning": "Detailed explanation of why these selections optimize for this strategy"
    }}
  ],
  "jointConsiderations": "Explanation of cross-item dependencies and trade-offs considered"
}}

The "selections" object maps bomItemId to the index of the selected offer (0-indexed).""",
            expected_output="A JSON object containing 2-4 optimization strategies with selections and reasoning",
            agent=self.analyst,
        )

        crew = Crew(
            agents=[self.analyst],
            tasks=[task],
            verbose=True,
        )

        result = crew.kickoff()
        return result.raw

    def general_chat(self, system_prompt: str, user_message: str) -> str:
        """Handle general chat requests about parts sourcing.

        Args:
            system_prompt: System context/instructions
            user_message: User's question or request

        Returns:
            Response string
        """
        task = Task(
            description=f"""Context: {system_prompt}

User Request: {user_message}

Provide a helpful, concise response.""",
            expected_output="A helpful response to the user's request about electronics parts",
            agent=self.analyst,
        )

        crew = Crew(
            agents=[self.analyst],
            tasks=[task],
            verbose=True,
        )

        result = crew.kickoff()
        return result.raw
