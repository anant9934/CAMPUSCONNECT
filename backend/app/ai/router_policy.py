import logging
from typing import List, Optional, Tuple
from app.core.config import settings
from app.ai.llm_provider import BaseLLMProvider
from app.ai.llm_registry import LLMRegistry
from app.ai.model_registry import ModelCapabilityRegistry, ModelCapability
from app.services.cache_service import FreeTierBudgetManager

logger = logging.getLogger(__name__)


class RouterPolicy:
    """
    Intelligent routing policy for CampusConnect V8:
    1. Evaluates query complexity (e.g. simple food lookup vs complex multi-turn benefit assessment/appeal).
    2. Identifies best model tier ('fast', 'balanced', 'deep').
    3. Selects active, healthy provider with available quota.
    4. Handles fallback cascades transparently across configured providers.
    """

    @classmethod
    def evaluate_task_complexity(cls, query: str, conversation_turn_count: int = 0) -> str:
        """
        Determines complexity tier: 'fast', 'balanced', or 'deep'.
        """
        q = query.lower()

        # Deep queries: multi-step regulations, attendance solver, appeals, disciplinary, research upgradation
        deep_triggers = [
            "attendance is low", "attendance benefit", "attendance shortage", "debarred",
            "disciplinary", "indiscipline", "appeal", "pro chancellor", "vice chancellor",
            "ca exemption", "course equivalence", "grade upgradation", "research paper",
            "patent", "startup revenue", "scrgm", "standing academic committee", "sac"
        ]
        if any(t in q for t in deep_triggers) or conversation_turn_count > 4:
            return "deep"

        # Balanced queries: project mapping, internships, hackathons, grievance guidance
        balanced_triggers = [
            "project", "hackathon", "internship", "stipend", "who to meet",
            "mentor", "coordinator", "hod", "fee installment", "rms"
        ]
        if any(t in q for t in balanced_triggers) or conversation_turn_count > 1:
            return "balanced"

        return "fast"

    @classmethod
    def select_provider_cascade(
        cls,
        query: str,
        conversation_turn_count: int = 0,
        preferred_provider: Optional[str] = None
    ) -> List[Tuple[str, BaseLLMProvider]]:
        """
        Returns an ordered cascade list of (provider_name, provider_instance) to attempt.
        """
        cascade: List[Tuple[str, BaseLLMProvider]] = []

        # 1. Preferred or default provider first (if within safe free-tier RPM budget)
        target_name = preferred_provider or settings.DEFAULT_LLM_PROVIDER
        throttled_providers: List[Tuple[str, BaseLLMProvider]] = []
        try:
            primary = LLMRegistry.get_provider(target_name)
            if primary.is_available():
                if FreeTierBudgetManager.is_provider_safe(target_name):
                    cascade.append((target_name, primary))
                else:
                    throttled_providers.append((target_name, primary))
        except Exception as e:
            logger.debug(f"Primary provider '{target_name}' unavailable: {e}")

        # 2. Add other available registered providers as fallbacks (prioritizing un-throttled free tiers)
        all_prov_info = LLMRegistry.list_providers()
        for p_info in all_prov_info:
            name = p_info["name"]
            if name == target_name or not p_info.get("available"):
                continue
            try:
                prov = LLMRegistry.get_provider(name)
                if FreeTierBudgetManager.is_provider_safe(name):
                    if (name, prov) not in cascade:
                        cascade.append((name, prov))
                else:
                    if (name, prov) not in throttled_providers:
                        throttled_providers.append((name, prov))
            except Exception:
                continue

        # Append soft-throttled providers at the end of the cascade as safety net
        for tp in throttled_providers:
            if tp not in cascade:
                cascade.append(tp)

        # If cascade is empty, still include default gemini instance to allow error handling/fallback
        if not cascade:
            cascade.append((target_name, LLMRegistry.get_default_provider()))

        return cascade

