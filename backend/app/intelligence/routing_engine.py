import time
import logging
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.model_router import ModelRouter, TaskRequirements, RoutingDecisionResult
from app.models.multi_llm import RoutingDecision

logger = logging.getLogger(__name__)


class RoutingEngine:
    """
    LAYER 5 — MODEL ROUTING ENGINE
    Selects the optimal model for each subtask within a turn, validating capabilities
    against budget constraints, and recording observability records.
    """

    @classmethod
    async def route_subtask(
        cls,
        task_name: str,
        intelligence_id: str,
        thinking_level: str,
        required_capabilities: list,
        request_id: str,
        db: Optional[AsyncSession] = None
    ) -> RoutingDecisionResult:
        start_time = time.time()

        req = TaskRequirements(
            task_name=task_name,
            required_capabilities=required_capabilities,
            intelligence_id=intelligence_id,
            thinking_level=thinking_level,
            latency_preference="ultra_fast" if thinking_level == "Low" else ("deep_reasoning" if thinking_level == "High" else "fast"),
        )

        decision = ModelRouter.select_model_for_task(req)
        latency_ms = int((time.time() - start_time) * 1000)

        # Record observability into database if session provided
        if db:
            try:
                rec = RoutingDecision(
                    request_id=request_id,
                    intelligence_id=intelligence_id,
                    subtask_name=task_name,
                    selected_provider=decision.provider_name,
                    selected_model=decision.model_id,
                    rationale=decision.rationale,
                    latency_ms=latency_ms,
                    cost_usd=decision.estimated_cost_usd
                )
                db.add(rec)
                await db.flush()
            except Exception as e:
                logger.warning(f"Could not persist RoutingDecision log: {e}")

        logger.info(
            f"RoutingEngine selected {decision.key} for subtask '{task_name}' ({intelligence_id.upper()}) - Rationale: {decision.rationale}"
        )
        return decision
