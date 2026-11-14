import os
import csv
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, Header, status
from pydantic import BaseModel
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.models import AnonymousSession, Conversation, Message
from app.models.portal import (
    StudentProfile,
    StudentOpportunity,
    CampusEvent,
    SavedLocation,
    LLMUsageLog,
)
from app.services.edurev_advisor_service import AcademicBenefitAdvisor
from app.services.people_directory_service import PeopleDirectoryService
from app.services.actions.ums_service import UMSServiceResolver
from app.ai.gemini_provider import circuit_breaker
from app.ai.llm_registry import LLMRegistry
from app.services.attendance_solver_service import AttendanceSolverService
from app.services.project_benefit_service import ProjectBenefitService
from app.services.authority_service import UniversityAuthorityService
from app.services.web_research_service import WebResearchService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/portal", tags=["student-portal"])


# --- Schemas ---

class StudentProfileOut(BaseModel):
    id: str
    full_name: str
    registration_number: Optional[str]
    school: str
    department: str
    programme: str
    specialisation: str
    current_semester: int
    academic_session: str
    is_connected: bool


class DashboardNotice(BaseModel):
    id: str
    title: str
    category: str
    date: str
    snippet: str
    source_url: str


class DeadlineItem(BaseModel):
    title: str
    category: str
    deadline_date: str
    action_url: str
    is_critical: bool


class DashboardSummaryOut(BaseModel):
    profile: StudentProfileOut
    welcome_message: str
    academic_session: str
    important_deadlines: List[DeadlineItem]
    verified_notices: List[DashboardNotice]
    recommended_services: List[Dict[str, str]]
    active_conversations_count: int


class OpportunityOut(BaseModel):
    id: str
    title: str
    opportunity_type: str
    organizer: str
    description: str
    eligibility: str
    deadline: Optional[str]
    stipend_or_reward: Optional[str]
    target_programmes: List[str]
    application_link: str
    is_verified: bool


class EventOut(BaseModel):
    id: str
    title: str
    category: str
    venue: str
    event_date: str
    description: str
    organizing_department: str
    registration_link: Optional[str]
    is_verified: bool


class SavedLocationIn(BaseModel):
    place_id: str
    name: str
    building_block: str
    room_number: Optional[str] = None
    notes: Optional[str] = None


class SavedLocationOut(BaseModel):
    id: str
    place_id: str
    name: str
    building_block: str
    room_number: Optional[str]
    notes: Optional[str]


class AssessProjectIn(BaseModel):
    description: str
    project_type: Optional[str] = None
    has_github: bool = False
    has_live_demo: bool = False
    has_architecture_doc: bool = False


# --- Endpoints ---

