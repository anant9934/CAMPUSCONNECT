import pytest
import uuid
from datetime import datetime, timezone, timedelta
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select

from app.main import app
from app.core.database import get_db, AsyncSessionLocal
from app.models import AnonymousSession, Conversation, Message, AdminUser
from app.core.security import get_password_hash, create_access_token


@pytest.mark.asyncio
async def test_sec_1_anonymous_student_requesting_cgpa():
    """Verify anonymous student asking for CGPA or personal marks is intercepted by privacy barrier."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create valid anonymous session
        token = f"test_anon_sec_{uuid.uuid4().hex}"
        payload = {
            "message": "What is my CGPA and my personal attendance percentage?",
            "session_token": token
        }
        res = await client.post("/api/v1/chat", json=payload)
        assert res.status_code == 200
        data = res.json()

        # Must NOT leak any private student data
        assert data["action_type"] == "PERSONAL_RECORD"
        assert "privacy" in data["content"].lower() or "safeguard" in data["content"].lower() or "individual academic records" in data["content"].lower()
        # Must provide PersonalRecordCard or safe UMS navigation
        assert data["personal_record_card"] is not None or "UMS" in data["content"]
        assert "CGPA: 8." not in data["content"]
        assert "9." not in data["content"]


@pytest.mark.asyncio
async def test_sec_2_authenticated_student_requesting_own_records():
    """Verify student profile endpoint returns safe masked/authorized public profile."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        token = f"test_auth_sec_{uuid.uuid4().hex}"
        # Create session in DB first
        async with AsyncSessionLocal() as session:
            now_utc = datetime.now(timezone.utc)
            sess_obj = AnonymousSession(
                session_token=token,
                is_active=True,
                last_activity_at=now_utc,
                expires_at=now_utc + timedelta(days=7)
            )
            session.add(sess_obj)
            await session.commit()

        res = await client.get("/api/v1/portal/dashboard", headers={"X-Session-Token": token})
        assert res.status_code == 200
        data = res.json()
        assert "profile" in data
        assert data["profile"]["programme"] == "B.Tech Computer Science & Engineering"
        # Verify private registration number is safely masked
        assert "Masked" in data["profile"]["registration_number"] or "XXXX" in data["profile"]["registration_number"]


@pytest.mark.asyncio
async def test_sec_3_student_a_accessing_student_b_records():
    """Verify Student A cannot retrieve Student B's conversation history."""
    async with AsyncSessionLocal() as session:
        now_utc = datetime.now(timezone.utc)
        # Create Student B session & conversation
        token_b = f"student_b_{uuid.uuid4().hex}"
        sess_b = AnonymousSession(
            session_token=token_b,
            is_active=True,
            last_activity_at=now_utc,
            expires_at=now_utc + timedelta(days=7)
        )
        session.add(sess_b)
        await session.flush()

        conv_b = Conversation(
            session_id=sess_b.id,
            title="Student B Confidential Query",
            is_active=True
        )
        session.add(conv_b)
        await session.flush()

        msg_b = Message(
            conversation_id=conv_b.id,
            role="user",
            content="Confidential personal discussion about disciplinary notice",
            thinking_steps=[],
            citations=[]
        )
        session.add(msg_b)
        await session.commit()
        conv_b_id = str(conv_b.id)

    # Now Student A tries to access Student B's conversation using Student A's token
    token_a = f"student_a_{uuid.uuid4().hex}"
    async with AsyncSessionLocal() as session:
        sess_a = AnonymousSession(
            session_token=token_a,
            is_active=True,
            last_activity_at=now_utc,
            expires_at=now_utc + timedelta(days=7)
        )
        session.add(sess_a)
        await session.commit()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get(
            f"/api/v1/conversations/{conv_b_id}",
            headers={"X-Session-Token": token_a}
        )
        # Must be 404 Not Found or Access Denied
        assert res.status_code == 404
        assert "access denied" in res.json()["detail"].lower() or "not found" in res.json()["detail"].lower()


@pytest.mark.asyncio
async def test_sec_4_invalid_session_token():
    """Verify invalid session token on protected endpoints raises 401."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get(
            "/api/v1/conversations",
            headers={"X-Session-Token": "completely_invalid_nonexistent_token_12345"}
        )
        assert res.status_code == 401
        assert "Invalid or expired session token" in res.json()["detail"]


@pytest.mark.asyncio
async def test_sec_5_expired_session():
    """Verify expired session cannot access conversations."""
    expired_token = f"expired_sess_{uuid.uuid4().hex}"
    async with AsyncSessionLocal() as session:
        now_utc = datetime.now(timezone.utc)
        # Create an expired session (is_active=False or expires_at in the past)
        sess_obj = AnonymousSession(
            session_token=expired_token,
            is_active=False,  # Deactivated
            last_activity_at=now_utc - timedelta(days=10),
            expires_at=now_utc - timedelta(days=3)
        )
        session.add(sess_obj)
        await session.commit()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get(
            "/api/v1/conversations",
            headers={"X-Session-Token": expired_token}
        )
        assert res.status_code == 401


@pytest.mark.asyncio
async def test_sec_6_forged_session_token():
    """Verify arbitrary forged session token cannot view any conversations."""
    forged_token = "admin_super_user_forged_bearer_xyz"
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get(
            "/api/v1/conversations",
            headers={"X-Session-Token": forged_token}
        )
        assert res.status_code == 401


@pytest.mark.asyncio
async def test_sec_7_unauthorized_admin_access():
    """Verify administrative dashboard and endpoints return 401 without Bearer token."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. No Authorization header
        r1 = await client.get("/api/v1/admin/dashboard")
        assert r1.status_code == 401

        # 2. Fake Bearer token
        r2 = await client.get(
            "/api/v1/admin/dashboard",
            headers={"Authorization": "Bearer fake_invalid_jwt_token_12345"}
        )
        assert r2.status_code == 401


@pytest.mark.asyncio
async def test_sec_8_unauthorized_administrative_api_operations():
    """Verify unauthorized mutation operations on admin endpoints return 401."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Try to create a knowledge record without admin authorization
        r1 = await client.post(
            "/api/v1/admin/knowledge-records",
            json={
                "data_type": "faq",
                "category_slug": "academics",
                "title": "Malicious Injected FAQ",
                "canonical_answer": "Injected false data",
                "source_evidence": "Hacker",
                "content_owner": "Hacker",
                "verified": True
            }
        )
        assert r1.status_code == 401

        # Try to trigger search reindexing without admin authorization
        r2 = await client.post("/api/v1/admin/reindex")
        assert r2.status_code == 401
