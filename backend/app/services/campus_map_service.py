import csv
import json
import logging
import os
import re
from typing import List, Optional, Dict, Any
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.campus_place import CampusPlace
from app.schemas.ums import CampusPlaceCard
from app.schemas.campus_navigation import (
    CampusRouteCard,
    CampusBlockDirectoryCard,
    CampusDirectoryItem,
    NavigationStep
)
from app.services.campus_place_directory import CampusPlaceDirectory
from app.services.campus_routing_engine import CampusRoutingEngine, haversine_distance_meters, CAMPUS_GRAPH_NODES

logger = logging.getLogger(__name__)


class PlaceWrapper:
    """Wrapper that adapts dictionary records to CampusPlace interface."""
    def __init__(self, data: Dict[str, Any]):
        self.place_id = data.get("place_id", "")
        self.name = data.get("official_name") or data.get("name", "")
        self.official_name = data.get("official_name") or data.get("name", "")
        self.block_number = data.get("block_number")
        self.building = data.get("building") or (f"Block {self.block_number}" if self.block_number else self.name)
        self.category = data.get("category", "Academic")
        self.building_description = data.get("building_description") or data.get("description", "")
        self.description = self.building_description
        self.campus_zone = data.get("campus_zone", "Central Academic Zone")
        self.floor_room = data.get("floor_room")
        self.floors = data.get("floors", [])
        self.rooms = data.get("rooms", [])
        self.facilities = data.get("facilities", [])
        self.services_available = data.get("services_available") or self.facilities
        self.latitude = data.get("latitude")
        self.longitude = data.get("longitude")
        self.coordinate_source = data.get("coordinate_source", "CAMPUS_CENTROID_ESTIMATE")
        self.coordinate_verification_status = data.get("coordinate_verification_status", "APPROXIMATE_DIAGRAM_PIN")
        self.accessibility = data.get("accessibility") or data.get("accessibility_information")
        self.accessibility_information = data.get("accessibility_information") or self.accessibility
        self.opening_hours = data.get("opening_hours", "Mon-Sat: 8:30 AM - 5:30 PM")
        self.nearby_places = data.get("nearby_places", [])
        self.official_source = data.get("official_source", "Official LPU Campus Directory")
        self.source_date = data.get("source_date", "2026-11-18")
        self.verification_status = data.get("verification_status", "USER_SUPPLIED_MAP_PENDING_VERIFICATION")
        self.discrepancy_note = data.get("discrepancy_note")
        self.official_map_url = "https://www.lpu.in/about_lpu/campus-tour.php"
        self.building_purpose = data.get("building_purpose")
        self.actual_office_service = data.get("actual_office_service")
        self.room_verification_status = data.get("room_verification_status", "VERIFIED_ROOM")
        self.evidence_status = data.get("evidence_status", "OFFICIAL_CURRENT_VERIFIED")


