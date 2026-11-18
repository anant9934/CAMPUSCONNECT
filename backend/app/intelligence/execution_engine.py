import time
import asyncio
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.llm_registry import LLMRegistry
from app.ai.cost_controller import CostController
from app.ai.shared_provider_registry import SharedProviderRegistry
from app.ai.model_router import ModelRouter, TaskRequirements
from app.models.multi_llm import AgentExecution, ToolExecution
from app.agents.specialists.argus_agent import ArgusAgent
from app.agents.specialists.hermes_agent import HermesAgent
from app.agents.specialists.forge_agent import ForgeAgent
from app.agents.specialists.vision_agent import VisionAgent
from app.agents.specialists.mnemos_agent import MnemosAgent

logger = logging.getLogger(__name__)


class ExecutionEngine:
    """
    LAYER 6 — EXECUTION ENGINE
    Manages live LLM generation, tool execution, and internal subagent delegation
    with parallel concurrency for independent subtasks.
    """

    _subagents_map = None

    @classmethod
    def _get_subagents(cls) -> Dict[str, Any]:
        if cls._subagents_map is None:
            cls._subagents_map = {
                "argus": ArgusAgent(),
                "hermes": HermesAgent(),
                "forge": ForgeAgent(),
                "vision": VisionAgent(),
                "mnemos": MnemosAgent(),
            }
        return cls._subagents_map

    @classmethod
    async def execute_subagents(
        cls,
        subagent_names: List[str],
        query: str,
        context: Dict[str, Any],
        db: Optional[AsyncSession],
        request_id: str,
        parent_intelligence: str
    ) -> List[Dict[str, Any]]:
        if db is None:
            from app.core.database import AsyncSessionLocal
            async with AsyncSessionLocal() as session:
                return await cls._execute_subagents_internal(
                    subagent_names=subagent_names,
                    query=query,
                    context=context,
                    db=session,
                    request_id=request_id,
                    parent_intelligence=parent_intelligence
                )
        return await cls._execute_subagents_internal(
            subagent_names=subagent_names,
            query=query,
            context=context,
            db=db,
            request_id=request_id,
            parent_intelligence=parent_intelligence
        )

    @classmethod
    async def _execute_subagents_internal(
        cls,
        subagent_names: List[str],
        query: str,
        context: Dict[str, Any],
        db: AsyncSession,
        request_id: str,
        parent_intelligence: str
    ) -> List[Dict[str, Any]]:
        """
        Executes internal specialist subagents in parallel using asyncio.gather.
        """
        subagents = cls._get_subagents()
        tasks = []
        valid_agents = []

        for name in subagent_names:
            agent = subagents.get(name.lower())
            if agent:
                valid_agents.append(name.lower())
                tasks.append(agent.execute(query=query, context=context, db=db))

        if not tasks:
            return []

        results = await asyncio.gather(*tasks, return_exceptions=True)
        agent_outputs: List[Dict[str, Any]] = []

        for name, res in zip(valid_agents, results):
            if isinstance(res, Exception):
                logger.error(f"Subagent {name.upper()} failed: {res}")
                continue

            findings = getattr(res, "findings", str(res))
            cards = getattr(res, "cards", {})
            citations = getattr(res, "citations", [])

            agent_outputs.append({
                "agent_name": name,
                "findings": findings,
                "cards": cards,
                "citations": citations,
            })

            # Record agent execution record in DB
            try:
                rec = AgentExecution(
                    request_id=request_id,
                    parent_intelligence=parent_intelligence,
                    agent_name=name,
                    status="completed",
                    findings=findings[:500] if findings else "",
                    latency_ms=getattr(res, "latency_ms", 50),
                )
                db.add(rec)
            except Exception as e:
                logger.warning(f"Could not persist AgentExecution record: {e}")

        return agent_outputs

    @classmethod
    async def call_routed_llm(
        cls,
        provider_name: str,
        model_id: str,
        prompt: str,
        system_instruction: str,
        conversation_history: List[Dict[str, str]],
        fallback_chain: List[str],
        user_identifier: str,
        intelligence_id: str,
        subtask_name: str,
        temperature: float = 0.2,
        max_output_tokens: int = 600
    ) -> Dict[str, Any]:
        """
        Executes LLM call with capability-aware fallback handling.
        """
        start_time = time.time()
        providers_to_try = [(provider_name, model_id)] + [
            tuple(fb.split("::")) for fb in fallback_chain if "::" in fb
        ]

        last_error = None
        for prov, mod in providers_to_try:
            try:
                active_provider = LLMRegistry.get_provider(prov)
                if not active_provider.is_available():
                    continue

                res = await active_provider.generate(
                    prompt=prompt,
                    system_instruction=system_instruction,
                    conversation_history=conversation_history,
                    temperature=temperature,
                    max_output_tokens=max_output_tokens
                )

                latency_ms = int((time.time() - start_time) * 1000)
                prompt_tok = len(prompt.split()) * 2  # approximate
                comp_tok = len(res.get("content", "").split()) * 2

                # Update health & record cost
                SharedProviderRegistry.update_health(prov, mod, success=True, latency_ms=latency_ms)
                CostController.record_execution_usage(
                    user_identifier=user_identifier,
                    intelligence_id=intelligence_id,
                    subtask_name=subtask_name,
                    provider_name=prov,
                    model_id=mod,
                    prompt_tokens=prompt_tok,
                    completion_tokens=comp_tok,
                    latency_ms=latency_ms
                )

                return {
                    "content": res["content"],
                    "provider": prov,
                    "model": mod,
                    "latency_ms": latency_ms,
                    "tokens": prompt_tok + comp_tok
                }
            except Exception as e:
                logger.warning(f"Provider {prov}::{mod} failed during execution: {e}. Trying fallback.")
                SharedProviderRegistry.update_health(prov, mod, success=False, error_msg=str(e))
                last_error = e

        raise RuntimeError(f"All routed LLM providers failed. Last error: {last_error}")
