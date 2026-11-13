import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base_agent import BaseSpecialistAgent
from app.agents.agent_registry import AgentRegistry
from app.schemas.agent import AgentOutput
from app.services.opportunities_service import OpportunitiesService

logger = logging.getLogger(__name__)


class ForgeAgent(BaseSpecialistAgent):
    """
    FORGE — Coding, Technical Projects & Architecture Specialist.
    Audits tech stack suitability, code repositories, and startup internship tracks.
    """

    def __init__(self):
        definition = AgentRegistry.get_agent("forge")
        if not definition:
            raise RuntimeError("FORGE agent definition not found in registry")
        super().__init__(definition)

    async def run(
        self,
        query: str,
        context: Dict[str, Any],
        db: AsyncSession,
        **kwargs
    ) -> AgentOutput:
        opps = await OpportunitiesService.get_opportunities(query=query)
        top_opps = opps[:3]

        findings: List[str] = [
            "**Technical Project Evaluation & Rubric:**\n"
            "- Codebases must include production Git history, automated test suites, and clean containerized architecture (Docker).\n"
            "- Full-stack and AI project tracks qualify under EDU-Revolution Category 5 (Revenue Generating) or Category 6 (Technical Project)."
        ]

        if top_opps:
            opp_lines = "\n".join([f"- **{o['title']}** at {o['company']} ({o['type']}) — *{o.get('stipend', 'Competitive')}*" for o in top_opps])
            findings.append(f"**Curated Technical Internship Matches:**\n{opp_lines}")

        structured_text = "\n\n".join(findings)

        return AgentOutput(
            agent_id=self.id,
            success=True,
            findings=structured_text,
            structured_data={"internship_matches": len(top_opps)},
            citations=[],
            cards={},
            confidence=0.94,
            model_used=self.definition.primary_model.model_id,
            provider_used=self.definition.primary_model.provider
        )

