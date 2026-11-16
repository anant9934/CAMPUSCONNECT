import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app.main import app
from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.core.security import create_access_token
from app.models.ums_catalog import UMSServiceCatalog
from app.models.action_workflow import ActionWorkflow
from app.models.campus_place import CampusPlace
from app.models.audit import AuditLog
from app.services.actions.action_classifier import ActionClassifier, ActionMode
from app.services.actions.ums_service import UMSServiceResolver
from app.services.actions.workflow_engine import WorkflowEngine
from app.services.campus_map_service import CampusMapService


# ========================================================
# 1. DATABASE INVENTORY & INTEGRITY ACCEPTANCE TESTS
# ========================================================

@pytest.mark.asyncio
async def test_all_234_ums_menu_entries_loaded():
    """Verify all 234 UMS menu entries from user screenshots are loaded in the database."""
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(UMSServiceCatalog))
        all_services = res.scalars().all()

        assert len(all_services) == 234, f"Expected 234 UMS services, got {len(all_services)}"

        # Verify default handoff URL and verification status across entries
        for svc in all_services:
            assert svc.deep_link_url == "https://ums.lpu.in/lpuums/"
            assert svc.verification_status in ["menu_label_observed_procedure_not_verified", "verified"]
            assert ">" in svc.navigation_path, f"Breadcrumb missing chevron in {svc.catalog_id}: {svc.navigation_path}"
            assert svc.navigation_path.startswith("UMS > ")

        # Verify key modules exist
        modules = {s.module for s in all_services}
        assert "Examination System" in modules
        assert "Residential Services" in modules
        assert "Health Services" in modules
        assert "Fee and Scholarship System" in modules
        assert "Relationship Management System (RMS)" in modules


@pytest.mark.asyncio
async def test_all_24_action_workflows_loaded():
    """Verify all 24 guided action workflows from SRS v3.0 are registered with steps & prereqs."""
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(ActionWorkflow))
        workflows = res.scalars().all()

        assert len(workflows) == 24, f"Expected 24 action workflows, got {len(workflows)}"

        intents = [w.user_intent.lower() for w in workflows]
        assert any("hostel" in i for i in intents)
        assert any("doctor" in i for i in intents)
        assert any("counsel" in i for i in intents)
        assert any("library" in i for i in intents)
        assert any("language lab" in i for i in intents)
        assert any("grievance" in i or "rms" in i for i in intents)
        assert any("re-appear" in i for i in intents)
        assert any("fee" in i for i in intents)

        for wf in workflows:
            assert len(wf.steps) > 0, f"Workflow {wf.action_id} must have steps"
            assert wf.handoff_url == "https://ums.lpu.in/lpuums/"


@pytest.mark.asyncio
async def test_campus_places_loaded():
    """Verify verified campus landmarks and blocks are registered with coordinates & hours."""
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(CampusPlace))
        places = res.scalars().all()

        assert len(places) >= 10, f"Expected at least 10 campus places, got {len(places)}"

        buildings = {p.building for p in places}
        assert "Block 34" in buildings
        assert "Block 13" in buildings
        assert "Block 30" in buildings
        assert any("36" in b or "Library" in p.name for b in buildings for p in places)
        assert any("UniMall" in b for b in buildings)


# ========================================================
# 2. ACTION CLASSIFIER 8-MODE ACCEPTANCE TESTS
# ========================================================

