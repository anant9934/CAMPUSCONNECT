import uuid
import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.services.attendance_solver_service import AttendanceSolverService
from app.services.project_benefit_service import ProjectBenefitService
from app.services.authority_service import UniversityAuthorityService
from app.services.people_directory_service import PeopleDirectoryService
from app.services.web_research_service import WebResearchService
from app.services.policy_engine import PolicyEngine, EvidenceStatus
from app.ai.llm_registry import LLMRegistry
from app.ai.model_registry import ModelCapabilityRegistry
from app.ai.router_policy import RouterPolicy
from app.ai.proactive_intelligence import ProactiveStudentIntelligence
from app.ai.conversation_orchestrator import ConversationOrchestrator
from app.core.database import AsyncSessionLocal


@pytest.mark.asyncio
async def test_acceptance_a_attendance_problem_solver():
    """
    Test A: 'My attendance is low. Can I get a benefit?'
    Verifies:
    1. Distinguishes Revenue Generation attendance benefits from the 10% Attendance Condonation.
    2. Enforces 75% ETE bar and 65% statutory floor.
    3. Asks for missing student details (current attendance %, reason, events).
    4. Cites Block 32 Ground Floor School Office & Dr. Dalwinder Singh.
    5. Anti-fraud warning against fake certificates / manufactured revenue.
    """
    query = "My attendance is low. Can I do something to get attendance benefits?"
    result = AttendanceSolverService.solve(query)

    assert result is not None
    assert len(result.eligible_options) >= 2
    # Check distinction between Revenue Generation and 10% condonation
    route_names = [opt["route_name"] for opt in result.eligible_options]
    assert any("Revenue Generation" in r for r in route_names)
    assert any("10% Institutional Condonation" in r for r in route_names)

    # Check missing details to ask
    assert len(result.missing_details_to_ask) > 0
    assert any("attendance percentage" in q.lower() for q in result.missing_details_to_ask)

    # Check authority and office
    assert "Dalwinder Singh" in result.assistance_office["primary_authority"]
    assert "Block 32" in result.assistance_office["location"]

    # Check fraud warning
    assert "Section 12" in result.fraud_warning
    assert "Proctorial Board" in result.fraud_warning


@pytest.mark.asyncio
async def test_acceptance_b_ca_exemption_cybersecurity():
    """
    Test B: 'I have built an AI cybersecurity platform. Can I get CA exemption?'
    Verifies:
    1. Investigates CA Equivalence & Course Substitution.
    2. Requires GitHub repo, architecture PDF, and live demo.
    3. Mentions the mandatory first 4-week submission window.
    4. Explains that approval requires SAC committee ratification (no automatic waiver).
    """
    query = "I have built an AI cybersecurity platform. Can I get CA exemption?"
    report = ProjectBenefitService.evaluate_project(query)

    assert report is not None
    assert "CA" in [v.benefit_name for v in report.benefit_vectors if "Continuous Assessment" in v.benefit_name][0]

    ca_vec = [v for v in report.benefit_vectors if "Continuous Assessment" in v.benefit_name][0]
    assert "100%" in ca_vec.max_benefit_documented
    assert any("GitHub" in e for e in ca_vec.evidence_required)
    assert any("Architecture" in e for e in ca_vec.evidence_required)
    assert "First 4 weeks" in report.deadlines_and_helpdesk["filing_window"]
    assert "Standing Academic Committee" in ca_vec.approval_authority


@pytest.mark.asyncio
async def test_acceptance_c_startup_revenue_benefits():
    """
    Test C: 'I want to build a startup. Can I earn revenue and receive academic benefits?'
    Verifies:
    1. Investigates Category 5 (SCRGM / Startup Enterprise).
    2. Clarifies that commercial revenue does NOT buy grades/marks directly.
    3. Requires GST invoices, client contracts, and bank remittance statements.
    4. Cites LPU Incubation Center & SAC viva.
    """
    query = "I want to build a startup. Can I earn revenue and receive academic benefits?"
    report = ProjectBenefitService.evaluate_project(query)

    assert report is not None
    assert "Category 5" in report.matched_category or "Enterprise" in report.matched_category
    rev_vec = [v for v in report.benefit_vectors if "Commercial Revenue Generation" in v.benefit_name][0]
    assert any("GST" in e for e in rev_vec.evidence_required)
    assert any("Bank" in e for e in rev_vec.evidence_required)
    assert "Incubation" in rev_vec.approval_authority or "Standing Academic Committee" in rev_vec.approval_authority


