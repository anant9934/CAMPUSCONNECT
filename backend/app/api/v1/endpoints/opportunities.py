"""
FastAPI Endpoints for CampusConnect Opportunities, Matches, and Placement Drives.
"""

from typing import List, Optional
from fastapi import APIRouter, Query
from app.schemas.opportunity import JobPostingResponse, OpportunityMatchResult, StudentProfile, PlacementDriveInfo
from app.services.opportunities.opportunity_repository import OpportunityRepository

router = APIRouter(prefix="/opportunities", tags=["opportunities"])
repo = OpportunityRepository()
repo.load_seed_corpus("data/naukri_corpus/job_postings_tech_punjab_delhi.jsonl")

@router.get("/search")
def search_opportunities(
    keyword: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    min_salary: Optional[float] = Query(None)
):
    return repo.search_jobs(keyword=keyword, location=location, min_salary=min_salary)

@router.post("/match", response_model=List[OpportunityMatchResult])
def match_student_opportunities(student: StudentProfile):
    return repo.match_student(
        student_skills=student.skills,
        student_cgpa=student.cgpa,
        student_backlogs=student.standing_backlogs,
        student_branch=student.branch
    )

@router.get("/taxonomy")
def get_skill_taxonomy():
    import json
    try:
        with open("data/naukri_corpus/lpu_skill_taxonomy_mapping.json", "r") as f:
            return json.load(f)
    except Exception:
        return {"status": "empty"}

@router.get("/drives")
def get_campus_drives():
    return [
        {"id": 1, "company_name": "Amazon AWS", "role_title": "Cloud Support Associate", "date": "2026-11-25T10:00:00", "venue": "Block 32 Auditorium", "ctc": "7-9.5 LPA", "min_cgpa": 7.0},
        {"id": 2, "company_name": "Infosys", "role_title": "Specialist Programmer", "date": "2026-12-02T09:30:00", "venue": "Shanti Devi Mittal Auditorium", "ctc": "6.5-9.5 LPA", "min_cgpa": 6.5}
    ]
