from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin, generate_uuid


class Feedback(Base, TimestampMixin):
    __tablename__ = "feedback"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    conversation_id = Column(String(36), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    message_id = Column(String(36), ForeignKey("messages.id", ondelete="CASCADE"), nullable=False, index=True)
    rating = Column(String(20), nullable=False)  # 'helpful', 'unhelpful'
    comment = Column(Text, nullable=True)
    session_id = Column(String(36), nullable=True)

    conversation = relationship("Conversation", back_populates="feedback")
    message = relationship("Message", back_populates="feedback")

