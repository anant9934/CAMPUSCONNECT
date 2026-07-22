"""
OpportunityResumeMatcher: Calculates semantic and keyword match scores between candidate skills and job requirements.
"""

from typing import List, Dict, Any, Tuple
from app.services.opportunities.job_normalizer import JobNormalizer

class OpportunityResumeMatcher:
    def __init__(self, normalizer: JobNormalizer = None):
        self.normalizer = normalizer or JobNormalizer()

    def match_skills(
        self,
        candidate_skills: List[str],
        required_skills: List[str]
    ) -> Dict[str, Any]:
        norm_cand = set(self.normalizer.resolve_skill_alias(s).lower() for s in candidate_skills)
        norm_req = set(self.normalizer.resolve_skill_alias(s).lower() for s in required_skills)

        matched = [s for s in required_skills if self.normalizer.resolve_skill_alias(s).lower() in norm_cand]
        missing = [s for s in required_skills if self.normalizer.resolve_skill_alias(s).lower() not in norm_cand]

        if not norm_req:
            score = 100.0
        else:
            score = round((len(matched) / len(norm_req)) * 100.0, 1)

        return {
            "match_score": score,
            "matched_skills": matched,
            "missing_skills": missing
        }

    def weighted_match_score(
        self,
        candidate_skills: List[str],
        mandatory_skills: List[str],
        optional_skills: List[str]
    ) -> float:
        res_mand = self.match_skills(candidate_skills, mandatory_skills)
        res_opt = self.match_skills(candidate_skills, optional_skills)
        score = (res_mand["match_score"] * 0.75) + (res_opt["match_score"] * 0.25)
        return round(score, 1)
