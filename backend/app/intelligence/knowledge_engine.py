import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.rag.hybrid_search import hybrid_search_engine
from app.services.orchestration.multi_domain_orchestrator import MultiDomainOrchestrator
from app.services.weather_service import WeatherService
from app.schemas.chat import Citation

logger = logging.getLogger(__name__)


class KnowledgeRetrievalResult:
    def __init__(
        self,
        evidence_context: str,
        citations: List[Dict[str, Any]],
        action_cards: Dict[str, Any],
        confidence_score: float,
        retrieval_strategy: str
    ):
        self.evidence_context = evidence_context
        self.citations = citations
        self.action_cards = action_cards
        self.confidence_score = confidence_score
        self.retrieval_strategy = retrieval_strategy


class KnowledgeEngine:
    """
    LAYER 4 — KNOWLEDGE ENGINE
    Interfaces with PostgreSQL, hybrid search (dense + BM25), multi-domain campus entities,
    and student contextual records.
    """

    @classmethod
    async def retrieve(
        cls,
        query: str,
        db: Optional[AsyncSession] = None,
        user_lat: Optional[float] = None,
        user_lon: Optional[float] = None,
        landmark: Optional[str] = None,
        category_slug: Optional[str] = None,
        thinking_level: str = "Balanced"
    ) -> KnowledgeRetrievalResult:
        if db is None:
            from app.core.database import AsyncSessionLocal
            async with AsyncSessionLocal() as session:
                return await cls._retrieve_internal(
                    query=query,
                    db=session,
                    user_lat=user_lat,
                    user_lon=user_lon,
                    landmark=landmark,
                    category_slug=category_slug,
                    thinking_level=thinking_level
                )
        return await cls._retrieve_internal(
            query=query,
            db=db,
            user_lat=user_lat,
            user_lon=user_lon,
            landmark=landmark,
            category_slug=category_slug,
            thinking_level=thinking_level
        )

    @classmethod
    async def _retrieve_internal(
        cls,
        query: str,
        db: AsyncSession,
        user_lat: Optional[float] = None,
        user_lon: Optional[float] = None,
        landmark: Optional[str] = None,
        category_slug: Optional[str] = None,
        thinking_level: str = "Balanced"
    ) -> KnowledgeRetrievalResult:
        top_k = 3 if thinking_level == "Low" else (5 if thinking_level == "Balanced" else 8)

        # 1. Calibrated hybrid search across 1035 institutional records
        search_res = await hybrid_search_engine.search(
            query=query,
            db=db,
            category_slug=category_slug,
            top_k=top_k
        )
        candidates = search_res.get("candidates", [])
        citations_data = search_res.get("citations", [])
        evidence_text = search_res.get("evidence_context", "")
        confidence_eval = search_res.get("confidence")
        conf_score = confidence_eval.score if confidence_eval else 0.85

        # 2. Multi-domain entity resolution (Places, Food, Faculty, Who-to-Meet, Benefits)
        multi_domain_res = await MultiDomainOrchestrator.orchestrate(
            query=query,
            db=db,
            user_lat=user_lat,
            user_lon=user_lon,
            landmark=landmark
        )

        cards: Dict[str, Any] = {
            "food_card": multi_domain_res.get("food_card"),
            "person_card": multi_domain_res.get("person_card"),
            "who_to_meet_card": multi_domain_res.get("who_to_meet_card"),
            "academic_benefit_card": multi_domain_res.get("academic_benefit_card"),
            "place_card": multi_domain_res.get("place_card"),
            "route_card": multi_domain_res.get("route_card"),
            "directory_card": multi_domain_res.get("directory_card"),
            "nav_card": multi_domain_res.get("nav_card"),
        }

        # If campus navigation route resolved, append verified pedestrian path details
        rc = cards.get("route_card")
        if rc:
            step_lines = "\n".join([f"  {s.step}. {s.instruction} ({s.distance_meters}m)" for s in rc.turn_by_turn_steps])
            evidence_text += (
                f"\n\n[CAMPUS PEDESTRIAN ROUTE]:\n"
                f"- Origin: {rc.origin_name}\n"
                f"- Destination: {rc.destination_name}\n"
                f"- Walking Distance: {rc.walking_distance_meters} meters (Walking duration: ~{rc.estimated_duration_minutes} min at 1.2 m/s)\n"
                f"- Straight-Line Distance: {rc.straight_line_distance_meters} meters\n"
                f"- Verified Pedestrian Walkway: {rc.is_pedestrian_path_verified}\n"
                f"- Turn-by-Turn Navigation Available: {rc.turn_by_turn_available}\n"
                f"- Accessibility: {rc.accessibility_notes}\n"
                f"- Steps:\n{step_lines}"
            )

        # If campus place card resolved, append verified block info
        pc = cards.get("place_card")
        if pc:
            evidence_text += (
                f"\n\n[CAMPUS PLACE VERIFIED INFO]:\n"
                f"- Name: {pc.name}\n"
                f"- Block: {pc.block_number or pc.building}\n"
                f"- Category: {pc.category}\n"
                f"- Zone: {pc.campus_zone}\n"
                f"- Verification Status: {pc.verification_status}\n"
                f"- Accessibility: {pc.accessibility_information}\n"
                f"- Facilities: {', '.join(pc.verified_facilities)}\n"
                f"- Description: {pc.building_description or pc.description}\n"
                f"- Discrepancy Note: {pc.discrepancy_note or 'None'}"
            )

        # If weather query, include live weather info
        if any(w in query.lower() for w in ["weather", "temperature", "rain", "forecast"]):
            w_info = await WeatherService.get_current_weather(lat=user_lat, lon=user_lon)
            evidence_text += f"\n\n[WEATHER INFO]: Temperature {w_info['temperature_c']}°C, {w_info['weather_condition']}, {w_info['campus_activity_advice']}"

        return KnowledgeRetrievalResult(
            evidence_context=evidence_text,
            citations=citations_data,
            action_cards=cards,
            confidence_score=conf_score,
            retrieval_strategy=f"hybrid_calibrated_{thinking_level.lower()}"
        )
