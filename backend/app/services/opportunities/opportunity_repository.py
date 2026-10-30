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

    def match_student(
        self,
        student_skills: List[str],
        student_cgpa: float,
        student_backlogs: int = 0,
        student_branch: str = "B.Tech CSE",
        limit: int = 10
    ) -> List[OpportunityMatchResult]:
        matches = []
        for j in self.jobs:
            match_res = self.matcher.match_skills(student_skills, j.get("required_skills", []))
            is_elig, reasons = self.eligibility.check_eligibility(
                student_cgpa, student_backlogs, student_branch, 2026,
                j.get("min_cgpa", 6.0), j.get("max_backlogs_allowed", 0), j.get("allowed_branches", ["ALL"])
            )
            min_s = j.get("min_salary")
            max_s = j.get("max_salary")
            sal_text = f"₹{int(min_s/100000)} - {int(max_s/100000)} LPA" if min_s and max_s else "Best in Industry"
            matches.append(OpportunityMatchResult(
                job_id=j.get("id", 1),
                job_title=j["title"],
                company_name=j["company_name"],
                location=j["location"],
                salary_text=sal_text,
                match_score=match_res["match_score"],
                is_eligible=is_elig,
                eligibility_notes=reasons,
                matched_skills=match_res["matched_skills"],
                missing_skills=match_res["missing_skills"],
                recommended_courses=[],
                apply_url=j.get("source_url")
            ))
        matches.sort(key=lambda m: (m.is_eligible, m.match_score), reverse=True)
        return matches[:limit]

    def load_seed_corpus(self, filepath: str) -> int:
        import json
        count = 0
        try:
            with open(filepath, "r") as f:
                for line in f:
                    if line.strip():
                        self.add_job(json.loads(line))
                        count += 1
        except Exception:
            pass
        return count

    def get_remote_high_stipend_jobs(self, min_stipend: float = 30000.0) -> List[Dict[str, Any]]:
        annual_min = min_stipend * 12.0
        return [j for j in self.jobs if j.get("work_mode") == "remote" and (j.get("min_salary") or 0) >= annual_min]
