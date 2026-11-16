import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.services.campus_food_service import CampusFoodService
from app.services.people_directory_service import PeopleDirectoryService
from app.services.campus_map_service import CampusMapService
from app.services.edurev_advisor_service import AcademicBenefitAdvisor
from app.services.issue_resolver_service import IssueToOfficeResolver
from app.schemas.ums import EvidenceClassification
from app.core.database import AsyncSessionLocal


@pytest.mark.asyncio
async def test_food_distance_and_punjabi_tadka_provenance():
    """
    Truth Audit: Distance must be labeled straight-line estimate, not walking distance.
    Punjabi Tadka (FOOD-002) must be flagged USER_REPORTED with campus centroid disclaimer.
    """
    res = CampusFoodService.search_food("Best soya chaap near me?", landmark="block 32")
    assert res is not None
    assert res.estimated_straight_line_distance_meters is not None
    assert res.distance_type == "straight_line_estimate"

    # Punjabi Tadka provenance checks
    assert res.outlet_id == "FOOD-002"
    assert "Punjabi Tadka" in res.display_name
    assert res.evidence_status == "USER_REPORTED"
    assert res.verification_notice is not None
    assert "centroid" in res.verification_notice.lower() or "unverified" in res.verification_notice.lower()
    # 100% vegetarian campus mandate maintained
    assert res.is_vegetarian is True


@pytest.mark.asyncio
async def test_people_directory_role_separation_and_seating():
    """
    Truth Audit: Separation of School HOD vs Department HOD.
    Dr. Mohit Arora is School HOD of CSE; Department HOD is None (no separate AI/ML HOD published).
    Dr. Rajeev Sobti is Executive Dean (historically Senior Dean) with unverified office seating.
    """
    # Test Dr. Mohit Arora (School HOD)
    hod_card = PeopleDirectoryService.search_person("Who is the AI & ML HOD? Where is the office?")
    assert hod_card is not None
    assert "Mohit Arora" in hod_card.full_name
    assert hod_card.school_hod is not None
    assert "Mohit Arora" in hod_card.school_hod
    assert hod_card.department_hod is None
    assert "School of Computer Science & Engineering" in hod_card.school_division
    assert hod_card.evidence_status == "OFFICIAL_CURRENT_VERIFIED"
    assert "Not Published" in hod_card.room_cabin

    # Test Dr. Rajeev Sobti (Executive Dean)
    dean_card = PeopleDirectoryService.search_person("Who is the Senior Dean of CSE?")
    assert dean_card is not None
    assert "Rajeev Sobti" in dean_card.full_name
    assert "Executive Dean" in dean_card.designation
    assert "Senior Dean" in dean_card.designation  # Reconciled historical designation
    assert dean_card.executive_dean is not None
    assert dean_card.office_seating_verified is False
    assert "unverified" in dean_card.room_cabin.lower() or "reception" in (dean_card.notes or "").lower()


@pytest.mark.asyncio
async def test_campus_places_room_verification_status():
    """
    Truth Audit: Verified block does not imply verified room.
    Historical 2024 records (DSR Block 32 Room 100, DIA Block 32 Room 308)
    must carry UNVERIFIED_ROOM_HISTORICAL and OFFICIAL_HISTORICAL.
    Block 27 Room 102 must carry VERIFIED_ROOM and OFFICIAL_CURRENT_VERIFIED.
    """
    async with AsyncSessionLocal() as db:
        # DSR check (Historical 2024 brochure record)
        dsr = await CampusMapService.find_matching_place("Where is Division of Student Relationship Room 100?", db)
        assert dsr is not None
        assert dsr.room_verification_status == "UNVERIFIED_ROOM_HISTORICAL"
        assert dsr.evidence_status == "OFFICIAL_HISTORICAL"

        # DIA check (Historical 2024 brochure record)
        dia = await CampusMapService.find_matching_place("Where is International Affairs Room 308?", db)
        assert dia is not None
        assert dia.room_verification_status == "UNVERIFIED_ROOM_HISTORICAL"
        assert dia.evidence_status == "OFFICIAL_HISTORICAL"

        # Block 27 Room 102 check (Current verified facility)
        edurev_desk = await CampusMapService.find_matching_place("Where is Block 27 Room 102?", db)
        assert edurev_desk is not None
        assert edurev_desk.room_verification_status == "VERIFIED_ROOM"
        assert edurev_desk.evidence_status == "OFFICIAL_CURRENT_VERIFIED"


@pytest.mark.asyncio
async def test_edurev_four_stage_portal_and_safeguards():
    """
    Truth Audit: EDU-Revolution advisory must ground in official 4-stage portal,
    enforce 4-week course mapping window, SEC viva & SAC ratification prerequisite,
    and disclaim automatic grade/mark/attendance grants.
    """
    res = AcademicBenefitAdvisor.assess_project("I built an AI project for my portfolio")
    assert res is not None
    assert res.category_id == "CAT-02"
    assert "Select Category" in res.portal_stage_name
    assert "4 weeks" in res.course_mapping_window
    assert "School Evaluation Committee" in res.approval_prerequisite
    assert "Standing Academic Committee" in res.approval_prerequisite
    assert "POTENTIAL ELIGIBILITY ONLY" in res.eligibility_vs_approval_notice
    assert "SCRGM" in res.scrgm_distinction
    assert res.evidence_status == "OFFICIAL_CURRENT_VERIFIED"


@pytest.mark.asyncio
async def test_issue_resolver_three_tier_hierarchy():
    """
    Truth Audit: Issue resolution for attendance must follow strict 3-tier hierarchy:
    Course Instructor -> Academic Coordinator / Program Coordinator -> Head of School.
    """
    res = IssueToOfficeResolver.resolve_issue("Whom should I meet for an attendance issue?")
    assert res is not None
    assert res.issue_key == "attendance_discrepancy"
    ladder = res.escalation_ladder
    assert len(ladder) >= 3
    assert "Course Instructor" in ladder[0]
    assert "Academic Coordinator" in ladder[1]
    assert "Head of School" in ladder[2]
    assert res.evidence_status in [e.value for e in EvidenceClassification]

