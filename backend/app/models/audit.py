from sqlalchemy import Column, String, Integer, Float, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin, generate_uuid


class QueryLog(Base, TimestampMixin):
    __tablename__ = "query_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("anonymous_sessions.id", ondelete="SET NULL"), nullable=True, index=True)
    query_text = Column(Text, nullable=False)
    normalized_query = Column(Text, nullable=False)
    matched_faq_id = Column(String(36), nullable=True)
    matched_category_id = Column(String(36), nullable=True)
    confidence_score = Column(Float, default=0.0, nullable=False)
    retrieval_strategy = Column(String(50), default="hybrid", nullable=False)  # 'hybrid', 'exact_keyword', 'fallback'
    gemini_status = Column(String(50), default="success", nullable=False)  # 'success', 'fallback_faq', 'quota_exceeded', 'error'
    latency_ms = Column(Integer, default=0, nullable=False)

    session = relationship("AnonymousSession", back_populates="query_logs")


class AuditLog(Base, TimestampMixin):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    admin_id = Column(String(36), ForeignKey("admin_users.id", ondelete="SET NULL"), nullable=True, index=True)
    action = Column(String(100), nullable=False)  # 'create_faq', 'approve_faq', 'upload_doc', etc.
    resource_type = Column(String(50), nullable=False)  # 'faq', 'document', 'category', 'user'
    resource_id = Column(String(36), nullable=True)
    details = Column(JSON, default=dict, nullable=False)
    ip_address = Column(String(45), nullable=True)

    admin = relationship("AdminUser", back_populates="audit_logs")

