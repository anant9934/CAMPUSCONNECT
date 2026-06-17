"""
Pydantic schemas for CampusConnect Opportunity & Placement Intelligence.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class JobPostingBase(BaseModel):
    title: str
    company_name: str
    location: str
    work_mode: str = "onsite"
    min_salary: Optional[float] = None
    max_salary: Optional[float] = None
    salary_currency: str = "INR"
    salary_period: str = "annual"
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    experience_min: float = 0.0
    experience_max: float = 1.0
    min_cgpa: float = 6.0
    allowed_branches: List[str] = Field(default_factory=lambda: ["ALL"])
    max_backlogs_allowed: int = 0
    source: str = "Naukri"
    source_url: Optional[str] = None
    description: Optional[str] = None
    application_deadline: Optional[datetime] = None
    is_active: bool = True

class JobPostingCreate(JobPostingBase):
    pass

class JobPostingResponse(JobPostingBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class StudentProfile(BaseModel):
    student_id: str
    full_name: str
    cgpa: float
    standing_backlogs: int = 0
    branch: str = "B.Tech CSE"
    graduation_year: int = 2026
    skills: List[str] = Field(default_factory=list)
    preferred_locations: List[str] = Field(default_factory=list)
    resume_summary: Optional[str] = None
