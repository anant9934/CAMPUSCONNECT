import logging
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class AttendanceAssessment:
    eligible_options: List[Dict[str, Any]]
    disqualifying_conditions: List[str]
    missing_details_to_ask: List[str]
    documentation_required: List[str]
    application_procedures: List[Dict[str, str]]
    assistance_office: Dict[str, str]
    fraud_warning: str
    statutory_notice: str


class AttendanceSolverService:
    """
    Intelligent attendance problem solver for LPU students.
    Addresses low-attendance queries by evaluating institutional policy,
    distinguishing Revenue Generation benefits from the 10% Condonation / Duty Leave benefit,
    clarifying missing details, and presenting verified legitimate escalation routes.
    """

    STATUTORY_MINIMUM_ATTENDANCE = 75.0
    ABSOLUTE_CONDONATION_FLOOR = 65.0

    @classmethod
    def is_attendance_query(cls, text: str) -> bool:
        q = text.lower()
        triggers = [
            "attendance", "shortage", "debar", "debarred", "low attendance",
            "attendance benefit", "attendance relaxation", "duty leave", "medical leave",
            "condonation", "75%", "65%"
        ]
        return any(t in q for t in triggers)

    @classmethod
    def extract_stated_attendance(cls, text: str) -> Optional[float]:
        """Attempts to extract a stated percentage from the user query."""
        match = re.search(r"(\d{1,2}(?:\.\d+)?)\s*%", text)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                pass
        return None

    @classmethod
    def solve(cls, query: str, context_details: Optional[Dict[str, Any]] = None) -> AttendanceAssessment:
        details = context_details or {}
        stated_pct = cls.extract_stated_attendance(query) or details.get("attendance_percentage")

        # Missing questions to clarify with the student
        missing_to_ask: List[str] = []
        if stated_pct is None:
            missing_to_ask.append("What is your current overall attendance percentage (as shown on UMS)?")
        if not any(k in query.lower() for k in ["medical", "sick", "hospital", "ill"]):
            missing_to_ask.append("Were you absent due to verified medical reasons or hospitalization?")
        if not any(k in query.lower() for k in ["hackathon", "sports", "cultural", "competition"]):
            missing_to_ask.append("Did you represent LPU in an officially approved hackathon, sports tournament, or cultural youth festival?")
        if not any(k in query.lower() for k in ["startup", "revenue", "client", "gst", "freelance"]):
            missing_to_ask.append("Do you run an active startup or live commercial project generating verified client revenue?")

        # Evaluate routes
        eligible_options = [
            {
                "route_name": "EDU-Revolution Revenue Generation Attendance Benefit",
                "policy_category": "EDU-Revolution Track (SCRGM / Cat-05 & Cat-09)",
                "benefit_scope": "Attendance relaxation for the active term as evaluated and recommended by the Standing Academic Committee (SAC).",
                "prerequisites": "Live project/startup registered with LPU Startup School / Incubation Center with documented commercial revenue (GST invoices, bank remittance statements, client work orders).",
                "distinction_note": "CRITICAL DISTINCTION: Commercial revenue does not automatically buy marks or attendance; it qualifies you for a formal viva before the School Evaluation Committee to seek attendance duty leave.",
            },
            {
                "route_name": "Up to 10% Institutional Condonation / Duty Leave Benefit",
                "policy_category": "LPU Academic Regulations — Duty Leave & Condonation",
                "benefit_scope": "Up to 10% attendance benefit, allowing students with 65%–74.9% attendance to meet the mandatory 75% ETE eligibility threshold.",
                "prerequisites": "Formal representation of LPU in recognized sports/cultural/hackathon events with prior HoS approval, OR serious medical illness with hospitalization.",
                "distinction_note": "This is entirely separate from revenue-based benefits. Condonation applies strictly to university-sanctioned activities and certified medical cases.",
            },
            {
                "route_name": "Biometric Punch Audit & Course Coordinator Review",
                "policy_category": "LPU Attendance Discrepancy Redressal",
                "benefit_scope": "Correction of system or punch discrepancies where a student attended classes physically but biometric logs did not register.",
                "prerequisites": "Application filed with Class Mentor within 3 working days of discrepancy with course timetable and instructor verification.",
                "distinction_note": "Restores legitimately earned attendance; does not waive unexcused absences.",
            }
        ]

        disqualifying_conditions = [
            "Attendance below 65% absolute threshold: Under standard university academic regulations, no routine condonation or duty leave can bridge attendance below 65% to the mandatory 75% bar without exceptional Vice-Chancellor dispensation.",
            "Late duty leave submission: Duty leaves must be applied on UMS within 7 calendar days of event completion; retrospective applications after the deadline are rejected.",
            "Unapproved external events: Participation in hackathons or internships without prior written sanction from the Head of School (HoS) is strictly ineligible for duty leave.",
            "Backlog courses: In re-appear or backlog courses, 100% attendance compliance is strictly enforced without condonation."
        ]

        # If user states attendance below 65%, add prominent notice
        if stated_pct is not None and stated_pct < 65.0:
            disqualifying_conditions.insert(
                0,
                f"Your stated attendance ({stated_pct}%) is below the statutory 65.0% condonation floor. Routine 10% condonation cannot bridge this gap. You must consult your Academic Coordinator immediately."
            )

        documentation_required = [
            "For Medical Grounds: Discharge summary and medical certificate authenticated by Chief Medical Officer (CMO), Uni-Hospital (Block 30).",
            "For Event / Hackathon Duty Leave: Official invitation letter, faculty escort sign-off, certificate of participation/award, and HoS pre-approval memo.",
            "For EDU-Revolution Revenue Track: Valid GST invoices, client agreements, bank transaction proof showing credited revenue, and technical deliverables (GitHub repo, live deployment).",
            "For Biometric Error: Course Instructor sign-off slip and Mentor attendance log sheet."
        ]

        application_procedures = [
            {
                "step": "Step 1: Apply on UMS",
                "action": "Sign in to UMS -> Student Services -> Attendance -> Duty Leave / Medical Leave Application. Submit within the mandatory filing window (7 days for DL, 3 days post-discharge for medical)."
            },
            {
                "step": "Step 2: Faculty Verification",
                "action": "Notify your Class Mentor to endorse the submitted leave request in their mentor workflow dashboard."
            },
            {
                "step": "Step 3: School Office Sign-off",
                "action": "For EDU-Rev or complex condonation, visit the Ground Floor School Office in Block 32 for review by Academic Coordinator Dr. Dalwinder Singh."
            }
        ]

        assistance_office = {
            "primary_authority": "Dr. Dalwinder Singh (Academic Coordinator & Attendance Lead)",
            "school_head": "Dr. Mohit Arora (Head of School, School of Computer Science & Engineering)",
            "location": "Ground Floor School Office / Reception, Block 32 (Note: Individual cabin seating is not published for public access; student queries are resolved at the School Office front desk)",
            "hours": "Student Consultation Hours: 3:00 PM – 5:00 PM on all official university working days"
        }

        fraud_warning = (
            "⚠️ STRICT UNIVERSITY CODE OF CONDUCT ADVISORY:\n"
            "Never attempt to manufacture false revenue, buy fake medical certificates, fabricate non-existent startup income, "
            "or tamper with attendance records. Under Section 12 of the LPU Student Disciplinary Regulations, submitting fraudulent "
            "documents constitutes Gross Misconduct, resulting in immediate disciplinary action by the Proctorial Board, "
            "forfeiture of term credits, or university suspension."
        )

        statutory_notice = (
            "LPU Statutory Policy: A minimum of 75% attendance is mandatory in each registered course to be eligible for End Term Examinations (ETE). "
            "Condonation up to 10% is discretionary upon valid documentation and cannot be demanded as a matter of right."
        )

        return AttendanceAssessment(
            eligible_options=eligible_options,
            disqualifying_conditions=disqualifying_conditions,
            missing_details_to_ask=missing_to_ask,
            documentation_required=documentation_required,
            application_procedures=application_procedures,
            assistance_office=assistance_office,
            fraud_warning=fraud_warning,
            statutory_notice=statutory_notice
        )

