"""
CampusConnect V6 End-to-End Intelligence & Retrieval Accuracy Test Suite.
Verifies:
1. Okapi BM25 ranking, phrase matching, and exact entity resolution.
2. Multi-Domain Orchestration across compound queries.
3. Faculty & People role separation, disclaimed personal cabin seating, and verification timestamps.
4. Academic Benefits missing evidence checklist, viva prerequisite, and strict SAC / SCRGM disclaimers.
5. Campus Food Discovery straight-line distance semantics and verified evidence statuses.
"""
import pytest
from app.core.database import AsyncSessionLocal
from app.services.rag.bm25_search import BM25SearchEngine, bm25_tokenize
from app.services.rag.entity_matcher import EntityMatcher
from app.services.rag.hybrid_search import hybrid_search_engine
from app.services.orchestration.multi_domain_orchestrator import MultiDomainOrchestrator
from app.services.people_directory_service import PeopleDirectoryService
from app.services.edurev_advisor_service import AcademicBenefitAdvisor
from app.services.campus_food_service import CampusFoodService


@pytest.mark.asyncio
async def test_bm25_ranking_and_exact_entity_resolution():
    """Verifies BM25 index and EntityMatcher precision."""
    async with AsyncSessionLocal() as db:
        await hybrid_search_engine.build_index(db)

        # 1. Test EntityMatcher patterns
        sobti_match = EntityMatcher.match_entity("Who is Dr. Rajeev Sobti?")
        assert sobti_match is not None
        assert sobti_match["record_id"] == "CSE-001"

        mohit_match = EntityMatcher.match_entity("Where is the AI & ML HOD office?")
        assert mohit_match is not None
        assert mohit_match["record_id"] == "LPU-FAC-004"

        aarti_match = EntityMatcher.match_entity("Who is Dr. Aarti faculty member in CSE?")
        assert aarti_match is not None
        assert aarti_match["record_id"] == "LPU-FAC-008"

        # 2. Test BM25 exact phrase boost and ranking
        res = await hybrid_search_engine.search("Who is Dr. Aarti faculty member in CSE?", db, top_k=3)
        assert len(res["candidates"]) > 0
        assert res["candidates"][0]["record_id"] == "LPU-FAC-008"

        # 3. Test wayfinding location resolution
        b34_res = await hybrid_search_engine.search("Where is Block 34 Division of Examination and Registrar Office located?", db, top_k=1)
        assert len(b34_res["candidates"]) > 0
        assert b34_res["candidates"][0]["record_id"] == "LOC-001"


@pytest.mark.asyncio
async def test_multi_domain_query_1_faculty_and_project():
    """
    Query 1: 'Where is the AI & ML HOD's office and whom should I meet about my project?'
    Must return compound response with person_card and who_to_meet_card.
    """
    async with AsyncSessionLocal() as db:
        query = "Where is the AI & ML HOD's office and whom should I meet about my project?"
        res = await MultiDomainOrchestrator.orchestrate(query, db)

        assert res["is_multi_domain"] is True
        assert res["person_card"] is not None
        assert res["who_to_meet_card"] is not None
        assert "Academic Leadership & Office Location" in res["content"]
        assert "Whom to Meet About Your Academic Project" in res["content"]
        assert "Block 27 Room 102" in res["content"]


@pytest.mark.asyncio
async def test_multi_domain_query_2_edurev_benefits_and_where():
    """
    Query 2: 'I built an AI application. Can I apply for EDU-Revolution benefits, where and how?'
    Must return academic_benefit_card, who_to_meet_card, and submission instructions.
    """
    async with AsyncSessionLocal() as db:
        query = "I built an AI application. Can I apply for EDU-Revolution benefits, where and how?"
        res = await MultiDomainOrchestrator.orchestrate(query, db)

        assert res["is_multi_domain"] is True
        assert res["academic_benefit_card"] is not None
        assert res["who_to_meet_card"] is not None
        assert "Block 27 Room 102" in res["content"]
        assert "first 4 weeks" in res["content"].lower()


