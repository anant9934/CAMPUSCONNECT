from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import QueryLog, Feedback, AdminUser
from app.api.v1.endpoints.admin_auth import get_current_admin
from app.schemas.analytics import QueryLogOut
from app.services.gemini_service import quota_manager

router = APIRouter()


@router.get("/admin/analytics")
async def get_analytics(
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve query logs, unanswered queries, and Gemini quota stats."""
    # 1. Recent query logs
    query_stmt = select(QueryLog).order_by(desc(QueryLog.created_at)).limit(50)
    query_res = await db.execute(query_stmt)
    queries = query_res.scalars().all()

    # 2. Unanswered/Low-confidence queries
    unanswered_stmt = (
        select(QueryLog)
        .where(QueryLog.confidence_score < 0.45)
        .order_by(desc(QueryLog.created_at))
        .limit(25)
    )
    unanswered_res = await db.execute(unanswered_stmt)
    unanswered = unanswered_res.scalars().all()

    # 3. Recent feedback
    fb_stmt = select(Feedback).order_by(desc(Feedback.created_at)).limit(25)
    fb_res = await db.execute(fb_stmt)
    feedbacks = fb_res.scalars().all()

    return {
        "gemini_quota": quota_manager.get_stats(),
        "recent_queries": [
            QueryLogOut(
                id=str(q.id),
                query_text=q.query_text,
                normalized_query=q.normalized_query,
                confidence_score=q.confidence_score,
                retrieval_strategy=q.retrieval_strategy,
                gemini_status=q.gemini_status,
                latency_ms=q.latency_ms,
                created_at=q.created_at,
            )
            for q in queries
        ],
        "unanswered_queries": [
            {
                "id": str(u.id),
                "query_text": u.query_text,
                "confidence_score": u.confidence_score,
                "gemini_status": u.gemini_status,
                "created_at": u.created_at,
            }
            for u in unanswered
        ],
        "feedback_logs": [
            {
                "id": str(f.id),
                "conversation_id": str(f.conversation_id),
                "message_id": str(f.message_id),
                "rating": f.rating,
                "comment": f.comment,
                "created_at": f.created_at,
            }
            for f in feedbacks
        ],
    }

