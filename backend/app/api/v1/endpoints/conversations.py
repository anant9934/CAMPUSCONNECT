from typing import List
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models import AnonymousSession, Conversation, Message
from app.schemas.session import ConversationSummary, ConversationDetail, MessageOut

router = APIRouter()


async def get_current_session(
    x_session_token: str = Header(..., alias="X-Session-Token"),
    db: AsyncSession = Depends(get_db)
) -> AnonymousSession:
    """Validate that the session token exists and is active."""
    stmt = select(AnonymousSession).where(
        AnonymousSession.session_token == x_session_token,
        AnonymousSession.is_active == True
    )
    result = await db.execute(stmt)
    sess = result.scalars().first()
    if not sess:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session token."
        )
    return sess


@router.get("/conversations", response_model=List[ConversationSummary])
async def list_conversations(
    session: AnonymousSession = Depends(get_current_session),
    db: AsyncSession = Depends(get_db)
):
    """List recent conversation threads for the active anonymous session."""
    stmt = (
        select(Conversation)
        .where(
            Conversation.session_id == session.id,
            Conversation.is_active == True
        )
        .order_by(Conversation.updated_at.desc())
    )
    res = await db.execute(stmt)
    conversations = res.scalars().all()

    summaries = []
    for c in conversations:
        # Count messages
        cnt_stmt = select(func.count(Message.id)).where(Message.conversation_id == c.id)
        cnt = (await db.execute(cnt_stmt)).scalar() or 0
        summaries.append(
            ConversationSummary(
                id=str(c.id),
                title=c.title,
                is_active=c.is_active,
                created_at=c.created_at,
                updated_at=c.updated_at,
                message_count=cnt
            )
        )
    return summaries


@router.get("/conversations/{id}", response_model=ConversationDetail)
async def get_conversation_detail(
    id: str,
    session: AnonymousSession = Depends(get_current_session),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve full message history for a specific conversation in the current session."""
    stmt = (
        select(Conversation)
        .options(selectinload(Conversation.messages))
        .where(
            Conversation.id == id,
            Conversation.session_id == session.id,
            Conversation.is_active == True
        )
    )
    res = await db.execute(stmt)
    conv = res.scalars().first()
    if not conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found or access denied."
        )

    messages_out = []
    for m in conv.messages:
        messages_out.append(
            MessageOut(
                id=str(m.id),
                conversation_id=str(m.conversation_id),
                role=m.role,
                content=m.content,
                thinking_steps=m.thinking_steps or [],
                citations=m.citations or [],
                confidence_score=m.confidence_score,
                created_at=m.created_at
            )
        )

    return ConversationDetail(
        id=str(conv.id),
        session_id=str(conv.session_id),
        title=conv.title,
        is_active=conv.is_active,
        created_at=conv.created_at,
        messages=messages_out
    )


class RenameConversationIn(BaseModel):
    title: str


@router.patch("/conversations/{id}")
async def rename_conversation(
    id: str,
    body: RenameConversationIn,
    session: AnonymousSession = Depends(get_current_session),
    db: AsyncSession = Depends(get_db)
):
    """Rename a conversation thread."""
    stmt = select(Conversation).where(
        Conversation.id == id,
        Conversation.session_id == session.id
    )
    res = await db.execute(stmt)
    conv = res.scalars().first()
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found.")

    new_title = body.title.strip()
    if not new_title:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Title cannot be empty.")

    conv.title = new_title[:255]
    await db.commit()
    return {"status": "success", "id": id, "title": conv.title}


@router.delete("/conversations/{id}")
async def delete_conversation(
    id: str,
    session: AnonymousSession = Depends(get_current_session),
    db: AsyncSession = Depends(get_db)
):
    """Delete a conversation thread within the current session."""
    stmt = select(Conversation).where(
        Conversation.id == id,
        Conversation.session_id == session.id
    )
    res = await db.execute(stmt)
    conv = res.scalars().first()
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found.")

    await db.delete(conv)
    await db.commit()
    return {"status": "success", "message": "Conversation deleted."}

