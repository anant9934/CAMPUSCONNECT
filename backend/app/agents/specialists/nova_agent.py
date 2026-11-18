import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base_agent import BaseSpecialistAgent
from app.agents.agent_registry import AgentRegistry
from app.schemas.agent import AgentOutput
from app.services.rag.hybrid_search import hybrid_search_engine

logger = logging.getLogger(__name__)


class NovaAgent(BaseSpecialistAgent):
    """
    NOVA — Everyday Help & Common University Queries.
    Fast general questions, simple explanations, campus timings, fee structures, and daily student support.
    """

    def __init__(self):
        definition = AgentRegistry.get_agent("nova")
        if not definition:
            raise RuntimeError("NOVA agent definition not found in registry")
        super().__init__(definition)

    async def run(
        self,
        query: str,
        context: Dict[str, Any],
        db: AsyncSession,
        **kwargs
    ) -> AgentOutput:
        q_lower = query.lower()
        findings: List[str] = []
        citations: List[Dict[str, Any]] = []

        # 1. Search institutional knowledge
        search_res = await hybrid_search_engine.search(
            query=query,
            db=db,
            category_slug=context.get("category_slug"),
            top_k=3
        )
        candidates = search_res.get("candidates", [])
        raw_citations = search_res.get("citations", [])

        for c in raw_citations[:3]:
            citations.append(c)

        if candidates:
            for cand in candidates[:2]:
                title = cand.get("question", "Campus Information")
                ans = cand.get("answer", "")
                findings.append(f"• **{title}**: {ans}")
        else:
            findings.append(
                "Lovely Professional University standard operating guidelines:\n"
                "- **Administrative Timings:** 9:00 AM – 5:00 PM (Monday to Saturday)\n"
                "- **Uni-Hospital:** 24/7 emergency medical care and campus ambulance\n"
                "- **Hostel Security & Turnstiles:** Biometric punch in before 7:30 PM (summer) / 7:00 PM (winter)\n"
                "- **Portal Access:** Authenticated student actions require official UMS at https://ums.lpu.in"
            )

        structured_text = "\n\n".join(findings)

        return AgentOutput(
            agent_id=self.id,
            success=True,
            findings=structured_text,
            structured_data={"type": "everyday_guidance", "items_count": len(candidates)},
            citations=citations,
            cards={},
            confidence=0.92,
            model_used=self.definition.primary_model.model_id,
            provider_used=self.definition.primary_model.provider
        )
