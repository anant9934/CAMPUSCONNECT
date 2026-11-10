import csv
import logging
import os
import re
from typing import List, Dict, Any, Optional

from app.schemas.ums import WhoToMeetCard

logger = logging.getLogger(__name__)


class IssueToOfficeResolver:
    """
    Deterministic Who-to-Meet Issue Routing Service for Lovely Professional University.
    Guides students to the verified physical office, responsible role, prerequisite steps,
    and escalation ladder rather than defaulting to HOD or escalating prematurely.
    """

    _routes: Optional[List[Dict[str, Any]]] = None

    @classmethod
    def _load_routes(cls) -> List[Dict[str, Any]]:
        if cls._routes is not None:
            return cls._routes

        candidates = [
            os.path.join(os.getcwd(), "data", "who_to_meet_issue_router.csv"),
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "who_to_meet_issue_router.csv"),
        ]
        file_path = None
        for c in candidates:
            if os.path.exists(c):
                file_path = c
                break

        routes = []
        if file_path:
            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    reval = row.get("revalidation_notice")
                    if reval and reval.strip().lower() in ["none", ""]:
                        reval = None

                    # Parse required docs
                    docs_str = row.get("required_documents", "")
                    docs = [d.strip() for d in docs_str.split(",") if d.strip()]

                    # Parse escalation ladder
                    esc_str = row.get("escalation_ladder", "")
                    ladder = [e.strip() for e in esc_str.split("->") if e.strip()]

                    routes.append({
                        "issue_key": row.get("issue_key"),
                        "category_title": row.get("category_title"),
                        "primary_contact_role": row.get("primary_contact_role"),
                        "named_contact_person": row.get("named_contact_person") if row.get("named_contact_person") and row.get("named_contact_person") != "None" else None,
                        "office_location": row.get("office_location"),
                        "room_details": row.get("room_details"),
                        "ums_navigation_path": row.get("ums_navigation_path"),
                        "prerequisite_action": row.get("prerequisite_action"),
                        "required_documents": docs,
                        "escalation_ladder": ladder,
                        "revalidation_notice": reval,
                        "evidence_status": row.get("evidence_status", "OFFICIAL_CURRENT_VERIFIED"),
                    })
        cls._routes = routes
        return routes

    @classmethod
    def resolve_issue(cls, query: str) -> Optional[WhoToMeetCard]:
        """
        Matches a student query to the verified resolution route.
        """
        routes = cls._load_routes()
        if not routes:
            return None

        q = query.lower().strip()

        # Trigger checks
        triggers = {
            "attendance_discrepancy": [
                "attendance", "shortage", "biometric", "attendance wrong", "attendance issue",
                "duty leave", "75% attendance", "attendance correction"
            ],
            "academic_benefits": [
                "edurev", "edu-revolution", "academic benefit", "project benefit",
                "where do i submit this project", "submit my project", "submit project",
                "prior learning", "github project benefit"
            ],
            "student_relationship_support": [
                "relationship", "dsr", "mentor issue", "division of student relationship",
                "student relationship"
            ],
            "formal_grievance_service": [
                "grievance", "complaint", "rms ticket", "ombudsman", "harassment"
            ],
            "international_visa": [
                "visa", "frro", "international student", "foreign student", "passport", "dia"
            ],
            "cse_leadership": [
                "cse leadership", "school of cse office", "meet hod cse", "cse hod office"
            ],
            "placements_career": [
                "placement", "internship drive", "career services", "job drive", "dcs"
            ],
            "medical_emergency": [
                "emergency", "ambulance", "chest pain", "collapsed", "urgent hospital"
            ],
            "doctor_appointment": [
                "doctor", "opd", "physician", "health checkup", "unihospital appointment", "book doctor"
            ],
            "mental_health_counseling": [
                "counseling", "counselling", "psychologist", "depressed", "depression", "anxiety",
                "mental health", "stressed", "mental wellness"
            ],
            "fee_challan_issue": [
                "fee", "challan", "fee receipt", "fee payment", "accounts", "tuition fee"
            ],
            "hostel_discipline_leave": [
                "hostel leave", "hostel warden", "hostel room", "mess change", "warden"
            ],
            "library_fine_access": [
                "library", "overdue fine", "book return", "discussion room", "radhakrishnan library"
            ],
            "wifi_it_support": [
                "wifi", "wi-fi", "lpu-wireless", "mac registration", "internet speed", "it helpdesk"
            ]
        }

        # Direct match for Proctorial Board / Disciplinary inquiries
        if any(k in q for k in ["proctor", "proctorial", "indiscipline", "disciplinary", "show cause notice", "misconduct"]):
            return WhoToMeetCard(
                issue_key="proctorial_disciplinary",
                category_title="Proctorial Board & Disciplinary Inquiries",
                primary_contact_role="Chief Proctor / Proctorial Board (DSW)",
                named_contact_person="Division of Student Welfare",
                office_location="Block 30",
                room_details="Proctorial Board Office, Ground Floor, Block 30 (Division of Student Welfare)",
                ums_navigation_path="UMS > Student Services > Relationship Management System",
                prerequisite_action="Consult your Class Mentor immediately and report with your LPU Student ID card and factual evidence.",
                required_documents=[
                    "LPU Student ID Card",
                    "Proctorial Show Cause Notice / Summons",
                    "Written factual statement",
                    "Verifiable supporting evidence (if applicable)"
                ],
                escalation_ladder=[
                    "1. Class Mentor",
                    "2. Assistant Director (Hostel / Security)",
                    "3. Proctorial Inquiry Committee",
                    "4. Chief Proctor",
                    "5. Dean Student Welfare (DSW)"
                ],
                revalidation_notice="Official protocol: Never avoid or ignore a Proctorial Board inquiry summons. Attend the hearing promptly at the scheduled time.",
                evidence_status="OFFICIAL_CURRENT_VERIFIED"
            )

        matched_key = None
        for key, keywords in triggers.items():
            if any(k in q for k in keywords):
                matched_key = key
                break

        if not matched_key:
            return None

        for r in routes:
            if r["issue_key"] == matched_key:
                return WhoToMeetCard(**r)

        return None

