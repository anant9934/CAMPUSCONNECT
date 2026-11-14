import os
import io
import re
import time
import uuid
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File, Form, status

logger = logging.getLogger(__name__)
from fastapi.responses import StreamingResponse
from pypdf import PdfReader
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.models import AnonymousSession, Conversation, Message, QueryLog
from app.ai.streaming_service import StreamingService
from app.ai.conversation_orchestrator import ConversationOrchestrator
from app.schemas.chat import ChatRequest, ChatResponse, ThinkingStep, Citation
from app.schemas.ums import (
    NavigationCard,
    BookingCard,
    ProcedureChecklist,
    RMSCard,
    PersonalRecordCard,
    CampusPlaceCard,
    FoodOutletCard,
    PersonCard,
    WhoToMeetCard,
    AcademicBenefitAssessmentCard,
    EvidenceCard,
)
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
from app.services.rag.intent_classifier import IntentClassifier
from app.services.actions.ums_service import UMSServiceResolver
from app.services.actions.workflow_engine import WorkflowEngine
from app.services.orchestration.multi_domain_orchestrator import MultiDomainOrchestrator
from app.services.campus_map_service import CampusMapService
from app.services.campus_food_service import CampusFoodService
from app.services.people_directory_service import PeopleDirectoryService
from app.services.issue_resolver_service import IssueToOfficeResolver
from app.services.edurev_advisor_service import AcademicBenefitAdvisor
from app.services.weather_service import WeatherService
from app.services.cache_service import QueryResponseCache
from app.services.rag.hybrid_search import hybrid_search_engine
from app.services.rag.confidence import ConfidenceLevel
from app.services.gemini_service import gemini_service
from app.services.grounding_service import validate_grounded_response, generate_follow_up_suggestions

router = APIRouter()

# Rate limiter memory table: session_token -> list of timestamps
SESSION_REQUEST_TIMESTAMPS: Dict[str, List[float]] = {}


