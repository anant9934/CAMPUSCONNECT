from sqlalchemy import Column, String, Boolean, Integer, Float, Text, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin, generate_uuid, get_utc_now


class StudentProfile(Base, TimestampMixin):
    """
    Personalized student profile for CampusConnect Portal.
    Strict privacy boundary: Personal academic records (CGPA, marks, attendance)
    are NOT fabricated; they remain strictly behind authorized UMS handoff.
    """
    __tablename__ = "student_profiles"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("anonymous_sessions.id", ondelete="CASCADE"), nullable=True, index=True)
    full_name = Column(String(150), default="Student", nullable=False)
    registration_number = Column(String(50), nullable=True)
    school = Column(String(200), default="School of Computer Science & Engineering", nullable=False)
    department = Column(String(200), default="Department of Computer Science & Engineering", nullable=False)
    programme = Column(String(200), default="B.Tech Computer Science & Engineering", nullable=False)
    specialisation = Column(String(200), default="Artificial Intelligence & Machine Learning", nullable=False)
    current_semester = Column(Integer, default=6, nullable=False)
    academic_session = Column(String(50), default="2025-2026", nullable=False)
    is_connected = Column(Boolean, default=False, nullable=False)


class StudentOpportunity(Base, TimestampMixin):
    """
    Verified campus opportunities: placements, internships, hackathons, research grants.
    """
    __tablename__ = "student_opportunities"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False, index=True)
    opportunity_type = Column(String(50), nullable=False, index=True)  # placement, internship, hackathon, competition, research, club
    organizer = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    eligibility = Column(String(300), nullable=False)
    deadline = Column(String(100), nullable=True)
    stipend_or_reward = Column(String(150), nullable=True)
    target_programmes = Column(JSON, default=list, nullable=False)
    application_link = Column(String(500), nullable=False)
    is_verified = Column(Boolean, default=True, nullable=False)


class CampusEvent(Base, TimestampMixin):
    """
    Verified university events and academic calendar deadlines.
    """
    __tablename__ = "campus_events"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False, index=True)
    category = Column(String(50), nullable=False, index=True)  # academic, cultural, technical, placement, sports
    venue = Column(String(200), nullable=False)
    event_date = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    organizing_department = Column(String(200), nullable=False)
    registration_link = Column(String(500), nullable=True)
    is_verified = Column(Boolean, default=True, nullable=False)


class SavedLocation(Base, TimestampMixin):
    """
    Student-bookmarked campus locations, offices, or labs.
    """
    __tablename__ = "saved_locations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("anonymous_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    place_id = Column(String(100), nullable=False)
    name = Column(String(200), nullable=False)
    building_block = Column(String(100), nullable=False)
    room_number = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)


class LLMUsageLog(Base, TimestampMixin):
    """
    Auditable log of LLM token usage, latencies, and circuit breaker health.
    """
    __tablename__ = "llm_usage_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), nullable=True, index=True)
    conversation_id = Column(String(36), nullable=True, index=True)
    model_name = Column(String(100), nullable=False)
    prompt_tokens = Column(Integer, default=0, nullable=False)
    completion_tokens = Column(Integer, default=0, nullable=False)
    total_tokens = Column(Integer, default=0, nullable=False)
    latency_ms = Column(Integer, default=0, nullable=False)
    status = Column(String(50), default="success", nullable=False)  # success, rate_limit, timeout, error, fallback
    error_message = Column(Text, nullable=True)
