import uuid
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models import AnonymousSession
from app.schemas.session import SessionCreateRequest, SessionResponse

router = APIRouter()


@router.post("/sessions", response_model=SessionResponse)
async def create_anonymous_session(
    body: SessionCreateRequest,
    req: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate a new random anonymous session token for student interactions.
    Zero personal identity required.
    """
    now = datetime.now(timezone.utc)
    token = f"lpu_sess_{uuid.uuid4().hex}"
    client_ip = req.client.host if req.client else None
    user_agent = (body.user_agent or req.headers.get("user-agent", ""))[:500]

    session = AnonymousSession(
        session_token=token,
        client_ip=client_ip,
        user_agent=user_agent,
        is_active=True,
        last_activity_at=now,
        expires_at=now + timedelta(days=7),
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)

    return SessionResponse(
        session_token=session.session_token,
        expires_at=session.expires_at,
        is_active=session.is_active,
    )

