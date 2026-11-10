import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class AuthorityGuidance:
    authority_name: str
    official_designation: str
    responsibility_scope: str  # "Administrative Apex", "Academic Leadership", "Disciplinary & Student Welfare", "Examination Grievance"
    office_location: str
    appointment_procedure: List[str]
    hierarchical_escalation_ladder: List[str]
    confidentiality_notice: str
    grievance_or_appeal_channel: str
    prohibited_actions: List[str]


class UniversityAuthorityService:
    """
    University Authority and Appointment Intelligence Engine for CampusConnect V8.
    Guides students on how to engage with institutional authorities:
    - Pro Chancellor (Mrs. Rashmi Mittal)
    - Vice Chancellor (Dr. Preeti Bajaj / VC Secretariat)
    - Head of School / Dean (Dr. Mohit Arora, School of CSE)
    - Academic Coordinator (Dr. Dalwinder Singh)
    - Proctorial Board / Student Disciplinary Committee
    - Examination Appeals & Grievance Division
    Enforces procedural compliance and confidentiality, preventing bypass of legitimate channels.
    """

    @classmethod
    def is_authority_query(cls, text: str) -> bool:
        q = text.lower()
        triggers = [
            "pro chancellor", "vice chancellor", "vc", "chancellor", "hod",
            "dean", "head of school", "academic coordinator", "meet authority",
            "disciplinary", "indiscipline", "proctor", "proctorial", "appeal",
            "appeal academic", "grievance committee"
        ]
        return any(t in q for t in triggers)

    @classmethod
    def resolve_authority(cls, query: str) -> AuthorityGuidance:
        q = query.lower()

        # 1. Pro Chancellor
        if "pro chancellor" in q:
            return AuthorityGuidance(
                authority_name="Mrs. Rashmi Mittal",
                official_designation="Pro Chancellor, Lovely Professional University",
                responsibility_scope="Executive and Institutional Apex Leadership",
                office_location="Pro Chancellor Secretariat, Executive Block / Block 30 (Restricted Access Zone)",
                appointment_procedure=[
                    "Step 1: Direct appointments are reserved for distinguished achievements, international delegations, and final institutional reviews.",
                    "Step 2: Submit a formal appointment request dossier via your Dean / Head of School (Block 32 School Office).",
                    "Step 3: The Dean's office forwards the vetted memorandum to the Pro Chancellor Secretariat with relevant case documents.",
                    "Step 4: The Secretariat schedules a protocol-confirmed time slot."
                ],
                hierarchical_escalation_ladder=[
                    "Tier 1: Class Mentor",
                    "Tier 2: Academic Coordinator (Dr. Dalwinder Singh)",
                    "Tier 3: Head of School (Dr. Mohit Arora, Block 32)",
                    "Tier 4: Executive Dean of Faculty",
                    "Apex: Pro Chancellor / Vice Chancellor"
                ],
                confidentiality_notice="All executive petitions are processed under strict administrative confidentiality.",
                grievance_or_appeal_channel="Standard academic or fee complaints must NOT bypass initial tiers; file via UMS -> RMS first.",
                prohibited_actions=[
                    "Do not approach the Executive Block without an official verified appointment confirmation token.",
                    "Do not attempt to bypass Departmental and School leadership for ordinary routine issues."
                ]
            )

        # 2. Vice Chancellor
        if "vice chancellor" in q or " vc " in f" {q} ":
            return AuthorityGuidance(
                authority_name="Dr. Preeti Bajaj",
                official_designation="Vice Chancellor, Lovely Professional University",
                responsibility_scope="Academic Apex & Chief Executive Authority",
                office_location="VC Secretariat, Block 30 (Administrative & Executive Floor)",
                appointment_procedure=[
                    "Step 1: File an initial grievance or formal request on UMS -> Relationship Management System (RMS).",
                    "Step 2: If the issue remains unresolved after review by the Head of School and Registrar, request an escalation token from the Dean's Office.",
                    "Step 3: Submit the dossier to the Vice Chancellor Secretariat for review.",
                    "Step 4: Formal appointment is granted based on Secretariat scheduling."
                ],
                hierarchical_escalation_ladder=[
                    "Tier 1: Class Mentor",
                    "Tier 2: Academic Coordinator (Dr. Dalwinder Singh)",
                    "Tier 3: Head of School (Dr. Mohit Arora, Block 32)",
                    "Tier 4: Registrar / Academic Council Secretariat",
                    "Apex: Vice Chancellor"
                ],
                confidentiality_notice="Vice Chancellor office proceedings maintain institutional privilege and student confidentiality.",
                grievance_or_appeal_channel="UMS -> RMS -> Central University Grievance Committee",
                prohibited_actions=[
                    "Direct walk-ins to the Vice Chancellor Secretariat are prohibited without approved token.",
                    "Routine exam re-checks or attendance queries must follow departmental channels."
                ]
            )

        # 3. Disciplinary / Indiscipline Cases
        if any(k in q for k in ["disciplinary", "indiscipline", "proctor", "proctorial", "police", "fight", "misconduct"]):
            return AuthorityGuidance(
                authority_name="Chief Proctor & Proctorial Board",
                official_designation="Proctorial Board / Division of Student Welfare (DSW)",
                responsibility_scope="Student Conduct, Campus Integrity, and Disciplinary Adjudication",
                office_location="Proctorial Board Office, Block 30 (Division of Student Welfare)",
                appointment_procedure=[
                    "Step 1: When issued a Proctorial Show Cause Notice or Inquiry Summons, do NOT avoid or ignore it.",
                    "Step 2: Consult your Class Mentor immediately for advisory guidance.",
                    "Step 3: Report to the Proctorial Board Office at the scheduled hearing date and time with your LPU Student ID card.",
                    "Step 4: Submit your factual written statement along with any verifiable evidence (CCTV footage request, witness statements, medical records).",
                    "Step 5: A formal inquiry committee reviews the facts impartially under the Student Disciplinary Code of Conduct."
                ],
                hierarchical_escalation_ladder=[
                    "Tier 1: Class Mentor & Assistant Director (Hostel / Security)",
                    "Tier 2: Proctorial Inquiry Committee (Block 30)",
                    "Tier 3: Dean of Student Welfare (DSW)",
                    "Appeal Body: University Appellate Disciplinary Authority (Chaired by Vice Chancellor)"
                ],
                confidentiality_notice="CRITICAL PRIVACY MANDATE: Disciplinary hearings and records are strictly confidential. CampusConnect does not disclose or record individual student disciplinary files.",
                grievance_or_appeal_channel="If you wish to appeal a disciplinary committee verdict, submit a formal appeal petition to the University Appellate Committee via the Registrar's Office within 7 working days of the order.",
                prohibited_actions=[
                    "NEVER attempt to bypass the Proctorial Board or contact senior university executives to interfere with active inquiries.",
                    "Do not fabricate witness testimonies or alter digital records; tampering aggravates the disciplinary penalty."
                ]
            )

        # 4. Academic Appeals & Grade / Attendance Review
        if any(k in q for k in ["appeal", "academic appeal", "appeal academic", "re-evaluation appeal", "unfair means", "umc"]):
            return AuthorityGuidance(
                authority_name="Controller of Examinations & Academic Council Appellate Board",
                official_designation="Division of Examination & Standing Academic Committee",
                responsibility_scope="Examination Audits, Grade Re-evaluations, and UMC Appeals",
                office_location="Examination Division, Block 30 (Ground Floor Student Facilitation Counter)",
                appointment_procedure=[
                    "Step 1: Check published datesheet and result notification on UMS.",
                    "Step 2: For grade re-evaluation or answer script inspection, submit application on UMS within 15 days of result declaration.",
                    "Step 3: For Unfair Means Committee (UMC) appeals, submit a formal appeal petition to the Controller of Examinations within 7 calendar days of verdict notification.",
                    "Step 4: The Appellate Committee conducts an independent audit of the answer booklet and invigilator report."
                ],
                hierarchical_escalation_ladder=[
                    "Tier 1: Course Instructor / Course Coordinator",
                    "Tier 2: Head of Department / Academic Coordinator (Dr. Dalwinder Singh)",
                    "Tier 3: Controller of Examinations (Block 30)",
                    "Apex: Standing Academic Committee (SAC)"
                ],
                confidentiality_notice="Examination evaluations and UMC proceedings are protected under institutional privacy statutes.",
                grievance_or_appeal_channel="UMS -> Examination Services -> Re-evaluation / Grievance Submission",
                prohibited_actions=[
                    "Do not approach examiners or evaluators directly; all communication must proceed via the Examination Division facilitation desk.",
                    "Do not miss the 15-day post-result filing deadline."
                ]
            )

        # 5. Head of School / Dean (Default for CSE leadership)
        return AuthorityGuidance(
            authority_name="Dr. Mohit Arora",
            official_designation="Head of School, School of Computer Science & Engineering",
            responsibility_scope="Academic Operations, Faculty Supervision, and Curriculum Governance",
            office_location="Ground Floor School Office / Reception, Block 32 (Public student interactions occur at the School Office front desk; private cabin numbers are withheld)",
            appointment_procedure=[
                "Step 1: Check with your Class Mentor first to confirm if the matter requires Head of School intervention.",
                "Step 2: Visit the Block 32 Ground Floor School Office during official Student Consultation Hours: 3:00 PM – 5:00 PM on working days.",
                "Step 3: Register your appointment token at the reception desk with your Registration Number.",
                "Step 4: Bring all supporting documents (printed application, mentor recommendation, UMS tickets)."
            ],
            hierarchical_escalation_ladder=[
                "Tier 1: Class Mentor",
                "Tier 2: Academic Coordinator (Dr. Dalwinder Singh)",
                "Tier 3: Head of School (Dr. Mohit Arora)",
                "Tier 4: Executive Dean of Faculty"
            ],
            confidentiality_notice="Student academic records discussed during appointments remain strictly within the Deanery governance.",
            grievance_or_appeal_channel="UMS -> RMS -> Select 'School of Computer Science & Engineering'",
            prohibited_actions=[
                "Do not roam faculty cabin corridors; student consultations are conducted at the designated School Office reception rooms.",
                "Always carry your official student identity card."
            ]
        )

