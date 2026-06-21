"""
SQLAlchemy data models for CampusConnect Opportunity & Placement Intelligence.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, JSON, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class JobPosting(Base):
    __tablename__ = "job_postings"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    company_name = Column(String(255), nullable=False, index=True)
    location = Column(String(255), nullable=False, index=True)
    work_mode = Column(String(50), default="onsite")  # remote, hybrid, onsite
    min_salary = Column(Float, nullable=True)
    max_salary = Column(Float, nullable=True)
    salary_currency = Column(String(10), default="INR")
    salary_period = Column(String(20), default="annual")  # annual, monthly
    required_skills = Column(JSON, default=list)
    preferred_skills = Column(JSON, default=list)
    experience_min = Column(Float, default=0.0)
    experience_max = Column(Float, default=1.0)
    min_cgpa = Column(Float, default=6.0)
    allowed_branches = Column(JSON, default=lambda: ["ALL"])
    max_backlogs_allowed = Column(Integer, default=0)
    source = Column(String(50), default="Naukri")
    source_url = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    application_deadline = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class StudentProfileModel(Base):
    __tablename__ = "student_profiles"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String(50), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    cgpa = Column(Float, nullable=False)
    standing_backlogs = Column(Integer, default=0)
    branch = Column(String(100), default="B.Tech CSE")
    graduation_year = Column(Integer, default=2026)
    skills = Column(JSON, default=list)
    preferred_locations = Column(JSON, default=list)
    resume_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class OpportunityMatchModel(Base):
    __tablename__ = "opportunity_matches"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String(50), nullable=False, index=True)
    job_id = Column(Integer, ForeignKey("job_postings.id"), nullable=False)
    match_score = Column(Float, nullable=False)
    is_eligible = Column(Boolean, default=True)
    matched_skills = Column(JSON, default=list)
    missing_skills = Column(JSON, default=list)
    eligibility_notes = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)

    job = relationship("JobPosting")
