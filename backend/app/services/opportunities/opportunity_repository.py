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