class CampusMapService:
    """
    Campus Wayfinding and Navigation Service for Lovely Professional University.
    Integrates 55-location master directory, pedestrian shortest-path routing,
    and category directory lookups.
    """

    _csv_places: Optional[List[Dict[str, Any]]] = None

    @classmethod
    def _load_csv_places(cls) -> List[Dict[str, Any]]:
        if cls._csv_places is not None:
            return cls._csv_places

        candidates = [
            os.path.join(os.getcwd(), "data", "campus_office_place_directory.csv"),
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "campus_office_place_directory.csv"),
        ]
        file_path = None
        for c in candidates:
            if os.path.exists(c):
                file_path = c
                break

        places = []
        if file_path:
            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        services = json.loads(row.get("services_available", "[]"))
                    except Exception:
                        services = [row.get("services_available", "")]

                    places.append({
                        "place_id": row.get("place_id"),
                        "name": row.get("name"),
                        "place_type": row.get("place_type"),
                        "building_block": row.get("building_block"),
                        "building_purpose": row.get("building_purpose"),
                        "actual_office_service": row.get("actual_office_service"),
                        "floor_room": row.get("floor_room"),
                        "room_verification_status": row.get("room_verification_status", "VERIFIED_ROOM"),
                        "latitude": float(row.get("latitude", 31.2548)),
                        "longitude": float(row.get("longitude", 75.7032)),
                        "coordinates_verification_status": row.get("coordinates_verification_status", "CAMPUS_CENTROID_ESTIMATE"),
                        "pedestrian_paths": row.get("pedestrian_paths"),
                        "accessibility": row.get("accessibility"),
                        "opening_hours": row.get("opening_hours"),
                        "services_available": services,
                        "source": row.get("source"),
                        "evidence_status": row.get("evidence_status", "OFFICIAL_CURRENT_VERIFIED"),
                        "validation_date": row.get("validation_date"),
                        "is_active": row.get("is_active") == "True",
                    })
        cls._csv_places = places
        return places

    @classmethod
    async def find_matching_place(
        cls,
        query: str,
        db: Optional[AsyncSession] = None
    ) -> Optional[Any]:
        """Matches a user query to a verified campus place in directory or database."""
        q = query.lower().strip()

        # 1. Exact block pattern extraction e.g. "Block 32", "blk 32", "Block 14"
        block_match = re.search(r"\b(?:block|blk|b)\s*([0-9]{1,2})\b", q)
        if block_match:
            bnum = block_match.group(1)
            p = CampusPlaceDirectory.get_by_block_number(bnum)
            if p:
                return PlaceWrapper(p)

        # 2. Key named campus landmarks
        if "chancellor" in q or "vc office" in q:
            p = CampusPlaceDirectory.get_by_block_number("30")
            if p:
                return PlaceWrapper(p)
        if "central administrative block" in q or "administrative block" in q and "31" not in q:
            p = CampusPlaceDirectory.get_by_block_number("32")
            if p:
                return PlaceWrapper(p)
        if "academic block 1" in q or "ab 1" in q or "agriculture" in q:
            p = CampusPlaceDirectory.get_by_block_number("53")
            if p:
                return PlaceWrapper(p)
        if "academic block 2" in q or "ab 2" in q:
            p = CampusPlaceDirectory.get_by_block_number("54")
            if p:
                return PlaceWrapper(p)
        if "academic block 3" in q or "ab 3" in q:
            p = CampusPlaceDirectory.get_by_block_number("55")
            if p:
                return PlaceWrapper(p)
        if "boys hostel 4" in q or "bh4" in q:
            p = CampusPlaceDirectory.get_by_block_number("46")
            if p:
                return PlaceWrapper(p)
        if "girls hostel 1" in q or "gh1" in q:
            p = CampusPlaceDirectory.get_by_block_number("09")
            if p:
                return PlaceWrapper(p)
        if "school of law" in q or "moot court" in q:
            p = CampusPlaceDirectory.get_by_block_number("21")
            if p:
                return PlaceWrapper(p)
        if "school of films" in q or "journalism" in q or "film school" in q:
            p = CampusPlaceDirectory.get_by_block_number("19")
            if p:
                return PlaceWrapper(p)
        if "hospital" in q or "unihospital" in q or "emergency" in q or "casualty" in q:
            p = CampusPlaceDirectory.get_by_block_number("08")
            if p:
                return PlaceWrapper(p)
        if "unimall" in q or "mall" in q and "mall-ii" not in q:
            p = CampusPlaceDirectory.get_by_block_number("15")
            if p:
                return PlaceWrapper(p)
        if "library" in q or "radhakrishnan" in q:
            p = CampusPlaceDirectory.get_by_block_number("14")
            if p:
                return PlaceWrapper(p)
        if "main gate" in q or "gt road" in q or "nh1" in q:
            p = CampusPlaceDirectory.get_by_place_id("GATE-01")
            if p:
                return PlaceWrapper(p)
        if "gurudwara" in q:
            p = CampusPlaceDirectory.get_by_place_id("LANDMARK-GURUDWARA")
            if p:
                return PlaceWrapper(p)

        # 3. Search Master Campus Place Directory by ranking
        matches = CampusPlaceDirectory.search_places(query)
        if matches:
            return PlaceWrapper(matches[0])

        # 4. Check CSV Directory
        csv_places = cls._load_csv_places()
        for cp in csv_places:
            if cp["place_id"] == "PLC-003" and ("102" in q or "edu-revolution" in q):
                return PlaceWrapper(cp)
            if cp["place_id"] == "PLC-010" and ("100" in q or "dsr" in q):
                return PlaceWrapper(cp)
            if cp["place_id"] == "PLC-011" and ("308" in q or "dia" in q):
                return PlaceWrapper(cp)
            if cp["place_id"] == "PLC-001" and ("32" in q):
                return PlaceWrapper(cp)

        # 5. Fallback to SQLite DB if session passed
        if db:
            stmt = select(CampusPlace)
            res = await db.execute(stmt)
            places = res.scalars().all()
            for p in places:
                if (p.block_number and p.block_number.lower() in q) or (p.name and p.name.lower() in q):
                    return p

        return None

    @classmethod
    def resolve_campus_navigation(
        cls,
        query: str,
        user_lat: Optional[float] = None,
        user_lon: Optional[float] = None,
        landmark: Optional[str] = None
    ) -> Optional[CampusRouteCard]:
        """
        Parses origin and destination from student prompt or user context,
        and computes verified pedestrian route via Dijkstra routing engine.
        """
        q = query.lower().strip()

        # Check if query is asking for navigation/routing
        nav_triggers = [
            "take me to", "take me from", "how do i reach", "how to reach",
            "how to go to", "directions to", "directions from", "route to",
            "route from", "navigate to", "path to", "way to", "walk to",
            "from block", "to block", "kaise jaye", "kahan se", "rasta"
        ]
        is_nav_query = any(t in q for t in nav_triggers)

        if not is_nav_query:
            return None

        origin_str: Optional[str] = None
        dest_str: Optional[str] = None

        # Pattern 1: "take me from X to Y" or "from X to Y"
        m1 = re.search(r"(?:from|start at|starting from|i am at)\s+([^,]+?)\s+(?:take me to|to|reach|go to)\s+(.+)", q)
        if m1:
            origin_str = m1.group(1).strip()
            dest_str = m1.group(2).strip()

        # Pattern 2: "how do i reach Y from X"
        m2 = re.search(r"how (?:do i|to) reach\s+(.+?)\s+from\s+(.+)", q)
        if m2:
            dest_str = m2.group(1).strip()
            origin_str = m2.group(2).strip()

        # Pattern 3: "take me to Y" or "directions to Y" (origin is implicit: user location / landmark / main gate)
        if not dest_str:
            m3 = re.search(r"(?:take me to|directions to|route to|navigate to|way to|how to reach|reach)\s+(.+)", q)
            if m3:
                dest_str = m3.group(1).strip()
                if landmark:
                    origin_str = landmark
                elif user_lat and user_lon:
                    # Find closest entrance node to user GPS
                    closest_node = None
                    min_dist = float("inf")
                    for nid, ndata in CAMPUS_GRAPH_NODES.items():
                        dist = haversine_distance_meters(user_lat, user_lon, ndata["lat"], ndata["lon"])
                        if dist < min_dist:
                            min_dist = dist
                            closest_node = nid
                    origin_str = closest_node or "GATE_MAIN"
                else:
                    origin_str = "GATE_MAIN"

        if not dest_str:
            return None

        # Resolve nodes
        orig_node_id = None
        if origin_str:
            orig_node_id = CampusRoutingEngine.find_node_by_name_or_keyword(origin_str)
            if not orig_node_id:
                # Try block lookup
                bmatch = re.search(r"([0-9]{1,2})", origin_str)
                if bmatch:
                    orig_node_id = CampusRoutingEngine.find_node_by_block(bmatch.group(1))

        dest_node_id = CampusRoutingEngine.find_node_by_name_or_keyword(dest_str)
        if not dest_node_id:
            bmatch = re.search(r"([0-9]{1,2})", dest_str)
            if bmatch:
                dest_node_id = CampusRoutingEngine.find_node_by_block(bmatch.group(1))

        if not orig_node_id:
            orig_node_id = "GATE_MAIN"

        if not dest_node_id:
            # Destination not recognized in graph
            return None

        # Calculate route using Dijkstra engine
        route_res = CampusRoutingEngine.calculate_route(orig_node_id, dest_node_id)

        # Map turn-by-turn steps to schema NavigationStep
        steps: List[NavigationStep] = []
        for s in route_res.get("turn_by_turn_steps", []):
            steps.append(NavigationStep(
                step=s["step"],
                instruction=s["instruction"],
                distance_meters=s["distance_meters"],
                landmark=s.get("landmark"),
                surface=s.get("surface"),
                wheelchair_accessible=s.get("wheelchair_accessible", True)
            ))

        return CampusRouteCard(
            origin_name=route_res["origin_name"],
            destination_name=route_res["destination_name"],
            walking_distance_meters=route_res.get("walking_distance_meters"),
            straight_line_distance_meters=route_res.get("straight_line_distance_meters"),
            is_pedestrian_path_verified=route_res.get("is_pedestrian_path_verified", False),
            turn_by_turn_available=route_res.get("turn_by_turn_available", False),
            estimated_duration_minutes=route_res.get("estimated_duration_minutes"),
            turn_by_turn_steps=steps,
            route_coordinates=route_res.get("route_coordinates", []),
            accessibility_notes=route_res.get("accessibility_notes", "Standard pedestrian walkway"),
            route_confidence=route_res.get("route_confidence", "VERIFIED_PEDESTRIAN_PATH"),
            data_limitations=route_res.get("data_limitations")
        )

    @classmethod
    def resolve_category_directory(cls, query: str) -> Optional[CampusBlockDirectoryCard]:
        """
        Resolves category browsing queries (e.g. 'show all academic blocks', 'find all hostel blocks').
        """
        q = query.lower().strip()

        matched_cat: Optional[str] = None
        filter_name = ""

        if "hostel" in q:
            matched_cat = "Hostel"
            filter_name = "Campus Residential Hostels"
        elif "academic" in q:
            matched_cat = "Academic"
            filter_name = "Academic Blocks & Institutes"
        elif "auditorium" in q or "auditoriums" in q:
            matched_cat = "Auditorium"
            filter_name = "Campus Auditoriums & Amphitheatres"
        elif "admin" in q or "administrative" in q:
            matched_cat = "Administration"
            filter_name = "Administrative & Executive Blocks"
        elif "library" in q or "libraries" in q:
            matched_cat = "Library"
            filter_name = "Campus Libraries & Reference Halls"
        elif "dining" in q or "food" in q or "mall" in q or "cafe" in q:
            matched_cat = "Dining & Retail"
            filter_name = "Dining Hubs & Commercial Concourse"

        if not matched_cat:
            return None

        places = CampusPlaceDirectory.get_by_category(matched_cat)
        if not places:
            return None

        items: List[CampusDirectoryItem] = []
        for p in places:
            items.append(CampusDirectoryItem(
                place_id=p["place_id"],
                block_number=p.get("block_number"),
                name=p["official_name"],
                category=p["category"],
                campus_zone=p.get("campus_zone", "Campus Sector"),
                verification_status=p.get("verification_status", "USER_SUPPLIED_MAP_PENDING_VERIFICATION"),
                accessibility=p.get("accessibility_information")
            ))

        return CampusBlockDirectoryCard(
            category=matched_cat,
            total_places=len(items),
            filter_applied=filter_name,
            places=items,
            provenance_note=f"Reconciled from official university directory and 01-55 site plan ({len(items)} places cataloged)."
        )

    @classmethod
    def build_place_card(cls, place: Any) -> CampusPlaceCard:
        """Constructs a fully populated, verified CampusPlaceCard for frontend rendering."""
        pid = getattr(place, "place_id", "")
        bnum = getattr(place, "block_number", None)
        name = getattr(place, "official_name", None) or getattr(place, "name", "")
        cat = getattr(place, "category", "Academic")
        desc = getattr(place, "building_description", None) or getattr(place, "description", "")
        zone = getattr(place, "campus_zone", "Central Academic Zone")
        v_status = getattr(place, "verification_status", "RECONCILED_UNIVERSITY_RECORD")
        coord_status = getattr(place, "coordinate_verification_status", "APPROXIMATE_DIAGRAM_PIN")
        coord_src = getattr(place, "coordinate_source", "CAMPUS_CENTROID_ESTIMATE")
        lat = getattr(place, "latitude", None)
        lon = getattr(place, "longitude", None)
        hours = getattr(place, "opening_hours", "Mon-Sat: 8:30 AM - 5:30 PM")
        access_info = getattr(place, "accessibility_information", None) or getattr(place, "accessibility", "Step-free ramp access")
        facs = getattr(place, "facilities", []) or getattr(place, "services_available", []) or []
        nearby = getattr(place, "nearby_places", []) or []
        src = getattr(place, "official_source", "Official LPU Campus Directory & 01-55 Site Plan")
        discrepancy = getattr(place, "discrepancy_note", None)
        floors = getattr(place, "floors", []) or []
        rooms = getattr(place, "rooms", []) or []

        return CampusPlaceCard(
            place_id=pid,
            name=name,
            block_number=bnum,
            category=cat,
            building_description=desc,
            campus_zone=zone,
            latitude=lat,
            longitude=lon,
            coordinate_source=coord_src,
            coordinate_verification_status=coord_status,
            verification_status=v_status,
            badge=v_status,
            accessibility_information=access_info,
            opening_hours=hours,
            verified_facilities=facs,
            nearby_landmarks=nearby,
            navigation_actions=[
                "Navigate Here",
                "View on Campus Map",
                "3D Walkthrough"
            ],
            source_attribution=src,
            discrepancy_note=discrepancy,
            floors=floors,
            rooms=rooms,
            # Legacy compatibility
            building=getattr(place, "building", f"Block {bnum}" if bnum else name),
            floor_room=getattr(place, "floor_room", None),
            accessibility=access_info,
            description=desc,
            services=facs,
            map_url=getattr(place, "official_map_url", "https://www.lpu.in/about_lpu/campus-tour.php"),
            building_purpose=getattr(place, "building_purpose", None),
            actual_office_service=getattr(place, "actual_office_service", None),
            room_verification_status=getattr(place, "room_verification_status", "VERIFIED_ROOM"),
            evidence_status=getattr(place, "evidence_status", "OFFICIAL_CURRENT_VERIFIED")
        )
