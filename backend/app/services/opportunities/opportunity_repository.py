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