def test_action_classifier_eight_modes():
    """Verify ActionClassifier cleanly distinguishes the 8 distinct SRS v3.0 action modes."""
    # 1. EXECUTE (Tier 5 transaction requests)
    mode, *_ = ActionClassifier.classify_intent("Please book a hostel room for me right now")
    assert mode == ActionMode.EXECUTE
    mode, *_ = ActionClassifier.classify_intent("Pay my tuition fees for me directly")
    assert mode == ActionMode.EXECUTE

    # 2. PERSONAL_RECORD (Tier 4 private student data)
    mode, *_ = ActionClassifier.classify_intent("What is my attendance in CSE101?")
    assert mode == ActionMode.PERSONAL_RECORD
    mode, *_ = ActionClassifier.classify_intent("Show my term end result and CGPA")
    assert mode == ActionMode.PERSONAL_RECORD
    mode, *_ = ActionClassifier.classify_intent("Download my fee receipt and fee statement")
    assert mode == ActionMode.PERSONAL_RECORD

    # 3. BOOK_HANDOFF (Tier 3 guided booking)
    mode, *_ = ActionClassifier.classify_intent("How do I book a routine doctor appointment at LPU clinic?")
    assert mode == ActionMode.BOOK_HANDOFF
    mode, *_ = ActionClassifier.classify_intent("Guide me through hostel room allotment and booking")
    assert mode == ActionMode.BOOK_HANDOFF
    mode, *_ = ActionClassifier.classify_intent("How can I book a discussion room in the library?")
    assert mode == ActionMode.BOOK_HANDOFF
    mode, *_ = ActionClassifier.classify_intent("How do I book a counselling session with YourDOST?")
    assert mode == ActionMode.BOOK_HANDOFF

    # 4. ESCALATE (Tier 3 emergency triage)
    mode, *_ = ActionClassifier.classify_intent("Emergency medical help! A student collapsed in block 34!")
    assert mode == ActionMode.ESCALATE
    mode, *_ = ActionClassifier.classify_intent("Call ambulance immediately someone has severe chest pain")
    assert mode == ActionMode.ESCALATE

    # 5. PREPARE (Tier 2 procedural preparation)
    mode, *_ = ActionClassifier.classify_intent("What documents do I need for re-appear exam registration?")
    assert mode == ActionMode.PREPARE
    mode, *_ = ActionClassifier.classify_intent("What is the procedure for fee refund?")
    assert mode == ActionMode.PREPARE

    # 6. NAVIGATE (Tier 1 UMS wayfinding)
    mode, *_ = ActionClassifier.classify_intent("Where can I find the exam date sheet menu in UMS?")
    assert mode == ActionMode.NAVIGATE
    mode, *_ = ActionClassifier.classify_intent("How do I navigate to the bus route details in UMS?")
    assert mode == ActionMode.NAVIGATE

    # 7. ABSTAIN (Tier 0 out-of-domain)
    mode, *_ = ActionClassifier.classify_intent("Who won the 2024 cricket world cup?")
    assert mode == ActionMode.ABSTAIN
    mode, *_ = ActionClassifier.classify_intent("Write a quicksort algorithm in C++")
    assert mode == ActionMode.ABSTAIN

    # 8. ANSWER (Tier 0 standard FAQ / Policy)
    mode, *_ = ActionClassifier.classify_intent("What is the minimum attendance requirement at LPU?")
    assert mode == ActionMode.ANSWER


# ========================================================
# 3. UMS SERVICE RESOLVER & NATURAL LANGUAGE SYNONYMS
# ========================================================

@pytest.mark.asyncio
async def test_ums_service_resolver_exact_and_synonyms():
    """Verify natural language resolution to exact 234 catalog entries and breadcrumb generation."""
    async with AsyncSessionLocal() as db:
        # Re-appear registration (UMS-031)
        svc = await UMSServiceResolver.find_matching_service("reappear exam form", db)
        assert svc is not None
        assert svc.catalog_id in ["UMS-031", "UMS-032", "UMS-033"]
        assert "Re-Appear" in svc.service_label
        assert svc.navigation_path.startswith("UMS > Examination System > Registration for Re-Appear")

        # Doctor appointment (UMS-207)
        svc_doc = await UMSServiceResolver.find_matching_service("appointment with campus doctor", db)
        assert svc_doc is not None
        assert svc_doc.catalog_id == "UMS-207"
        assert "Doctor" in svc_doc.service_label
        assert svc_doc.navigation_path == "UMS > Health Services > Doctor Appointment"

        # Internet password reset (UMS-171)
        svc_net = await UMSServiceResolver.find_matching_service("reset internet password", db)
        assert svc_net is not None
        assert svc_net.catalog_id == "UMS-171"
        assert "Internet" in svc_net.service_label
        assert svc_net.navigation_path == "UMS > Account and Miscellaneous > Reset Internet Password"

        # Navigation Card generation
        card = UMSServiceResolver.build_navigation_card(svc)
        assert card.service_title == svc.service_label
        assert card.breadcrumb == svc.navigation_path
        assert card.handoff_url == "https://ums.lpu.in/lpuums/"


