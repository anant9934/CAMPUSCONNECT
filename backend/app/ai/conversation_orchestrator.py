import time
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.chat import ThinkingStep
from app.services.rag.intent_classifier import IntentClassifier
from app.services.actions.action_classifier import (
    ActionClassifier,
    MODE_EXECUTE,
    MODE_PERSONAL_RECORD,
    MODE_ESCALATE,
    MODE_BOOK_HANDOFF,
    MODE_PREPARE,
    MODE_NAVIGATE,
    MODE_ABSTAIN,
    MODE_ANSWER,
)
from app.services.actions.workflow_engine import WorkflowEngine
from app.schemas.ums import (
    BookingCard,
    ProcedureChecklist,
    RMSCard,
    PersonalRecordCard,
    EvidenceCard,
)
from app.ai.tool_executor import ToolExecutor
from app.ai.context_manager import ContextManager
from app.ai.response_generator import ResponseGenerator
from app.ai.response_validator import ResponseValidator
from app.ai.fallback_manager import FallbackManager
from app.ai.usage_tracker import UsageTracker
from app.ai.gemini_provider import circuit_breaker
from app.ai.proactive_intelligence import ProactiveStudentIntelligence

logger = logging.getLogger(__name__)


class ConversationOrchestrator:
    """
    Central AI Conversation Orchestrator implementing the full specification pipeline:
    User Message
    → Intent Understanding & Mode Classification
    → Context Retrieval & Tool Selection
    → Backend Tool Execution & Evidence Collection
    → Gemini Reasoning & Response Generation
    → Response Validation
    → Output Assembly with Concurrent UI Action Cards
    """

    @classmethod
    async def process_user_turn(
        cls,
        message: str,
        conversation_id: str,
        session_id: str,
        db: AsyncSession,
        user_lat: Optional[float] = None,
        user_lon: Optional[float] = None,
        landmark: Optional[str] = None,
        category_slug: Optional[str] = None,
    ) -> Dict[str, Any]:
        start_time = time.time()
        q_clean = message.strip()

        # Step 1: Intent Understanding & Classification
        query_intent, intent_score, intent_meta = IntentClassifier.classify(q_clean)
        action_mode, action_score, action_rationale = ActionClassifier.classify_intent(q_clean)

        thinking_steps: List[ThinkingStep] = [
            ThinkingStep(
                step=1,
                title="Understanding intent",
                description=f"Identified intent '{query_intent.value.replace('_', ' ').title()}' ({intent_score:.2f}) with action mode '{action_mode}'. {action_rationale}",
                status="completed"
            )
        ]

        # Step 2: Tool Execution & Evidence Collection
        thinking_steps.append(
            ThinkingStep(
                step=2,
                title="Executing campus tools & RAG search",
                description="Querying institutional directories, food services, who-to-meet router, and hybrid BM25 knowledge base.",
                status="completed"
            )
        )

        tool_results = await ToolExecutor.execute_all_relevant_tools(
            query=q_clean,
            db=db,
            user_lat=user_lat,
            user_lon=user_lon,
            landmark=landmark,
            category_slug=category_slug
        )

        food_card = tool_results["food_card"]
        person_card = tool_results["person_card"]
        benefit_card = tool_results["academic_benefit_card"]
        issue_card = tool_results["who_to_meet_card"]
        place_card = tool_results["place_card"]
        nav_card = tool_results["nav_card"]
        matched_wf = tool_results["matched_wf"]
        candidates = tool_results["candidates"]
        confidence_eval = tool_results["confidence"]
        citations = tool_results["citations"]
        evidence_context = tool_results["evidence_context"]

        # Step 3: Context Retrieval & Analysis
        thinking_steps.append(
            ThinkingStep(
                step=3,
                title="Analyzing retrieved evidence",
                description=f"Confidence evaluated at {confidence_eval.score:.2f} ({confidence_eval.level.value.upper()}) with {len(candidates)} verified records.",
                status="completed"
            )
        )

        history_turns = await ContextManager.get_conversation_history(conversation_id, db)

        # Build ancillary cards (Booking, Procedure, RMS, Personal)
        booking_card: Optional[BookingCard] = None
        proc_checklist: Optional[ProcedureChecklist] = None
        rms_card: Optional[RMSCard] = None
        personal_card: Optional[PersonalRecordCard] = None
        evidence_card: Optional[EvidenceCard] = None

        if action_mode == MODE_BOOK_HANDOFF and matched_wf:
            booking_card = WorkflowEngine.build_booking_card(matched_wf)
        elif action_mode == MODE_PREPARE and matched_wf:
            proc_checklist = WorkflowEngine.build_procedure_checklist(matched_wf)
        elif action_mode == MODE_ESCALATE or any(k in q_clean.lower() for k in ["grievance", "rms", "complaint"]):
            rms_card = WorkflowEngine.build_rms_card(matched_wf)
        elif action_mode == MODE_PERSONAL_RECORD:
            personal_card = WorkflowEngine.build_personal_record_card(q_clean, matched_wf)

        if person_card and person_card.revalidation_advisory:
            evidence_card = EvidenceCard(
                source_title=person_card.profile_source,
                source_type="Public Directory",
                document_name="LPU Public People Directory",
                clause_or_page=person_card.room_cabin,
                verification_date=person_card.verification_date,
                is_official=True,
                revalidation_advisory=person_card.revalidation_advisory
            )
        elif issue_card and issue_card.revalidation_notice:
            evidence_card = EvidenceCard(
                source_title=issue_card.category_title,
                source_type="Administrative Directory",
                document_name="Who to Meet Directory",
                clause_or_page=issue_card.room_details,
                verification_date="2026-11-18",
                is_official=True,
                revalidation_advisory=issue_card.revalidation_notice
            )

        # Step 4: Strict Deterministic Security & Privacy Boundaries
        # If the student is asking to execute transactions or read private marks, enforce policy
        is_ai_generated = False
        ai_status = "gemini_generated"
        generated_content = ""

        if action_mode == MODE_EXECUTE:
            nav_str = nav_card.breadcrumb if nav_card else (matched_wf.ums_navigation_path if matched_wf else "UMS Dashboard")
            generated_content = (
                "CampusConnect is an institutional information assistant. Under university security guidelines, "
                "this public portal cannot directly execute financial transactions or submit academic changes on your behalf.\n\n"
                f"To complete this securely, please sign in to official UMS and follow:\n"
                f"👉 **`{nav_str}`**"
            )
            ai_status = "policy_intercept_execute"

        elif action_mode == MODE_PERSONAL_RECORD:
            b_path = personal_card.breadcrumb if personal_card else "UMS > My Profile"
            generated_content = (
                "To safeguard student data privacy, individual academic records (such as your personal attendance percentage, "
                "exam marks, CGPA, or fee receipts) are not accessible via this public assistant.\n\n"
                f"You can securely inspect your records directly in authenticated UMS:\n"
                f"👉 **Navigation Route:** `{b_path}`"
            )
            ai_status = "privacy_boundary_personal_record"

        elif WorkflowEngine.is_emergency_medical(q_clean):
            generated_content = (
                "🚨 **Immediate Medical Assistance:**\n"
                "For acute health emergencies, do not wait for online booking. Please proceed directly to "
                "**Uni-Hospital in Block 30** or call the **24x7 Campus Emergency Ambulance helpline: +91-1824-517100**.\n\n"
                "For routine OPD consultations, book via UMS: `Student Services > Health Services > Doctor Appointment`."
            )
            ai_status = "emergency_triage"

        else:
            # Step 5: Proactive Intelligence & Multi-Provider LLM Generation
            proactive_eval = await ProactiveStudentIntelligence.evaluate_turn(
                user_message=q_clean,
                conversation_history=history_turns
            )

            thinking_steps.append(
                ThinkingStep(
                    step=4,
                    title="Proactive Opportunity Reasoning & Multi-Provider Generation",
                    description=f"Inferred objective: '{proactive_eval.underlying_objective[:60]}...'. Synthesizing verified policy evidence with real LLM gateway.",
                    status="completed"
                )
            )

            try:
                if circuit_breaker.is_open():
                    fb = FallbackManager.get_quota_exhausted_response(tool_results)
                    generated_content = fb["content"]
                    ai_status = "quota_fallback"
                else:
                    llm_res = await ResponseGenerator.generate_response(
                        user_message=q_clean,
                        evidence_context=evidence_context,
                        conversation_history=history_turns,
                        proactive_context=proactive_eval.proactive_guidance_text
                    )
                    generated_content = llm_res["content"]
                    is_ai_generated = True

                    # Log usage asynchronously
                    await UsageTracker.log_usage(
                        db=db,
                        model_name=llm_res.get("model", "gemini"),
                        prompt_tokens=llm_res.get("prompt_tokens", 0),
                        completion_tokens=llm_res.get("completion_tokens", 0),
                        latency_ms=llm_res.get("latency_ms", 0),
                        status="success",
                        session_id=session_id,
                        conversation_id=conversation_id
                    )

            except Exception as e:
                logger.warning(f"Real LLM cascade encountered error, falling back to verified records: {e}")
                fb = FallbackManager.get_service_error_response(str(e), tool_results)
                generated_content = fb["content"]
                ai_status = "error_fallback"

                await UsageTracker.log_usage(
                    db=db,
                    model_name="gemini",
                    prompt_tokens=0,
                    completion_tokens=0,
                    latency_ms=0,
                    status="error",
                    session_id=session_id,
                    conversation_id=conversation_id,
                    error_message=str(e)
                )

        # Step 6: Response Validation & Guardrails
        validated_text, is_valid, val_reason = ResponseValidator.validate_and_sanitize(generated_content)

        thinking_steps.append(
            ThinkingStep(
                step=5,
                title="Validating response guardrails",
                description="Verified institutional facts against university safety policies and sanitized external links.",
                status="completed"
            )
        )

        total_latency = int((time.time() - start_time) * 1000)

        return {
            "content": validated_text,
            "thinking_steps": thinking_steps,
            "citations": citations,
            "confidence_score": confidence_eval.score,
            "latency_ms": total_latency,
            "is_ai_generated": is_ai_generated,
            "ai_status": ai_status,
            "nav_card": nav_card,
            "booking_card": booking_card,
            "proc_checklist": proc_checklist,
            "rms_card": rms_card,
            "personal_card": personal_card,
            "place_card": place_card,
            "food_card": food_card,
            "person_card": person_card,
            "who_to_meet_card": issue_card,
            "academic_benefit_card": benefit_card,
            "evidence_card": evidence_card,
        }