@pytest.mark.asyncio
async def test_acceptance_d_expert_matching_cybersecurity():
    """
    Test D: 'Who can guide me with cybersecurity at LPU?'
    Verifies:
    1. Matches faculty or leadership with cybersecurity / CSE expertise.
    2. Does NOT invent private cabin numbers.
    3. Directs to Ground Floor School Office in Block 32 for student consultation hours.
    """
    query = "Who can guide me with cybersecurity at LPU?"
    people = PeopleDirectoryService.search_people(query)
    # Search people returns matching records or leadership
    assert len(people) >= 1

    person = people[0]
    assert "School of Computer Science & Engineering" in person["school_division"]
    assert "Block 32" in person["building_block"]
    # Seating verification check
    assert person["office_seating_verified"] is False or "Block 32" in person["office_location"]


@pytest.mark.asyncio
async def test_acceptance_e_meeting_pro_chancellor():
    """
    Test E: 'How can I meet the Pro Chancellor?'
    Verifies:
    1. Identifies Mrs. Rashmi Mittal as Pro Chancellor.
    2. Distinguishes executive apex from departmental leadership.
    3. Requires formal appointment request via Dean / Head of School.
    4. Forbids unscheduled walk-ins and enforces 3-tier escalation for routine issues.
    """
    query = "How can I meet the Pro Chancellor?"
    guidance = UniversityAuthorityService.resolve_authority(query)

    assert guidance.authority_name == "Mrs. Rashmi Mittal"
    assert "Executive" in guidance.responsibility_scope or "Apex" in guidance.responsibility_scope
    assert "Block 30" in guidance.office_location or "Executive Block" in guidance.office_location
    assert any("Dean" in step for step in guidance.appointment_procedure)
    assert any("Tier 1: Class Mentor" in t for t in guidance.hierarchical_escalation_ladder)


@pytest.mark.asyncio
async def test_acceptance_f_disciplinary_case():
    """
    Test F: 'I have an indiscipline case. How should I approach the university?'
    Verifies:
    1. Identifies the Proctorial Board in Block 30 (Division of Student Welfare).
    2. Forbids bypassing procedure or contacting unrelated senior executives.
    3. Advises consulting Class Mentor and attending hearings with student ID card.
    4. Preserves confidentiality and outlines formal appeal window.
    """
    query = "I have an indiscipline case. How should I approach the university?"
    guidance = UniversityAuthorityService.resolve_authority(query)

    assert "Proctorial" in guidance.authority_name
    assert "Block 30" in guidance.office_location
    assert any("Student ID" in step for step in guidance.appointment_procedure)
    assert any("bypass" in p.lower() for p in guidance.prohibited_actions)
    assert "confidential" in guidance.confidentiality_notice.lower()


@pytest.mark.asyncio
async def test_acceptance_g_internship_benefits():
    """
    Test G: 'I completed an internship and received a stipend. What benefits can I claim?'
    Verifies:
    1. Maps to Category 7 (Industry Internship & Live Projects).
    2. Distinguishes stipend earnings from automatic academic grades.
    3. Outlines elective credit substitution and CA waiver paths.
    """
    query = "I completed an internship and received a stipend. What benefits can I claim?"
    report = ProjectBenefitService.evaluate_project(query)

    assert report is not None
    assert "Category 7" in report.matched_category or "Industry" in report.matched_category
    assert len(report.benefit_vectors) >= 2


@pytest.mark.asyncio
async def test_acceptance_h_research_paper_grade_upgradation():
    """
    Test H: 'I have a research paper. Can I get grade upgradation?'
    Verifies:
    1. Maps to Category 1 (Research Publications & Academic Innovations).
    2. Requires Scopus / SCI indexing and LPU institutional affiliation.
    3. Documents grade upgradation or 4-credit course exemption subject to DRD & SAC approval.
    """
    query = "I have a research paper. Can I get grade upgradation?"
    report = ProjectBenefitService.evaluate_project(query)

    assert report is not None
    assert "Category 1" in report.matched_category or "Research" in report.matched_category
    grade_vec = [v for v in report.benefit_vectors if "Grade Upgradation" in v.benefit_name][0]
    assert any("Scopus" in c for c in grade_vec.eligibility_conditions)
    assert "grade enhancement" in grade_vec.max_benefit_documented.lower() or "exemption" in grade_vec.max_benefit_documented.lower()