# ========================================================
# 4. EMERGENCY MEDICAL TRIAGE & WORKFLOW ENGINE TESTS
# ========================================================

@pytest.mark.asyncio
async def test_doctor_appointment_vs_emergency_triage():
    """Verify distinction between routine doctor booking and UniHospital Block 30 emergency."""
    async with AsyncSessionLocal() as db:
        # 1. Routine doctor appointment
        routine_wf = await WorkflowEngine.match_workflow("book routine doctor appointment", db)
        assert routine_wf is not None
        assert routine_wf.action_id == "ACT-002"
        card = WorkflowEngine.build_booking_card(routine_wf)
        assert "Doctor" in card.booking_type
        assert card.handoff_url == "https://ums.lpu.in/lpuums/"

        # 2. Emergency medical query
        is_emerg = WorkflowEngine.is_emergency_medical("emergency heart attack in hostel")
        assert is_emerg is True
        emerg_info = WorkflowEngine.get_emergency_contacts()
        assert "+91-1824-517100" in emerg_info["ambulance_phones"]
        assert "Block 30" in emerg_info["hospital_location"]


@pytest.mark.asyncio
async def test_rms_grievance_workflow_5_stage_hierarchy():
    """Verify RMS grievance workflow generates 5-stage hierarchy and tracking paths."""
    async with AsyncSessionLocal() as db:
        wf = await WorkflowEngine.match_workflow("how to register grievance in RMS", db)
        assert wf is not None
        assert wf.action_id == "ACT-007"

        rms_card = WorkflowEngine.build_rms_card(wf)
        assert rms_card.submission_path == "UMS > Student Services > Relationship Management System > Log Request"
        assert rms_card.tracking_path == "UMS > Student Services > Relationship Management System > View Request Status"
        assert len(rms_card.stages) == 5
        assert "Message Type" in rms_card.stages[0]
        assert "Department" in rms_card.stages[1]
        assert "Category" in rms_card.stages[2]
        assert "confidentiality" in rms_card.privacy_notice.lower()


# ========================================================
# 5. CAMPUS MAP WAYFINDING TESTS
# ========================================================

@pytest.mark.asyncio
async def test_campus_map_service_matching():
    """Verify campus wayfinding matching for key LPU blocks and amenities."""
    async with AsyncSessionLocal() as db:
        # Block 34 (Examination)
        p34 = await CampusMapService.find_matching_place("where is block 34?", db)
        assert p34 is not None
        assert p34.building == "Block 34"
        assert "Examination" in p34.name

        # Block 30 UniHospital
        p30 = await CampusMapService.find_matching_place("how to reach unihospital?", db)
        assert p30 is not None
        assert p30.building == "Block 30"
        assert "Hospital" in p30.name

        # Central Library
        plib = await CampusMapService.find_matching_place("central library location", db)
        assert plib is not None
        assert "Library" in plib.name

        # CampusPlaceCard generation
        card = CampusMapService.build_place_card(p34)
        assert card.building == "Block 34"
        assert card.place_id == "LOC-001"
        assert card.map_url == "https://www.lpu.in/about_lpu/campus-tour.php"


# ========================================================
# 6. END-TO-END CHAT API ACTION ENRICHMENT TESTS
# ========================================================

