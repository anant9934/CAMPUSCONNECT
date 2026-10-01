"""
NaukriOpportunityTool: Agent tool allowing CampusConnect agents to search opportunities.
"""

from typing import Dict, Any, List, Optional
from app.services.opportunities.opportunity_repository import OpportunityRepository

repo = OpportunityRepository()
repo.load_seed_corpus("data/naukri_corpus/job_postings_tech_punjab_delhi.jsonl")

def search_opportunities_tool(keyword: Optional[str] = None, location: Optional[str] = None) -> List[Dict[str, Any]]:
    results = repo.search_jobs(keyword=keyword, location=location)
    return results[:5]

def analyze_skill_gap_tool(student_skills: List[str], target_role: str) -> Dict[str, Any]:
    jobs = repo.search_jobs(keyword=target_role)
    req_skills = []
    for j in jobs:
        req_skills.extend(j.get("required_skills", []))
    unique_req = list(dict.fromkeys(req_skills))
    return repo.matcher.analyze_skill_gap(student_skills, unique_req)
