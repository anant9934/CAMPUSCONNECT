"""
Tests for Data Quality v4.0 & Typed Knowledge Architecture (30 types)
Verifies PDF extraction, HTML extraction, UMS normalization, intent classification,
and admin curation endpoints.
"""
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select, func
from app.core.config import settings
from app.main import app
from app.core.database import AsyncSessionLocal
from app.models.knowledge_record import KnowledgeRecord
from app.schemas.typed_knowledge import KnowledgeType
from app.services.ingestion.pdf_extractor import PDFExtractor
from app.services.ingestion.html_extractor import HTMLExtractor
from app.services.rag.intent_classifier import IntentClassifier, QueryIntent


def test_30_knowledge_types_defined():
    """Verify all 30 knowledge types are enumerated in KnowledgeType."""
    assert len(KnowledgeType) == 30
    types = [t.value for t in KnowledgeType]
    assert "faq" in types
    assert "policy" in types
    assert "academic_regulation" in types
    assert "process_sop" in types
    assert "ums_service" in types
    assert "action_workflow" in types
    assert "fee_structure" in types
    assert "scholarship_scheme" in types
    assert "examination_rule" in types
    assert "grading_system" in types
    assert "attendance_policy" in types
    assert "hostel_rule" in types
    assert "transport_route" in types
    assert "campus_facility" in types
    assert "office_directory" in types
    assert "faculty_profile" in types
    assert "academic_programme" in types
    assert "placement_policy" in types
    assert "medical_health_service" in types
    assert "security_emergency_protocol" in types
    assert "library_resource" in types
    assert "grievance_redressal_mechanism" in types


def test_pdf_extractor_edu_revolution():
    """Verify PDF extractor parses 12 structured policy and regulation records from EDU Revolution Guide."""
    pe = PDFExtractor()
    records = pe.extract_records()
    assert len(records) >= 12
    rec_ids = [r["record_id"] for r in records]
    assert "LPU-EDREV-001" in rec_ids  # Framework
    assert "LPU-EDREV-003" in rec_ids  # Revenue Generation
    assert "LPU-EDREV-008" in rec_ids  # Scopus Q1 Grade Upgradation
    assert "LPU-EDREV-009" in rec_ids  # 10% Attendance Benefit
    assert "LPU-EDREV-012" in rec_ids  # Block 38-205B Query Zone


def test_html_extractor_dossier():
    """Verify HTML extractor parses faculty profiles, academic programmes, and scholarships."""
    he = HTMLExtractor()
    records = he.extract_records()
    assert len(records) >= 90
    fac = [r for r in records if r["record_type"] == KnowledgeType.FACULTY_PROFILE.value]
    prg = [r for r in records if r["record_type"] == KnowledgeType.ACADEMIC_PROGRAMME.value]
    sch = [r for r in records if r["record_type"] == KnowledgeType.SCHOLARSHIP_SCHEME.value]
    assert len(fac) >= 70
    assert len(prg) >= 5
    assert len(sch) >= 3


def test_intent_classifier_12_categories():
    """Verify IntentClassifier categorizes student inquiries into the 12 intents."""
    intent1, score1, _ = IntentClassifier.classify("Where is the ambulance and campus hospital?")
    assert intent1 == QueryIntent.HEALTH_EMERGENCY

    intent2, score2, _ = IntentClassifier.classify("How do I register a complaint on RMS portal?")
    assert intent2 == QueryIntent.GRIEVANCE_RMS

    intent3, score3, _ = IntentClassifier.classify("What is the fee for B.Tech CSE AI and ML?")
    assert intent3 == QueryIntent.FEES_SCHOLARSHIP

    intent4, score4, _ = IntentClassifier.classify("When is the reappear exam datesheet released?")
    assert intent4 == QueryIntent.EXAMINATION_SCHEDULE

    intent5, score5, _ = IntentClassifier.classify("What electrical appliances are allowed in hostel rooms?")
    assert intent5 == QueryIntent.HOSTEL_HOUSING

    intent6, score6, _ = IntentClassifier.classify("How does the 10% attendance benefit work for GATE?")
    assert intent6 == QueryIntent.ACADEMIC_REGULATION

    intent7, score7, _ = IntentClassifier.classify("Who is Dr. Rajeev Sobti?")
    assert intent7 == QueryIntent.FACULTY_DIRECTORY


@pytest.mark.asyncio
async def test_database_populated_with_30_types():
    """Verify knowledge_records in campusconnect.db has hundreds of curated records across types."""
    async with AsyncSessionLocal() as session:
        total = (await session.execute(select(func.count(KnowledgeRecord.id)))).scalar()
        assert total >= 450

        ums_count = (await session.execute(
            select(func.count(KnowledgeRecord.id)).where(KnowledgeRecord.record_type == "ums_service")
        )).scalar()
        assert ums_count >= 200

        fac_count = (await session.execute(
            select(func.count(KnowledgeRecord.id)).where(KnowledgeRecord.record_type == "faculty_profile")
        )).scalar()
        assert fac_count >= 70


@pytest.mark.asyncio
async def test_admin_statistics_and_conflicts_endpoints():
    """Verify admin statistics and conflicts endpoints."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Login admin
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

        # Check statistics
        stats_resp = await client.get("/api/v1/admin/knowledge-records/statistics", headers=headers)
        assert stats_resp.status_code == 200
        stats = stats_resp.json()
        assert stats["total_records"] >= 450
        assert stats["approved_records"] >= 450
        assert "ums_service" in stats["type_distribution"]
        assert "faculty_profile" in stats["type_distribution"]

        # Check conflicts
        conflicts_resp = await client.get("/api/v1/admin/knowledge-records/conflicts", headers=headers)
        assert conflicts_resp.status_code == 200
        assert isinstance(conflicts_resp.json(), list)
