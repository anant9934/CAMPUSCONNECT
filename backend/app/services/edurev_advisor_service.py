import csv
import logging
import os
import re
from typing import List, Dict, Any, Optional

from app.schemas.ums import AcademicBenefitAssessmentCard

logger = logging.getLogger(__name__)


class AcademicBenefitAdvisor:
    """
    EDU-Revolution & Academic Benefit Advisor for Lovely Professional University.
    Analyzes student project outputs, maps them to the 9 institutional benefit categories,
    outlines required evidence, and enforces strict academic policy caveats
    (no automatic grades/attendance waivers, SCRGM revenue distinction).
    """

    _categories: Optional[List[Dict[str, Any]]] = None

    @classmethod
    def _load_categories(cls) -> List[Dict[str, Any]]:
        if cls._categories is not None:
            return cls._categories

        candidates = [
            os.path.join(os.getcwd(), "data", "edurev_project_academic_benefit_mapping.csv"),
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "edurev_project_academic_benefit_mapping.csv"),
        ]
        file_path = None
        for c in candidates:
            if os.path.exists(c):
                file_path = c
                break

        cats = []
        if file_path:
            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    cats.append({
                        "category_id": row.get("category_id", ""),
                        "category_name": row.get("category_name", ""),
                        "portal_stage_name": row.get("portal_stage_name", "Select Category"),
                        "output_criteria": row.get("output_criteria", ""),
                        "potential_eligible_benefits": row.get("potential_eligible_benefits") or row.get("eligible_academic_benefits", ""),
                        "eligible_academic_benefits": row.get("potential_eligible_benefits") or row.get("eligible_academic_benefits", ""),
                        "required_evidence": row.get("required_evidence", ""),
                        "course_mapping_window": row.get("course_mapping_window", "First 4 weeks of active academic semester"),
                        "approval_prerequisite": row.get("approval_prerequisite", "School Evaluation Committee viva & Standing Academic Committee ratification"),
                        "limitations_and_exclusions": row.get("limitations_and_exclusions", ""),
                        "submission_channel": row.get("submission_channel", "UMS > RMS > Edu-Revolution: Be the change"),
                        "support_location": row.get("support_location", "Block 27 Room 102 (Query & Assistance Zone)"),
                        "evidence_status": row.get("evidence_status", "OFFICIAL_CURRENT_VERIFIED"),
                        "provenance_notes": row.get("provenance_notes", "")
                    })
        cls._categories = cats
        return cats

    @classmethod
    def assess_project(cls, query: str) -> Optional[AcademicBenefitAssessmentCard]:
        """
        Assesses a student's project, achievement, or credential against the 9 EDU-Revolution categories.
        """
        cats = cls._load_categories()
        if not cats:
            return None

        q = query.lower().strip()

        # Check if query touches upon EDU-Rev / project academic benefits
        edurev_triggers = [
            "edu-revolution", "edurev", "academic benefit", "project benefit",
            "built an ai", "built a project", "made an app", "github project",
            "submit this project", "submit my project", "where do i submit this project",
            "certification benefit", "mooc benefit", "hackathon benefit", "startup benefit",
            "attendance benefit", "attendance benefits", "ca exemption", "continuous assessment",
            "duty leave", "attendance relaxation", "earn your fee"
        ]
        has_trigger = any(t in q for t in edurev_triggers)
        if not has_trigger:
            return None

        # Determine best category
        # CAT-01: Certifications
        if any(w in q for w in ["certification", "aws", "google cloud", "cisco", "red hat", "azure", "prior learning"]):
            target_cat_id = "CAT-01"
        # CAT-03: MOOCs
        elif any(w in q for w in ["mooc", "nptel", "coursera", "edx", "online course"]):
            target_cat_id = "CAT-03"
        # CAT-04: Hackathons & Competitions
        elif any(w in q for w in ["hackathon", "sih", "smart india hackathon", "coding competition", "icpc"]):
            target_cat_id = "CAT-04"
        # CAT-05: Startup & Enterprise
        elif any(w in q for w in ["startup", "incubation", "dpiit", "pvt ltd", "llp", "company"]):
            target_cat_id = "CAT-05"
        # CAT-06: Competitive exams & Exam Attendance Benefits
        elif any(w in q for w in ["gate", "cat exam", "gre", "upsc", "competitive exam", "recruitment exam"]):
            target_cat_id = "CAT-06"
        # CAT-07: Consultancy
        elif any(w in q for w in ["consultancy", "sponsored project", "corporate client"]):
            target_cat_id = "CAT-07"
        # CAT-08: Social impact
        elif any(w in q for w in ["social impact", "ngo", "community", "sdg", "rural"]):
            target_cat_id = "CAT-08"
        # CAT-09: Freelancing
        elif any(w in q for w in ["freelance", "upwork", "fiverr", "client project", "commercialization"]):
            target_cat_id = "CAT-09"
        # CA Exemption via projects -> CAT-02
        elif any(w in q for w in ["ca exemption", "continuous assessment", "ca benefit"]):
            target_cat_id = "CAT-02"
        # Attendance Benefit default via competitive exams or projects
        elif any(w in q for w in ["attendance benefit", "attendance relaxation", "duty leave"]):
            target_cat_id = "CAT-06" if any(w in q for w in ["exam", "gate", "cat", "upsc"]) else "CAT-02"
        # Default for AI / software / general projects -> CAT-02
        else:
            target_cat_id = "CAT-02"

        matched = next((c for c in cats if c["category_id"] == target_cat_id), cats[1])

        # Parse required evidence list
        raw_evidence = matched["required_evidence"]
        evidence_list = [e.strip() for e in raw_evidence.split(",") if e.strip()]

        # Compute missing evidence based on user query contents
        missing_evidence = []
        if not any(w in q for w in ["github", "git", "repo", "repository"]):
            if target_cat_id in ("CAT-02", "CAT-04", "CAT-07", "CAT-09"):
                missing_evidence.append("Public GitHub repository link with full commit history")

        if not any(w in q for w in ["live", "demo", "url", "deployed", "app link", "apk"]):
            if target_cat_id in ("CAT-02", "CAT-04", "CAT-05", "CAT-07", "CAT-09"):
                missing_evidence.append("Live working demo / deployment link for expert committee evaluation")

        if not any(w in q for w in ["architecture", "pdf", "report", "documentation", "doc"]):
            missing_evidence.append("Comprehensive technical architecture specification (PDF)")

        if not any(w in q for w in ["mentor", "faculty", "signed", "mapping form"]):
            missing_evidence.append("Faculty Mentor Course Mapping Endorsement Form (First 4 weeks of term)")

        # Parse limitations
        raw_limits = matched["limitations_and_exclusions"]
        limitations_list = [l.strip() for l in raw_limits.split(";") if l.strip()]

        return AcademicBenefitAssessmentCard(
            category_id=matched["category_id"],
            category_name=matched["category_name"],
            portal_stage_name=matched.get("portal_stage_name", "Select Category"),
            matched_criteria=matched["output_criteria"],
            eligible_academic_benefits=matched.get("potential_eligible_benefits") or matched.get("eligible_academic_benefits", ""),
            missing_evidence=missing_evidence,
            evidence_checklist=evidence_list,
            technical_originality_check="Must be student's original engineering output; tutorial clones or plagiarized submissions disqualified.",
            limitations_and_caveats=limitations_list,
            course_mapping_window=matched.get("course_mapping_window", "First 4 weeks of active academic semester"),
            approval_prerequisite=matched.get("approval_prerequisite", "School Evaluation Committee viva & Standing Academic Committee ratification"),
            submission_route="UMS > Relationship Management System (RMS) > Edu-Revolution: Be the change > Apply for EDU Revolution",
            physical_helpdesk="Block 27 Room 102 (Query & Assistance Zone)",
            guarantee_disclaimer="Benefits require Standing Academic Committee approval and active term course mapping. No automatic grades, marks, or attendance waivers are guaranteed.",
            scrgm_distinction="Student-Centric Revenue Generation Model (SCRGM) is a commercial revenue framework and does NOT convert money/sales into academic marks or credits.",
            eligibility_vs_approval_notice="POTENTIAL ELIGIBILITY ONLY: Assessment indicates preliminary alignment. Formal benefit approval requires syllabus matching with your course instructor in the first 4 weeks, demonstration before the School Evaluation Committee, and ratification by the Standing Academic Committee. No marks, grades, or attendance dispensations are guaranteed without formal SAC ratification.",
            evidence_status="OFFICIAL_CURRENT_VERIFIED"
        )

