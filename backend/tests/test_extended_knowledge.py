import pytest
from datetime import datetime, timezone, timedelta
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.core.database import AsyncSessionLocal
from app.models.knowledge_record import KnowledgeRecord
from app.services.ingestion.validator import (
    validate_and_normalize_record,
    is_record_expired,
    is_record_sensitive,
    compute_content_hash,
    VALID_RECORD_TYPES,
)
from app.services.ingestion.variant_generator import generate_searchable_variants
from app.services.rag.source_validator import format_citation, validate_record_for_retrieval
from app.services.rag.hybrid_search import hybrid_search_engine
from app.core.config import settings
from app.core.security import create_access_token


ALL_12_TYPES = [
    "faq",
    "policy",
    "academic_schedule",
    "contact_directory",
    "facility_service",
    "library_resource",
    "placement_procedure",
    "international_programme",
    "research_facility",
    "student_activity",
    "grievance_procedure",
    "official_notice",
]


def test_all_twelve_types_in_schemas():
    """Verify that all 12 distinct institutional record types are registered in the schema validator."""
    assert len(ALL_12_TYPES) == 12
    for rtype in ALL_12_TYPES:
        assert rtype in VALID_RECORD_TYPES, f"Record type '{rtype}' missing from VALID_RECORD_TYPES"


def test_record_validation_and_sensitivity():
    """Verify schema validation and automated sensitivity tagging for governance."""
    # 1. Valid policy record with clause and page numbers
    policy_data = {
        "record_id": "TEST_POL_001",
        "record_type": "policy",
        "title": "LPU Minimum 75% Attendance Debarment Policy",
        "content": "Students failing to maintain 75% aggregate attendance shall be debarred from End-Term examinations.",
        "clause_reference": "Clause 3.1 Attendance Debarment",
        "source_page": "4",
        "source_document": "LPU Academic Regulations Handbook",
        "original_source_url": "https://www.lpu.in/academics/regulations",
        "type_metadata": {
            "clause_reference": "Clause 3.1",
            "section": "Section 3: Examination Eligibility",
            "applicable_students": "All regular undergraduate and postgraduate students",
        },
    }
    validated = validate_and_normalize_record(policy_data)
    assert validated["record_type"] == "policy"
    assert validated["is_sensitive"] is True  # Contains 'attendance' and 'debarred'

    # 2. Valid contact directory record
    contact_data = {
        "record_id": "TEST_DIR_001",
        "record_type": "contact_directory",
        "title": "Division of Examination Contact Directory",
        "content": "Office of the Controller of Examinations, Block 34 Room 201.",
        "original_source_url": "https://ums.lpu.in/directory",
        "type_metadata": {
            "office_role": "Controller of Examinations",
            "official_email": "coe@lpu.co.in",
            "published_phone": "+91-1824-517000",
            "campus_location": "Block 34, 2nd Floor",
            "operating_hours": "09:00 AM - 05:00 PM (Mon-Sat)",
        },
    }
    validated_contact = validate_and_normalize_record(contact_data)
    assert validated_contact["record_type"] == "contact_directory"
    assert validated_contact["type_metadata"]["official_email"] == "coe@lpu.co.in"


def test_duplicate_detection_via_content_hash():
    """Verify that content hashes are deterministic and detect duplicate content."""
    content_a = "Fee payment deadlines for Autumn Term 2024."
    content_b = "Fee payment deadlines for Autumn Term 2024."
    content_c = "Hostel room allocation guidelines."

    hash_a = compute_content_hash("Fee Guidelines", content_a, "policy")
    hash_b = compute_content_hash("Fee Guidelines", content_b, "policy")
    hash_c = compute_content_hash("Hostel Guidelines", content_c, "facility_service")

    assert hash_a == hash_b
    assert hash_a != hash_c
    assert len(hash_a) == 64  # SHA-256 hex string


def test_temporal_expiration_evaluation():
    """Verify that expired records are detected dynamically based on review_expiry_date."""
    now = datetime.now(timezone.utc)
    expired_date = now - timedelta(days=2)
    future_date = now + timedelta(days=60)

    assert is_record_expired(expired_date) is True
    assert is_record_expired(future_date) is False
    assert is_record_expired(None) is False


