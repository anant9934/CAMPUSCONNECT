import logging
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

from app.services.attendance_solver_service import AttendanceSolverService
from app.services.project_benefit_service import ProjectBenefitService
from app.services.authority_service import UniversityAuthorityService
from app.services.people_directory_service import PeopleDirectoryService
from app.services.web_research_service import WebResearchService
from app.services.policy_engine import PolicyEngine

logger = logging.getLogger(__name__)


@dataclass
class ProactiveEvaluationResult:
    explicit_question: str
    underlying_objective: str
    academic_opportunities: List[str]
    potential_benefits: List[str]
    applicable_policies: List[str]
    missing_eligibility_info: List[str]
    relevant_authorities: List[Dict[str, str]]
    required_evidence: List[str]
    official_workflows: List[str]
    recommended_next_action: str
    proactive_guidance_text: str
    is_proactive_active: bool = True


class ProactiveStudentIntelligence:
    """
    CampusConnect V8 Proactive Campus Intelligence Engine.
    Evaluates every student turn along 10 institutional dimensions:
    1. Explicit Question
    2. Underlying Problem / Objective
    3. Relevant Academic Opportunities
    4. Potential University Benefits
    5. Applicable Policies
    6. Missing Eligibility Information
    7. Relevant Faculty, HODs, or Authorities
    8. Required Evidence and Documents
    9. Official UMS / University Workflows
    10. Recommended Next Action
    """

    @classmethod
    async def evaluate_turn(
        cls,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        context_data: Optional[Dict[str, Any]] = None
    ) -> ProactiveEvaluationResult:
        q = user_message.strip()
        q_lower = q.lower()
        hist = conversation_history or []
        combined_text = " ".join([h.get("content", "") for h in hist] + [q])

        underlying_objective = "General campus information and navigation inquiry"
        opportunities: List[str] = []
        benefits: List[str] = []
        policies: List[str] = []
        missing_info: List[str] = []
        authorities: List[Dict[str, str]] = []
        evidence: List[str] = []
        workflows: List[str] = []
        next_action = "Review verified guidance and proceed through official UMS portal."

        # Case 1: Attendance Problem
        if AttendanceSolverService.is_attendance_query(q):
            underlying_objective = "Improve attendance standing, prevent examination debarment, and explore legitimate condonation or duty leave avenues."
            att_result = AttendanceSolverService.solve(combined_text)

            opportunities.append("EDU-Revolution Revenue Generation Attendance Benefit (SCRGM)")
            opportunities.append("Institutional Duty Leave (Hackathons, Sports, Cultural Representation)")
            opportunities.append("Medical Condonation up to 10% (Hospitalization / CMO authenticated)")
            opportunities.append("Biometric Punch Audit & Correction")

            benefits.append("Up to 10% attendance condonation to meet 75% End Term Examination threshold")
            benefits.append("Official Duty Leave credit on UMS for sanctioned university activities")

            policies.append("LPU Academic Regulations — Attendance & Examination Eligibility (Clause 4.1 - 4.3)")
            policies.append("Student Code of Conduct Section 12 (Strict prohibition against fabricated medical/revenue records)")

            missing_info.extend(att_result.missing_details_to_ask)

            authorities.append({
                "name": att_result.assistance_office["primary_authority"],
                "role": "Academic Coordinator & Attendance Lead",
                "location": att_result.assistance_office["location"],
                "hours": att_result.assistance_office["hours"]
            })
            authorities.append({
                "name": att_result.assistance_office["school_head"],
                "role": "Head of School, School of CSE",
                "location": "Ground Floor School Office, Block 32",
                "hours": "3:00 PM – 5:00 PM"
            })

            evidence.extend(att_result.documentation_required)
            workflows.append("UMS -> Student Services -> Attendance -> Duty Leave / Medical Leave Application")
            workflows.append("Consult Class Mentor to verify attendance ledger discrepancies within 3 working days.")
            next_action = "Check your exact attendance percentage on UMS. If above 65%, submit your valid Duty Leave/Medical Certificate on UMS immediately, then visit Block 32 School Office during student hours."

        # Case 2: Project / Startup / Research / Benefit Assessment
        elif any(k in q_lower for k in ["project", "built", "startup", "revenue", "ca exemption", "course equivalence", "grade upgradation", "research paper", "patent", "internship"]):
            underlying_objective = "Gain academic credit, CA exemption, grade enhancement, or attendance credit for technical projects and achievements."
            proj_result = ProjectBenefitService.evaluate_project(combined_text)

            opportunities.append(proj_result.matched_category)
            for vec in proj_result.benefit_vectors:
                benefits.append(f"{vec.benefit_name}: {vec.max_benefit_documented}")
                policies.append(vec.applicable_policy)
                evidence.extend(vec.evidence_required[:2])

            missing_info.extend(proj_result.missing_information_to_ask)

            authorities.append({
                "name": "Dr. Mohit Arora",
                "role": "Head of School, School of CSE",
                "location": "Ground Floor School Office, Block 32",
                "hours": "3:00 PM – 5:00 PM"
            })
            authorities.append({
                "name": "Dr. Dalwinder Singh",
                "role": "Academic Coordinator",
                "location": "Ground Floor School Office, Block 32",
                "hours": "3:00 PM – 5:00 PM"
            })

            workflows.append("UMS -> RMS -> Edu-Revolution: Be the change -> Apply for EDU Revolution (Within first 4 weeks)")
            workflows.append("Block 27 Room 102 (Query & Assistance Zone) for syllabus mapping submission.")
            next_action = "Prepare your GitHub repository with architecture documentation, and submit course mapping on UMS within the active 4-week window."

        # Case 3: University Authority & Disciplinary Queries
        elif UniversityAuthorityService.is_authority_query(q):
            underlying_objective = "Engage with senior university leadership or navigate formal disciplinary/grievance procedures."
            auth_result = UniversityAuthorityService.resolve_authority(q)

            opportunities.append(f"Formal Representation via {auth_result.responsibility_scope}")
            policies.append(auth_result.confidentiality_notice)
            policies.append(auth_result.grievance_or_appeal_channel)

            authorities.append({
                "name": auth_result.authority_name,
                "role": auth_result.official_designation,
                "location": auth_result.office_location,
                "hours": "Prior Token / Scheduled Official Appointment Required"
            })

            evidence.append("Official Student ID Card and printed appointment dossier with mentor endorsement.")
            workflows.extend(auth_result.appointment_procedure[:2])
            next_action = f"Follow the official escalation ladder: Consult Class Mentor first, then approach {auth_result.office_location} with a verified appointment token."

        # Case 4: Technical Expertise & Faculty Matching
        elif any(k in q_lower for k in ["guide", "faculty", "cybersecurity", "cyber", "ai & ml", "machine learning", "cloud", "robotics", "iot", "who can help"]):
            underlying_objective = "Find verified research mentors, domain experts, or project guides within the university faculty."
            # Search people database
            matched_people = PeopleDirectoryService.search_people(q)

            opportunities.append("Undergraduate Research Mentorship & Capstone Project Guidance")
            benefits.append("Expert co-authorship on research publications, patents, and hackathon advisement.")

            if matched_people:
                for p in matched_people[:2]:
                    authorities.append({
                        "name": p.get("full_name", ""),
                        "role": p.get("designation", "") + " — " + p.get("department", ""),
                        "location": p.get("office_location", "Block 32 School Office"),
                        "hours": "Student Consultation Hours: 3:00 PM – 5:00 PM"
                    })
            else:
                authorities.append({
                    "name": "Dr. Dalwinder Singh",
                    "role": "Academic Coordinator (AI & ML Specialization Lead)",
                    "location": "Ground Floor School Office, Block 32",
                    "hours": "3:00 PM – 5:00 PM"
                })

            evidence.append("1-page Project Synopsis / GitHub repository preview.")
            workflows.append("Send a formal email from your official @lpu.in student email account with your project abstract.")
            next_action = "Draft a structured project brief and visit the Block 32 School Office during student hours (3:00 PM – 5:00 PM) to connect with the faculty guide."

        # Case 5: Default General Academic Query
        else:
            underlying_objective = "Access accurate university records, procedures, and navigation breadcrumbs."
            opportunities.append("Standard LPU Academic & Student Services")
            policies.append("LPU Student Handbooks & UMS Services Catalogue")
            workflows.append("UMS -> Navigation Dashboard")

        # Synthesize proactive guidance text
        synth_blocks = [
            f"**Underlying Objective:** {underlying_objective}",
        ]
        if opportunities:
            synth_blocks.append(f"**Potential Opportunities:** {', '.join(opportunities[:2])}")
        if missing_info:
            synth_blocks.append(f"**Missing Parameters to Clarify:** {'; '.join(missing_info[:2])}")
        if authorities:
            synth_blocks.append(f"**Key University Contact:** {authorities[0]['name']} ({authorities[0]['role']}, {authorities[0]['location']})")
        synth_blocks.append(f"**Recommended Next Action:** {next_action}")

        proactive_text = "\n".join(synth_blocks)

        return ProactiveEvaluationResult(
            explicit_question=q,
            underlying_objective=underlying_objective,
            academic_opportunities=opportunities,
            potential_benefits=benefits,
            applicable_policies=policies,
            missing_eligibility_info=missing_info,
            relevant_authorities=authorities,
            required_evidence=evidence,
            official_workflows=workflows,
            recommended_next_action=next_action,
            proactive_guidance_text=proactive_text,
            is_proactive_active=True
        )

