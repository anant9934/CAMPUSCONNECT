from sqlalchemy import Column, String, Boolean, Integer, Text, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin, generate_uuid


class KnowledgeDocument(Base, TimestampMixin):
    __tablename__ = "knowledge_documents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    category_id = Column(String(36), ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True)
    title = Column(String(255), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(BigInteger, default=0, nullable=False)
    mime_type = Column(String(100), default="text/plain", nullable=False)
    status = Column(String(30), default="pending", nullable=False, index=True)  # 'pending', 'approved', 'rejected'
    is_approved = Column(Boolean, default=False, nullable=False, index=True)
    total_chunks = Column(Integer, default=0, nullable=False)
    uploaded_by_id = Column(String(36), ForeignKey("admin_users.id", ondelete="SET NULL"), nullable=True)

    category = relationship("Category", back_populates="documents")
    chunks = relationship("KnowledgeChunk", back_populates="document", cascade="all, delete-orphan")


class KnowledgeChunk(Base, TimestampMixin):
    __tablename__ = "knowledge_chunks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    document_id = Column(String(36), ForeignKey("knowledge_documents.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    clean_text = Column(Text, nullable=False)
    page_number = Column(Integer, nullable=True)
    token_count = Column(Integer, default=0, nullable=False)

    document = relationship("KnowledgeDocument", back_populates="chunks")

