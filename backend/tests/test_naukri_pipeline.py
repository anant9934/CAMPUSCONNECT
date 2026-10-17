"""
Comprehensive test suite for CampusConnect Naukri & Career Intelligence Pipeline.
"""

import pytest
from app.services.opportunities.job_normalizer import JobNormalizer
from app.services.opportunities.eligibility_evaluator import EligibilityEvaluator
from app.services.opportunities.resume_matcher import OpportunityResumeMatcher
from app.services.opportunities.opportunity_repository import OpportunityRepository
from app.ml.training_config import TrainingConfig
from app.ml.evaluation_benchmark import EvaluationBenchmark

def test_job_normalizer_salary():
    norm = JobNormalizer()
    min_s, max_s, period = norm.parse_salary_inr("6 - 12 LPA")
    assert min_s == 600000.0
    assert max_s == 1200000.0
    assert period == "annual"

def test_job_normalizer_location():
    norm = JobNormalizer()
    assert norm.normalize_location("Mohali, Punjab") == "Punjab-Tricity"
    assert norm.normalize_location("Gurgaon, Haryana") == "Delhi-NCR"
    assert norm.normalize_location("Work From Home") == "Remote"

def test_eligibility_evaluator():
    evaluator = EligibilityEvaluator()
    is_elig, reasons = evaluator.check_eligibility(
        student_cgpa=8.2, student_backlogs=0, student_branch="B.Tech CSE", student_year=2026,
        job_min_cgpa=7.0, job_max_backlogs=0, job_allowed_branches=["B.Tech CSE", "B.Tech IT"]
    )
    assert is_elig is True
    assert len(reasons) == 0

    # Failing on backlogs
    is_elig2, reasons2 = evaluator.check_eligibility(
        student_cgpa=8.2, student_backlogs=2, student_branch="B.Tech CSE", student_year=2026,
        job_min_cgpa=7.0, job_max_backlogs=0, job_allowed_branches=["ALL"]
    )
    assert is_elig2 is False
    assert any("backlog" in r.lower() for r in reasons2)

def test_resume_matcher_and_repository():
    repo = OpportunityRepository()
    repo.load_seed_corpus("data/naukri_corpus/job_postings_tech_punjab_delhi.jsonl")
    assert len(repo.jobs) >= 5

    # Match student
    matches = repo.match_student(
        student_skills=["Python", "SQL", "FastAPI", "React"],
        student_cgpa=8.0,
        student_backlogs=0,
        student_branch="B.Tech CSE"
    )
    assert len(matches) > 0
    top_match = matches[0]
    assert top_match.is_eligible is True
    assert top_match.match_score > 0
