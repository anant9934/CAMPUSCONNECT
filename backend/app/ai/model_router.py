import time
import logging
from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel, Field

from app.ai.shared_provider_registry import SharedProviderRegistry, ProviderModelDescriptor
from app.ai.cost_controller import CostController

logger = logging.getLogger(__name__)


class TaskRequirements(BaseModel):
    task_name: str  # e.g. "intent_planning", "everyday_faq", "policy_reasoning", "coding_debug", "web_synthesis", "verification"
    required_capabilities: List[str] = Field(default_factory=list)  # "streaming", "tools", "vision", "reasoning", "structured_output"
    minimum_context_window: int = 16000
    expected_output_tokens: int = 600
    latency_preference: str = "fast"  # ultra_fast, fast, standard, deep_reasoning
    max_budget_usd: float = 0.05
    intelligence_id: str = "nova"
    thinking_level: str = "Balanced"  # "Low", "Balanced", "High"
    allow_subtask_fanout: bool = False


class RoutingDecisionResult(BaseModel):
    provider_name: str
    model_id: str
    key: str
    rationale: str
    score: float
    estimated_cost_usd: float
    fallback_chain: List[str] = Field(default_factory=list)


class ModelRouter:
    """
    Dynamic Capability-Aware Model Router:
    Selects the optimal configured model for each subtask within a turn, evaluating:
    1. Capability match (tools, vision, reasoning, context length)
    2. Quality benchmark score
    3. Latency tier & availability
    4. Rate limits & Circuit breaker health
    5. Token pricing & remaining budget
    """

    @classmethod
    def select_model_for_task(cls, req: TaskRequirements) -> RoutingDecisionResult:
        all_models = SharedProviderRegistry.list_models(active_only=True)
        if not all_models:
            # Emergency offline fallback
            return RoutingDecisionResult(
                provider_name="gemini",
                model_id="gemini-2.5-flash",
                key="gemini::gemini-2.5-flash",
                rationale="Default primary model selected (registry cold).",
                score=50.0,
                estimated_cost_usd=0.0001,
                fallback_chain=[],
            )

        scored_candidates: List[Tuple[float, ProviderModelDescriptor, str]] = []

        for m in all_models:
            # 1. Hard filters: context window
            if m.capabilities.context_window < req.minimum_context_window:
                continue

            # 2. Hard filters: capabilities required
            caps = m.capabilities
            if "vision" in req.required_capabilities and not caps.image_input:
                continue
            if "tools" in req.required_capabilities and not caps.tool_calling:
                continue
            if "structured_output" in req.required_capabilities and not caps.structured_output:
                continue
            if "reasoning" in req.required_capabilities and not caps.reasoning_mode and req.thinking_level == "High":
                continue

            # 3. Circuit breaker check
            if m.health.circuit_state == "open":
                continue

            # 4. Scoring Algorithm
            score = 100.0

            # Quality benchmark weighting
            if req.thinking_level == "High" or req.intelligence_id in ["athena", "oracle"]:
                if m.latency_tier == "deep_reasoning" or "70b" in m.model_id or "pro" in m.model_id:
                    score += 40.0
            elif req.thinking_level == "Low" or req.intelligence_id == "nova":
                if m.latency_tier == "ultra_fast" or "free" in m.model_id or "flash" in m.model_id or "small" in m.model_id:
                    score += 50.0

            # Latency preference penalty
            if req.latency_preference == "ultra_fast" and m.latency_tier != "ultra_fast":
                score -= 20.0
            elif req.latency_preference == "deep_reasoning" and m.latency_tier == "ultra_fast":
                score -= 30.0

            # Price penalty to prevent budget exhaustion
            estimated_cost = CostController.calculate_cost(
                m.provider_name, m.model_id, req.minimum_context_window, req.expected_output_tokens
            )
            if estimated_cost > req.max_budget_usd:
                score -= 60.0
            elif estimated_cost == 0.0:
                score += 15.0  # reward free tier models for simple tasks

            # Health & Latency bonuses
            if m.health.avg_latency_ms < 500:
                score += 10.0

            rationale = (
                f"Matched requirements for {req.task_name}: caps={req.required_capabilities}, "
                f"tier={m.latency_tier}, latency={m.health.avg_latency_ms:.0f}ms, cost=${estimated_cost:.5f}"
            )
            scored_candidates.append((score, m, rationale))

        if not scored_candidates:
            # Fallback to standard versatile model (Gemini Flash or Groq Llama)
            fallback = SharedProviderRegistry.get_model("gemini", "gemini-2.5-flash") or all_models[0]
            return RoutingDecisionResult(
                provider_name=fallback.provider_name,
                model_id=fallback.model_id,
                key=f"{fallback.provider_name}::{fallback.model_id}",
                rationale="Fallback model selected after no candidate met strict capability threshold.",
                score=40.0,
                estimated_cost_usd=0.0001,
                fallback_chain=[],
            )

        scored_candidates.sort(key=lambda x: x[0], reverse=True)
        best_score, best_model, best_rationale = scored_candidates[0]

        # Prepare fallback chain from other viable candidates
        fallbacks = [
            f"{cand.provider_name}::{cand.model_id}"
            for _, cand, _ in scored_candidates[1:4]
        ]

        est_cost = CostController.calculate_cost(
            best_model.provider_name, best_model.model_id, req.minimum_context_window, req.expected_output_tokens
        )

        return RoutingDecisionResult(
            provider_name=best_model.provider_name,
            model_id=best_model.model_id,
            key=f"{best_model.provider_name}::{best_model.model_id}",
            rationale=best_rationale,
            score=round(best_score, 1),
            estimated_cost_usd=est_cost,
            fallback_chain=fallbacks,
        )

    @classmethod
    def get_fallback_model(
        cls,
        failed_key: str,
        req: TaskRequirements,
        error_type: str = "timeout"
    ) -> Optional[ProviderModelDescriptor]:
        """
        Capability-aware fallback selector when a provider experiences a failure or rate-limit.
        """
        logger.warning(f"Initiating capability-aware fallback for {failed_key} due to {error_type}.")
        curr_model = SharedProviderRegistry.get_by_key(failed_key)
        
        # 1. Check model's declared fallback compatibility list
        if curr_model and curr_model.fallback_compatibles:
            for fallback_key in curr_model.fallback_compatibles:
                fb = SharedProviderRegistry.get_by_key(fallback_key)
                if fb and fb.is_available and fb.health.is_healthy:
                    logger.info(f"Selected explicit fallback compatible: {fallback_key}")
                    return fb

        # 2. Select alternative from router excluding the failed key
        all_models = SharedProviderRegistry.list_models(active_only=True)
        eligible = [m for m in all_models if f"{m.provider_name}::{m.model_id}" != failed_key and m.health.is_healthy]
        if eligible:
            return eligible[0]

        return None
