import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.services.campus_food_service import CampusFoodService
from app.services.people_directory_service import PeopleDirectoryService
from app.services.issue_resolver_service import IssueToOfficeResolver
from app.services.edurev_advisor_service import AcademicBenefitAdvisor
from app.services.campus_map_service import CampusMapService
from app.core.database import AsyncSessionLocal


@pytest.mark.asyncio
async def test_acceptance_1_soya_chaap_discovery():
    """
    Acceptance Criterion 1: 'Best soya chaap near me?'
    Must match verified Punjabi Tadka (Block 27) with verified items,
    approximate distance, open status, vegetarian reminder, and zero fake vendors.
    """
    card = CampusFoodService.search_food("Best soya chaap near me?", landmark="block 32")
    assert card is not None
    assert card.outlet_id == "FOOD-002"
    assert "Punjabi Tadka" in card.display_name
    assert "Block 27" in card.location_description
    assert any("Soya Chaap" in item for item in card.matched_items)
    assert card.is_vegetarian is True
    assert card.distance_meters is not None
    assert card.distance_meters > 0
    assert card.walking_minutes is not None
    assert card.query_match_status == "exact"
    assert "Rs. 130" in card.price_sample


@pytest.mark.asyncio
async def test_acceptance_2_food_near_block_32():
    """
    Acceptance Criterion 2: 'Find food outlets inside LPU near Block 32'
    Must calculate distance from Block 32 and return nearby outlets.
    """
    card = CampusFoodService.search_food("Find food outlets inside LPU near Block 32")
    assert card is not None
    assert card.distance_meters is not None
    # Block 32 has Subway (0m) or nearby Block 34 / Block 27 outlets
    assert card.distance_meters <= 200
    assert card.is_vegetarian is True


@pytest.mark.asyncio
async def test_acceptance_3_unmatched_food_alternative():
    """
    Acceptance Criterion 3: Unmatched food query (e.g. 'sushi')
    Must report no verified match in official campus food records,
    reiterate 100% pure vegetarian campus, and provide verified vegetarian alternatives.
    """
    card = CampusFoodService.search_food("Is there any sushi restaurant or food outlet inside campus?")
    assert card is not None
    assert card.query_match_status == "unmatched_alternative"
    assert len(card.alternatives) > 0
    assert card.is_vegetarian is True


@pytest.mark.asyncio
async def test_acceptance_4_where_is_block_32():
    """
    Acceptance Criterion 4: 'Where is Block 32?'
    Returns verified place card for School of Computer Science & Engineering.
    """
    async with AsyncSessionLocal() as db:
        place = await CampusMapService.find_matching_place("Where is Block 32?", db)
        assert place is not None
        assert "Block 32" in place.building
        assert "Computer Science" in place.name


@pytest.mark.asyncio
async def test_acceptance_5_where_is_block_27_room_102():
    """
    Acceptance Criterion 5: 'Where is Block 27 Room 102?'
    Returns verified place card for EDU-Revolution Query & Assistance Zone.
    """
    async with AsyncSessionLocal() as db:
        place = await CampusMapService.find_matching_place("Where is Block 27 Room 102?", db)
        assert place is not None
        assert "Block 27" in place.building
        assert "102" in (place.floor_room or "")
        assert "EDU-Revolution" in place.name


@pytest.mark.asyncio
async def test_acceptance_6_ai_ml_hod_distinction_and_no_room_fabrication():
    """
    Acceptance Criterion 6: 'Who is the AI & ML HOD? Where is the office?'
    Identifies Dr. Mohit Arora as Professor & Head of School (School of CSE),
    explicitly clarifies no separate AI & ML Department HOD exists,
    and NEVER invents a room number (directs to Block 32 Ground Floor School Office).
    """
    person = PeopleDirectoryService.search_person("Who is the AI & ML HOD? Where is the office?")
    assert person is not None
    assert person.full_name == "Dr. Mohit Arora"
    assert "Head of School" in person.designation or "HOD" in person.designation
    assert "School of Computer Science & Engineering" in person.school_division
    assert "Block 32" in person.building_block
    # Must NOT fabricate a room number
    assert "Not Published" in person.room_cabin
    # Must note distinction in notes
    assert "NO distinct public AI & ML Department HOD" in person.notes


