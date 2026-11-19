import time
import logging
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.ai.shared_provider_registry import SharedProviderRegistry

logger = logging.getLogger(__name__)


@dataclass
class IntelligenceBudgetConfig:
    max_calls_per_turn: int = 3
    max_input_tokens: int = 4000
    max_output_tokens: int = 1000
    max_request_cost_usd: float = 0.02
    max_parallel_agents: int = 2
    max_retries: int = 2
    verification_allowance: bool = True
    daily_user_quota_tokens: int = 60000
    daily_user_cost_limit_usd: float = 0.50


# Configured cost & resource limits per intelligence identity
INTELLIGENCE_BUDGETS: Dict[str, IntelligenceBudgetConfig] = {
    "nova": IntelligenceBudgetConfig(
        max_calls_per_turn=2,
        max_input_tokens=2500,
        max_output_tokens=600,
        max_request_cost_usd=0.005,
        max_parallel_agents=1,
        max_retries=1,
        verification_allowance=False,
    ),
    "themis": IntelligenceBudgetConfig(
        max_calls_per_turn=3,
        max_input_tokens=4000,
        max_output_tokens=800,
        max_request_cost_usd=0.015,
        max_parallel_agents=2,
        max_retries=2,
        verification_allowance=True,
    ),
    "athena": IntelligenceBudgetConfig(
        max_calls_per_turn=4,
        max_input_tokens=6000,
        max_output_tokens=1500,
        max_request_cost_usd=0.030,
        max_parallel_agents=2,
        max_retries=2,
        verification_allowance=True,
    ),
    "oracle": IntelligenceBudgetConfig(
        max_calls_per_turn=4,
        max_input_tokens=8000,
        max_output_tokens=1500,
        max_request_cost_usd=0.040,
        max_parallel_agents=3,
        max_retries=2,
        verification_allowance=True,
    ),
    "aegis": IntelligenceBudgetConfig(
        max_calls_per_turn=5,
        max_input_tokens=8000,
        max_output_tokens=1200,
        max_request_cost_usd=0.035,
        max_parallel_agents=3,
        max_retries=2,
        verification_allowance=True,
    ),
}


class CostController:
    """
    Central Cost Controller and Quota Manager:
    - Calculates real dollar costs per provider pricing
    - Enforces input/output token ceilings
    - Attributes cost by intelligence identity and subtask
    - Halts execution when user quota or request budget is breached
    """

    # In-memory user quota state: user_key -> {"tokens_today": int, "cost_today": float, "reset_timestamp": float}
    _user_quotas: Dict[str, Dict[str, Any]] = {}

    # Aggregated metrics by intelligence: intelligence_id -> {"total_tokens": int, "total_cost_usd": float, "calls": int}
    _attribution: Dict[str, Dict[str, Any]] = {
        "nova": {"total_tokens": 0, "total_cost_usd": 0.0, "calls": 0},
        "themis": {"total_tokens": 0, "total_cost_usd": 0.0, "calls": 0},
        "athena": {"total_tokens": 0, "total_cost_usd": 0.0, "calls": 0},
        "oracle": {"total_tokens": 0, "total_cost_usd": 0.0, "calls": 0},
        "aegis": {"total_tokens": 0, "total_cost_usd": 0.0, "calls": 0},
    }

    @classmethod
    def get_budget(cls, intelligence_id: str) -> IntelligenceBudgetConfig:
        return INTELLIGENCE_BUDGETS.get(intelligence_id.lower(), INTELLIGENCE_BUDGETS["themis"])

    @classmethod
    def calculate_cost(
        cls,
        provider_name: str,
        model_id: str,
        prompt_tokens: int,
        completion_tokens: int
    ) -> float:
        """
        Calculates exact cost in USD based on provider model descriptor pricing.
        """
        model = SharedProviderRegistry.get_model(provider_name, model_id)
        if not model:
            # Fallback estimation ($0.20 per 1M blended)
            return ((prompt_tokens + completion_tokens) / 1000000.0) * 0.20

        cost_in = (prompt_tokens / 1000000.0) * model.pricing.input_usd_per_1m
        cost_out = (completion_tokens / 1000000.0) * model.pricing.output_usd_per_1m
        return round(cost_in + cost_out, 6)

    @classmethod
    def check_and_enforce_budget(
        cls,
        user_identifier: str,
        intelligence_id: str,
        estimated_input_tokens: int,
        call_count_in_turn: int
    ) -> Tuple[bool, Optional[str]]:
        """
        Validates if request is within both intelligence ceilings and user daily quotas.
        """
        budget = cls.get_budget(intelligence_id)

        # 1. Enforce turn call limit
        if call_count_in_turn > budget.max_calls_per_turn:
            return False, f"Maximum model invocations ({budget.max_calls_per_turn}) exceeded for {intelligence_id.upper()}."

        # 2. Enforce input token boundary
        if estimated_input_tokens > budget.max_input_tokens:
            return False, f"Input context ({estimated_input_tokens} tokens) exceeds budget limit ({budget.max_input_tokens}) for {intelligence_id.upper()}."

        # 3. Enforce User Daily Quota
        user_record = cls._get_or_create_user_quota(user_identifier)
        if user_record["tokens_today"] + estimated_input_tokens > budget.daily_user_quota_tokens:
            return False, "Daily student AI quota reached. Free-tier resets in 24 hours."

        if user_record["cost_today"] > budget.daily_user_cost_limit_usd:
            return False, f"Daily cost ceiling (${budget.daily_user_cost_limit_usd:.2f}) reached. Please contact campus admin."

        return True, None

    @classmethod
    def record_execution_usage(
        cls,
        user_identifier: str,
        intelligence_id: str,
        subtask_name: str,
        provider_name: str,
        model_id: str,
        prompt_tokens: int,
        completion_tokens: int,
        latency_ms: int
    ) -> float:
        """
        Logs token consumption, computes cost, updates user quotas and intelligence attribution.
        """
        total_tokens = prompt_tokens + completion_tokens
        cost_usd = cls.calculate_cost(provider_name, model_id, prompt_tokens, completion_tokens)

        # Update User Quota
        user_record = cls._get_or_create_user_quota(user_identifier)
        user_record["tokens_today"] += total_tokens
        user_record["cost_today"] += cost_usd

        # Update Intelligence Attribution
        intel_key = intelligence_id.lower()
        if intel_key not in cls._attribution:
            cls._attribution[intel_key] = {"total_tokens": 0, "total_cost_usd": 0.0, "calls": 0}
        cls._attribution[intel_key]["total_tokens"] += total_tokens
        cls._attribution[intel_key]["total_cost_usd"] += cost_usd
        cls._attribution[intel_key]["calls"] += 1

        logger.info(
            f"[{intelligence_id.upper()}:{subtask_name}] Used {total_tokens} tokens (${cost_usd:.6f}) via {provider_name}::{model_id} in {latency_ms}ms"
        )
        return cost_usd

    @classmethod
    def get_attribution_summary(cls) -> Dict[str, Any]:
        return {
            intel: {
                "total_tokens": data["total_tokens"],
                "total_cost_usd": round(data["total_cost_usd"], 4),
                "calls": data["calls"],
            }
            for intel, data in cls._attribution.items()
        }

    @classmethod
    def _get_or_create_user_quota(cls, user_key: str) -> Dict[str, Any]:
        now = time.time()
        record = cls._user_quotas.get(user_key)
        if not record or now > record["reset_timestamp"]:
            record = {
                "tokens_today": 0,
                "cost_today": 0.0,
                "reset_timestamp": now + 86400.0,  # 24h reset
            }
            cls._user_quotas[user_key] = record
        return record