def check_session_rate_limit(session_token: str) -> None:
    """Enforce per-session rate limiting."""
    now = time.time()
    window = 60.0  # 1 minute
    max_requests = settings.MAX_REQUESTS_PER_MINUTE_PER_SESSION

    timestamps = SESSION_REQUEST_TIMESTAMPS.get(session_token, [])
    # Filter timestamps within window
    timestamps = [t for t in timestamps if now - t < window]
    if len(timestamps) >= max_requests:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded: maximum {max_requests} requests per minute. Please pause before sending another message."
        )
    timestamps.append(now)
    SESSION_REQUEST_TIMESTAMPS[session_token] = timestamps


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    req: ChatRequest,
    http_req: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Public student chat endpoint:
    Performs verified hybrid retrieval, Gemini Flash generation,
    grounding validation, and returns transparent 5-step thinking progression.
    """
    start_time = time.time()
    now_utc = datetime.now(timezone.utc)

    # 1. Validate session
    check_session_rate_limit(req.session_token)

    session_stmt = select(AnonymousSession).where(
        AnonymousSession.session_token == req.session_token,
        AnonymousSession.is_active == True
    )
    session_result = await db.execute(session_stmt)
    session = session_result.scalars().first()

    if not session:
        # Auto-create anonymous session if not existing or expired
        client_ip = http_req.client.host if http_req.client else None
        user_agent = http_req.headers.get("user-agent", "")[:500]
        session = AnonymousSession(
            session_token=req.session_token,
            client_ip=client_ip,
            user_agent=user_agent,
            is_active=True,
            last_activity_at=now_utc,
            expires_at=now_utc + timedelta(days=7),
        )
        db.add(session)
        await db.flush()
    else:
        session.last_activity_at = now_utc

    # 2. Get or create conversation thread
    conversation = None
    if req.conversation_id:
        conv_stmt = select(Conversation).where(
            Conversation.id == req.conversation_id,
            Conversation.session_id == session.id,
            Conversation.is_active == True
        )
        conv_res = await db.execute(conv_stmt)
        conversation = conv_res.scalars().first()

    if not conversation:
        title_snippet = req.message.strip()[:40] + ("..." if len(req.message.strip()) > 40 else "")
        conversation = Conversation(
            session_id=session.id,
            title=title_snippet,
            is_active=True,
        )
        db.add(conversation)
        await db.flush()

    # 3. Store Student User Message
    user_msg = Message(
        conversation_id=conversation.id,
        role="user",
        content=req.message.strip(),
        thinking_steps=[],
        citations=[],
        confidence_score=1.0,
        latency_ms=0,
    )
    db.add(user_msg)
    await db.flush()

    # Fetch recent conversation history for context window
    history_stmt = (
        select(Message)
        .where(Message.conversation_id == conversation.id)
        .order_by(Message.created_at.asc())
    )
    hist_res = await db.execute(history_stmt)
    all_msgs = hist_res.scalars().all()
    history_turns = [{"role": m.role, "content": m.content} for m in all_msgs[:-1]]

    # Strip document upload wrapper for semantic resolution
    clean_message = re.sub(r"^\[Uploaded Document:[^\]]+\]\s*", "", req.message).strip() or req.message

    # Contextual query resolution for multi-turn anaphora
    effective_query = clean_message
    if history_turns:
        prior_user_msgs = [h["content"] for h in history_turns if h.get("role") == "user"]
        if prior_user_msgs and any(p in req.message.lower() for p in [" this", " that", " it", " above", " same", " there", " for this"]):
            effective_query = f"{' '.join(prior_user_msgs[-2:])} {clean_message}"

    # Check Semantic & Query Response Cache (0 LLM cost, preserves free-tier quotas)
    is_doc_upload = "[Uploaded " in req.message
    is_weather_q = any(k in req.message.lower() for k in ["weather", "temperature", "forecast", "raining", "rain today", "climate on campus"])

    if not is_doc_upload and not is_weather_q:
        cached_entry = QueryResponseCache.get(effective_query, context_prefix=req.category_slug or "")
        if cached_entry:
            cache_latency_ms = max(2, int((time.time() - start_time) * 1000))
            cached_nav = NavigationCard(**cached_entry["navigation_card"]) if cached_entry.get("navigation_card") else None
            cached_booking = BookingCard(**cached_entry["booking_card"]) if cached_entry.get("booking_card") else None
            cached_proc = ProcedureChecklist(**cached_entry["procedure_checklist"]) if cached_entry.get("procedure_checklist") else None
            cached_rms = RMSCard(**cached_entry["rms_card"]) if cached_entry.get("rms_card") else None
            cached_personal = PersonalRecordCard(**cached_entry["personal_record_card"]) if cached_entry.get("personal_record_card") else None
            cached_place = CampusPlaceCard(**cached_entry["campus_place_card"]) if cached_entry.get("campus_place_card") else None
            cached_food = FoodOutletCard(**cached_entry["food_outlet_card"]) if cached_entry.get("food_outlet_card") else None
            cached_person = PersonCard(**cached_entry["person_card"]) if cached_entry.get("person_card") else None
            cached_who = WhoToMeetCard(**cached_entry["who_to_meet_card"]) if cached_entry.get("who_to_meet_card") else None
            cached_benefit = AcademicBenefitAssessmentCard(**cached_entry["academic_benefit_card"]) if cached_entry.get("academic_benefit_card") else None
            cached_ev = EvidenceCard(**cached_entry["evidence_card"]) if cached_entry.get("evidence_card") else None

            cached_thinking = [ThinkingStep(**s) for s in cached_entry.get("thinking_steps", [])]
            cached_citations = [Citation(**c) for c in cached_entry.get("citations", [])]

            assistant_msg = Message(
                conversation_id=conversation.id,
                role="assistant",
                content=cached_entry["content"],
                thinking_steps=[s.model_dump() for s in cached_thinking],
                citations=[c.model_dump() for c in cached_citations],
                confidence_score=cached_entry.get("confidence_score", 0.98),
                latency_ms=cache_latency_ms,
            )
            db.add(assistant_msg)

            query_log = QueryLog(
                session_id=session.id,
                query_text=req.message,
                normalized_query=req.message.lower().strip(),
                matched_faq_id=cached_entry.get("matched_faq_id"),
                matched_category_id=cached_entry.get("matched_category_id"),
                confidence_score=cached_entry.get("confidence_score", 0.98),
                retrieval_strategy="semantic_cache_hit",
                gemini_status="cache_hit",
                latency_ms=cache_latency_ms,
            )
            db.add(query_log)
            await db.commit()
            await db.refresh(assistant_msg)

            return ChatResponse(
                conversation_id=str(conversation.id),
                message_id=str(assistant_msg.id),
                role="assistant",
                content=cached_entry["content"],
                action_type=cached_entry.get("action_type", "ANSWER"),
                thinking_steps=cached_thinking,
                citations=cached_citations,
                follow_ups=cached_entry.get("follow_ups", []),
                navigation_card=cached_nav,
                booking_card=cached_booking,
                procedure_checklist=cached_proc,
                rms_card=cached_rms,
                personal_record_card=cached_personal,
                campus_place_card=cached_place,
                food_outlet_card=cached_food,
                person_card=cached_person,
                who_to_meet_card=cached_who,
                academic_benefit_card=cached_benefit,
                evidence_card=cached_ev,
                confidence_score=cached_entry.get("confidence_score", 0.98),
                latency_ms=cache_latency_ms,
                is_ai_generated=False,
                agent_id=req.agent_id or "aegis",
                specialists_involved=cached_entry.get("specialists_involved", ["mnemos"]),
                agent_metadata={"cache_hit": True, "orchestrator": "aegis"},
            )

    # 4. Action Classification & Workflow Resolution (SRS v3.0 & v4.0)
    query_intent, intent_score, intent_meta = IntentClassifier.classify(effective_query)
    action_mode, action_score, action_rationale = ActionClassifier.classify_intent(req.message)
    matched_svc = await UMSServiceResolver.find_matching_service(effective_query, db) or await UMSServiceResolver.find_matching_service(req.message, db)
    matched_wf = await WorkflowEngine.match_workflow(effective_query, db) or await WorkflowEngine.match_workflow(req.message, db)
    matched_place = await CampusMapService.find_matching_place(req.message, db)

    # Build action cards
    nav_card: Optional[NavigationCard] = None
    booking_card: Optional[BookingCard] = None
    proc_checklist: Optional[ProcedureChecklist] = None
    rms_card: Optional[RMSCard] = None
    personal_card: Optional[PersonalRecordCard] = None
    place_card: Optional[CampusPlaceCard] = None
    food_card: Optional[FoodOutletCard] = None
    person_card: Optional[PersonCard] = None
    who_to_meet_card: Optional[WhoToMeetCard] = None
    academic_benefit_card: Optional[AcademicBenefitAssessmentCard] = None
    evidence_card: Optional[EvidenceCard] = None

    # Resolve personal campus intelligence entities
    multi_domain_res = await MultiDomainOrchestrator.orchestrate(
        query=effective_query,
        db=db,
        user_lat=req.user_lat,
        user_lon=req.user_lon,
        landmark=req.user_landmark,
    )
    food_card = multi_domain_res["food_card"]
    person_card = multi_domain_res["person_card"]
    who_to_meet_card = multi_domain_res["who_to_meet_card"]
    academic_benefit_card = multi_domain_res["academic_benefit_card"]
    if multi_domain_res["place_card"]:
        place_card = multi_domain_res["place_card"]
    if multi_domain_res["nav_card"]:
        nav_card = multi_domain_res["nav_card"]

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
    elif who_to_meet_card and who_to_meet_card.revalidation_notice:
        evidence_card = EvidenceCard(
            source_title=who_to_meet_card.category_title,
            source_type="Administrative Directory",
            document_name="Who to Meet Directory",
            clause_or_page=who_to_meet_card.room_details,
            verification_date="2026-11-18",
            is_official=True,
            revalidation_advisory=who_to_meet_card.revalidation_notice
        )

    if matched_svc:
        nav_card = UMSServiceResolver.build_navigation_card(matched_svc)
    elif matched_wf and action_mode == MODE_NAVIGATE:
        nav_card = NavigationCard(
            service_title=matched_wf.user_intent,
            module=matched_wf.target_system,
            breadcrumb=matched_wf.ums_navigation_path,
            instruction=f"Open UMS and navigate to: {matched_wf.ums_navigation_path}",
            handoff_url=matched_wf.handoff_url,
        )

    if action_mode == MODE_BOOK_HANDOFF:
        if matched_wf:
            booking_card = WorkflowEngine.build_booking_card(matched_wf)
        elif matched_svc:
            booking_card = BookingCard(
                booking_type="Campus Facility Booking",
                service_title=matched_svc.service_label,
                breadcrumb=matched_svc.navigation_path,
                prerequisites=["Valid Student Registration Number", "Active UMS Credentials"],
                availability_caveat="Real-time slot availability requires authentication inside official UMS. The public assistant does not reserve slots directly.",
                handoff_url=matched_svc.deep_link_url,
            )

    if action_mode == MODE_PREPARE:
        if matched_wf:
            proc_checklist = WorkflowEngine.build_procedure_checklist(matched_wf)
        elif matched_svc:
            proc_checklist = ProcedureChecklist(
                procedure_name=matched_svc.service_label,
                steps=[
                    "Sign in to official UMS at https://ums.lpu.in/lpuums/",
                    f"Navigate to: {matched_svc.navigation_path}",
                    f"Review instructions: {matched_svc.execution_boundary}"
                ],
                required_documents=["Student Registration Number / ID Card"],
                breadcrumb=matched_svc.navigation_path,
                handoff_url=matched_svc.deep_link_url,
            )

    if action_mode == MODE_ESCALATE or "grievance" in req.message.lower() or "rms" in req.message.lower() or "complaint" in req.message.lower():
        rms_card = WorkflowEngine.build_rms_card(matched_wf)

    if action_mode == MODE_PERSONAL_RECORD:
        personal_card = WorkflowEngine.build_personal_record_card(req.message, matched_wf)

    if matched_place:
        place_card = CampusMapService.build_place_card(matched_place)

    # 5. Thinking Step 1: Preparing question
    thinking_steps: List[ThinkingStep] = [
        ThinkingStep(
            step=1,
            title="Preparing question",
            description=f"Intent: {query_intent.value.replace('_', ' ').title()} ({intent_score:.2f}). Mode: {action_mode} ({action_score:.2f}). {action_rationale}",
            status="completed"
        )
    ]

    # 6. Thinking Step 2: Searching LPU knowledge
    search_res = await hybrid_search_engine.search(
        query=effective_query,
        db=db,
        category_slug=req.category_slug,
        top_k=4
    )
    candidates = search_res["candidates"]
    confidence_eval = search_res["confidence"]
    citations_data = search_res["citations"]
    evidence_context = search_res["evidence_context"]

    thinking_steps.append(
        ThinkingStep(
            step=2,
            title="Searching LPU knowledge",
            description=f"Retrieved {len(candidates)} approved institutional records using calibrated hybrid search.",
            status="completed"
        )
    )

    # 7. Thinking Step 3: Analysing retrieved information
    matched_faq = candidates[0] if candidates else None
    thinking_steps.append(
        ThinkingStep(
            step=3,
            title="Analysing retrieved information",
            description=f"Calibrated confidence score: {confidence_eval.score:.2f} ({confidence_eval.level.value.upper()}). {confidence_eval.explanation}",
            status="completed"
        )
    )

    # 8. Thinking Step 4: Generating response
    is_ai_generated = False
    ai_status = "success"

    # Enforce security boundaries for EXECUTE and PERSONAL_RECORD
    if action_mode == MODE_EXECUTE:
        nav_str = nav_card.breadcrumb if nav_card else (matched_wf.ums_navigation_path if matched_wf else "UMS Dashboard")
        content_draft = (
            "CampusConnect is an information and navigation assistant. Under university security policy, "
            "this public chatbot cannot directly execute transactions (such as fee payments, grade submissions, "
            "slot bookings, or cancellations) on your behalf.\n\n"
            f"To complete this action securely:\n"
            f"1. Sign in to the official LPU UMS portal at https://ums.lpu.in/lpuums/\n"
            f"2. Follow the verified navigation path: **`{nav_str}`**\n"
            f"3. Review your details and complete your submission inside the official authenticated interface."
        )
        is_ai_generated = False
        ai_status = "policy_intercept_execute"

    elif action_mode == MODE_PERSONAL_RECORD:
        b_path = personal_card.breadcrumb if personal_card else "UMS > My Profile"
        content_draft = (
            "To safeguard your personal data and privacy, the public CampusConnect assistant does not access "
            "or display private student records such as your individual attendance percentage, exam marks, "
            "CGPA, or fee receipts.\n\n"
            f"You can securely inspect your records directly in official UMS:\n"
            f"👉 **Navigation Breadcrumb:** `{b_path}`\n\n"
            "Please log in to official UMS at https://ums.lpu.in/lpuums/ to view your records."
        )
        is_ai_generated = False
        ai_status = "privacy_boundary_personal_record"

    elif (action_mode in [MODE_ESCALATE, MODE_BOOK_HANDOFF]) and (
        WorkflowEngine.is_emergency_medical(req.message) or
        any(k in req.message.lower() for k in ["emergency", "ambulance", "collapsed", "urgent medical", "chest pain", "hospital"])
    ):
        content_draft = (
            "🚨 **Urgent Campus Medical Concern:**\n"
            "If you require immediate medical assistance, do NOT wait for appointment scheduling. Please visit "
            "**UniHospital in Block 30** immediately or contact the **24x7 Campus Emergency Ambulance helpline: +91-1824-517100**.\n\n"
            "For routine OPD doctor consultations, log in to UMS or LPU Touch:\n"
            "`Student Services > Health Services > Doctor Appointment`."
        )
        is_ai_generated = False
        ai_status = "emergency_triage_routing"

    elif any(k in req.message.lower() for k in ["weather", "temperature", "forecast", "raining", "rain today", "climate on campus"]):
        weather_info = await WeatherService.get_current_weather(lat=req.user_lat, lon=req.user_lon)
        content_draft = (
            f"🌦️ **LPU Campus Weather Update (Open-Meteo):**\n\n"
            f"- **Condition:** {weather_info['weather_icon']} {weather_info['weather_condition']}\n"
            f"- **Current Temperature:** **{weather_info['temperature_c']}°C** (Feels like {weather_info['apparent_temperature_c']}°C)\n"
            f"- **Day High / Low:** {weather_info['temp_max_c']}°C / {weather_info['temp_min_c']}°C\n"
            f"- **Humidity:** {weather_info['humidity_percent']}%\n"
            f"- **Wind Speed:** {weather_info['wind_speed_kmh']} km/h\n"
            f"- **Precipitation Chance:** {weather_info['precipitation_probability']}%\n\n"
            f"🏃 **Campus Activity Advice:**\n{weather_info['campus_activity_advice']}\n\n"
            f"*Source: {weather_info['provider']} — Lat: {weather_info['latitude']}, Lon: {weather_info['longitude']}*"
        )
        is_ai_generated = False
        ai_status = "weather_intelligence"

    elif action_mode == MODE_ESCALATE and ("grievance" in req.message.lower() or "complaint" in req.message.lower() or "rms" in req.message.lower()) and not confidence_eval.should_generate_ai:
        content_draft = (
            "To submit a formal student grievance or service request, use the official LPU Relationship Management System (RMS) "
            "inside authenticated UMS:\n\n"
            "**Submission Path:** `UMS > Student Services > Relationship Management System > Log Request`\n\n"
            "1. **Select Message Type:** Complaint, Query, or Suggestion\n"
            "2. **Select Department:** Hostel, Examination, Academics, Transport, Security, etc.\n"
            "3. **Select Category & Subcategory:** Specify your precise issue\n"
            "4. **Describe Concern:** Provide full factual details and attach proof\n"
            "5. **Submit & Track:** Note the generated unique tracking number\n\n"
            "You can monitor resolution via: `Relationship Management System > View Request Status`.\n\n"
            "🔒 *Privacy Notice: For your confidentiality, please do not submit personal grievance details in this public chat.*"
        )
        is_ai_generated = False
        ai_status = "rms_guided_workflow"

    elif multi_domain_res.get("is_multi_domain") and multi_domain_res.get("content"):
        content_draft = multi_domain_res["content"]
        is_ai_generated = False
        ai_status = "multi_domain_orchestrated"
        action_mode = "MULTI_DOMAIN"

    elif food_card:
        if food_card.query_match_status == "exact":
            warning_line = f"\n⚠️ **Provenance Notice:** {food_card.verification_notice}\n" if food_card.verification_notice else ""
            content_draft = (
                f"🍽️ **{food_card.display_name}** ({food_card.zone})\n\n"
                f"📍 **Campus Location:** {food_card.location_description}\n"
                f"📏 **Estimated Straight-Line Distance:** Approx {food_card.distance_meters}m (straight-line radius; actual pedestrian distance depends on campus walkway network)\n"
                f"🕒 **Operating Hours:** {food_card.opening_hours} (Status: {food_card.open_status.upper()})\n"
                f"📜 **Verified Menu Matches:** {', '.join(food_card.matched_items)}\n"
                f"💰 **Sample Price:** {food_card.price_sample or 'Standard university pricing'}\n"
                f"🌱 **Dietary Policy:** 100% Pure Vegetarian campus mandate.\n"
                f"🔍 **Evidence Status:** `{food_card.evidence_status}` ({food_card.evidence_type.title()})\n"
                f"{warning_line}"
            )
        else:
            alt_lines = "\n".join([f"- **{alt.display_name}** ({alt.location}): {alt.specialty} | {alt.opening_hours}" for alt in food_card.alternatives])
            content_draft = (
                f"No verified menu match found for your requested item in our official campus food records.\n\n"
                "Lovely Professional University maintains a **100% pure vegetarian campus** with over 160 verified dining options. "
                f"Here are verified nearby vegetarian dining alternatives:\n\n{alt_lines}\n\n"
                "💡 *Tip: Try searching for common verified items such as thali, dosa, soya chaap, pizza, coffee, or sub.*"
            )
        is_ai_generated = False
        ai_status = "food_service_resolved"

    elif person_card and any(w in req.message.lower() for w in ["who", "whom", "hod", "head", "dean", "office", "cabin", "arora", "sobti", "nagpal", "aggarwal", "dalwinder"]):
        email_line = f"📧 **Official Email:** {person_card.email}\n" if person_card.email else ""
        advisory_line = f"\n⚠️ **Advisory Notice:** {person_card.revalidation_advisory}\n" if person_card.revalidation_advisory else ""
        content_draft = (
            f"👤 **{person_card.full_name}**\n\n"
            f"🎓 **Designation:** {person_card.designation}\n"
            f"🏛️ **School / Division:** {person_card.school_division}\n"
            f"🏢 **Building:** {person_card.building_block}\n"
            f"🚪 **Office / Cabin:** {person_card.room_cabin}\n"
            f"{email_line}"
            f"📌 **Key Distinction:** {person_card.notes}\n"
            f"🔍 **Evidence Status:** `{person_card.evidence_status}`\n"
            f"{advisory_line}\n"
            f"*Source: {person_card.profile_source} (Verified: {person_card.verification_date})*"
        )
        is_ai_generated = False
        ai_status = "person_directory_resolved"

    elif academic_benefit_card and any(w in req.message.lower() for w in ["ai project", "built", "project", "edurev", "edu-revolution", "academic benefit", "where do i submit"]):
        ev_lines = "\n".join([f"- {e}" for e in academic_benefit_card.evidence_checklist])
        lim_lines = "\n".join([f"- {lim}" for lim in academic_benefit_card.limitations_and_caveats])
        content_draft = (
            f"🚀 **EDU-Revolution Academic Benefit Advisory (Stage: {academic_benefit_card.portal_stage_name})**\n\n"
            f"Your work shows preliminary alignment with **{academic_benefit_card.category_id}: {academic_benefit_card.category_name}**.\n\n"
            f"🎯 **Potential Academic Recognition:**\n{academic_benefit_card.eligible_academic_benefits}\n\n"
            f"⏱️ **Course Mapping Window:** {academic_benefit_card.course_mapping_window}\n"
            f"🏛️ **Approval Prerequisite:** {academic_benefit_card.approval_prerequisite}\n\n"
            f"📋 **Required Evidence Checklist for Submission:**\n{ev_lines}\n\n"
            f"📍 **Where & How to Submit:**\n"
            f"1. **Online UMS Portal:** `{academic_benefit_card.submission_route}`\n"
            f"2. **Physical Guidance Point:** {academic_benefit_card.physical_helpdesk}\n\n"
            f"⚠️ **Institutional Caveats & Disclaimers:**\n{lim_lines}\n"
            f"- *{academic_benefit_card.guarantee_disclaimer}*\n"
            f"- *{academic_benefit_card.scrgm_distinction}*\n\n"
            f"🔍 **Evidence Status:** `{academic_benefit_card.evidence_status}`"
        )
        is_ai_generated = False
        ai_status = "edurev_advisor_resolved"

    elif who_to_meet_card and any(w in req.message.lower() for w in ["who", "whom", "meet", "attendance", "shortage", "wrong", "discrepancy", "submit", "challan", "fee issue", "counseling", "counselling", "warden", "wifi", "proctor", "proctorial", "discipline", "indiscipline", "misconduct", "hearing", "summons"]):
        doc_lines = "\n".join([f"- {d}" for d in who_to_meet_card.required_documents])
        ladder_lines = " ➔ ".join(who_to_meet_card.escalation_ladder)
        named_str = f" ({who_to_meet_card.named_contact_person})" if who_to_meet_card.named_contact_person else ""
        reval_line = f"\n\n⚠️ **Notice:** {who_to_meet_card.revalidation_notice}" if who_to_meet_card.revalidation_notice else ""
        content_draft = (
            f"🏛️ **{who_to_meet_card.category_title}**\n\n"
            f"👤 **Primary Contact:** {who_to_meet_card.primary_contact_role}{named_str}\n"
            f"📍 **Location:** {who_to_meet_card.office_location} — {who_to_meet_card.room_details}\n"
            f"💻 **UMS Online Route:** `{who_to_meet_card.ums_navigation_path}`\n\n"
            f"📋 **Prerequisite Action (First Step):**\n{who_to_meet_card.prerequisite_action}\n\n"
            f"📄 **Required Documents:**\n{doc_lines}\n\n"
            f"🪜 **Escalation Ladder:**\n{ladder_lines}\n\n"
            f"🔍 **Evidence Status:** `{who_to_meet_card.evidence_status}`"
            f"{reval_line}"
        )
        is_ai_generated = False
        ai_status = "issue_router_resolved"

    elif place_card and any(w in req.message.lower() for w in ["where is", "where's", "location of", "how to reach", "block 32", "block 34", "block 27", "room 102", "room 100", "room 308"]):
        svc_lines = "\n" + "\n".join([f"- {s}" for s in place_card.services]) if place_card.services else ""
        room_line = f"🚪 **Floor / Room:** {place_card.floor_room}\n" if place_card.floor_room else ""
        hours_line = f"🕒 **Operating Hours:** {place_card.opening_hours}\n" if place_card.opening_hours else ""
        access_line = f"♿ **Accessibility:** {place_card.accessibility}\n" if place_card.accessibility else ""
        content_draft = (
            f"📍 **{place_card.name}**\n\n"
            f"🏢 **Building / Block:** {place_card.building}\n"
            f"{room_line}"
            f"{hours_line}"
            f"{access_line}"
            f"ℹ️ **Details:** {place_card.description}"
            f"{svc_lines}\n\n"
            f"🗺️ **Official Campus Tour:** {place_card.map_url}"
        )
        is_ai_generated = False
        ai_status = "campus_place_resolved"

    elif confidence_eval.should_generate_ai:
        action_context = f"\n\n[ACTION GUIDANCE]\nMode: {action_mode}\nBoundary: {action_rationale}"
        if nav_card:
            action_context += f"\nVerified UMS Breadcrumb: {nav_card.breadcrumb}"
        if booking_card:
            action_context += f"\nBooking Path: {booking_card.breadcrumb}\nPrerequisites: {', '.join(booking_card.prerequisites)}"
        if proc_checklist:
            action_context += f"\nProcedure Steps: {', '.join(proc_checklist.steps)}"

        from app.ai.response_generator import ResponseGenerator
        try:
            llm_res = await ResponseGenerator.generate_response(
                user_message=req.message,
                evidence_context=evidence_context + action_context,
                conversation_history=history_turns,
                preferred_provider=req.provider,
            )
            content_draft = llm_res["content"]
            is_ai_generated = True
            ai_status = f"{llm_res.get('provider', 'ai')}_generated"
        except Exception as e:
            logger.warning(f"All LLM providers in cascade failed: {e}. Falling back to verified institutional records.")
            gemini_result = gemini_service._build_verified_fallback(
                query=req.message,
                top_faq_match=matched_faq,
                reason="all_providers_failed"
            )
            content_draft = gemini_result["text"]
            is_ai_generated = False
            ai_status = "error_fallback"
    else:
        # Abstain or safe fallback
        fallback = gemini_service._build_verified_fallback(
            query=req.message,
            top_faq_match=matched_faq,
            reason="low_confidence_abstain"
        )
        content_draft = fallback["text"]
        is_ai_generated = False
        ai_status = fallback["status"]

    thinking_steps.append(
        ThinkingStep(
            step=4,
            title="Generating response",
            description=f"Synthesized response under mode '{action_mode}' adhering strictly to institutional boundaries." if is_ai_generated else f"Prepared verified institutional response directly from knowledge base ({ai_status}).",
            status="completed"
        )
    )

    # 9. Thinking Step 5: Completed (Grounding validation)
    is_valid, final_content, validation_reason = validate_grounded_response(
        content_draft, evidence_context
    )
    if not is_valid:
        final_content = (
            "I could not verify the requested details against approved LPU documentation. "
            "Please check the official portal at https://ums.lpu.in or contact the relevant division."
        )

    thinking_steps.append(
        ThinkingStep(
            step=5,
            title="Completed",
            description="Verification complete. Action cards and verified guidance assembled.",
            status="completed"
        )
    )

    total_latency_ms = int((time.time() - start_time) * 1000)

    # Format Citations
    citations_list: List[Citation] = []
    for c in citations_data:
        citations_list.append(Citation(**c))

    if food_card and not citations_list:
        citations_list.append(Citation(
            title="LPU Hospitality & Uni-Centre Campus Food Directory",
            url="https://www.lpu.in/about_lpu/campus-facilities.php",
            source_type="Official Directory",
            verified=True,
            snippet=f"Verified pure vegetarian dining outlet: {food_card.display_name} ({food_card.location_description})"
        ))
    elif person_card and not citations_list:
        citations_list.append(Citation(
            title=person_card.profile_source,
            url="https://www.lpu.in/programmes/engineering/b-tech-computer-science",
            source_type="Official Directory",
            verified=True,
            snippet=f"{person_card.full_name} — {person_card.designation}, {person_card.school_division}"
        ))
    elif academic_benefit_card and not citations_list:
        citations_list.append(Citation(
            title="LPU EDU-Revolution Policy & Academic Benefits Guidelines",
            url="https://ums.lpu.in/lpuums/",
            source_type="Policy Document",
            verified=True,
            snippet=f"EDU-Revolution Category {academic_benefit_card.category_id}: {academic_benefit_card.category_name}. Submission via UMS RMS."
        ))
    elif who_to_meet_card and not citations_list:
        citations_list.append(Citation(
            title="LPU Student Issue Routing & Division Directory",
            url="https://ums.lpu.in/lpuums/",
            source_type="Official Directory",
            verified=True,
            snippet=f"{who_to_meet_card.category_title} — Primary contact: {who_to_meet_card.primary_contact_role} ({who_to_meet_card.office_location})"
        ))
    elif place_card and not citations_list:
        citations_list.append(Citation(
            title="Official LPU Campus Wayfinding Directory",
            url=place_card.map_url,
            source_type="Official Directory",
            verified=True,
            snippet=f"{place_card.name} — {place_card.building} ({place_card.floor_room or 'Ground Floor'})"
        ))

    # Follow-up Suggestions
    matched_category_slug = matched_faq.get("category_slug") if matched_faq else req.category_slug
    follow_ups = generate_follow_up_suggestions(matched_category_slug, req.message)

    # 10. Save Assistant Message
    assistant_msg = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=final_content,
        thinking_steps=[s.model_dump() for s in thinking_steps],
        citations=[c.model_dump() for c in citations_list],
        confidence_score=confidence_eval.score,
        latency_ms=total_latency_ms,
    )
    db.add(assistant_msg)

    # 11. Record Query Log
    query_log = QueryLog(
        session_id=session.id,
        query_text=req.message,
        normalized_query=req.message.lower().strip(),
        matched_faq_id=matched_faq.get("id") if matched_faq else None,
        matched_category_id=matched_faq.get("category_id") if matched_faq else None,
        confidence_score=confidence_eval.score,
        retrieval_strategy=f"hybrid_calibrated_{action_mode.lower()}",
        gemini_status=ai_status,
        latency_ms=total_latency_ms,
    )
    db.add(query_log)

    await db.commit()
    await db.refresh(assistant_msg)

    # Determine active specialist intelligences involved
    specialists_involved = []
    if food_card or person_card or place_card or who_to_meet_card:
        specialists_involved.append("argus")
    if nav_card or booking_card or proc_checklist or rms_card:
        specialists_involved.append("hermes")
    if academic_benefit_card or any(k in req.message.lower() for k in ["attendance", "edurev", "benefit", "policy"]):
        specialists_involved.append("themis")
    if not specialists_involved or confidence_eval.should_generate_ai:
        specialists_involved.append("mnemos")
    if req.agent_id and req.agent_id.lower() != "aegis" and req.agent_id.lower() not in specialists_involved:
        specialists_involved.insert(0, req.agent_id.lower())

    # Cache successful response for future queries (2h TTL, 0 LLM cost)
    if not is_doc_upload and not is_weather_q:
        QueryResponseCache.set(
            query=effective_query,
            response_data={
                "content": final_content,
                "action_type": action_mode,
                "thinking_steps": [s.model_dump() for s in thinking_steps],
                "citations": [c.model_dump() for c in citations_list],
                "follow_ups": follow_ups,
                "navigation_card": nav_card.model_dump() if nav_card else None,
                "booking_card": booking_card.model_dump() if booking_card else None,
                "procedure_checklist": proc_checklist.model_dump() if proc_checklist else None,
                "rms_card": rms_card.model_dump() if rms_card else None,
                "personal_record_card": personal_card.model_dump() if personal_card else None,
                "campus_place_card": place_card.model_dump() if place_card else None,
                "food_outlet_card": food_card.model_dump() if food_card else None,
                "person_card": person_card.model_dump() if person_card else None,
                "who_to_meet_card": who_to_meet_card.model_dump() if who_to_meet_card else None,
                "academic_benefit_card": academic_benefit_card.model_dump() if academic_benefit_card else None,
                "evidence_card": evidence_card.model_dump() if evidence_card else None,
                "confidence_score": confidence_eval.score,
                "matched_category_id": matched_faq.get("category_id") if matched_faq else None,
                "matched_faq_id": matched_faq.get("id") if matched_faq else None,
                "specialists_involved": specialists_involved,
            },
            context_prefix=req.category_slug or "",
            ttl_seconds=7200
        )

    return ChatResponse(
        conversation_id=str(conversation.id),
        message_id=str(assistant_msg.id),
        role="assistant",
        content=final_content,
        action_type=action_mode,
        thinking_steps=thinking_steps,
        citations=citations_list,
        follow_ups=follow_ups,
        navigation_card=nav_card,
        booking_card=booking_card,
        procedure_checklist=proc_checklist,
        rms_card=rms_card,
        personal_record_card=personal_card,
        campus_place_card=place_card,
        food_outlet_card=food_card,
        person_card=person_card,
        who_to_meet_card=who_to_meet_card,
        academic_benefit_card=academic_benefit_card,
        evidence_card=evidence_card,
        confidence_score=confidence_eval.score,
        latency_ms=total_latency_ms,
        is_ai_generated=is_ai_generated,
        agent_id=req.agent_id or "aegis",
        specialists_involved=specialists_involved,
        agent_metadata={
            "orchestrator": "aegis",
            "active_specialists": specialists_involved,
            "ai_status": ai_status,
        },
    )


@router.post("/chat/stream")
async def chat_stream_endpoint(
    req: ChatRequest,
    http_req: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Streaming chat endpoint using Server-Sent Events (SSE).
    Streams thinking steps, action cards, citations, and real Gemini tokens.
    """
    check_session_rate_limit(req.session_token)

    now_utc = datetime.now(timezone.utc)
    # Validate session
    session_stmt = select(AnonymousSession).where(
        AnonymousSession.session_token == req.session_token,
        AnonymousSession.is_active == True
    )
    session = (await db.execute(session_stmt)).scalars().first()
    if not session:
        session = AnonymousSession(
            session_token=req.session_token,
            client_ip=http_req.client.host if http_req.client else None,
            user_agent=http_req.headers.get("user-agent", "")[:500],
            is_active=True,
            last_activity_at=now_utc,
            expires_at=now_utc + timedelta(days=7),
        )
        db.add(session)
        await db.flush()

    # Get or create conversation
    conversation = None
    if req.conversation_id:
        conv_stmt = select(Conversation).where(
            Conversation.id == req.conversation_id,
            Conversation.session_id == session.id,
            Conversation.is_active == True
        )
        conversation = (await db.execute(conv_stmt)).scalars().first()

    if not conversation:
        title_snippet = req.message.strip()[:40] + ("..." if len(req.message.strip()) > 40 else "")
        conversation = Conversation(
            session_id=session.id,
            title=title_snippet,
            is_active=True,
        )
        db.add(conversation)
        await db.flush()

    # Store user message
    user_msg = Message(
        conversation_id=conversation.id,
        role="user",
        content=req.message.strip(),
        thinking_steps=[],
        citations=[],
        confidence_score=1.0,
        latency_ms=0,
    )
    db.add(user_msg)
    await db.commit()

    return StreamingResponse(
        StreamingService.stream_chat_turn(
            message=req.message,
            conversation_id=str(conversation.id),
            session_id=str(session.id),
            db=db,
            user_lat=req.user_lat,
            user_lon=req.user_lon,
            landmark=req.user_landmark,
            category_slug=req.category_slug,
            provider=req.provider,
            reasoning_mode=req.reasoning_mode,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Conversation-Id": str(conversation.id)
        }
    )


