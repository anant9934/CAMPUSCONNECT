from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models import FAQ, KnowledgeDocument, QueryLog, Feedback, AdminUser, KnowledgeRecord
from app.api.v1.endpoints.admin_auth import get_current_admin
from app.schemas.analytics import DashboardMetrics

router = APIRouter()


@router.get("/admin/dashboard", response_model=DashboardMetrics)
async def get_dashboard_metrics(
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Calculates live operational metrics from real database events."""
    # 1. FAQs count
    approved_faqs_cnt = (await db.execute(
        select(func.count(FAQ.id)).where(FAQ.is_approved == True, FAQ.approval_status == "approved")
    )).scalar() or 0

    pending_faqs_cnt = (await db.execute(
        select(func.count(FAQ.id)).where(FAQ.approval_status == "pending")
    )).scalar() or 0

    # 2. Documents count
    total_docs = (await db.execute(select(func.count(KnowledgeDocument.id)))).scalar() or 0
    pending_docs = (await db.execute(
        select(func.count(KnowledgeDocument.id)).where(KnowledgeDocument.status == "pending")
    )).scalar() or 0

    # 3. Knowledge Records count (12 Types)
    total_kr = (await db.execute(select(func.count(KnowledgeRecord.id)))).scalar() or 0
    sensitive_kr = (await db.execute(
        select(func.count(KnowledgeRecord.id)).where(KnowledgeRecord.is_sensitive == True)
    )).scalar() or 0

    type_counts_res = await db.execute(
        select(KnowledgeRecord.record_type, func.count(KnowledgeRecord.id))
        .group_by(KnowledgeRecord.record_type)
    )
    records_by_type = dict(type_counts_res.all())

    # 4. Query logs count
    total_queries = (await db.execute(select(func.count(QueryLog.id)))).scalar() or 0

    low_conf_cnt = (await db.execute(
        select(func.count(QueryLog.id)).where(QueryLog.confidence_score < 0.45, QueryLog.confidence_score >= 0.30)
    )).scalar() or 0

    unanswered_cnt = (await db.execute(
        select(func.count(QueryLog.id)).where(QueryLog.confidence_score < 0.30)
    )).scalar() or 0

    gemini_failures_cnt = (await db.execute(
        select(func.count(QueryLog.id)).where(QueryLog.gemini_status.like("%error%"))
    )).scalar() or 0

    # 4. Feedback stats
    helpful_cnt = (await db.execute(
        select(func.count(Feedback.id)).where(Feedback.rating == "helpful")
    )).scalar() or 0

    unhelpful_cnt = (await db.execute(
        select(func.count(Feedback.id)).where(Feedback.rating == "unhelpful")
    )).scalar() or 0

    total_fb = helpful_cnt + unhelpful_cnt
    satisfaction_rate = (helpful_cnt / total_fb * 100.0) if total_fb > 0 else 100.0

    return DashboardMetrics(
        total_approved_faqs=approved_faqs_cnt,
        pending_faqs=pending_faqs_cnt,
        total_documents=total_docs,
        pending_documents=pending_docs,
        total_knowledge_records=total_kr,
        sensitive_records_count=sensitive_kr,
        records_by_type=records_by_type,
        total_queries=total_queries,
        low_confidence_queries=low_conf_cnt,
        unanswered_queries=unanswered_cnt,
        gemini_failures=gemini_failures_cnt,
        feedback_helpful_count=helpful_cnt,
        feedback_unhelpful_count=unhelpful_cnt,
        satisfaction_rate_percent=round(satisfaction_rate, 1),
    )

