import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class BenefitVector:
    benefit_name: str
    applicable_policy: str
    eligibility_conditions: List[str]
    evidence_required: List[str]
    evaluation_method: str
    max_benefit_documented: str
    approval_authority: str
    application_route: str
    status: str = "POTENTIAL_ELIGIBLE"  # POTENTIAL_ELIGIBLE, REQUIRES_CLARIFICATION, INELIGIBLE


@dataclass
class ProjectBenefitComprehensiveReport:
    project_summary: str
    matched_category: str
    category_id: str
    benefit_vectors: List[BenefitVector]
    missing_information_to_ask: List[str]
    technical_originality_rule: str
    disclaimer_notice: str
    deadlines_and_helpdesk: Dict[str, str]


class ProjectBenefitService:
    """
    Project-to-Benefit Intelligence Engine for CampusConnect V8.
    Automatically evaluates projects against 7 potential university benefit tracks:
    1. EDU-Revolution Category Mapping
    2. Revenue Generation / Commercialization (SCRGM)
    3. Continuous Assessment (CA) Equivalence
    4. Course Equivalence / Credit Transfer
    5. Grade Upgradation (Research / Patents / High-Tier Hackathons)
    6. Attendance Benefit / Duty Leave
    7. Recognition of Prior Learning (RPL) / Industry Certifications
    """

    @classmethod
    def evaluate_project(
        cls,
        query: str,
        project_details: Optional[Dict[str, Any]] = None
    ) -> ProjectBenefitComprehensiveReport:
        q = query.lower()
        details = project_details or {}

        # 1. Detect domain and project type
        is_ai_ml = any(k in q for k in ["ai", "machine learning", "deep learning", "llm", "nlp", "computer vision", "neural"])
        is_cyber = any(k in q for k in ["cyber", "security", "penetration", "soc", "crypto", "malware", "vulnerability"])
        is_research = any(k in q for k in ["research paper", "scopus", "sci", "ieee", "springer", "journal", "conference paper"])
        is_patent = any(k in q for k in ["patent", "ipr", "provisional patent", "intellectual property", "patent application"])
        is_startup_rev = any(k in q for k in ["startup", "revenue", "client", "gst", "freelance", "earning", "stipend", "commercial"])
        is_hackathon = any(k in q for k in ["hackathon", "sih", "smart india", "devfolio", "competition", "winner", "runner up"])
        is_internship = any(k in q for k in ["internship", "intern", "company", "offer letter", "stipend"])

        # 2. Determine Primary EDU-Rev Category
        if is_research:
            cat_id = "CAT-01-RES"
            cat_name = "Category 1: Research Publications & Academic Innovations"
        elif is_patent:
            cat_id = "CAT-03-IPR"
            cat_name = "Category 3: Intellectual Property & Patents"
        elif is_internship:
            cat_id = "CAT-07-IND"
            cat_name = "Category 7: Industry Projects & Live Internships"
        elif is_startup_rev or "revenue" in q:
            cat_id = "CAT-05-SCRGM"
            cat_name = "Category 5: Student-Centric Revenue Generation & Enterprise"
        elif is_hackathon:
            cat_id = "CAT-04-HACK"
            cat_name = "Category 4: Hackathons & Prestigious Competitions"
        else:
            cat_id = "CAT-02-LIVE"
            cat_name = "Category 2: Live Engineering & Software Projects"

        # 3. Build Multi-Benefit Vectors
        benefit_vectors: List[BenefitVector] = []

        # Vector 1: CA Equivalence (Always investigated for engineering projects)
        benefit_vectors.append(
            BenefitVector(
                benefit_name="Continuous Assessment (CA) Equivalence",
                applicable_policy="LPU EDU-Revolution Policy — CA Waiver & Project Substitution Clause",
                eligibility_conditions=[
                    "Project syllabus and deliverables must map to specific Course Outcomes (COs) of an active term theoretical/practical course.",
                    "Endorsement from respective Course Instructor and Faculty Mentor secured within the first 4 weeks of the term.",
                    "Working code demonstration before the Department Evaluation Committee."
                ],
                evidence_required=[
                    "Public GitHub/GitLab repository with full commit history",
                    "Live working deployment / testable application URL",
                    "Technical Architecture & System Design Specification (PDF)",
                    "Signed Course Mapping Approval Form"
                ],
                evaluation_method="Mid-term progress viva + End-term technical demonstration by School Evaluation Committee.",
                max_benefit_documented="Up to 100% exemption from internal Continuous Assessment (CA) components for mapped courses.",
                approval_authority="School Evaluation Committee & Standing Academic Committee (SAC) ratification",
                application_route="UMS -> RMS -> Edu-Revolution: Be the change -> Apply for EDU Revolution"
            )
        )

        # Vector 2: Revenue Generation (SCRGM)
        benefit_vectors.append(
            BenefitVector(
                benefit_name="Commercial Revenue Generation (SCRGM / Startup)",
                applicable_policy="LPU Student-Centric Revenue Generation Model (SCRGM) Regulations",
                eligibility_conditions=[
                    "Project must generate legitimate commercial client revenue or contract payments.",
                    "Proof of genuine client engagements (invoices with GST, formal work orders, bank credit transactions).",
                    "Entity registered under LPU Incubation Center or recognized as student enterprise."
                ],
                evidence_required=[
                    "Bank account transaction statements reflecting received client payments",
                    "Valid GST/Tax invoices and client service agreement",
                    "Client appreciation/completion sign-off certificate",
                    "Registration certificate with LPU Startup School / Incubation Center"
                ],
                evaluation_method="Financial audit by University Incubation & Accounts Board + technical viva.",
                max_benefit_documented="Attendance relaxation during commercial launch phases + eligibility for university startup grants/seed funding.",
                approval_authority="University Incubation Council & Standing Academic Committee",
                application_route="UMS -> Startup & Incubation -> Revenue Generation Submission"
            )
        )

        # Vector 3: Grade Upgradation / Course Substitution
        if is_research or is_patent:
            benefit_vectors.append(
                BenefitVector(
                    benefit_name="Grade Upgradation & Academic Honor Credits",
                    applicable_policy="LPU Research Incentive and Patent Recognition Guidelines",
                    eligibility_conditions=[
                        "Publication in Scopus / Web of Science (SCI) indexed peer-reviewed journal or reputed conference.",
                        "LPU institutional affiliation must be listed as primary author affiliation.",
                        "For patents: Official Indian Patent Office / International publication receipt."
                    ],
                    evidence_required=[
                        "Published paper PDF with DOI and Scopus indexing verification link",
                        "Acceptance letter on official editorial letterhead",
                        "Patent filing receipt and published specification copy"
                    ],
                    evaluation_method="Peer audit by Central Research Committee (Division of Research & Development).",
                    max_benefit_documented="One letter grade enhancement in relevant department elective OR 4-credit course exemption.",
                    approval_authority="Standing Academic Committee (SAC) chaired by Executive Dean / DRD",
                    application_route="UMS -> Research & Publications -> Submit Research Output"
                )
            )
        else:
            benefit_vectors.append(
                BenefitVector(
                    benefit_name="Elective Course Equivalence / Credit Substitution",
                    applicable_policy="LPU Curriculum Flexibility & Course Exemption Policy",
                    eligibility_conditions=[
                        "Substantial engineering scope matching 3-credit or 4-credit departmental elective.",
                        "Minimum student CGPA >= 6.5 with no active term backlogs.",
                        "Submission and syllabus mapping completed in the first 4 weeks."
                    ],
                    evidence_required=[
                        "Modular source code with unit test suite (>70% coverage)",
                        "Comparative mapping matrix between project modules and course syllabus",
                        "Faculty Mentor recommendation letter"
                    ],
                    evaluation_method="Formal Viva Voce before External Industry Examiner & School Academic Council.",
                    max_benefit_documented="Full substitution of one departmental elective with direct awarded grade based on project viva.",
                    approval_authority="Standing Academic Committee (SAC)",
                    application_route="UMS -> RMS -> Edu-Revolution -> Course Equivalence Request"
                )
            )

        # Vector 4: Attendance Benefit & Duty Leave
        benefit_vectors.append(
            BenefitVector(
                benefit_name="Official Attendance Benefit & Duty Leave",
                applicable_policy="LPU Competition & Field Trial Duty Leave Regulations",
                eligibility_conditions=[
                    "Participation in an officially approved national/international hackathon (e.g. Smart India Hackathon) or scheduled client deployment.",
                    "Prior written approval memo from Head of School obtained prior to travel/event.",
                    "Filing on UMS within 7 calendar days of event completion."
                ],
                evidence_required=[
                    "Official selection/invitation letter from organizing body",
                    "HoS prior-sanction memo",
                    "Certificate of attendance/presentation stamped by organizers",
                    "Travel tickets / geo-tagged presence logs"
                ],
                evaluation_method="Administrative verification by Class Mentor and School Attendance Office.",
                max_benefit_documented="Duty Leave credit up to event duration (subject to the 65% statutory minimum institutional floor).",
                approval_authority="Head of School & Academic Coordinator (Dr. Dalwinder Singh)",
                application_route="UMS -> Student Services -> Attendance -> Duty Leave Application"
            )
        )

        # 4. Formulate Missing Information Checklist
        missing_to_ask = []
        if not any(k in q for k in ["github", "gitlab", "repo", "code"]):
            missing_to_ask.append("Public repository link (GitHub/GitLab) with active commits.")
        if not any(k in q for k in ["live", "demo", "deployed", "url", "hosted"]):
            missing_to_ask.append("Live deployment URL or demonstration link where the project can be reviewed.")
        if not any(k in q for k in ["tech", "python", "react", "node", "aws", "docker", "stack"]):
            missing_to_ask.append("Exact technical stack and architectural frameworks used.")
        if not any(k in q for k in ["client", "user", "revenue", "downloads", "traffic", "gst"]):
            missing_to_ask.append("Client engagements, active user metrics, or commercial revenue figures (if applicable).")
        if not any(k in q for k in ["cgpa", "gpa", "semester", "term"]):
            missing_to_ask.append("Your current semester and CGPA (to confirm course equivalence eligibility).")

        return ProjectBenefitComprehensiveReport(
            project_summary=query.strip(),
            matched_category=cat_name,
            category_id=cat_id,
            benefit_vectors=benefit_vectors,
            missing_information_to_ask=missing_to_ask,
            technical_originality_rule="Originality Mandate: All submissions undergo automated plagiarism & AI-code screening. Direct clones of YouTube tutorials or open-source templates without distinct novel engineering will lead to disqualification and disciplinary referral.",
            disclaimer_notice="STATUTORY DISCLAIMER: Preliminary assessment reflects potential alignment with university guidelines. Formal award of CA waivers, attendance leaves, or course credits is strictly subject to demonstration before the School Evaluation Committee and written ratification by the Standing Academic Committee (SAC). No automatic grade or attendance credit is guaranteed.",
            deadlines_and_helpdesk={
                "filing_window": "First 4 weeks of the ongoing academic semester",
                "physical_helpdesk": "Block 27 Room 102 (Query & Assistance Zone)",
                "academic_head": "Dr. Mohit Arora (Head of School) / Dr. Dalwinder Singh (Academic Coordinator, Block 32 School Office)"
            }
        )
