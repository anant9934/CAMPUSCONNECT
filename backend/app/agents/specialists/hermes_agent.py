import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base_agent import BaseSpecialistAgent
from app.agents.agent_registry import AgentRegistry
from app.schemas.agent import AgentOutput
from app.services.actions.ums_service import UMSServiceResolver
from app.services.actions.workflow_engine import WorkflowEngine
from app.services.actions.action_classifier import (
    ActionClassifier,
    MODE_EXECUTE,
    MODE_PERSONAL_RECORD,
    MODE_ESCALATE,
    MODE_BOOK_HANDOFF,
    MODE_PREPARE,
    MODE_NAVIGATE,
)

logger = logging.getLogger(__name__)


class HermesAgent(BaseSpecialistAgent):
    """
    HERMES — UMS Navigation, Services & Workflow Specialist.
    Maps student requests to 234 official UMS pathways, prepares procedural checklists,
    and constructs verified navigation cards and RMS escalation routes.
    """

    def __init__(self):
        definition = AgentRegistry.get_agent("hermes")
        if not definition:
            raise RuntimeError("HERMES agent definition not found in registry")
        super().__init__(definition)

    async def run(
        self,
        query: str,
        context: Dict[str, Any],
        db: AsyncSession,
        **kwargs
    ) -> AgentOutput:
        q_clean = query.strip()
        action_mode, action_score, action_rationale = ActionClassifier.classify_intent(q_clean)
        
        # 1. Match UMS Catalog Entry (234 pathways)
        matched_svc = await UMSServiceResolver.find_matching_service(q_clean, db)
        matched_wf = await WorkflowEngine.match_workflow(q_clean, db)

        cards: Dict[str, Any] = {}
        citations: List[Dict[str, Any]] = []
        findings: List[str] = []

        # 2. Build Navigation Card
        nav_card = None
        if matched_svc:
            nav_card = UMSServiceResolver.build_navigation_card(matched_svc)
        elif matched_wf:
            nav_card = WorkflowEngine.build_navigation_card(matched_wf)

        if nav_card:
            cards["nav_card"] = nav_card.model_dump()
            citations.append({
                "title": f"LPU UMS Service Directory — {nav_card.service_title}",
                "url": nav_card.handoff_url,
                "source_type": "Official UMS Portal",
                "verified": True,
                "snippet": f"Verified navigation breadcrumb: {nav_card.breadcrumb}"
            })
            findings.append(f"Official UMS Navigation Path: **`{nav_card.breadcrumb}`** ({nav_card.instruction})")

        # 3. Handle Workflows (Booking, Prepare/Checklist, RMS Grievance)
        if action_mode == MODE_BOOK_HANDOFF and matched_wf:
            booking_card = WorkflowEngine.build_booking_card(matched_wf)
            cards["booking_card"] = booking_card.model_dump()
            findings.append(f"Booking handoff: {booking_card.availability_caveat}")

        if action_mode == MODE_PREPARE and matched_wf:
            proc_card = WorkflowEngine.build_procedure_checklist(matched_wf)
            cards["procedure_checklist"] = proc_card.model_dump()
            findings.append(f"Required Steps:\n" + "\n".join([f"- {s}" for s in proc_card.steps]))

        if action_mode == MODE_ESCALATE or any(k in q_clean.lower() for k in ["rms", "grievance", "complaint"]):
            rms_card = WorkflowEngine.build_rms_card(matched_wf)
            cards["rms_card"] = rms_card.model_dump()
            findings.append(f"Submit formal ticket via: `{rms_card.submission_path}`")

        # 4. Handle Security Intercepts (EXECUTE and PERSONAL_RECORD)
        if action_mode == MODE_EXECUTE:
            findings.append(
                "🔒 **Security Policy Boundary:** Under university security mandate, public AI assistants "
                "cannot directly execute transactions (such as fee payments, registrations, or room changes). "
                f"Please log in to official UMS at https://ums.lpu.in and navigate to: **`{nav_card.breadcrumb if nav_card else 'UMS Portal'}`**."
            )
        elif action_mode == MODE_PERSONAL_RECORD:
            personal_card = WorkflowEngine.build_personal_record_card(q_clean, matched_wf)
            cards["personal_record_card"] = personal_card.model_dump()
            findings.append(
                "🔒 **Student Privacy Protection:** Private records (individual CGPA, attendance %, fee receipts) "
                f"are protected behind university authentication. Navigate to: **`{personal_card.breadcrumb}`** inside official UMS."
            )

        structured_text = "\n\n".join(findings) if findings else "UMS pathway resolved."

        return AgentOutput(
            agent_id=self.id,
            success=True,
            findings=structured_text,
            structured_data={
                "action_mode": action_mode,
                "service_label": matched_svc.service_label if matched_svc else None,
                "breadcrumb": nav_card.breadcrumb if nav_card else None,
            },
            citations=citations,
            cards=cards,
            confidence=0.98 if nav_card else 0.85,
            model_used=self.definition.primary_model.model_id,
            provider_used=self.definition.primary_model.provider
        )