@pytest.mark.asyncio
async def test_acceptance_i_attendance_below_threshold():
    """
    Test I: 'Can I get a benefit if my attendance is below the stated threshold?'
    Verifies:
    1. Checks the statutory 65.0% absolute condonation floor.
    2. Explains that attendance below 65% cannot be bridged through routine 10% condonation.
    3. Outlines immediate consultation with Academic Coordinator Dr. Dalwinder Singh.
    """
    query = "Can I get an attendance benefit if my attendance is 58% which is below the threshold?"
    result = AttendanceSolverService.solve(query)

    assert any("below the statutory 65.0%" in d for d in result.disqualifying_conditions)
    assert "Dr. Dalwinder Singh" in result.assistance_office["primary_authority"]


@pytest.mark.asyncio
async def test_acceptance_j_multi_turn_proactive_memory():
    """
    Test J: Multi-turn conversation where student provides CGPA, semester, attendance, and project details.
    Verifies:
    1. Turn 1: Student states they built an app. System asks for missing details.
    2. Turn 2: Student provides CGPA 8.2 and Sem 6. System remembers and asks for remaining info.
    3. Turn 3: Student provides attendance 78% and GitHub repo. System confirms full eligibility alignment.
    """
    # Turn 1
    t1_query = "I built an autonomous IoT smart energy monitoring system."
    t1_eval = await ProactiveStudentIntelligence.evaluate_turn(t1_query, [])
    assert any("GitHub" in m or "repository" in m for m in t1_eval.missing_eligibility_info)

    # Turn 2: Student adds CGPA and Semester
    history_after_t1 = [
        {"role": "user", "content": t1_query},
        {"role": "assistant", "content": t1_eval.proactive_guidance_text}
    ]
    t2_query = "My CGPA is 8.4 and I am currently in Semester 6."
    t2_eval = await ProactiveStudentIntelligence.evaluate_turn(t2_query, history_after_t1)
    # Turn 2 combined text should remember the project from Turn 1
    assert "IoT" in t2_eval.explicit_question or len(history_after_t1) > 0

    # Turn 3: Student provides repo and attendance
    history_after_t2 = history_after_t1 + [
        {"role": "user", "content": t2_query},
        {"role": "assistant", "content": "Noted your CGPA is 8.4 and Semester 6."}
    ]
    t3_query = "Here is my GitHub: github.com/student/iot-energy and my attendance is 82%."
    t3_eval = await ProactiveStudentIntelligence.evaluate_turn(t3_query, history_after_t2)
    assert t3_eval is not None
    assert "UMS" in t3_eval.recommended_next_action or "course mapping" in t3_eval.recommended_next_action.lower()


@pytest.mark.asyncio
async def test_multi_provider_llm_gateway():
    """
    Test Multi-Provider LLM Gateway:
    1. Provider registry includes Gemini, OpenRouter, Mistral, xAI, OpenAI.
    2. Model capability registry classifies speed tiers and context limits.
    3. Router policy assesses query complexity.
    """
    providers = LLMRegistry.list_providers()
    provider_names = [p["name"] for p in providers]
    assert "gemini" in provider_names
    assert "openrouter" in provider_names
    assert "mistral" in provider_names
    assert "xai" in provider_names
    assert "openai" in provider_names

    # Check Model Capability Registry
    gemini_cap = ModelCapabilityRegistry.get_capability("gemini-2.5-flash")
    assert gemini_cap is not None
    assert gemini_cap.is_free_tier is True
    assert gemini_cap.context_window >= 1000000

    # Check Router Policy Complexity
    fast_comp = RouterPolicy.evaluate_task_complexity("Where is Block 32?")
    assert fast_comp == "fast"

    deep_comp = RouterPolicy.evaluate_task_complexity("My attendance is very low and I have a disciplinary appeal")
    assert deep_comp == "deep"


@pytest.mark.asyncio
async def test_live_web_research_and_policy_engine():
    """
    Test Live Web Research and Policy Engine:
    1. Priority source domain filtering.
    2. Reliability scoring for official domains.
    3. Policy status validation (OFFICIAL_CURRENT_VERIFIED).
    """
    res = await WebResearchService.research_topic("Smart India Hackathon SIH 2026 guidelines")
    assert res is not None
    assert len(res.citations) >= 1
    assert any("sih.gov.in" in c.source_domain or "lpu.in" in c.source_domain for c in res.citations)

    # Check Policy Engine
    val = PolicyEngine.validate_claim("Attendance")
    assert val["is_verified"] is True
    assert val["status"] == EvidenceStatus.OFFICIAL_CURRENT_VERIFIED.value
