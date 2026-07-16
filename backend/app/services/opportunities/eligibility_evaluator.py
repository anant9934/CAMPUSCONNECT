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
