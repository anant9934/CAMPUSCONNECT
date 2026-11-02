from sqlalchemy import Column, String, Boolean, Integer, Float, Text, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin, generate_uuid, get_utc_now


class AnonymousSession(Base, TimestampMixin):
    __tablename__ = "anonymous_sessions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_token = Column(String(64), unique=True, index=True, nullable=False)
    client_ip = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    last_activity_at = Column(DateTime, default=get_utc_now, nullable=False)
    expires_at = Column(DateTime, nullable=False)

    conversations = relationship("Conversation", back_populates="session", cascade="all, delete-orphan")
    query_logs = relationship("QueryLog", back_populates="session", cascade="all, delete-orphan")


class Conversation(Base, TimestampMixin):
    __tablename__ = "conversations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("anonymous_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), default="New Conversation", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    session = relationship("AnonymousSession", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan", order_by="Message.created_at")
    feedback = relationship("Feedback", back_populates="conversation", cascade="all, delete-orphan")


class Message(Base, TimestampMixin):
    __tablename__ = "messages"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    conversation_id = Column(String(36), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)
    thinking_steps = Column(JSON, default=list, nullable=False)  # Recorded 5-step thinking items
    citations = Column(JSON, default=list, nullable=False)  # Retrieved source citations
    confidence_score = Column(Float, nullable=True)
    latency_ms = Column(Integer, nullable=True)

    conversation = relationship("Conversation", back_populates="messages")
    feedback = relationship("Feedback", back_populates="message", cascade="all, delete-orphan")

