import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base_agent import BaseSpecialistAgent
from app.agents.agent_registry import AgentRegistry
from app.schemas.agent import AgentOutput
from app.services.web_research_service import WebResearchService

logger = logging.getLogger(__name__)


class OracleAgent(BaseSpecialistAgent):
    """
    ORACLE — Web Research, Source Verification & Evidence Synthesis Specialist.
    Researches fresh external updates (SIH hackathons, UGC/AICTE notifications),
    enforcing priority domains and scoring source reliability.
    """

    def __init__(self):
        definition = AgentRegistry.get_agent("oracle")
        if not definition:
            raise RuntimeError("ORACLE agent definition not found in registry")
        super().__init__(definition)

    async def run(
        self,
        query: str,
        context: Dict[str, Any],
        db: AsyncSession,
        **kwargs
    ) -> AgentOutput:
        research_res = await WebResearchService.research_topic(query)
        
        citations: List[Dict[str, Any]] = []
        for c in research_res.citations:
            citations.append({
                "title": c.title,
                "url": c.url,
                "source_type": "Government Regulatory" if c.is_official_regulatory else "Official University",
                "verified": c.reliability_score >= 0.85,
                "snippet": c.extracted_claims[0] if c.extracted_claims else "",
                "reliability_score": c.reliability_score,
            })

        return AgentOutput(
            agent_id=self.id,
            success=True,
            findings=research_res.synthesized_findings,
            structured_data={
                "authority_verdict": research_res.source_authority_verdict,
                "citations_count": len(citations),
            },
            citations=citations,
            cards={},
            confidence=0.92,
            model_used=self.definition.primary_model.model_id,
            provider_used=self.definition.primary_model.provider
        )