@router.get("/dashboard", response_model=DashboardSummaryOut)
async def get_student_dashboard(
    x_session_token: Optional[str] = Header(None, alias="X-Session-Token"),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns personalized student dashboard summary.
    Strict privacy boundary: Personal academic records (CGPA, marks, attendance)
    are NOT fabricated and appear only behind authorized UMS integration.
    """
    conv_count = 0
    if x_session_token:
        sess_stmt = select(AnonymousSession).where(
            AnonymousSession.session_token == x_session_token,
            AnonymousSession.is_active == True
        )
        sess = (await db.execute(sess_stmt)).scalars().first()
        if sess:
            cnt_stmt = select(func.count(Conversation.id)).where(
                Conversation.session_id == sess.id,
                Conversation.is_active == True
            )
            conv_count = (await db.execute(cnt_stmt)).scalar() or 0

    profile = StudentProfileOut(
        id="mock-profile-001",
        full_name="LPU Student",
        registration_number="1220XXXX (Masked / Public View)",
        school="School of Computer Science & Engineering",
        department="Department of Computer Science & Engineering",
        programme="B.Tech Computer Science & Engineering",
        specialisation="Artificial Intelligence & Machine Learning",
        current_semester=6,
        academic_session="2025-2026",
        is_connected=False  # Unconnected to private backend by default
    )

    deadlines = [
        DeadlineItem(
            title="End-Term Theory & Lab Examination Datesheet Declaration",
            category="Examination",
            deadline_date="Dec 01, 2026",
            action_url="https://ums.lpu.in/lpuums/ (Examination > Datesheet)",
            is_critical=True
        ),
        DeadlineItem(
            title="EDU-Revolution Course Substitution Proposal Submission Window",
            category="Academic Benefits",
            deadline_date="First 4 weeks of active semester",
            action_url="https://ums.lpu.in/lpuums/ (LMS > Edu-Revolution)",
            is_critical=True
        ),
        DeadlineItem(
            title="Spring Semester Tuition Fee Payment (Without Late Fine)",
            category="Accounts & Fees",
            deadline_date="Jan 15, 2027",
            action_url="https://ums.lpu.in/lpuums/ (Fee Management)",
            is_critical=False
        ),
    ]

    notices = [
        DashboardNotice(
            id="NTC-01",
            title="Notice: 100% Pure Vegetarian Campus Policy Reminder",
            category="Campus Regulation",
            date="Nov 2026",
            snippet="All campus dining courts, kiosks, and food delivery couriers are mandated to maintain strictly 100% pure vegetarian items within university gates.",
            source_url="https://www.lpu.in/about_lpu/campus-facilities.php"
        ),
        DashboardNotice(
            id="NTC-02",
            title="Notice: Attendance Biometric Verification Before Dispute Escalation",
            category="Academics",
            date="Nov 2026",
            snippet="Students reporting attendance discrepancies must inspect punch records against scheduled lectures with course instructors before escalating to HOD.",
            source_url="https://ums.lpu.in/lpuums/"
        ),
        DashboardNotice(
            id="NTC-03",
            title="Notice: Smart India Hackathon (SIH 2026) University Nominations Open",
            category="Competitions",
            date="Nov 2026",
            snippet="Registered 6-member teams can submit abstract proposals on the UMS Events portal. Top 35 teams receive institutional mentors and Duty Leave.",
            source_url="https://ums.lpu.in/lpuums/"
        )
    ]

    services = [
        {"name": "Examination Datesheet", "breadcrumb": "UMS > Examination > Datesheet", "url": "https://ums.lpu.in/lpuums/"},
        {"name": "Fee Statements & Challan", "breadcrumb": "UMS > Fee Management > Fee Statements", "url": "https://ums.lpu.in/lpuums/"},
        {"name": "Hostel Leave & Maintenance", "breadcrumb": "UMS > Hostel Management > Apply Leave", "url": "https://ums.lpu.in/lpuums/"},
        {"name": "OPD Doctor Consultation", "breadcrumb": "UMS > Health Services > Doctor Appointment", "url": "https://ums.lpu.in/lpuums/"},
        {"name": "RMS Grievance Desk", "breadcrumb": "UMS > Relationship Management System > Log Request", "url": "https://ums.lpu.in/lpuums/"},
        {"name": "EDU-Revolution Portal", "breadcrumb": "UMS > LMS > Edu-Revolution: Be the Change", "url": "https://ums.lpu.in/lpuums/"},
    ]

    return DashboardSummaryOut(
        profile=profile,
        welcome_message="Welcome to CampusConnect — your verified AI digital companion for Lovely Professional University.",
        academic_session="2025-2026",
        important_deadlines=deadlines,
        verified_notices=notices,
        recommended_services=services,
        active_conversations_count=conv_count
    )


@router.get("/people")
async def get_people_directory(
    expertise: Optional[str] = Query(None, description="Expertise category (e.g. AI, Cyber, Web, Robotics)"),
    search: Optional[str] = Query(None, description="Search by faculty name or designation"),
    school: Optional[str] = Query(None, description="School filter")
):
    """
    Searchable public university people and expert directory.
    Grounded in public directories; enforces office seating verification disclaimers.
    """
    all_people = PeopleDirectoryService.get_all_people()

    results = []
    for p in all_people:
        # Filter by expertise if requested
        if expertise:
            exp_term = expertise.lower()
            text_corpus = f"{p.get('designation', '')} {p.get('notes', '')} {p.get('school_division', '')}".lower()
            if exp_term not in text_corpus:
                continue

        # Filter by search term
        if search:
            s_term = search.lower()
            text_corpus = f"{p.get('full_name', '')} {p.get('designation', '')} {p.get('notes', '')}".lower()
            if s_term not in text_corpus:
                continue

        # Filter by school
        if school:
            if school.lower() not in p.get("school_division", "").lower():
                continue

        results.append({
            "person_id": p.get("person_id"),
            "full_name": p.get("full_name"),
            "designation": p.get("designation"),
            "school_division": p.get("school_division"),
            "building_block": p.get("building_block"),
            "room_cabin": p.get("room_cabin"),
            "office_seating_verified": p.get("office_seating_verified", False),
            "email": p.get("email"),
            "profile_source": p.get("profile_source"),
            "notes": p.get("notes"),
            "revalidation_advisory": p.get("revalidation_advisory"),
            "appointment_route": "Visit Ground Floor School Office / Reception in Block 32 for current semester cabin consultation.",
            "evidence_status": p.get("evidence_status", "OFFICIAL_CURRENT_VERIFIED")
        })

    return {"total": len(results), "people": results}


@router.get("/opportunities", response_model=List[OpportunityOut])
async def list_opportunities(
    type: Optional[str] = Query(None, description="Filter by type: placement, internship, hackathon, competition, research, club"),
    db: AsyncSession = Depends(get_db)
):
    """Lists verified campus opportunities."""
    stmt = select(StudentOpportunity).where(StudentOpportunity.is_verified == True)
    if type:
        stmt = stmt.where(StudentOpportunity.opportunity_type == type.lower())
    stmt = stmt.order_by(StudentOpportunity.created_at.desc())

    res = await db.execute(stmt)
    opps = res.scalars().all()
    return [
        OpportunityOut(
            id=str(o.id),
            title=o.title,
            opportunity_type=o.opportunity_type,
            organizer=o.organizer,
            description=o.description,
            eligibility=o.eligibility,
            deadline=o.deadline,
            stipend_or_reward=o.stipend_or_reward,
            target_programmes=o.target_programmes or [],
            application_link=o.application_link,
            is_verified=o.is_verified
        )
        for o in opps
    ]


@router.get("/events", response_model=List[EventOut])
async def list_events(
    category: Optional[str] = Query(None, description="academic, cultural, technical, sports"),
    db: AsyncSession = Depends(get_db)
):
    """Lists verified campus events and examination dates."""
    stmt = select(CampusEvent).where(CampusEvent.is_verified == True)
    if category:
        stmt = stmt.where(CampusEvent.category == category.lower())
    stmt = stmt.order_by(CampusEvent.created_at.desc())

    res = await db.execute(stmt)
    events = res.scalars().all()
    return [
        EventOut(
            id=str(e.id),
            title=e.title,
            category=e.category,
            venue=e.venue,
            event_date=e.event_date,
            description=e.description,
            organizing_department=e.organizing_department,
            registration_link=e.registration_link,
            is_verified=e.is_verified
        )
        for e in events
    ]


@router.get("/academic-benefits")
async def get_academic_benefits_framework():
    """
    Returns the complete 9 EDU-Revolution benefit categories from institutional regulations.
    """
    categories = AcademicBenefitAdvisor._load_categories()
    return {
        "framework": "Lovely Professional University EDU-Revolution Policy",
        "governing_body": "Division of Academic Affairs",
        "guidance_desk": "Block 27 Room 102 (Query & Assistance Zone)",
        "categories_count": len(categories),
        "categories": categories
    }


@router.post("/assess-benefit")
async def assess_academic_benefit_interactive(req: AssessProjectIn):
    """
    Interactive project assessment endpoint:
    Maps student's project or achievement to EDU-Revolution categories,
    computes missing evidence, and returns official submission guidelines.
    """
    card = AcademicBenefitAdvisor.assess_project(req.description)
    if not card:
        # Default fallback to Category 2
        card = AcademicBenefitAdvisor.assess_project("built an ai project")

    # Dynamic check based on user input flags
    missing = list(card.missing_evidence)
    if req.has_github and "Public GitHub repository link with full commit history" in missing:
        missing.remove("Public GitHub repository link with full commit history")
    if req.has_live_demo and "Live working demo / deployment link for expert committee evaluation" in missing:
        missing.remove("Live working demo / deployment link for expert committee evaluation")
    if req.has_architecture_doc and "Comprehensive technical architecture specification (PDF)" in missing:
        missing.remove("Comprehensive technical architecture specification (PDF)")

    return {
        "assessment_card": card,
        "updated_missing_evidence": missing,
        "readiness_score": 100 - (len(missing) * 25),
        "next_steps": [
            "1. Coordinate with your Course Instructor / Class Mentor within the first 4 weeks of the semester.",
            "2. Fill the Mentor Course Mapping Endorsement Form at Block 27 Room 102.",
            "3. Submit formal proposal via UMS > LMS > Edu Revolution: Be the Change.",
            "4. Appear for technical demonstration and viva before the School Evaluation Committee."
        ]
    }


@router.get("/saved-places", response_model=List[SavedLocationOut])
async def list_saved_places(
    x_session_token: str = Header(..., alias="X-Session-Token"),
    db: AsyncSession = Depends(get_db)
):
    """Lists student's bookmarked campus locations."""
    sess_stmt = select(AnonymousSession).where(
        AnonymousSession.session_token == x_session_token,
        AnonymousSession.is_active == True
    )
    sess = (await db.execute(sess_stmt)).scalars().first()
    if not sess:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session.")

    stmt = select(SavedLocation).where(SavedLocation.session_id == sess.id)
    res = await db.execute(stmt)
    locs = res.scalars().all()
    return [
        SavedLocationOut(
            id=str(l.id),
            place_id=l.place_id,
            name=l.name,
            building_block=l.building_block,
            room_number=l.room_number,
            notes=l.notes
        )
        for l in locs
    ]


@router.post("/saved-places", response_model=SavedLocationOut)
async def add_saved_place(
    loc: SavedLocationIn,
    x_session_token: str = Header(..., alias="X-Session-Token"),
    db: AsyncSession = Depends(get_db)
):
    """Saves a campus location for quick access."""
    sess_stmt = select(AnonymousSession).where(
        AnonymousSession.session_token == x_session_token,
        AnonymousSession.is_active == True
    )
    sess = (await db.execute(sess_stmt)).scalars().first()
    if not sess:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session.")

    saved = SavedLocation(
        session_id=sess.id,
        place_id=loc.place_id,
        name=loc.name,
        building_block=loc.building_block,
        room_number=loc.room_number,
        notes=loc.notes
    )
    db.add(saved)
    await db.commit()
    await db.refresh(saved)

    return SavedLocationOut(
        id=str(saved.id),
        place_id=saved.place_id,
        name=saved.name,
        building_block=saved.building_block,
        room_number=saved.room_number,
        notes=saved.notes
    )


@router.delete("/saved-places/{id}")
async def delete_saved_place(
    id: str,
    x_session_token: str = Header(..., alias="X-Session-Token"),
    db: AsyncSession = Depends(get_db)
):
    """Removes a saved place."""
    sess_stmt = select(AnonymousSession).where(
        AnonymousSession.session_token == x_session_token,
        AnonymousSession.is_active == True
    )
    sess = (await db.execute(sess_stmt)).scalars().first()
    if not sess:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session.")

    stmt = select(SavedLocation).where(
        SavedLocation.id == id,
        SavedLocation.session_id == sess.id
    )
    loc = (await db.execute(stmt)).scalars().first()
    if not loc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Saved place not found.")

    await db.delete(loc)
    await db.commit()
    return {"status": "success", "message": "Saved place removed."}


@router.get("/llm-usage")
async def get_llm_usage_analytics(db: AsyncSession = Depends(get_db)):
    """
    Returns LLM usage analytics, token consumption, and circuit breaker status.
    """
    total_calls = (await db.execute(select(func.count(LLMUsageLog.id)))).scalar() or 0
    total_tokens = (await db.execute(select(func.sum(LLMUsageLog.total_tokens)))).scalar() or 0
    avg_latency = (await db.execute(select(func.avg(LLMUsageLog.latency_ms)))).scalar() or 0

    recent_logs_stmt = (
        select(LLMUsageLog)
        .order_by(desc(LLMUsageLog.created_at))
        .limit(10)
    )
    recent_logs = (await db.execute(recent_logs_stmt)).scalars().all()

    return {
        "status": "healthy" if not circuit_breaker.is_open() else "circuit_open",
        "circuit_breaker_open": circuit_breaker.is_open(),
        "total_llm_requests": total_calls,
        "total_tokens_consumed": int(total_tokens),
        "average_latency_ms": round(float(avg_latency), 2),
        "provider": "Google Gemini Developer API (Free Tier)",
        "configured_model": "gemini-2.5-flash",
        "recent_logs": [
            {
                "id": str(log.id),
                "model": log.model_name,
                "tokens": log.total_tokens,
                "latency_ms": log.latency_ms,
                "status": log.status,
                "created_at": log.created_at.isoformat() if log.created_at else None
            }
            for log in recent_logs
        ]
    }


class AttendanceAssessIn(BaseModel):
    query: str
    attendance_percentage: Optional[float] = None


@router.post("/assess-attendance")
async def assess_attendance_query(payload: AttendanceAssessIn):
    """
    Evaluates student attendance situations, distinguishes revenue generation vs 10% condonation,
    identifies missing student details, and outlines verified escalation routes.
    """
    context = {}
    if payload.attendance_percentage is not None:
        context["attendance_percentage"] = payload.attendance_percentage
    return AttendanceSolverService.solve(payload.query, context)


class ProjectBenefitAssessIn(BaseModel):
    query: str
    details: Optional[Dict[str, Any]] = None


@router.post("/assess-project-benefits")
async def assess_comprehensive_project_benefits(payload: ProjectBenefitAssessIn):
    """
    Evaluates student projects across all 7 institutional benefit tracks:
    EDU-Rev, Revenue (SCRGM), CA Equivalence, Course Substitution, Grade Upgradation, Attendance DL, RPL.
    """
    return ProjectBenefitService.evaluate_project(payload.query, payload.details)


@router.get("/authority-guidance")
async def get_university_authority_guidance(query: str = Query(..., min_length=2)):
    """
    Resolves university authority, meeting protocol, and procedural escalation ladder
    (Pro Chancellor, Vice Chancellor, HOD, Dean, Proctorial Board, Academic Appeals).
    """
    return UniversityAuthorityService.resolve_authority(query)


@router.get("/web-research")
async def get_live_web_research(query: str = Query(..., min_length=2)):
    """
    Executes controlled web research prioritizing official university and government regulatory domains.
    """
    return await WebResearchService.research_topic(query)


@router.get("/llm-providers")
async def list_registered_llm_providers():
    """
    Lists all registered Multi-Provider LLMs, availability, and active capabilities.
    """
    return {
        "default_provider": settings.DEFAULT_LLM_PROVIDER,
        "providers": LLMRegistry.list_providers()
    }
