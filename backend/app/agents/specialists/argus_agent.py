import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base_agent import BaseSpecialistAgent
from app.agents.agent_registry import AgentRegistry
from app.schemas.agent import AgentOutput
from app.services.people_directory_service import PeopleDirectoryService
from app.services.campus_map_service import CampusMapService
from app.services.campus_food_service import CampusFoodService
from app.services.issue_resolver_service import IssueToOfficeResolver

logger = logging.getLogger(__name__)


class ArgusAgent(BaseSpecialistAgent):
    """
    ARGUS — Faculty, Leadership, Experts & Campus Intelligence Specialist.
    Finds faculty seating, consultation hours (3:00 PM - 5:00 PM), physical wayfinding,
    and 100% pure vegetarian campus dining outlets.
    """

    def __init__(self):
        definition = AgentRegistry.get_agent("argus")
        if not definition:
            raise RuntimeError("ARGUS agent definition not found in registry")
        super().__init__(definition)

    async def run(
        self,
        query: str,
        context: Dict[str, Any],
        db: AsyncSession,
        **kwargs
    ) -> AgentOutput:
        q_lower = query.lower()
        findings: List[str] = []
        cards: Dict[str, Any] = {}
        citations: List[Dict[str, Any]] = []

        # 1. Faculty / Person Directory Lookup
        person_card = PeopleDirectoryService.search_person(query)
        if person_card:
            cards["person_card"] = person_card.model_dump()
            citations.append({
                "title": f"LPU Directory — {person_card.full_name}",
                "url": "https://www.lpu.in",
                "source_type": "Official Faculty Directory",
                "verified": True,
                "snippet": f"{person_card.full_name} — {person_card.designation}, {person_card.school_division}"
            })
            email_info = f"\n- **Email:** {person_card.email}" if person_card.email else ""
            findings.append(
                f"👤 **{person_card.full_name}** ({person_card.designation})\n"
                f"- **School / Division:** {person_card.school_division}\n"
                f"- **Location:** {person_card.building_block} — {person_card.room_cabin}\n"
                f"- **Consultation Hours:** 3:00 PM – 5:00 PM (Working days){email_info}\n"
                f"- **Note:** {person_card.notes}"
            )

        # 2. Campus Place / Spatial POI Lookup
        place_match = await CampusMapService.find_matching_place(query, db)
        if place_match:
            place_card = CampusMapService.build_place_card(place_match)
            cards["campus_place_card"] = place_card.model_dump()
            citations.append({
                "title": f"LPU Campus Wayfinding — {place_card.name}",
                "url": place_card.map_url,
                "source_type": "Official Campus Map",
                "verified": True,
                "snippet": f"{place_card.name} located at {place_card.building}"
            })
            findings.append(
                f"📍 **{place_card.name}**\n"
                f"- **Building:** {place_card.building} ({place_card.floor_room or 'Ground Floor'})\n"
                f"- **Details:** {place_card.description}\n"
                f"- **Hours:** {place_card.opening_hours}"
            )

        # 3. Pure-Veg Dining Discovery
        user_lat = context.get("user_lat")
        user_lon = context.get("user_lon")
        food_res = CampusFoodService.search_food(
            query=query,
            user_lat=user_lat,
            user_lon=user_lon,
            landmark=context.get("landmark")
        )
        if food_res and food_res.query_match_status == "exact":
            cards["food_outlet_card"] = food_res.model_dump()
            citations.append({
                "title": f"LPU Dining — {food_res.display_name}",
                "url": "https://www.lpu.in/about_lpu/campus-facilities.php",
                "source_type": "Official Dining Directory",
                "verified": True,
                "snippet": f"100% Pure Veg: {food_res.display_name} at {food_res.location_description}"
            })
            findings.append(
                f"🍽️ **{food_res.display_name}** ({food_res.zone})\n"
                f"- **Location:** {food_res.location_description}\n"
                f"- **Hours:** {food_res.opening_hours} ({food_res.open_status.upper()})\n"
                f"- **Specialty:** {', '.join(food_res.matched_items)}\n"
                f"- **Policy:** 100% Pure Vegetarian campus mandate."
            )

        # 4. Issue-to-Office & Leadership Escalation Routing
        who_card = IssueToOfficeResolver.resolve_issue(query)
        if who_card and any(k in q_lower for k in ["meet", "who to", "whom", "escalat", "shortage", "dispute"]):
            cards["who_to_meet_card"] = who_card.model_dump()
            findings.append(
                f"🏛️ **{who_card.category_title}**\n"
                f"- **Primary Contact:** {who_card.primary_contact_role}\n"
                f"- **Office Location:** {who_card.office_location} — {who_card.room_details}\n"
                f"- **Escalation Path:** {' ➔ '.join(who_card.escalation_ladder)}"
            )

        structured_text = "\n\n".join(findings) if findings else "Campus intelligence checked."

        return AgentOutput(
            agent_id=self.id,
            success=True,
            findings=structured_text,
            structured_data={
                "has_person": person_card is not None,
                "has_place": place_match is not None,
                "has_food": food_res is not None,
            },
            citations=citations,
            cards=cards,
            confidence=0.97 if findings else 0.80,
            model_used=self.definition.primary_model.model_id,
            provider_used=self.definition.primary_model.provider
        )
