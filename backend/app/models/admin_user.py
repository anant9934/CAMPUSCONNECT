from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin, generate_uuid


class AdminUser(Base, TimestampMixin):
    __tablename__ = "admin_users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    role = Column(String(30), default="admin", nullable=False)  # 'superadmin', 'admin', 'editor'
    is_active = Column(Boolean, default=True, nullable=False)

    audit_logs = relationship("AuditLog", back_populates="admin", cascade="all, delete-orphan")

