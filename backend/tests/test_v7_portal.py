import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.database import AsyncSessionLocal
from app.ai.llm_registry import LLMRegistry
from app.ai.gemini_provider import GeminiProvider
from app.ai.conversation_orchestrator import ConversationOrchestrator
from app.models.session import AnonymousSession, Conversation


@pytest.mark.asyncio
async def test_llm_registry_and_gemini_provider():
    """Verify GeminiProvider is registered as default real LLM provider."""
    provider = LLMRegistry.get_default_provider()
    assert provider is not None
    assert provider.provider_name == "gemini"
    assert "gemini" in provider.model_name


@pytest.mark.asyncio
async def test_portal_dashboard_endpoint():
    """Verify Student Dashboard returns valid profile, deadlines, and notices."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/portal/dashboard")
        assert res.status_code == 200
        data = res.json()
        assert "welcome_message" in data
        assert data["profile"]["school"] == "School of Computer Science & Engineering"
        assert data["profile"]["is_connected"] is False  # Privacy safeguard
        assert len(data["important_deadlines"]) >= 3
        assert len(data["verified_notices"]) >= 3


@pytest.mark.asyncio
async def test_people_expert_discovery_filter():
    """Verify expert discovery by domain expertise (AI/ML, Cyber, etc.)."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/portal/people?expertise=AI")
        assert res.status_code == 200
        data = res.json()
        assert data["total"] > 0
        names = [p["full_name"] for p in data["people"]]
        assert any("Mohit Arora" in n for n in names)
        # Verify office seating disclaimer is present
        for p in data["people"]:
            assert "appointment_route" in p
            assert p["office_seating_verified"] in (True, False)


@pytest.mark.asyncio
async def test_opportunities_and_events_endpoints():
    """Verify verified campus opportunities and events."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        opp_res = await ac.get("/api/v1/portal/opportunities")
        assert opp_res.status_code == 200
        opps = opp_res.json()
        assert len(opps) >= 4
        assert any(o["opportunity_type"] == "placement" for o in opps)
        assert any(o["opportunity_type"] == "hackathon" for o in opps)

        evt_res = await ac.get("/api/v1/portal/events")
        assert evt_res.status_code == 200
        evts = evt_res.json()
        assert len(evts) >= 3
        assert any(e["category"] == "academic" for e in evts)


@pytest.mark.asyncio
async def test_academic_benefit_assessment_interactive():
    """Verify interactive project assessment with missing checklist."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        payload = {
            "description": "I built an AI healthcare disease detection system using PyTorch and FastAPI.",
            "has_github": True,
            "has_live_demo": False,
            "has_architecture_doc": True
        }
        res = await ac.post("/api/v1/portal/assess-benefit", json=payload)
        assert res.status_code == 200
        data = res.json()
        card = data["assessment_card"]
        assert card["category_id"] == "CAT-02"
        assert "Public GitHub repository link with full commit history" not in data["updated_missing_evidence"]
        assert any("Live working demo" in m for m in data["updated_missing_evidence"])
        assert data["readiness_score"] >= 50


@pytest.mark.asyncio
async def test_conversation_orchestrator_pipeline():
    """Verify ConversationOrchestrator end-to-end execution pipeline."""
    import uuid
    async with AsyncSessionLocal() as db:
        token = f"test_token_{uuid.uuid4().hex}"
        sess = AnonymousSession(
            session_token=token,
            is_active=True,
            expires_at=AnonymousSession.create_expiry_date() if hasattr(AnonymousSession, 'create_expiry_date') else None
        )
        if not sess.expires_at:
            from datetime import datetime, timezone, timedelta
            sess.expires_at = datetime.now(timezone.utc) + timedelta(days=7)
        db.add(sess)
        await db.flush()

        conv = Conversation(session_id=sess.id, title="Test V7 Orchestration")
        db.add(conv)
        await db.flush()

        res = await ConversationOrchestrator.process_user_turn(
            message="Who is the AI & ML HOD? Where does he sit?",
            conversation_id=str(conv.id),
            session_id=str(sess.id),
            db=db
        )

        assert "content" in res
        assert len(res["thinking_steps"]) == 5
        assert res["person_card"] is not None
        assert "Mohit Arora" in res["person_card"].full_name
        assert res["person_card"].office_seating_verified is False


@pytest.mark.asyncio
async def test_document_upload_endpoint():
    """Verify file upload for document understanding."""
    import uuid
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        files = {"file": ("test_doc.txt", b"Student project architecture for autonomous robot navigation.", "text/plain")}
        data = {"session_token": f"test_token_upload_{uuid.uuid4().hex[:8]}"}
        res = await ac.post("/api/v1/chat/upload", files=files, data=data)
        assert res.status_code == 200
        body = res.json()
        assert body["status"] == "success"
        assert body["characters_extracted"] > 0
        assert "autonomous robot" in body["extracted_content"]


@pytest.mark.asyncio
async def test_conversation_rename_endpoint():
    """Verify conversation rename via PATCH."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Create session first
        sess_res = await ac.post("/api/v1/sessions", json={})
        token = sess_res.json()["session_token"]

        # Send a message to start conversation
        chat_res = await ac.post("/api/v1/chat", json={
            "message": "Where is Block 32?",
            "session_token": token
        })
        conv_id = chat_res.json()["conversation_id"]

        # Rename conversation
        rename_res = await ac.patch(
            f"/api/v1/conversations/{conv_id}",
            headers={"X-Session-Token": token},
            json={"title": "Campus Navigation: Block 32"}
        )
        assert rename_res.status_code == 200
        assert rename_res.json()["title"] == "Campus Navigation: Block 32"
