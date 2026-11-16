import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.core.config import settings


@pytest.mark.asyncio
async def test_health_endpoints():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert "CampusConnect" in data["service"]

        ai_resp = await client.get("/api/v1/health/ai")
        assert ai_resp.status_code == 200
        ai_data = ai_resp.json()
        assert "configured_model" in ai_data


@pytest.mark.asyncio
async def test_categories_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/categories")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 6
        slugs = [c["slug"] for c in data]
        assert "academics" in slugs
        assert "examinations" in slugs
        assert "hostel" in slugs


@pytest.mark.asyncio
async def test_anonymous_session_and_chat_flow():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Create anonymous session
        sess_resp = await client.post("/api/v1/sessions", json={"user_agent": "Pytest-Client"})
        assert sess_resp.status_code == 200
        sess_data = sess_resp.json()
        token_a = sess_data["session_token"]
        assert token_a.startswith("lpu_sess_")

        # 2. Chat with LPU Assistant
        chat_payload = {
            "message": "How do I download my examination date sheet?",
            "session_token": token_a,
        }
        chat_resp = await client.post("/api/v1/chat", json=chat_payload)
        assert chat_resp.status_code == 200
        chat_data = chat_resp.json()

        assert "conversation_id" in chat_data
        assert "message_id" in chat_data
        assert len(chat_data["thinking_steps"]) == 5
        assert chat_data["thinking_steps"][0]["title"] == "Preparing question"
        assert chat_data["thinking_steps"][1]["title"] == "Searching LPU knowledge"
        assert chat_data["thinking_steps"][2]["title"] == "Analysing retrieved information"
        assert chat_data["thinking_steps"][3]["title"] == "Generating response"
        assert chat_data["thinking_steps"][4]["title"] == "Completed"
        assert len(chat_data["citations"]) > 0
        conv_id = chat_data["conversation_id"]

        # 3. Retrieve conversation history for Session A
        hist_resp = await client.get(
            f"/api/v1/conversations/{conv_id}",
            headers={"X-Session-Token": token_a}
        )
        assert hist_resp.status_code == 200
        hist_data = hist_resp.json()
        assert len(hist_data["messages"]) >= 2  # user and assistant

        # 4. Session Isolation Test: Session B must NOT be able to view Session A's conversation
        sess_b_resp = await client.post("/api/v1/sessions", json={"user_agent": "Pytest-Client-B"})
        token_b = sess_b_resp.json()["session_token"]

        leak_attempt = await client.get(
            f"/api/v1/conversations/{conv_id}",
            headers={"X-Session-Token": token_b}
        )
        assert leak_attempt.status_code == 404

        # 5. Submit Feedback
        fb_payload = {
            "conversation_id": conv_id,
            "message_id": chat_data["message_id"],
            "rating": "helpful",
            "comment": "Accurate examination guidelines",
            "session_token": token_a
        }
        fb_resp = await client.post("/api/v1/feedback", json=fb_payload)
        assert fb_resp.status_code == 200
        assert fb_resp.json()["rating"] == "helpful"


@pytest.mark.asyncio
async def test_admin_auth_and_dashboard_metrics():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Admin Login
        login_resp = await client.post(
            "/api/v1/admin/auth/login",
            json={
                "username": settings.ADMIN_DEFAULT_USERNAME,
                "password": settings.ADMIN_DEFAULT_PASSWORD,
            }
        )
        assert login_resp.status_code == 200
        login_data = login_resp.json()
        token = login_data["access_token"]
        assert token is not None

        # Access Protected Admin Dashboard
        dash_resp = await client.get(
            "/api/v1/admin/dashboard",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert dash_resp.status_code == 200
        dash_data = dash_resp.json()
        assert dash_data["total_approved_faqs"] >= 10
        assert "satisfaction_rate_percent" in dash_data

        # Unauthenticated request must be rejected
        unauth_resp = await client.get("/api/v1/admin/dashboard")
        assert unauth_resp.status_code == 401

