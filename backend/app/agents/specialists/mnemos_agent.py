import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base_agent import BaseSpecialistAgent
from app.agents.agent_registry import AgentRegistry
from app.schemas.agent import AgentOutput
from app.services.rag.hybrid_search import hybrid_search_engine

logger = logging.getLogger(__name__)


class MnemosAgent(BaseSpecialistAgent):
    """
    MNEMOS — Retrieval, Knowledge & Authorized Memory Specialist.
    Retrieves facts from approved institutional knowledge records and syllabus documents.
    """

    def __init__(self):
        definition = AgentRegistry.get_agent("mnemos")
        if not definition:
            raise RuntimeError("MNEMOS agent definition not found in registry")
        super().__init__(definition)

    async def run(
        self,
        query: str,
        context: Dict[str, Any],
        db: AsyncSession,
        **kwargs
    ) -> AgentOutput:
        cat_slug = context.get("category_slug")
        search_res = await hybrid_search_engine.search(
            query=query,
            db=db,
            category_slug=cat_slug,
            top_k=4
        )

        candidates = search_res.get("candidates", [])
        evidence_context = search_res.get("evidence_context", "")
        citations = search_res.get("citations", [])
        conf = search_res.get("confidence")

        findings = evidence_context[:1000] if evidence_context else "No direct institutional records found."

        return AgentOutput(
            agent_id=self.id,
            success=len(candidates) > 0,
            findings=findings,
            structured_data={
                "candidate_count": len(candidates),
                "top_category": candidates[0].get("category_slug") if candidates else None,
                "evidence_context": evidence_context,
            },
            citations=citations,
            cards={},
            confidence=conf.score if conf else 0.85,
            model_used=self.definition.primary_model.model_id,
            provider_used=self.definition.primary_model.provider
        )

