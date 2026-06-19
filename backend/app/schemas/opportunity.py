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

class OpportunityMatchResult(BaseModel):
    job_id: int
    job_title: str
    company_name: str
    location: str
    salary_text: str
    match_score: float  # 0 to 100%
    is_eligible: bool
    eligibility_notes: List[str] = Field(default_factory=list)
    matched_skills: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    recommended_courses: List[str] = Field(default_factory=list)
    apply_url: Optional[str] = None

class SkillGapAnalysis(BaseModel):
    target_role: str
    overall_fit_percentage: float
    acquired_skills: List[str]
    missing_skills: List[str]
    curriculum_gap_solutions: Dict[str, str]
    preparation_roadmap: List[str]

class PlacementDriveInfo(BaseModel):
    id: int
    company_name: str
    role_title: str
    drive_date: datetime
    venue: str
    eligible_branches: List[str]
    min_cgpa: float
    ctc_offered: str
    registration_deadline: datetime
    instructions: Optional[str] = None
    contact_email: Optional[str] = None

class JobSearchQuery(BaseModel):
    keyword: Optional[str] = None
    location: Optional[str] = None
    min_salary: Optional[float] = None
    work_mode: Optional[str] = None
    skills: Optional[List[str]] = None
    experience_max: Optional[float] = None
