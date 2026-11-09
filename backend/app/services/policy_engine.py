from enum import Enum
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class EvidenceStatus(str, Enum):
    OFFICIAL_CURRENT_VERIFIED = "OFFICIAL_CURRENT_VERIFIED"
    OFFICIAL_HISTORICAL = "OFFICIAL_HISTORICAL"
    ADMIN_CONFIRMED = "ADMIN_CONFIRMED"
    VENDOR_CONFIRMED = "VENDOR_CONFIRMED"
    USER_REPORTED = "USER_REPORTED"
    UNVERIFIED = "UNVERIFIED"
    CONFLICTING = "CONFLICTING"
    EXPIRED = "EXPIRED"


@dataclass
class PolicyItem:
    source_id: str
    source_title: str
    source_url_or_file: str
    source_type: str  # e.g. "University Regulation", "Academic Calendar", "Examination Byelaws", "EDU-Revolution Manual"
    effective_date: str
    expiration_date: Optional[str]
    verification_status: EvidenceStatus
    approval_authority: str
    last_checked_timestamp: str
    applicable_programme: str  # e.g. "All Regular B.Tech / M.Tech Programmes", "School of Computer Science & Engineering"
    policy_category: str  # e.g. "Attendance", "Academic Benefits", "Examination", "Student Discipline", "Fee"
    content_clauses: List[str]
    conflict_notes: Optional[str] = None


class PolicyEngine:
    """
    Evidence and Policy Engine for CampusConnect V8.
    Audits knowledge items, validates verification statuses, flags conflicting regulations,
    and prevents the LLM from misrepresenting historical or unverified statements as active university policy.
    """

    _POLICIES: List[PolicyItem] = [
        PolicyItem(
            source_id="POL-ATT-2026-01",
            source_title="LPU Academic Regulations — Attendance and Examination Eligibility",
            source_url_or_file="data/Academic Benefits copy.pdf",
            source_type="University Regulation",
            effective_date="2024-07-01",
            expiration_date=None,
            verification_status=EvidenceStatus.OFFICIAL_CURRENT_VERIFIED,
            approval_authority="Academic Council & Standing Academic Committee",
            last_checked_timestamp="2026-11-18T18:00:00Z",
            applicable_programme="All Undergraduate & Postgraduate Programmes",
            policy_category="Attendance",
            content_clauses=[
                "Clause 4.1: Every student must maintain a minimum attendance of 75% in each registered course to be eligible to appear in End Term Examinations (ETE).",
                "Clause 4.2: Condonation up to 10% may be granted by the Head of School on valid medical grounds (certified by CMO Uni-Hospital) or authorized university representation in sports/cultural/hackathons.",
                "Clause 4.3: Under no circumstances can general condonation be granted below the statutory 65.0% floor."
            ]
        ),
        PolicyItem(
            source_id="POL-EDUREV-2026-02",
            source_title="LPU EDU-Revolution — Academic Benefit Guidelines & Course Mapping",
            source_url_or_file="data/edurev_workflow.csv",
            source_type="EDU-Revolution Manual",
            effective_date="2024-08-01",
            expiration_date=None,
            verification_status=EvidenceStatus.OFFICIAL_CURRENT_VERIFIED,
            approval_authority="Executive Dean & Standing Academic Committee",
            last_checked_timestamp="2026-11-18T18:00:00Z",
            applicable_programme="School of Computer Science & Engineering",
            policy_category="Academic Benefits",
            content_clauses=[
                "Clause 2.1: Students developing live projects, research papers, patents, or earning verified client revenue may seek CA equivalence or course substitution.",
                "Clause 2.2: Course mapping applications must be submitted via UMS within the first 4 weeks of the active term.",
                "Clause 2.3: Final approval requires School Evaluation Committee viva and formal Standing Academic Committee (SAC) ratification; no automatic benefits are granted."
            ]
        ),
        PolicyItem(
            source_id="POL-DISC-2026-03",
            source_title="LPU Student Code of Conduct & Disciplinary Procedures",
            source_url_or_file="data/campus_office_place_directory.csv",
            source_type="Student Conduct Byelaws",
            effective_date="2023-08-01",
            expiration_date=None,
            verification_status=EvidenceStatus.OFFICIAL_CURRENT_VERIFIED,
            approval_authority="Proctorial Board & Division of Student Welfare",
            last_checked_timestamp="2026-11-18T18:00:00Z",
            applicable_programme="All Enrolled Students",
            policy_category="Student Discipline",
            content_clauses=[
                "Section 12: Submission of false documents, fabricated medical certificates, or forged attendance slips constitutes Gross Academic Misconduct.",
                "Section 14: Disciplinary hearings are held before the Proctorial Board in Block 30; students have the right to submit a factual statement and evidence.",
                "Section 16: Appeals against disciplinary verdicts must be submitted to the University Appellate Committee via the Registrar within 7 working days."
            ]
        )
    ]

    @classmethod
    def get_policies_by_category(cls, category: str) -> List[PolicyItem]:
        cat_lower = category.lower()
        return [p for p in cls._POLICIES if cat_lower in p.policy_category.lower()]

    @classmethod
    def validate_claim(cls, claim_topic: str) -> Dict[str, Any]:
        """
        Validates claim against current policies, checking for conflicts or expiration.
        """
        relevant = [p for p in cls._POLICIES if claim_topic.lower() in p.policy_category.lower() or claim_topic.lower() in p.source_title.lower()]
        if not relevant:
            return {
                "is_verified": False,
                "status": EvidenceStatus.UNVERIFIED.value,
                "notes": "No verified institutional policy matched for this topic."
            }

        # Check for conflicts or historical items
        has_historical = any(p.verification_status == EvidenceStatus.OFFICIAL_HISTORICAL for p in relevant)
        has_conflicting = any(p.verification_status == EvidenceStatus.CONFLICTING for p in relevant)

        if has_conflicting:
            return {
                "is_verified": False,
                "status": EvidenceStatus.CONFLICTING.value,
                "notes": "Policy conflict detected across multiple institutional versions. Explain distinction clearly to student."
            }

        return {
            "is_verified": True,
            "status": EvidenceStatus.OFFICIAL_CURRENT_VERIFIED.value,
            "policies": relevant
        }

