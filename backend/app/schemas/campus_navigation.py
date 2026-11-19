"""
Pydantic Schemas for Campus Block Discovery, Pedestrian Navigation, and Action Cards.
Provides typed payload schemas for CampusPlaceCard, CampusRouteCard, and CampusBlockDirectoryCard.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class Coordinates(BaseModel):
    latitude: float
    longitude: float


class NavigationStep(BaseModel):
    step: int
    instruction: str
    distance_meters: int
    landmark: Optional[str] = None
    surface: Optional[str] = None
    wheelchair_accessible: bool = True


class CampusPlaceCard(BaseModel):
    """
    Enriched location action card rendered when a student discovers or asks about a campus place.
    """
    place_id: str
    name: str
    block_number: Optional[str] = None
    category: str
    building_description: str
    campus_zone: str = "Central Academic Zone"
    coordinates: Optional[Coordinates] = None
    coordinate_source: str = "CAMPUS_CENTROID_ESTIMATE"
    coordinate_verification_status: str = "APPROXIMATE_DIAGRAM_PIN"
    verification_status: str = "USER_SUPPLIED_MAP_PENDING_VERIFICATION"
    badge: str = "USER_SUPPLIED_MAP_PENDING_VERIFICATION"
    accessibility_information: Optional[str] = "Step-free ramp access at primary entrance"
    opening_hours: Optional[str] = "Mon-Sat: 8:30 AM - 5:30 PM"
    verified_facilities: List[str] = Field(default_factory=list)
    nearby_landmarks: List[str] = Field(default_factory=list)
    navigation_actions: List[str] = Field(default_factory=lambda: [
        "Navigate Here",
        "View on Campus Map",
        "3D Walkthrough"
    ])
    source_attribution: str = "Official LPU Campus Directory & 01-55 Site Plan"
    discrepancy_note: Optional[str] = None
    floors: List[str] = Field(default_factory=list)
    rooms: List[Dict[str, Any]] = Field(default_factory=list)

    # Legacy compatibility fields
    building: Optional[str] = None
    floor_room: Optional[str] = None
    accessibility: Optional[str] = None
    description: Optional[str] = None
    services: List[str] = Field(default_factory=list)
    map_url: str = "https://www.lpu.in/about_lpu/campus-tour.php"
    building_purpose: Optional[str] = None
    actual_office_service: Optional[str] = None
    room_verification_status: str = "VERIFIED_ROOM"
    evidence_status: str = "OFFICIAL_CURRENT_VERIFIED"


class CampusRouteCard(BaseModel):
    """
    Pedestrian navigation action card displaying shortest walking path, duration,
    turn-by-turn guidance, and explicit distinction from straight-line distance.
    """
    origin_name: str
    origin_block: Optional[str] = None
    destination_name: str
    destination_block: Optional[str] = None
    walking_distance_meters: Optional[int] = None
    straight_line_distance_meters: Optional[int] = None
    is_pedestrian_path_verified: bool = False
    turn_by_turn_available: bool = False
    estimated_duration_minutes: Optional[int] = None
    turn_by_turn_steps: List[NavigationStep] = Field(default_factory=list)
    route_coordinates: List[List[float]] = Field(default_factory=list)
    accessibility_notes: str = "Standard pedestrian walkway"
    route_confidence: str = "VERIFIED_PEDESTRIAN_PATH"
    data_limitations: Optional[str] = None
    walkway_surface: str = "Paved concrete & granite promenade"
    speed_basis: str = "Calculated at standard pedestrian walking pace of 1.2 m/s"


class CampusDirectoryItem(BaseModel):
    place_id: str
    block_number: Optional[str] = None
    name: str
    category: str
    campus_zone: str
    verification_status: str
    accessibility: Optional[str] = None


class CampusBlockDirectoryCard(BaseModel):
    """
    Directory summary card returned for category queries (e.g. 'all academic blocks', 'hostels').
    """
    category: str
    total_places: int
    filter_applied: str
    places: List[CampusDirectoryItem] = Field(default_factory=list)
    provenance_note: str = "Sourced from reconciled LPU Campus Directory (01-55 site plan and official records)"

