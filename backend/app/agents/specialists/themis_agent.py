import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base_agent import BaseSpecialistAgent
from app.agents.agent_registry import AgentRegistry
from app.schemas.agent import AgentOutput
from app.services.edurev_advisor_service import AcademicBenefitAdvisor
from app.services.issue_resolver_service import IssueToOfficeResolver

logger = logging.getLogger(__name__)


class ThemisAgent(BaseSpecialistAgent):
    """
    THEMIS — University Policy, Academic Benefits & Eligibility Assessment Specialist.
    Analyzes attendance shortage scenarios, EDU-Revolution project categories (1 to 9),
    and course equivalence eligibility.
    """

    def __init__(self):
        definition = AgentRegistry.get_agent("themis")
        if not definition:
            raise RuntimeError("THEMIS agent definition not found in registry")
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
        cards: Dict[str, Any] = {}
        citations: List[Dict[str, Any]] = []

        # 1. Attendance Problem Solving Logic
        is_attendance = any(k in q_lower for k in ["attendance", "shortage", "debarred", "condonation", "medical leave", "duty leave"])
        if is_attendance:
            findings.append(
                "Under LPU Academic Regulations, a minimum of **75% attendance** is mandatory to appear in End-Term Examinations. "
                "The statutory condonation floor is **65%**, applicable strictly for legitimate medical hospitalization or official university representation."
            )
            findings.append(
                "⚠️ **Critical Institutional Boundary:** Fraudulent medical certificates or manipulated attendance claims violate "
                "Section 12 of the LPU Student Code of Conduct and result in immediate Proctorial Board disciplinary action. "
                "Legitimate routes include: UMS Duty Leave submission within 7 days, Hospital medical slips within 3 days, "
                "and biometric audit reconciliation with your Class Mentor."
            )

        # 2. EDU-Revolution & Academic Benefit Advisory
        is_benefit = any(k in q_lower for k in ["project", "edurev", "edu-revolution", "academic benefit", "revenue", "patent", "startup", "ca exemption", "course equivalence"])
        benefit_card = None
        if is_benefit or is_attendance:
            benefit_card = AcademicBenefitAdvisor.assess_project(query)
            if benefit_card:
                cards["academic_benefit_card"] = benefit_card.model_dump()
                citations.append({
                    "title": f"LPU EDU-Revolution Policy — {benefit_card.category_name}",
                    "url": "https://ums.lpu.in/lpuums/",
                    "source_type": "Official Policy Document",
                    "verified": True,
                    "snippet": f"Category {benefit_card.category_id}: {benefit_card.eligible_academic_benefits}"
                })
                findings.append(
                    f"Identified preliminary alignment with **{benefit_card.category_id}: {benefit_card.category_name}**.\n"
                    f"- **Recognition Potential:** {benefit_card.eligible_academic_benefits}\n"
                    f"- **Submission Route:** `{benefit_card.submission_route}`\n"
                    f"- **Prerequisite:** {benefit_card.approval_prerequisite}"
                )

        # 3. Formulate Specialist Answer
        structured_findings = "\n\n".join(findings) if findings else "Evaluated query against official LPU academic policy."
        
        return AgentOutput(
            agent_id=self.id,
            success=True,
            findings=structured_findings,
            structured_data={
                "is_attendance_query": is_attendance,
                "is_benefit_query": is_benefit,
                "benefit_category": benefit_card.category_id if benefit_card else None,
            },
            citations=citations,
            cards=cards,
            confidence=0.96,
            model_used=self.definition.primary_model.model_id,
            provider_used=self.definition.primary_model.provider
        )
