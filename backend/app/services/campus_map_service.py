import logging
import re
from typing import List, Optional
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.campus_place import CampusPlace
from app.schemas.ums import CampusPlaceCard

logger = logging.getLogger(__name__)


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

logger = logging.getLogger(__name__)


class PlaceWrapper:
    """Wrapper that mimics CampusPlace for CSV-sourced places."""
    def __init__(self, data: Dict[str, Any]):
        self.place_id = data["place_id"]
        self.name = data["name"]
        self.building = data["building_block"]
        self.floor_room = data["floor_room"]
        self.latitude = data["latitude"]
        self.longitude = data["longitude"]
        self.opening_hours = data["opening_hours"]
        self.accessibility = data["accessibility"]
        self.description = f"{data['name']}. Located along {data.get('pedestrian_paths', '')}."
        self.services_available = data["services_available"]
        self.official_map_url = "https://www.lpu.in/about_lpu/campus-tour.php"
        self.building_purpose = data.get("building_purpose")
        self.actual_office_service = data.get("actual_office_service")
        self.room_verification_status = data.get("room_verification_status", "VERIFIED_ROOM")
        self.coordinates_verification_status = data.get("coordinates_verification_status", "CAMPUS_CENTROID_ESTIMATE")
        self.evidence_status = data.get("evidence_status", "OFFICIAL_CURRENT_VERIFIED")


class CampusMapService:
    """
    Campus Wayfinding and Location Service for Lovely Professional University.
    Provides verified building, block, room, and accessibility details.
    Searches both SQLite database records and campus_office_place_directory.csv.
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
        db: AsyncSession
    ) -> Optional[Any]:
        """Matches a user query to a verified campus place."""
        q = query.lower().strip()

        # 1. Check for specific room or block 32 queries in CSV first
        csv_places = cls._load_csv_places()
        for cp in csv_places:
            bld_low = cp["building_block"].lower()
            room_low = (cp.get("floor_room") or "").lower()

            # Room 102 (EDU-Revolution Query Cell at Block 27)
            if cp["place_id"] == "PLC-003" and ("102" in q or "edu-revolution" in q):
                return PlaceWrapper(cp)

            # Room 100 (DSR at Block 32)
            if cp["place_id"] == "PLC-010" and ("100" in q or "dsr" in q):
                return PlaceWrapper(cp)

            # Room 308 (DIA at Block 32)
            if cp["place_id"] == "PLC-011" and ("308" in q or "dia" in q):
                return PlaceWrapper(cp)

            # Block 32 (School of Computer Science & Engineering)
            if cp["place_id"] == "PLC-001" and ("32" in q):
                return PlaceWrapper(cp)

        # 2. Search database CampusPlace records (LOC-001 to LOC-010)
        stmt = select(CampusPlace)
        res = await db.execute(stmt)
        places = res.scalars().all()

        best_place = None
        best_score = 0.0

        for p in places:
            name_lower = p.name.lower()
            bld_lower = p.building.lower()
            desc_lower = p.description.lower()

            score = 0.0

            if bld_lower in q:
                score += 8.0
            elif bld_lower.replace(" ", "") in q.replace(" ", ""):
                score += 8.0

            if "unihospital" in q and ("hospital" in name_lower or "unihospital" in desc_lower):
                score += 9.0
            if "library" in q and ("library" in name_lower or "36" in bld_lower):
                score += 9.0
            if "unimall" in q and "unimall" in name_lower:
                score += 9.0
            if ("stadium" in q or "sports" in q or "swimming" in q) and "stadium" in name_lower:
                score += 8.0
            if ("unipolis" in q or "auditorium" in q) and "unipolis" in name_lower:
                score += 9.0
            if ("cse" in q or "computer science" in q) and ("cse" in name_lower or "computer" in name_lower):
                score += 8.0
            if ("dsa" in q or "student welfare" in q) and "13" in bld_lower:
                score += 8.0
            if ("exam cell" in q or "coe" in q or "registrar" in q) and "34" in bld_lower:
                score += 8.0

            q_words = set(re.findall(r"\w+", q))
            p_words = set(re.findall(r"\w+", f"{name_lower} {bld_lower}"))
            score += len(q_words.intersection(p_words)) * 2.0

            if score > best_score:
                best_score = score
                best_place = p

        if best_place and best_score >= 4.0:
            return best_place

        # 3. Fallback to remaining CSV directory places
        best_csv = None
        best_csv_score = 0.0

        for cp in csv_places:
            score = 0.0
            name_low = cp["name"].lower()
            bld_low = cp["building_block"].lower()

            if bld_low in q or bld_low.replace(" ", "") in q.replace(" ", ""):
                score += 10.0

            if score > best_csv_score:
                best_csv_score = score
                best_csv = cp

        if best_csv and best_csv_score >= 8.0:
            return PlaceWrapper(best_csv)

        return None

    @classmethod
    async def list_places(
        cls,
        db: AsyncSession,
        category: Optional[str] = None
    ) -> List[CampusPlace]:
        """Lists all verified campus places, optionally filtered by category."""
        stmt = select(CampusPlace)
        if category:
            stmt = stmt.where(CampusPlace.category == category)
        res = await db.execute(stmt)
        return res.scalars().all()

    @classmethod
    def build_place_card(cls, place: Any) -> CampusPlaceCard:
        """Constructs a CampusPlaceCard for frontend rendering."""
        return CampusPlaceCard(
            place_id=getattr(place, "place_id", ""),
            name=getattr(place, "name", ""),
            building=getattr(place, "building", ""),
            floor_room=getattr(place, "floor_room", None),
            opening_hours=getattr(place, "opening_hours", None),
            accessibility=getattr(place, "accessibility", None),
            description=getattr(place, "description", ""),
            services=getattr(place, "services_available", []) or [],
            map_url=getattr(place, "official_map_url", "https://www.lpu.in/about_lpu/campus-tour.php"),
            building_purpose=getattr(place, "building_purpose", None),
            actual_office_service=getattr(place, "actual_office_service", None),
            room_verification_status=getattr(place, "room_verification_status", "VERIFIED_ROOM"),
            coordinates_verification_status=getattr(place, "coordinates_verification_status", "VERIFIED_MAP_PIN"),
            evidence_status=getattr(place, "evidence_status", "OFFICIAL_CURRENT_VERIFIED"),
        )