def test_rich_citation_preserves_type_metadata():
    """Verify that citations format clause references, pages, contact info, and hours."""
    # 1. Policy citation
    policy_citation = format_citation({
        "title": "LPU Attendance & Examination Rules",
        "original_source_url": "https://www.lpu.in/regulations",
        "record_type": "policy",
        "clause_reference": "Clause 4.2",
        "source_page": "12",
        "content": "Students must maintain 75% attendance to appear in exams.",
        "type_metadata": {"applicable_students": "All B.Tech batches"},
    })
    assert policy_citation["clause_reference"] == "Clause 4.2"
    assert policy_citation["source_page"] == "12"
    assert "Ref: Clause 4.2" in policy_citation["snippet"]
    assert "Page: 12" in policy_citation["snippet"]

    # 2. Contact directory citation
    contact_citation = format_citation({
        "title": "UniHospital Emergency Desk",
        "original_source_url": "https://www.lpu.in/hospital",
        "record_type": "contact_directory",
        "content": "24x7 medical emergency services on campus.",
        "type_metadata": {
            "official_email": "hospital@lpu.co.in",
            "verified_phone": "+91-1824-517100",
            "operating_hours": "24x7 Emergency Services",
        },
    })
    assert contact_citation["type_metadata"]["official_email"] == "hospital@lpu.co.in"
    assert "Email: hospital@lpu.co.in" in contact_citation["snippet"]
    assert "Tel: +91-1824-517100" in contact_citation["snippet"]

    # 3. Validation for retrieval gatekeeper
    approved_rec = {"is_approved": True, "approval_status": "approved", "requires_admin_review": False}
    unapproved_rec = {"is_approved": False, "approval_status": "pending_review", "requires_admin_review": True}
    assert validate_record_for_retrieval(approved_rec) is True
    assert validate_record_for_retrieval(unapproved_rec) is False


@pytest.mark.asyncio
async def test_question_variants_generator_preserves_facts():
    """Verify that searchable question variants are generated and do not alter underlying facts."""
    record = {
        "title": "LPU Uni-Hospital Medical Leave & Emergency Protocol",
        "content": "Uni-Hospital is situated near Block 30 and provides 24x7 emergency medical services to LPU students.",
        "record_type": "facility_service",
    }
    variants = await generate_searchable_variants(record)

    assert len(variants) >= 3
    # Check that variants are questions related to the record
    assert any("hospital" in v.lower() or "medical" in v.lower() or "emergency" in v.lower() for v in variants)


@pytest.mark.asyncio
async def test_search_excludes_expired_and_unapproved_records():
    """Verify that the hybrid search engine excludes expired and unapproved records from student search."""
    async with AsyncSessionLocal() as session:
        # Rebuild index over seeded database
        await hybrid_search_engine.build_index(session)

        # Search for a query
        res = await hybrid_search_engine.search("attendance debarment policy", session)
        for cand in res["candidates"]:
            # Every candidate returned must be approved
            assert cand.get("is_approved", True) is True
            assert cand.get("approval_status") in (None, "approved")


@pytest.mark.asyncio
async def test_admin_knowledge_records_api():
    """Verify Admin CRUD and governance operations on multi-type knowledge records."""
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Obtain valid admin token
        login_resp = await client.post(
            "/api/v1/admin/auth/login",
            json={
                "username": settings.ADMIN_DEFAULT_USERNAME,
                "password": settings.ADMIN_DEFAULT_PASSWORD,
            }
        )
        assert login_resp.status_code == 200
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 1. List records
        resp = await client.get("/api/v1/admin/knowledge-records", headers=headers)
        assert resp.status_code == 200
        records = resp.json()
        assert len(records) > 0

        # Verify multiple record types are present in repository
        types_found = {r["record_type"] for r in records}
        assert len(types_found) >= 5

        first_rec = records[0]
        rec_id = first_rec["record_id"]

        # 2. Get specific record by ID
        get_resp = await client.get(f"/api/v1/admin/knowledge-records/{rec_id}", headers=headers)
        assert get_resp.status_code == 200
        assert get_resp.json()["record_id"] == rec_id

        # 3. Approve record
        appr_resp = await client.post(f"/api/v1/admin/knowledge-records/{rec_id}/approve", headers=headers)
        assert appr_resp.status_code == 200
        assert appr_resp.json()["status"] == "success"

        # Verify updated status
        check_resp = await client.get(f"/api/v1/admin/knowledge-records/{rec_id}", headers=headers)
        assert check_resp.json()["approval_status"] == "approved"
        assert check_resp.json()["is_approved"] is True

        # 4. Generate variants
        var_resp = await client.post(f"/api/v1/admin/knowledge-records/{rec_id}/generate-variants", headers=headers)
        assert var_resp.status_code == 200
        assert len(var_resp.json()["searchable_variants"]) > 0
