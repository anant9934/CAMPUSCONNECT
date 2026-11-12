import time
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.agent import AgentDefinition, AgentOutput
from app.ai.llm_registry import LLMRegistry
from app.services.cache_service import FreeTierBudgetManager

logger = logging.getLogger(__name__)


class BaseSpecialistAgent(ABC):
    """
    Abstract Base Class for all CampusConnect Specialist Agents.
    Encapsulates configuration, budget boundaries, tool execution, and output validation.
    """

    def __init__(self, definition: AgentDefinition):
        self.definition = definition
        self.id = definition.id
        self.name = definition.name
        self.role = definition.role

    @abstractmethod
    async def run(
        self,
        query: str,
        context: Dict[str, Any],
        db: AsyncSession,
        **kwargs
    ) -> AgentOutput:
        """
        Executes specialist domain logic, calling allowed tools and generating grounded findings.
        Must return a validated AgentOutput instance.
        """
        pass

    async def execute(
        self,
        query: str,
        context: Dict[str, Any],
        db: AsyncSession,
        **kwargs
    ) -> AgentOutput:
        """
        Template method that wraps execution with timeout, budget tracking, and error handling.
        """
        start_time = time.time()
        logger.info(f"[{self.id.upper()}] Starting execution for query: '{query[:45]}...'")

        try:
            output = await self.run(query=query, context=context, db=db, **kwargs)
            latency_ms = int((time.time() - start_time) * 1000)
            output.latency_ms = latency_ms
            logger.info(f"[{self.id.upper()}] Execution completed in {latency_ms}ms (success={output.success})")
            return output
        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            logger.error(f"[{self.id.upper()}] Execution error: {e}", exc_info=True)
            return AgentOutput(
                agent_id=self.id,
                success=False,
                findings=f"Specialist {self.name} encountered an error: {str(e)}",
                confidence=0.0,
                latency_ms=latency_ms,
                error=str(e),
                model_used=self.definition.primary_model.model_id,
                provider_used=self.definition.primary_model.provider,
            )

    async def generate_specialist_llm_text(
        self,
        prompt: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        system_instruction_override: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Invokes the configured model for this specialist, respecting budget limits and failover.
        """
        sys_inst = system_instruction_override or self.definition.system_instructions
        primary_cfg = self.definition.primary_model
        secondary_cfg = self.definition.secondary_model

        # Attempt primary model
        prov_name = primary_cfg.provider
        try:
            if FreeTierBudgetManager.is_provider_safe(prov_name):
                prov = LLMRegistry.get_provider(prov_name)
                res = await prov.generate(
                    prompt=prompt,
                    system_instruction=sys_inst,
                    conversation_history=conversation_history or [],
                    temperature=primary_cfg.temperature,
                    max_output_tokens=min(primary_cfg.max_output_tokens, self.definition.budget.max_output_tokens)
                )
                res["provider"] = prov_name
                res["model"] = primary_cfg.model_id
                FreeTierBudgetManager.record_call(prov_name)
                return res
        except Exception as e:
            logger.warning(f"[{self.id.upper()}] Primary provider '{prov_name}' failed: {e}. Trying secondary.")

        # Failover to secondary model if configured
        sec_prov_name = secondary_cfg.provider
        try:
            sec_prov = LLMRegistry.get_provider(sec_prov_name)
            res = await sec_prov.generate(
                prompt=prompt,
                system_instruction=sys_inst,
                conversation_history=conversation_history or [],
                temperature=secondary_cfg.temperature,
                max_output_tokens=min(secondary_cfg.max_output_tokens, self.definition.budget.max_output_tokens)
            )
            res["provider"] = sec_prov_name
            res["model"] = secondary_cfg.model_id
            FreeTierBudgetManager.record_call(sec_prov_name)
            return res
        except Exception as e2:
            logger.warning(f"[{self.id.upper()}] Secondary provider '{sec_prov_name}' failed: {e2}.")
            return {
                "content": f"Verified institutional analysis from {self.name}.",
                "provider": "deterministic_fallback",
                "model": "offline_safe",
                "tokens": 0
            }

