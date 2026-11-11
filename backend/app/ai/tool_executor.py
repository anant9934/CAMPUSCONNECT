import logging
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.campus_food_service import CampusFoodService
from app.services.people_directory_service import PeopleDirectoryService
from app.services.edurev_advisor_service import AcademicBenefitAdvisor
from app.services.issue_resolver_service import IssueToOfficeResolver
from app.services.campus_map_service import CampusMapService
from app.services.actions.ums_service import UMSServiceResolver
from app.services.actions.workflow_engine import WorkflowEngine
from app.services.rag.hybrid_search import hybrid_search_engine
from app.services.attendance_solver_service import AttendanceSolverService
from app.services.authority_service import UniversityAuthorityService

logger = logging.getLogger(__name__)


class ToolExecutor:
    """
    Executes authorized backend tools deterministically and aggregates
    institutional evidence and UI action cards for the LLM reasoning pipeline.
    """

    @classmethod
    async def execute_all_relevant_tools(
        cls,
        query: str,
        db: AsyncSession,
        user_lat: Optional[float] = None,
        user_lon: Optional[float] = None,
        landmark: Optional[str] = None,
        category_slug: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Executes domain analyzers in parallel / sequence and collects:
        - action_cards (Food, Person, WhoToMeet, BenefitAssessment, CampusPlace, Navigation)
        - evidence_context (formatted textual facts for Gemini)
        - citations (structured source citations)
        - confidence_eval (RAG confidence assessment)
        """
        q_lower = query.lower()

        # 1. Food Discovery
        food_card = None
        food_keywords = ["food", "chaap", "eat", "cafe", "restaurant", "canteen", "lunch", "dinner", "snack", "thali", "dosa", "pizza", "coffee", "tadka"]
        if any(k in q_lower for k in food_keywords):
            food_card = CampusFoodService.search_food(
                item_query=query,
                user_lat=user_lat,
                user_lon=user_lon,
                landmark_preference=landmark
            )

        # 2. People & Experts
        person_card = None
        people_keywords = ["who", "whom", "faculty", "hod", "dean", "professor", "mentor", "dr.", "arora", "sobti", "singh", "sharma", "rawat", "guide", "teacher", "cabin", "seating"]
        if any(k in q_lower for k in people_keywords):
            person_card = PeopleDirectoryService.search_person(query)

        # 3. Academic Benefits & EDU-Revolution
        benefit_card = AcademicBenefitAdvisor.assess_project(query)

        # 4. Issue & Grievance Routing (Who to Meet)
        issue_card = IssueToOfficeResolver.resolve_issue(query)

        # 5. Campus POIs & Map
        place_card = await CampusMapService.find_matching_place(query, db)

        # 6. UMS Service Catalog & Action Workflows
        matched_svc = await UMSServiceResolver.find_matching_service(query, db)
        matched_wf = await WorkflowEngine.match_workflow(query, db)
        nav_card = None
        if matched_svc:
            nav_card = UMSServiceResolver.build_navigation_card(matched_svc)
        elif matched_wf:
            nav_card = WorkflowEngine.build_booking_card(matched_wf) if matched_wf.is_transactional else None

        # 7. Attendance Solver Analysis
        attendance_facts = None
        if AttendanceSolverService.is_attendance_query(query):
            att_eval = AttendanceSolverService.solve(query)
            attendance_facts = (
                f"[ATTENDANCE POLICY & PROBLEM SOLVER EVIDENCE]\n"
                f"- Statutory Policy: 75% minimum mandatory attendance in each course for ETE eligibility. Condonation up to 10% permitted down to 65% statutory floor.\n"
                f"- Key Distinction: Revenue Generation attendance benefits (EDU-Rev / SCRGM) apply to active commercial startups and require SAC committee ratification; separate from the 10% Institutional Condonation / Duty Leave for sports, cultural events, or hospitalization.\n"
                f"- Official Routes:\n"
                f"  1. UMS Duty Leave (within 7 calendar days of event completion with mentor sign-off).\n"
                f"  2. Medical Leave (Uni-Hospital Block 30 / CMO certified within 3 working days).\n"
                f"  3. Biometric Audit (Class Mentor & Academic Coordinator Dr. Dalwinder Singh, Block 32 School Office).\n"
                f"- Anti-Fraud Rule: Strictly prohibit manufacturing fake revenue or false medical certificates under Section 12 of Student Code of Conduct (Gross Misconduct -> Proctorial Board).\n"
                f"- Contact Office: Ground Floor School Office / Reception, Block 32 (Dr. Dalwinder Singh / Dr. Mohit Arora; 3:00 PM - 5:00 PM)."
            )

        # 8. University Authority & Appointment Intelligence
        authority_facts = None
        if UniversityAuthorityService.is_authority_query(query):
            auth_eval = UniversityAuthorityService.resolve_authority(query)
            authority_facts = (
                f"[UNIVERSITY AUTHORITY & APPOINTMENT GUIDANCE EVIDENCE]\n"
                f"- Authority: {auth_eval.authority_name} ({auth_eval.official_designation})\n"
                f"- Scope: {auth_eval.responsibility_scope}\n"
                f"- Office Location: {auth_eval.office_location}\n"
                f"- Meeting Protocol: Official appointment token / scheduled request dossier required; direct unscheduled walk-ins strictly restricted.\n"
                f"- Escalation Ladder: {' -> '.join(auth_eval.hierarchical_escalation_ladder)}\n"
                f"- Appeal & Grievance Channel: {auth_eval.grievance_or_appeal_channel}\n"
                f"- Confidentiality: {auth_eval.confidentiality_notice}\n"
                f"- Warning: Never attempt to bypass hierarchical tiers or Proctorial disciplinary inquiries."
            )

        # 9. Hybrid RAG Search over Official Knowledge
        rag_res = await hybrid_search_engine.search(
            query=query,
            db=db,
            category_slug=category_slug,
            top_k=4
        )

        candidates = rag_res["candidates"]
        confidence_eval = rag_res["confidence"]
        citations = rag_res["citations"]
        evidence_text = rag_res["evidence_context"]

        # Synthesize collected structured tool facts into evidence_text for Gemini
        tool_facts = []

        if food_card and food_card.query_match_status == "exact":
            tool_facts.append(
                f"[CAMPUS FOOD OUTLET EVIDENCE]\n"
                f"- Name: {food_card.display_name} ({food_card.zone})\n"
                f"- Location: {food_card.location_description}\n"
                f"- Distance: Approx {food_card.distance_meters}m (straight-line radius)\n"
                f"- Hours: {food_card.opening_hours} (Status: {food_card.open_status.upper()})\n"
                f"- Verified Menu Items: {', '.join(food_card.matched_items)}\n"
                f"- Sample Price: {food_card.price_sample or 'Standard pricing'}\n"
                f"- Policy: 100% Pure Vegetarian campus mandate. Non-veg strictly prohibited.\n"
                f"- Evidence Status: {food_card.evidence_status}"
            )

        if person_card:
            tool_facts.append(
                f"[FACULTY & LEADERSHIP DIRECTORY EVIDENCE]\n"
                f"- Name: {person_card.full_name}\n"
                f"- Title: {person_card.designation}\n"
                f"- School/Division: {person_card.school_division}\n"
                f"- Building: {person_card.building_block}\n"
                f"- Cabin/Seating: {person_card.room_cabin} (Verified: {person_card.office_seating_verified})\n"
                f"- Institutional Note: {person_card.notes}\n"
                f"- Seating Guidance: Personal cabin numbers are not published in public directories. Direct student to Ground Floor School Office / Reception in Block 32 for current cabin assignments."
            )

        if benefit_card:
            tool_facts.append(
                f"[EDU-REVOLUTION ACADEMIC BENEFITS EVIDENCE]\n"
                f"- Assessed Category: {benefit_card.category_id} ({benefit_card.category_name})\n"
                f"- Portal Stage: {benefit_card.portal_stage_name}\n"
                f"- Criteria: {benefit_card.matched_criteria}\n"
                f"- Potential Benefits: {benefit_card.eligible_academic_benefits}\n"
                f"- Missing Requirements: {', '.join(benefit_card.missing_evidence) if benefit_card.missing_evidence else 'None'}\n"
                f"- Submission Channel: {benefit_card.submission_route}\n"
                f"- Helpdesk: {benefit_card.physical_helpdesk}\n"
                f"- Mandatory Window: Must apply within the first 4 weeks of active semester.\n"
                f"- Statutory Caveats: Requires School Evaluation Committee viva and Standing Academic Committee (SAC) ratification. No automatic marks or waivers are guaranteed. SCRGM commercial revenue is distinct."
            )

        if issue_card:
            tool_facts.append(
                f"[WHO-TO-MEET & ISSUE ROUTING EVIDENCE]\n"
                f"- Issue Category: {issue_card.category_title}\n"
                f"- First Point of Contact: {issue_card.primary_contact_role}\n"
                f"- Physical Location: {issue_card.office_location} ({issue_card.room_details})\n"
                f"- Prerequisite Action: {issue_card.prerequisite_action}\n"
                f"- Required Documents: {', '.join(issue_card.required_documents)}\n"
                f"- Escalation Ladder: {' -> '.join(issue_card.escalation_ladder)}\n"
                f"- Online UMS Route: {issue_card.ums_navigation_path}"
            )

        if place_card:
            tool_facts.append(
                f"[CAMPUS PLACE EVIDENCE]\n"
                f"- Place Name: {place_card.name}\n"
                f"- Building Block: {place_card.building}\n"
                f"- Coordinates: {place_card.latitude}, {place_card.longitude}\n"
                f"- Description: {place_card.description}\n"
                f"- Services: {', '.join(place_card.services)}"
            )

        if nav_card:
            tool_facts.append(
                f"[UMS NAVIGATION EVIDENCE]\n"
                f"- Service Title: {nav_card.service_title}\n"
                f"- Breadcrumb Path: {nav_card.breadcrumb}\n"
                f"- Instructions: {nav_card.instruction}\n"
                f"- Official Handoff URL: {nav_card.handoff_url}"
            )

        if attendance_facts:
            tool_facts.append(attendance_facts)

        if authority_facts:
            tool_facts.append(authority_facts)

        # Merge tool facts into unified evidence text
        combined_evidence = "\n\n".join(tool_facts)
        if evidence_text:
            combined_evidence = f"{combined_evidence}\n\n[OFFICIAL INSTITUTIONAL POLICIES & NOTICES]\n{evidence_text}" if combined_evidence else evidence_text

        return {
            "food_card": food_card,
            "person_card": person_card,
            "academic_benefit_card": benefit_card,
            "who_to_meet_card": issue_card,
            "place_card": place_card,
            "nav_card": nav_card,
            "matched_wf": matched_wf,
            "candidates": candidates,
            "confidence": confidence_eval,
            "citations": citations,
            "evidence_context": combined_evidence
        }
