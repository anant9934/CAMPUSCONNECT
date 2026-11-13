from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models import Feedback, Message, Conversation
from app.schemas.feedback import FeedbackCreate, FeedbackOut

router = APIRouter()


@router.post("/feedback", response_model=FeedbackOut)
async def submit_feedback(
    body: FeedbackCreate,
    db: AsyncSession = Depends(get_db)
):
    """Submit student rating (helpful / unhelpful) and optional comment for a response."""
    msg_stmt = select(Message).where(Message.id == body.message_id)
    msg_res = await db.execute(msg_stmt)
    msg = msg_res.scalars().first()
    if not msg:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found.")

    feedback = Feedback(
        conversation_id=body.conversation_id,
        message_id=body.message_id,
        rating=body.rating,
        comment=body.comment,
        session_id=body.session_token,
    )
    db.add(feedback)
    await db.commit()
    await db.refresh(feedback)

    return FeedbackOut(
        id=str(feedback.id),
        conversation_id=str(feedback.conversation_id),
        message_id=str(feedback.message_id),
        rating=feedback.rating,
        comment=feedback.comment,
    )

