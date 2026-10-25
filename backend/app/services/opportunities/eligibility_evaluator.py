"""
EligibilityEvaluator: Validates candidate CGPA, backlogs, branch, and graduation batch.
"""

from typing import Dict, Any, List, Tuple

class EligibilityEvaluator:
    def __init__(self):
        pass

    def check_eligibility(
        self,
        student_cgpa: float,
        student_backlogs: int,
        student_branch: str,
        student_year: int,
        job_min_cgpa: float,
        job_max_backlogs: int,
        job_allowed_branches: List[str],
        eligible_years: List[int] = None
    ) -> Tuple[bool, List[str]]:
        reasons = []
        is_eligible = True

        if student_cgpa < job_min_cgpa:
            is_eligible = False
            reasons.append(f"CGPA {student_cgpa:.2f} is below minimum requirement of {job_min_cgpa:.2f}")

        if student_backlogs > job_max_backlogs:
            is_eligible = False
            reasons.append(f"Candidate has {student_backlogs} standing backlogs (maximum allowed: {job_max_backlogs})")

        if "ALL" not in job_allowed_branches and student_branch not in job_allowed_branches:
            is_eligible = False
            reasons.append(f"Branch {student_branch} not in allowed streams: {job_allowed_branches}")

        if eligible_years and student_year not in eligible_years:
            is_eligible = False
            reasons.append(f"Batch {student_year} not in eligible graduation years: {eligible_years}")

        return is_eligible, reasons

    def convert_percentage_to_cgpa(self, percentage: float) -> float:
        return round(percentage / 9.5, 2)

    def can_clear_backlog_before_drive(self, backlogs: int, months_until_drive: int) -> bool:
        return backlogs <= 1 and months_until_drive >= 3

    def normalize_branch_code(self, branch_str: str) -> str:
        b = branch_str.upper()
        if "CSE" in b or "COMPUTER SCIENCE" in b:
            return "B.Tech CSE"
        if "IT" in b or "INFORMATION TECH" in b:
            return "B.Tech IT"
        if "ECE" in b or "ELECTRONICS" in b:
            return "B.Tech ECE"
        return branch_str

    def check_diversity_hiring(self, job_criteria: Dict[str, Any], candidate_info: Dict[str, Any]) -> bool:
        target_gender = job_criteria.get("preferred_gender")
        if target_gender and candidate_info.get("gender") != target_gender:
            return False
        return True

    def composite_eligibility_score(self, cgpa: float, backlogs: int, branch_match: bool) -> float:
        score = 0.0
        score += min(cgpa / 10.0, 1.0) * 50.0
        score += 30.0 if backlogs == 0 else (15.0 if backlogs == 1 else 0.0)
        score += 20.0 if branch_match else 5.0
        return round(score, 1)

    def normalize_lateral_entry_cgpa(self, diploma_percentage: float, btech_cgpa: float) -> float:
        diploma_cgpa = diploma_percentage / 9.5
        return round((diploma_cgpa * 0.4) + (btech_cgpa * 0.6), 2)
