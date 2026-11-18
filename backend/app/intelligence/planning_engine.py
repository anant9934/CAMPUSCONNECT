import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from app.intelligence.intent_engine import IntentAnalysisResult
from app.ai.cost_controller import CostController

logger = logging.getLogger(__name__)


class ExecutionPlan(BaseModel):
    intelligence_id: str
    thinking_level: str  # "Low", "Balanced", "High"
    steps: List[str]
    required_tools: List[str]
    required_subagents: List[str]
    parallel_subtasks: List[str] = Field(default_factory=list)
    sequential_subtasks: List[str] = Field(default_factory=list)
    max_model_calls: int = 2
    estimated_cost_usd: float = 0.005
    rationale: str = ""


class PlanningEngine:
    """
    LAYER 3 — PLANNING ENGINE
    Deconstructs user requests into explicit execution pipelines, identifying
    required knowledge collections, tools, internal subagents, and cost allowances.
    """

    @classmethod
    def create_plan(
        cls,
        intent: IntentAnalysisResult,
        intelligence_id: str,
        thinking_level: str = "Balanced",
        context: Optional[Dict[str, Any]] = None
    ) -> ExecutionPlan:
        intel = intelligence_id.lower()
        level = thinking_level.title()
        budget = CostController.get_budget(intel)

        tools: List[str] = []
        subagents: List[str] = []
        steps: List[str] = ["understand_intent"]
        parallel: List[str] = []
        sequential: List[str] = []

        # 1. Low Thinking Level (Fast, Minimal Calls)
        if level == "Low" or intel == "nova":
            steps.extend(["retrieve_knowledge", "synthesize_response"])
            tools = ["hybrid_search"]
            subagents = []  # avoid multi-agent delegation for simple low-tier turns
            max_calls = 1
            cost = 0.001

        # 2. Balanced Thinking Level
        elif level == "Balanced":
            steps.extend(["retrieve_knowledge", "dispatch_specialists", "validate_sources", "synthesize_response"])
            tools = ["hybrid_search"]
            if intent.needs_spatial_tools:
                tools.extend(["campus_map", "food_directory"])
                subagents.append("argus")
            if intent.primary_intent in ["policy_compliance", "academic_benefit"]:
                subagents.append("themis")
                subagents.append("hermes")
            if intent.primary_intent == "technical_reasoning":
                subagents.append("forge")
            if intent.needs_web_search:
                tools.append("tavily_web_search")

            parallel = [f"exec_{s}" for s in subagents[:2]]
            sequential = ["verify_grounding", "assemble_cards"]
            max_calls = min(2, budget.max_calls_per_turn)
            cost = 0.005

        # 3. High Thinking Level (Deep Reasoning & Multi-Agent Verification)
        else:
            steps.extend([
                "deep_knowledge_retrieval",
                "parallel_specialist_consultation",
                "cross_reference_official_policy",
                "independent_source_verification",
                "synthesize_comprehensive_answer"
            ])
            tools = ["hybrid_search", "ums_resolver", "evidence_verifier"]
            if intent.needs_spatial_tools:
                tools.extend(["campus_map", "food_directory"])
                subagents.append("argus")
            if intent.primary_intent in ["policy_compliance", "academic_benefit"]:
                subagents.extend(["themis", "hermes"])
            if intent.primary_intent == "technical_reasoning":
                subagents.append("forge")
            if intent.needs_web_search or intel == "oracle":
                tools.append("tavily_web_search")

            # Always add memory retrieval for high-depth tasks
            subagents.append("mnemos")

            parallel = [f"exec_{s}" for s in subagents[:budget.max_parallel_agents]]
            sequential = ["independent_fact_check", "synthesize_response"]
            max_calls = min(3, budget.max_calls_per_turn)
            cost = 0.015

        # Dedup subagents
        dedup_subagents = list(dict.fromkeys(subagents))

        return ExecutionPlan(
            intelligence_id=intel,
            thinking_level=level,
            steps=steps,
            required_tools=tools,
            required_subagents=dedup_subagents,
            parallel_subtasks=parallel,
            sequential_subtasks=sequential,
            max_model_calls=max_calls,
            estimated_cost_usd=cost,
            rationale=f"Plan generated for {intel.upper()} at {level} depth. Tools: {len(tools)}, Subagents: {len(dedup_subagents)}."
        )
