"""
OpportunityRepository: In-memory and SQLite repository for job postings and matching.
"""

from typing import List, Optional, Dict, Any
from app.schemas.opportunity import JobPostingBase, OpportunityMatchResult
from app.services.opportunities.job_normalizer import JobNormalizer
from app.services.opportunities.eligibility_evaluator import EligibilityEvaluator
from app.services.opportunities.resume_matcher import OpportunityResumeMatcher

class OpportunityRepository:
    def __init__(self):
        self.jobs: List[Dict[str, Any]] = []
        self.normalizer = JobNormalizer()
        self.eligibility = EligibilityEvaluator()
        self.matcher = OpportunityResumeMatcher(self.normalizer)

    def add_job(self, job: Dict[str, Any]) -> None:
        # Deduplicate by company and title
        key = f"{job['company_name'].lower()}:{job['title'].lower()}"
        if not any(f"{j['company_name'].lower()}:{j['title'].lower()}" == key for j in self.jobs):
            self.jobs.append(job)

    def search_jobs(
        self,
        keyword: Optional[str] = None,
        location: Optional[str] = None,
        min_salary: Optional[float] = None,
        skills: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        results = self.jobs
        if keyword:
            kw = keyword.lower()
            results = [j for j in results if kw in j["title"].lower() or kw in j["company_name"].lower()]
        if location:
            loc = location.lower()
            results = [j for j in results if loc in j["location"].lower() or loc in self.normalizer.normalize_location(j["location"]).lower()]
        if min_salary:
            results = [j for j in results if (j.get("min_salary") or 0) >= min_salary]
        return results
