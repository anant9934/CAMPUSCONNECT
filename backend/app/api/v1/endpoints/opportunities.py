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