@pytest.mark.asyncio
async def test_multi_domain_query_3_food_and_block_32():
    """
    Query 3: 'Find verified food options near Block 32.'
    Must return food_card and place_card for Block 32 / UniMall.
    """
    async with AsyncSessionLocal() as db:
        query = "Find verified food options near Block 32."
        res = await MultiDomainOrchestrator.orchestrate(query, db)

        assert res["is_multi_domain"] is True
        assert res["food_card"] is not None
        assert res["place_card"] is not None
        assert "Verified Food Outlets Near Block 32" in res["content"]
        assert "Block 32" in res["content"]


@pytest.mark.asyncio
async def test_multi_domain_query_4_attendance_procedure_and_first_contact():
    """
    Query 4: 'My attendance is incorrect. Explain the procedure and identify the first contact.'
    Must return who_to_meet_card and statutory 3-tier attendance procedure.
    """
    async with AsyncSessionLocal() as db:
        query = "My attendance is incorrect. Explain the procedure and identify the first contact."
        res = await MultiDomainOrchestrator.orchestrate(query, db)

        assert res["is_multi_domain"] is True
        assert res["who_to_meet_card"] is not None
        assert "Class Mentor" in res["content"]
        assert "Course Instructor" in res["content"]
        assert "Academic Coordinator" in res["content"]
        assert "Head of School" in res["content"]


@pytest.mark.asyncio
async def test_multi_domain_query_5_hostel_and_fee_pathways():
    """
    Query 5: 'I have a hostel maintenance issue and fee query. Which UMS services should I use?'
    Must return dual-pathway UMS guidance for hostel and fee administration.
    """
    async with AsyncSessionLocal() as db:
        query = "I have a hostel maintenance issue and fee query. Which UMS services should I use?"
        res = await MultiDomainOrchestrator.orchestrate(query, db)

        assert res["is_multi_domain"] is True
        assert res["nav_card"] is not None
        assert "Hostel Management Pathway" in res["content"]
        assert "Fee Management & Accounts Pathway" in res["content"]
        assert "Block 34" in res["content"]


def test_faculty_role_separation_and_seating_disclaimers():
    """Verifies that faculty cards disclaim personal cabin seating and correctly assign roles."""
    card = PeopleDirectoryService.search_person("Who is the AI & ML HOD?")

    assert card is not None
    assert card.full_name == "Dr. Mohit Arora"
    assert card.school_hod == "Dr. Mohit Arora"
    assert card.department_hod is None  # Must be None: no independent department HOD for AI/ML
    assert card.executive_dean == "Dr. Rajeev Sobti"
    assert card.academic_coordinator == "Dr. Dalwinder Singh"
    assert card.office_seating_verified is False  # Must NOT claim verified personal seating
    assert card.verification_timestamp == "2026-11-18T00:00:00Z"
    assert card.evidence_status == "OFFICIAL_CURRENT_VERIFIED"


def test_academic_benefit_advisor_evidence_and_disclaimers():
    """Verifies missing evidence calculation, timeline, viva prerequisite, and SCRGM distinction."""
    card = AcademicBenefitAdvisor.assess_project("I built an AI project with deep learning.")

    assert card is not None
    assert "Innovative Projects" in card.category_name
    assert len(card.missing_evidence) >= 3
    assert "GitHub" in str(card.missing_evidence)
    assert "First 4 weeks of active academic semester" in card.course_mapping_window
    assert "School Evaluation Committee viva" in card.approval_prerequisite
    assert "Standing Academic Committee" in card.guarantee_disclaimer
    assert "SCRGM" in card.scrgm_distinction
    assert "POTENTIAL ELIGIBILITY ONLY" in card.eligibility_vs_approval_notice


def test_campus_food_discovery_semantics():
    """Verifies distance semantics, hours, and verified evidence types."""
    card = CampusFoodService.search_food("Best soya chaap near me?")

    assert card is not None
    assert card.display_name == "Punjabi Tadka Veg Hub"
    assert card.distance_type == "straight_line_estimate"
    assert card.walking_minutes is None or isinstance(card.walking_minutes, int)
    assert card.opening_hours != ""
    assert card.evidence_status == "USER_REPORTED"
    assert card.price_sample == "Rs. 130"