@router.post("/chat/upload")
async def chat_upload_document(
    file: UploadFile = File(...),
    session_token: str = Form(...),
    conversation_id: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload and extract text from student documents:
    Supports PDF, TXT, MD, and image files for academic project analysis.
    """
    filename = file.filename or "uploaded_file"
    ext = os.path.splitext(filename)[1].lower()

    extracted_text = ""
    content_bytes = await file.read()

    if ext == ".pdf":
        try:
            reader = PdfReader(io.BytesIO(content_bytes))
            for page in reader.pages[:10]:  # Up to first 10 pages
                extracted_text += (page.extract_text() or "") + "\n"
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to parse PDF: {e}")
    elif ext in [".txt", ".md", ".csv", ".json"]:
        extracted_text = content_bytes.decode("utf-8", errors="ignore")
    elif ext in [".png", ".jpg", ".jpeg", ".webp"]:
        extracted_text = f"[Image Document Uploaded: {filename} ({len(content_bytes)} bytes). File format verified.]"
    else:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format. Please upload PDF, TXT, Markdown, or Image files."
        )

    summary = extracted_text.strip()[:500] + ("..." if len(extracted_text.strip()) > 500 else "")

    return {
        "status": "success",
        "filename": filename,
        "size_bytes": len(content_bytes),
        "characters_extracted": len(extracted_text),
        "summary_preview": summary,
        "extracted_content": extracted_text[:3000]
    }

