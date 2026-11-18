"""
Multi-Domain Intelligence & Orchestration Engine (CampusConnect v6.0).
Coordinates entity resolution, RAG retrieval, and action card generation across
multiple institutional domains in a single conversational turn.
Supports:
1. Faculty/Leadership + Issue Routing / Project Advice
2. EDU-Revolution Project Advisory + Physical Location + Submission Route
3. Campus Food Discovery + Block / Location Wayfinding
4. Attendance / Grievance Resolution + Statutory Procedure + First Contact
5. Multi-System UMS Service Pathways (e.g. Dual Hostel + Fee navigation)
"""
import logging
from typing import Dict, Any, Optional, Tuple, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.ums import (
    NavigationCard,
    BookingCard,
    ProcedureChecklist,
    RMSCard,
    PersonalRecordCard,
    CampusPlaceCard,
    FoodOutletCard,
    PersonCard,
    WhoToMeetCard,
    AcademicBenefitAssessmentCard,
    EvidenceCard,
)
from app.services.campus_food_service import CampusFoodService
from app.services.people_directory_service import PeopleDirectoryService
from app.services.issue_resolver_service import IssueToOfficeResolver
from app.services.edurev_advisor_service import AcademicBenefitAdvisor
from app.services.campus_map_service import CampusMapService
from app.services.actions.ums_service import UMSServiceResolver
from app.services.actions.workflow_engine import WorkflowEngine

logger = logging.getLogger(__name__)


