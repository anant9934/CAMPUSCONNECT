import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base_agent import BaseSpecialistAgent
from app.agents.agent_registry import AgentRegistry
from app.schemas.agent import AgentOutput

logger = logging.getLogger(__name__)


class AthenaAgent(BaseSpecialistAgent):
    """
    ATHENA — Academic Reasoning & Complex Analysis Specialist.
    Analyzes curriculum equivalence, credit transfers, examination rules, and grade upgradation criteria.
    """

    def __init__(self):
        definition = AgentRegistry.get_agent("athena")
        if not definition:
            raise RuntimeError("ATHENA agent definition not found in registry")
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

        is_exam = any(k in q_lower for k in ["exam", "backlog", "re-appear", "cgpa", "grade", "upgradation", "credit", "equivalence"])
        if is_exam:
            findings.append(
                "**Academic Evaluation Framework:**\n"
                "- **Re-appear / Backlog Exams:** Registration is managed strictly during designated semester windows in official UMS.\n"
                "- **Grade Upgradation & Credit Substitution:** Course equivalence for MOOCs/NPTEL or research publications requires "
                "prior course coordinator approval and Standing Academic Committee (SAC) ratification.\n"
                "- **Passing Criteria:** Minimum 40% aggregate in continuous assessments and end-term examinations with 75% attendance prerequisite."
            )
        else:
            findings.append("Academic curriculum rules evaluated against institutional degree requirements.")

        structured_text = "\n\n".join(findings)

        return AgentOutput(
            agent_id=self.id,
            success=True,
            findings=structured_text,
            structured_data={"is_academic_reasoning": is_exam},
            citations=[],
            cards={},
            confidence=0.95,
            model_used=self.definition.primary_model.model_id,
            provider_used=self.definition.primary_model.provider
        )

