import logging
import re
from typing import Dict, Any, Optional, Tuple, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.action_workflow import ActionWorkflow
from app.models.ums_catalog import UMSServiceCatalog
from app.schemas.ums import (
    BookingCard,
    ProcedureChecklist,
    RMSCard,
    PersonalRecordCard,
    NavigationCard,
)

logger = logging.getLogger(__name__)


class WorkflowEngine:
    """
    Executes guided SOP workflows for campus services:
    - Doctor, hostel, counselling, library-room, language-lab bookings
    - RMS grievance logging & tracking
    - Personal record boundaries (attendance, result, marks, receipts)
    - Procedure checklists (re-appear, re-evaluation, refunds, RFID)
    """

    @classmethod
    async def match_workflow(
        cls,
        query: str,
        db: AsyncSession
    ) -> Optional[ActionWorkflow]:
        """Matches a user query against the 24 registered action workflows."""
        q = query.lower().strip()
        stmt = select(ActionWorkflow).where(ActionWorkflow.is_active == True)
        res = await db.execute(stmt)
        workflows = res.scalars().all()

        best_wf = None
        best_score = 0.0

        for wf in workflows:
            intent_lower = wf.user_intent.lower()
            flow_lower = wf.chatbot_flow.lower()
            nav_lower = wf.ums_navigation_path.lower()

            score = 0.0
            # Direct intent phrase match
            if intent_lower in q:
                score += 8.0
            for token in intent_lower.split():
                if len(token) > 3 and token in q:
                    score += 2.0

            # Action-specific heuristics
            if "hostel" in q and "hostel" in intent_lower:
                score += 5.0
            if ("doctor" in q or "medical" in q or "clinic" in q) and "doctor" in intent_lower:
                score += 5.0
            if ("counseling" in q or "counselling" in q or "psychologist" in q) and "counseling" in intent_lower:
                score += 5.0
            if ("discussion room" in q or "study room" in q) and "discussion room" in intent_lower:
                score += 5.0
            if "language lab" in q and "language lab" in intent_lower:
                score += 5.0
            if ("grievance" in q or "complaint" in q or "rms" in q) and "grievance" in intent_lower:
                score += 5.0
            if ("fee receipt" in q or "fee statement" in q) and "fee statement" in intent_lower:
                score += 5.0
            if ("refund" in q or "reimbursement" in q) and "refund" in intent_lower:
                score += 5.0
            if ("attendance" in q) and "attendance" in intent_lower:
                score += 5.0
            if ("re-appear" in q or "reappear" in q or "backlog" in q) and "re-appear" in intent_lower:
                score += 5.0
            if ("re-evaluation" in q or "reevaluation" in q) and "re-evaluation" in intent_lower:
                score += 5.0
            if ("date sheet" in q or "exam schedule" in q) and "date sheet" in intent_lower:
                score += 5.0
            if ("rfid" in q or "parent pass" in q) and "rfid" in intent_lower:
                score += 5.0
            if ("duplicate id" in q or "duplicate card" in q) and "duplicate" in intent_lower:
                score += 5.0
            if ("lost" in q and "found" in q) and "lost property" in intent_lower:
                score += 5.0

            if score > best_score:
                best_score = score
                best_wf = wf

        if best_wf and best_score >= 3.0:
            return best_wf
        return None

    @classmethod
    def build_booking_card(cls, wf: ActionWorkflow) -> BookingCard:
        """Constructs a BookingCard for reservable services."""
        intent = wf.user_intent
        booking_type = "Campus Facility Booking"

        if "doctor" in intent.lower():
            booking_type = "Doctor OPD Consultation"
        elif "hostel" in intent.lower():
            booking_type = "Residential Hostel Allocation"
        elif "counseling" in intent.lower() or "psychologist" in intent.lower():
            booking_type = "Confidential Psychologist Appointment (YourDOST)"
        elif "discussion room" in intent.lower():
            booking_type = "Central Library Discussion Room"
        elif "language lab" in intent.lower():
            booking_type = "LMS Language Lab Practice Slot"
        elif "authority" in intent.lower() or "appointment" in intent.lower():
            booking_type = "Official Appointment with University Authority"

        return BookingCard(
            booking_type=booking_type,
            service_title=wf.user_intent,
            breadcrumb=wf.ums_navigation_path,
            prerequisites=wf.prerequisites or [],
            availability_caveat="Real-time slot availability requires authentication inside official UMS / LPU Touch. The public assistant does not reserve slots directly.",
            handoff_url=wf.handoff_url,
            button_label="Continue to Official UMS Booking",
        )

    @classmethod
    def build_procedure_checklist(cls, wf: ActionWorkflow) -> ProcedureChecklist:
        """Constructs a ProcedureChecklist for SOP workflows."""
        return ProcedureChecklist(
            procedure_name=wf.user_intent,
            steps=wf.steps or [],
            required_documents=wf.prerequisites or [],
            deadline_or_fees="Check active UMS circulars for applicable term fees and last submission dates.",
            breadcrumb=wf.ums_navigation_path,
            handoff_url=wf.handoff_url,
        )

    @classmethod
    def build_rms_card(cls, wf: Optional[ActionWorkflow] = None) -> RMSCard:
        """Constructs an RMSCard for student grievance guidance."""
        return RMSCard()

    @classmethod
    def build_personal_record_card(cls, query: str, wf: Optional[ActionWorkflow] = None) -> PersonalRecordCard:
        """Constructs a PersonalRecordCard establishing the public/private boundary."""
        q = query.lower()
        rec_type = "Academic / Administrative Record"
        title = "Personal Student Record"
        breadcrumb = "UMS > My Profile"
        explanation = (
            "To safeguard your personal data and privacy, the public CampusConnect assistant does not access "
            "or display private student records such as personal attendance, exam marks, CGPA, or fee receipts. "
            "You can securely view your own records by signing in to the official LPU UMS portal."
        )

        if "attendance" in q:
            rec_type = "Personal Attendance Record"
            title = "View Your Course Attendance"
            breadcrumb = "UMS > Learning Management System (LMS) > View Attendance"
            explanation = "Your course-wise aggregate and daily attendance is maintained privately in UMS. Please log in to UMS to inspect your current attendance percentage."
        elif "result" in q or "marks" in q or "cgpa" in q or "grade" in q:
            rec_type = "Examination Marks & Transcripts"
            title = "Academic Results & Grades"
            breadcrumb = "UMS > Examination System > Academic Result"
            explanation = "Individual term results, grade point averages, and marks statements are confidential student records accessible exclusively via authenticated UMS."
        elif "fee" in q or "receipt" in q or "dues" in q or "balance" in q:
            rec_type = "Financial & Fee Statement"
            title = "Fee Receipts & Account Statement"
            breadcrumb = "UMS > Fee and Scholarship System > Fee Dashboard / View Fee Receipts"
            explanation = "Fee payment status, installment receipts, and balance summaries require authenticated access in UMS for financial confidentiality."
        elif "timetable" in q or "time table" in q:
            rec_type = "Class Schedule & Timetable"
            title = "Personal Course Timetable"
            breadcrumb = "UMS > Learning Management System (LMS) > View Time Table"
            explanation = "Your section-specific class timetable and lab schedules are accessible directly on your student LMS dashboard."

        if wf and wf.ums_navigation_path:
            breadcrumb = wf.ums_navigation_path

        return PersonalRecordCard(
            record_type=rec_type,
            title=title,
            breadcrumb=breadcrumb,
            boundary_explanation=explanation,
            handoff_url="https://ums.lpu.in/lpuums/",
        )

    @classmethod
    def is_emergency_medical(cls, query: str) -> bool:
        """Determines if query represents an acute medical or safety emergency."""
        q = query.lower()
        emergency_terms = [
            "emergency", "ambulance", "collapsed", "unconscious", "chest pain",
            "heart attack", "bleeding", "severe injury", "accident", "trauma"
        ]
        return any(term in q for term in emergency_terms)

    @classmethod
    def get_emergency_contacts(cls) -> Dict[str, Any]:
        """Returns verified campus emergency numbers and UniHospital Block 30 triage details."""
        return {
            "hospital_name": "UniHospital - 24x7 Multi-Specialty Campus Hospital",
            "hospital_location": "Block 30 (Near Gate 1 & Residential Blocks)",
            "ambulance_phones": ["+91-1824-517100", "+91-1824-517101", "+91-98788-51710"],
            "security_helpline": "+91-1824-517000",
            "instructions": "In case of life-threatening distress, contact UniHospital emergency triage immediately or proceed to Block 30 ground floor.",
        }