class MultiDomainOrchestrator:
    @classmethod
    async def orchestrate(
        cls,
        query: str,
        db: AsyncSession,
        user_lat: Optional[float] = None,
        user_lon: Optional[float] = None,
        landmark: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Orchestrates multi-domain queries by running parallel entity resolution,
        identifying compound user intents, and assembling structured multi-domain output.
        """
        q_lower = query.lower().strip()

        # 1. Resolve domain entities
        food_card = CampusFoodService.search_food(query=query, user_lat=user_lat, user_lon=user_lon, landmark=landmark)
        person_card = PeopleDirectoryService.search_person(query)
        who_to_meet_card = IssueToOfficeResolver.resolve_issue(query)
        academic_benefit_card = AcademicBenefitAdvisor.assess_project(query)
        matched_place = await CampusMapService.find_matching_place(query, db)
        matched_svc = await UMSServiceResolver.find_matching_service(query, db)
        matched_wf = await WorkflowEngine.match_workflow(query, db)

        place_card = CampusMapService.build_place_card(matched_place) if matched_place else None
        nav_card = UMSServiceResolver.build_navigation_card(matched_svc) if matched_svc else None
        route_card = CampusMapService.resolve_campus_navigation(query=query, user_lat=user_lat, user_lon=user_lon, landmark=landmark)
        directory_card = CampusMapService.resolve_category_directory(query=query)

        # Count active domain hits
        active_domains: List[str] = []
        if food_card:
            active_domains.append("food")
        if person_card:
            active_domains.append("person")
        if who_to_meet_card:
            active_domains.append("who_to_meet")
        if academic_benefit_card:
            active_domains.append("edurev")
        if place_card:
            active_domains.append("place")
        if route_card:
            active_domains.append("route")
        if directory_card:
            active_domains.append("directory")
        if nav_card or matched_wf:
            active_domains.append("ums_service")

        # Specific compound checks
        has_hostel_and_fee = ("hostel" in q_lower) and ("fee" in q_lower or "fees" in q_lower or "challan" in q_lower)
        is_faculty_leadership = person_card and (person_card.person_id in ("CSE-001", "CSE-002", "CSE-004") or any(k in q_lower for k in ["hod", "dean", "leadership", "head"]))
        has_faculty_and_project = is_faculty_leadership and (academic_benefit_card or who_to_meet_card or "project" in q_lower)
        has_edurev_and_where = academic_benefit_card and (place_card or any(k in q_lower for k in ["where", "how", "submit", "apply", "benefit", "exemption", "criteria", "attendance", "ca"]))
        has_food_and_place = food_card and (place_card or "block 32" in q_lower or "block 34" in q_lower or "uni-mall" in q_lower)
        has_attendance_and_procedure = ("attendance" in q_lower) and ("procedure" in q_lower or "first contact" in q_lower or "who" in q_lower or "whom" in q_lower or "shortage" in q_lower or "incorrect" in q_lower)

        is_multi_domain = (
            len(active_domains) >= 2 or
            has_hostel_and_fee or
            has_faculty_and_project or
            has_edurev_and_where or
            has_food_and_place or
            has_attendance_and_procedure
        )

        if not is_multi_domain:
            return {
                "is_multi_domain": False,
                "food_card": food_card,
                "person_card": person_card,
                "who_to_meet_card": who_to_meet_card,
                "academic_benefit_card": academic_benefit_card,
                "place_card": place_card,
                "nav_card": nav_card,
                "matched_wf": matched_wf,
                "content": None
            }

        # Build compound multi-domain content
        sections: List[str] = []

        # Domain A: Dual UMS Pathways (Hostel + Fee)
        if has_hostel_and_fee:
            sections.append(
                "## 🌐 Multi-System UMS Pathways (Hostel & Fee Management)\n\n"
                "### 1. Hostel Management Pathway\n"
                "- **Navigation Path:** `UMS > Hostel Management > Apply Leave / Maintenance Request / Mess Change`\n"
                "- **Key Functions:** Apply for residential day/night leave, request room maintenance, and register mess preferences.\n"
                "- **In-Person Helpdesk:** Ground Floor Warden Office in your assigned hostel block (BH/GH) or Chief Warden Annex (Block 13).\n"
                "- **Prerequisite:** Ensure leave requests are submitted at least 24 hours prior to travel with parental SMS consent.\n\n"
                "### 2. Fee Management & Accounts Pathway\n"
                "- **Navigation Path:** `UMS > Fee Management > Fee Statements / Pay Fee / Download Challan`\n"
                "- **Key Functions:** Inspect active semester tuition fee balances, generate bank challans, and download official payment receipts.\n"
                "- **In-Person Helpdesk:** Ground Floor Accounts Wing, Block 34 (Executive Block).\n"
                "- **Discrepancy Resolution:** Allow 24–48 hours for online banking reconciliation before logging a payment dispute via UMS RMS."
            )
            if not nav_card:
                nav_card = NavigationCard(
                    service_title="Hostel & Fee Management Dual Navigation",
                    module="Hostel Management / Fee Management",
                    breadcrumb="UMS > Hostel Management / Fee Management",
                    instruction="Open UMS and navigate to the respective module for Hostel or Fee administration.",
                    handoff_url="https://ums.lpu.in/lpuums/"
                )

        # Domain B: Faculty / Leadership + Project Guidance
        elif has_faculty_and_project:
            p_name = person_card.full_name if person_card else "Dr. Mohit Arora"
            p_desig = person_card.designation if person_card else "Professor and HOD, School of Computer Science & Engineering"
            p_block = person_card.building_block if person_card else "Block 32"
            p_cabin = person_card.room_cabin if person_card else "Not Published (Consult School Office, Block 32 Ground Floor)"

            sections.append(
                f"## 👤 1. Academic Leadership & Office Location\n\n"
                f"- **Designated Official:** **{p_name}**\n"
                f"- **Official Title:** {p_desig}\n"
                f"- **Building / School:** {p_block} (School of Computer Science & Engineering)\n"
                f"- **Cabin / Office Status:** {p_cabin}\n"
                f"- **Statutory Clarification:** Dr. Mohit Arora leads the entire School of CSE. In LPU's academic organization, AI & ML is a domain specialization cluster, **not an independent department with a separate HOD**. Personal cabin seating is not published in the public directory; visit the Ground Floor School Office in Block 32 for appointments."
            )

            # Project Advice / Who to meet
            sections.append(
                "## 🚀 2. Whom to Meet About Your Academic Project\n\n"
                "- **Primary Guidance Point:** **Academic Benefits Coordinator (EDU-Revolution Cell)**\n"
                "- **In-Person Location:** **Block 27 Room 102 (Query & Assistance Zone)**\n"
                "- **Online UMS Route:** `UMS > Relationship Management System (RMS) > Edu-Revolution: Be the change > Apply for EDU Revolution`\n"
                "- **Mandatory Timeline:** Course substitution requests must be initiated within the **first 4 weeks of the active semester**.\n"
                "- **Prerequisites:** Working code repository (GitHub), live working deployment/demo, project architecture PDF, and mentor syllabus mapping endorsement.\n"
                "- **Escalation Ladder:** 1. EDU-Revolution Cell (Block 27 Room 102) ➔ 2. School Evaluation Committee (Viva) ➔ 3. Standing Academic Committee (SAC Ratification)."
            )

            # Ensure who_to_meet_card is attached for Block 27 Room 102
            if not who_to_meet_card:
                who_to_meet_card = IssueToOfficeResolver.resolve_issue("Where do I submit this project?")

        # Domain C: EDU-Revolution Benefits + Where & How to Apply
        elif has_edurev_and_where and academic_benefit_card:
            ev_list = "\n".join([f"  - {e}" for e in academic_benefit_card.evidence_checklist])
            lim_list = "\n".join([f"  - {lim}" for lim in academic_benefit_card.limitations_and_caveats])

            sections.append(
                f"## 🚀 1. EDU-Revolution Category Alignment & Potential Benefits\n\n"
                f"- **Assessed Category:** **{academic_benefit_card.category_id}: {academic_benefit_card.category_name}**\n"
                f"- **Portal Stage:** {academic_benefit_card.portal_stage_name}\n"
                f"- **Assessed Criteria:** {academic_benefit_card.matched_criteria}\n"
                f"- **Potential Academic Recognition:** {academic_benefit_card.eligible_academic_benefits}\n\n"
                f"- **Required Evidence Checklist:**\n{ev_list}\n\n"
                f"## 📍 2. Where & How to Submit (Online & In-Person)\n\n"
                f"- **Online UMS Submission Route:** `{academic_benefit_card.submission_route}`\n"
                f"- **Physical Assistance Desk:** **{academic_benefit_card.physical_helpdesk}**\n"
                f"- **Strict Submission Window:** **{academic_benefit_card.course_mapping_window}**\n"
                f"- **Approval Prerequisite:** {academic_benefit_card.approval_prerequisite}\n\n"
                f"## ⚠️ 3. Institutional Policy Caveats & Disclaimers\n\n"
                f"{lim_list}\n"
                f"- *{academic_benefit_card.guarantee_disclaimer}*\n"
                f"- *{academic_benefit_card.scrgm_distinction}*"
            )

            # Specific criteria for Attendance Benefits or CA Exemption from Academic Benefits Guide
            has_att_benefit_query = any(w in q_lower for w in ["attendance", "duty leave", "dl", "shortage"])
            has_ca_benefit_query = any(w in q_lower for w in ["ca exemption", "continuous assessment", "ca benefit", "exam exemption"])

            if has_att_benefit_query or has_ca_benefit_query:
                specific_subsections = []
                if has_att_benefit_query:
                    specific_subsections.append(
                        "### 📋 Attendance Benefits Under EDU-Revolution (Statutory Criteria)\n"
                        "- **Competitive Exams (Clause 11):** Up to **10% attendance benefit** across courses in active semester for appearing in/preparing for GATE, CAT, UPSC Civil Services, GRE, GMAT, or verified corporate recruitment drives. Requires verified exam admit card submitted on UMS LMS.\n"
                        "- **Duty Leave (DL) Policy (Clause 12):** **100% attendance credit** (marked present) for officially sanctioned dates when representing LPU in national/international hackathons, sports, or technical competitions. Must be sanctioned within 7 days of event.\n"
                        "- **Earn Your Fee / Revenue Generation (Clause 4):** Up to **15% overall attendance benefit** for registered student ventures or verified external revenue.\n"
                        "- **Debarment Limit:** Overall attendance below 65% after all condonations cannot be waived."
                    )
                if has_ca_benefit_query:
                    specific_subsections.append(
                        "### 📝 Continuous Assessment (CA) Exemption & Course Substitution\n"
                        "- **Innovative AI / Systems (CAT-02):** Functional, original software platforms or AI solutions can substitute for Continuous Assessment (CA) components, Term Paper, or Capstone Project upon School Evaluation Committee viva demonstration.\n"
                        "- **Hackathons & Competitions (CAT-04):** Winners or top finalists in recognized national/international hackathons (Smart India Hackathon, ICPC) are eligible for CA relaxation and specialized technical elective credits.\n"
                        "- **Mandatory Window:** Must apply within the **first 4 weeks of the active semester** with mentor syllabus mapping."
                    )
                if specific_subsections:
                    sections.append("\n\n".join(specific_subsections))

        # Domain D: Food Discovery + Place (Block 32 / Campus Hub)
        elif has_food_and_place and food_card:
            warning_line = f"\n⚠️ **Provenance Notice:** {food_card.verification_notice}\n" if food_card.verification_notice else ""
            dist_str = f"Approx {food_card.distance_meters}m" if food_card.distance_meters else "On-site"

            sections.append(
                f"## 🍽️ 1. Verified Food Outlets Near Block 32\n\n"
                f"- **Recommended Outlet:** **{food_card.display_name}** ({food_card.zone})\n"
                f"- **Exact Location:** {food_card.location_description}\n"
                f"- **Straight-Line Proximity:** {dist_str} (straight-line radius; walking distance depends on campus pathways)\n"
                f"- **Operating Hours:** {food_card.opening_hours} (Status: {food_card.open_status.upper()})\n"
                f"- **Menu Matches:** {', '.join(food_card.matched_items) if food_card.matched_items else 'Pure vegetarian items'}\n"
                f"- **Sample Price:** {food_card.price_sample or 'Standard pricing'}\n"
                f"- **Dietary Policy:** 100% Pure Vegetarian campus mandate.\n"
                f"- **Evidence Status:** `{food_card.evidence_status}`\n"
                f"{warning_line}"
            )

            if place_card:
                sections.append(
                    f"## 🏢 2. About {place_card.name}\n\n"
                    f"- **Building:** {place_card.building}\n"
                    f"- **Description:** {place_card.description}\n"
                    f"- **Services Available:** {', '.join(place_card.services)}\n"
                    f"- **Accessibility:** {place_card.accessibility or 'Elevators and wheelchair ramps available at entrance'}"
                )

        # Domain E: Attendance Discrepancy + Procedure + First Contact
        elif has_attendance_and_procedure and who_to_meet_card:
            doc_lines = "\n".join([f"  - {d}" for d in who_to_meet_card.required_documents])
            ladder = " ➔ ".join(who_to_meet_card.escalation_ladder)

            sections.append(
                f"## 📋 1. Attendance Discrepancy Procedure & First Contact\n\n"
                f"- **First Point of Contact:** **{who_to_meet_card.primary_contact_role}**\n"
                f"- **Office Location:** {who_to_meet_card.office_location} — {who_to_meet_card.room_details}\n"
                f"- **Mandatory First Step (Prerequisite):** {who_to_meet_card.prerequisite_action}\n\n"
                f"- **Required Supporting Documents:**\n{doc_lines}\n\n"
                f"## 🪜 2. Statutory Escalation Ladder\n\n"
                f"{ladder}\n\n"
                f"- **Official UMS Route:** `{who_to_meet_card.ums_navigation_path}`\n"
                f"- **Evidence Status:** `{who_to_meet_card.evidence_status}`"
            )

        multi_domain_content = "\n\n".join(sections) if sections else None

        return {
            "is_multi_domain": bool(multi_domain_content),
            "food_card": food_card,
            "person_card": person_card,
            "who_to_meet_card": who_to_meet_card,
            "academic_benefit_card": academic_benefit_card,
            "place_card": place_card,
            "route_card": route_card,
            "directory_card": directory_card,
            "nav_card": nav_card,
            "matched_wf": matched_wf,
            "content": multi_domain_content
        }
