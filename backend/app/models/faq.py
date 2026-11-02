from sqlalchemy import Column, String, Boolean, Integer, Text, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin, generate_uuid, get_utc_now


class FAQ(Base, TimestampMixin):
    __tablename__ = "faqs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    category_id = Column(String(36), ForeignKey("categories.id", ondelete="CASCADE"), nullable=False, index=True)
    canonical_question = Column(Text, nullable=False, index=True)
    alternative_questions = Column(JSON, default=list, nullable=False)  # List of string paraphrases
    answer = Column(Text, nullable=False)
    keywords = Column(JSON, default=list, nullable=False)  # List of domain keywords
    source_url = Column(String(500), nullable=True)
    source_title = Column(String(255), nullable=True)
    source_type = Column(String(50), default="Official Portal", nullable=False)  # e.g., 'Portal', 'Handbook', 'Notice'
    last_reviewed = Column(DateTime, default=get_utc_now, nullable=False)
    approval_status = Column(String(30), default="approved", nullable=False, index=True)  # 'approved', 'pending', 'rejected'
    is_approved = Column(Boolean, default=True, nullable=False, index=True)
    content_owner = Column(String(100), default="Division of Student Affairs", nullable=False)
    version = Column(Integer, default=1, nullable=False)

    category = relationship("Category", back_populates="faqs")
    sources = relationship("FAQSource", back_populates="faq", cascade="all, delete-orphan")


class FAQSource(Base, TimestampMixin):
    __tablename__ = "faq_sources"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    faq_id = Column(String(36), ForeignKey("faqs.id", ondelete="CASCADE"), nullable=False, index=True)
    url = Column(String(500), nullable=False)
    title = Column(String(255), nullable=False)
    source_type = Column(String(50), default="official_webpage", nullable=False)
    verified = Column(Boolean, default=True, nullable=False)
    last_verified_at = Column(DateTime, default=get_utc_now, nullable=False)

    faq = relationship("FAQ", back_populates="sources")