@pytest.mark.asyncio
async def test_chat_action_cards_integration():
    """Verify chat endpoint returns appropriate action cards and guardrails."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create session
        sess_resp = await client.post("/api/v1/sessions", json={"user_agent": "ActionTest"})
        session_token = sess_resp.json()["session_token"]

        # Case 1: Private student record (Attendance)
        att_resp = await client.post(
            "/api/v1/chat",
            json={"message": "What is my current attendance percentage in CSE?", "session_token": session_token}
        )
        assert att_resp.status_code == 200
        att_data = att_resp.json()
        assert att_data["action_type"] == "PERSONAL_RECORD"
        assert att_data["personal_record_card"] is not None
        assert "Attendance" in att_data["personal_record_card"]["breadcrumb"]
        assert "private" in att_data["personal_record_card"]["boundary_explanation"].lower() or "privately" in att_data["personal_record_card"]["boundary_explanation"].lower()

        # Case 2: Direct Execution Refusal Guardrail (Tier 5)
        exec_resp = await client.post(
            "/api/v1/chat",
            json={"message": "Book my hostel room immediately for me", "session_token": session_token}
        )
        assert exec_resp.status_code == 200
        exec_data = exec_resp.json()
        assert exec_data["action_type"] in ["EXECUTE", "BOOK_HANDOFF"]
        assert "public" in exec_data["content"].lower() or "authenticated" in exec_data["content"].lower()

        # Case 3: Emergency medical query
        emerg_resp = await client.post(
            "/api/v1/chat",
            json={"message": "Medical emergency! Someone collapsed in Block 34, call ambulance!", "session_token": session_token}
        )
        assert emerg_resp.status_code == 200
        emerg_data = emerg_resp.json()
        assert emerg_data["action_type"] == "ESCALATE"
        assert "+91-1824-517100" in emerg_data["content"]
        assert "Block 30" in emerg_data["content"]


# ========================================================
# 7. UMS PUBLIC & ADMIN API ENDPOINTS TESTS
# ========================================================

@pytest.mark.asyncio
async def test_ums_public_and_admin_endpoints():
    """Verify public retrieval and admin update endpoints for UMS service catalog."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Public list UMS services
        list_resp = await client.get("/api/v1/ums/services?limit=10")
        assert list_resp.status_code == 200
        services = list_resp.json()
        assert len(services) == 10

        # 2. Public get single service by catalog ID
        svc_resp = await client.get("/api/v1/ums/services/UMS-001")
        assert svc_resp.status_code == 200
        svc_data = svc_resp.json()
        assert svc_data["catalog_id"] == "UMS-001"
        assert svc_data["navigation_path"] == "UMS > Cohorts > Career Profiling"

        # Check UMS-021 Date Sheet
        ds_resp = await client.get("/api/v1/ums/services/UMS-021")
        assert ds_resp.status_code == 200
        assert ds_resp.json()["navigation_path"] == "UMS > Examination System > Examination Date Sheet"

        # 3. Public list workflows
        wf_resp = await client.get("/api/v1/ums/workflows")
        assert wf_resp.status_code == 200
        workflows = wf_resp.json()
        assert len(workflows) == 24

        # 4. Public list campus places
        places_resp = await client.get("/api/v1/campus/places")
        assert places_resp.status_code == 200
        places = places_resp.json()
        assert len(places) >= 10

        # 5. Admin endpoints (authenticate via admin login)
        login_resp = await client.post(
            "/api/v1/admin/auth/login",
            json={
                "username": settings.ADMIN_DEFAULT_USERNAME,
                "password": settings.ADMIN_DEFAULT_PASSWORD,
            }
        )
        assert login_resp.status_code == 200
        admin_token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {admin_token}"}

        admin_list = await client.get("/api/v1/admin/ums-catalog?limit=5", headers=headers)
        assert admin_list.status_code == 200
        assert len(admin_list.json()) == 5

        # 6. Admin update UMS service
        update_payload = {
            "notes": "Verified against 2026 examination schedule.",
            "verification_status": "verified"
        }
        put_resp = await client.put("/api/v1/admin/ums-catalog/UMS-001", json=update_payload, headers=headers)
        assert put_resp.status_code == 200
        updated = put_resp.json()
        assert updated["verification_status"] == "verified"
        assert updated["notes"] == "Verified against 2026 examination schedule."
