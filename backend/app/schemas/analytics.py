from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class DashboardMetrics(BaseModel):
    total_approved_faqs: int
    pending_faqs: int
    total_documents: int
    pending_documents: int
    total_knowledge_records: int = 0
    sensitive_records_count: int = 0
    records_by_type: Dict[str, int] = {}
    total_queries: int
    low_confidence_queries: int
    unanswered_queries: int
    gemini_failures: int
    feedback_helpful_count: int
    feedback_unhelpful_count: int
    satisfaction_rate_percent: float


class QueryLogOut(BaseModel):
    id: str
    query_text: str
    normalized_query: str
    confidence_score: float
    retrieval_strategy: str
    gemini_status: str
    latency_ms: int
    created_at: datetime