@pytest.mark.asyncio
async def test_acceptance_7_senior_dean_cse():
    """
    Acceptance Criterion 7: 'Who is the Senior Dean of CSE?'
    Identifies Dr. Rajeev Sobti (Block 34 Executive Wing).
    """
    person = PeopleDirectoryService.search_person("Who is the Senior Dean of CSE?")
    assert person is not None
    assert person.full_name == "Dr. Rajeev Sobti"
    assert "Senior Dean" in person.designation
    assert "Block 34" in person.building_block


@pytest.mark.asyncio
async def test_acceptance_8_attendance_issue_resolver():
    """
    Acceptance Criterion 8: 'Whom should I meet for an attendance issue?'
    Routes to Class Mentor / Course Instructor first, lists required documents,
    and specifies escalation ladder.
    """
    route = IssueToOfficeResolver.resolve_issue("Whom should I meet for an attendance issue?")
    assert route is not None
    assert route.issue_key == "attendance_discrepancy"
    assert "Class Mentor" in route.primary_contact_role or "Course Instructor" in route.primary_contact_role
    assert "Block 32" in route.office_location
    assert "UMS > Attendance" in route.ums_navigation_path
    assert any("biometric" in doc.lower() for doc in route.required_documents)
    assert len(route.escalation_ladder) >= 3
    assert "Course Instructor" in route.escalation_ladder[0]


@pytest.mark.asyncio
async def test_acceptance_9_edurev_ai_project_advisor():
    """
    Acceptance Criterion 9: 'I built an AI project. What EDU-Revolution or academic-benefit category could apply?'
    Maps to CAT-02 (Innovative Projects, AI Products & Systems), specifies evidence checklist,
    caveats (no automatic marks/attendance), and SCRGM revenue distinction.
    """
    advisor = AcademicBenefitAdvisor.assess_project(
        "I built an AI project. What EDU-Revolution or academic-benefit category could apply?"
    )
    assert advisor is not None
    assert advisor.category_id == "CAT-02"
    assert "Innovative Projects" in advisor.category_name
    assert any("GitHub" in ev for ev in advisor.evidence_checklist)
    assert "Block 27 Room 102" in advisor.physical_helpdesk
    assert "Edu-Revolution: Be the change" in advisor.submission_route
    assert "Standing Academic Committee" in advisor.guarantee_disclaimer
    assert "SCRGM" in advisor.scrgm_distinction


@pytest.mark.asyncio
async def test_acceptance_10_where_to_submit_project():
    """
    Acceptance Criterion 10: 'Where do I submit this project?'
    Directs to UMS RMS Edu-Revolution module and Block 27 Room 102.
    """
    route = IssueToOfficeResolver.resolve_issue("Where do I submit this project?")
    assert route is not None
    assert route.issue_key == "academic_benefits"
    assert "Block 27" in route.office_location
    assert "102" in route.room_details
    assert "Edu-Revolution: Be the change" in route.ums_navigation_path


@pytest.mark.asyncio
async def test_acceptance_11_chat_api_soya_chaap_end_to_end():
    """
    Acceptance Criterion 11: End-to-end Chat API call for 'Best soya chaap near me?'
    Returns FoodOutletCard, verified text content, pure vegetarian reminder, and citations.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.post("/api/v1/chat", json={
            "message": "Best soya chaap near me?",
            "session_token": "test-session-token-v4-001"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["food_outlet_card"] is not None
        assert data["food_outlet_card"]["outlet_id"] == "FOOD-002"
        assert "Punjabi Tadka" in data["food_outlet_card"]["display_name"]
        assert "Punjabi Tadka" in data["content"]
        assert "Vegetarian" in data["content"] or "vegetarian" in data["content"]
        assert len(data["citations"]) > 0


@pytest.mark.asyncio
async def test_acceptance_12_chat_api_revalidation_advisory():
    """
    Acceptance Criterion 12: Historical/stale records from 2024 brochure
    (e.g. DSR Block 32 Room 100) must surface a revalidation advisory notice.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.post("/api/v1/chat", json={
            "message": "Whom should I meet for student relationship or mentor issue in DSR?",
            "session_token": "test-session-token-v4-002"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["who_to_meet_card"] is not None
        assert data["who_to_meet_card"]["revalidation_notice"] is not None
        assert "revalidate" in data["who_to_meet_card"]["revalidation_notice"].lower() or "2024" in data["who_to_meet_card"]["revalidation_notice"]

