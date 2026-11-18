from sqlalchemy import Column, String, Float, Text, JSON, DateTime
from app.core.database import Base
from app.models.base import TimestampMixin, generate_uuid, get_utc_now


class CampusPlace(Base, TimestampMixin):
    """
    Campus Place and Wayfinding Directory for Lovely Professional University.
    Comprehensive geospatial and institutional directory covering all blocks (01-55),
    administrative divisions, student hostels, amenities, and health centers.
    """
    __tablename__ = "campus_places"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    place_id = Column(String(50), unique=True, index=True, nullable=False)    # e.g., 'LOC-001', 'BLK-32', 'PLC-001'
    block_number = Column(String(50), index=True, nullable=True)              # e.g., '32', '14', '01'
    name = Column(String(255), index=True, nullable=False)                    # e.g., 'Block 32 - School of Computer Science & Engineering'
    official_name = Column(String(255), index=True, nullable=True)            # Reconciled official institutional name
    alternative_names = Column(JSON, default=list, nullable=False)            # e.g., ['Central Administrative Block', 'CSE Block', 'Block 32']
    category = Column(String(100), index=True, nullable=False)                # Academic, Administration, Hostel, Dining, Healthcare, Sports, etc.
    building = Column(String(100), index=True, nullable=False)                # Legacy building identifier e.g., 'Block 32'
    building_description = Column(Text, nullable=True)                        # Detailed description of building architecture & occupants
    description = Column(Text, nullable=False)                                # General description & landmarks
    campus_zone = Column(String(100), default="Central Academic Zone", nullable=False)  # North Sector, South Sector, Central Promenade, etc.
    floor_room = Column(String(100), nullable=True)                           # Verified office/room or null for whole blocks
    floors = Column(JSON, default=list, nullable=False)                       # e.g., ['Ground Floor', '1st Floor', '2nd Floor', '3rd Floor', '4th Floor']
    rooms = Column(JSON, default=list, nullable=False)                        # List of verified room entities (never assumed or fabricated)
    facilities = Column(JSON, default=list, nullable=False)                   # e.g., ['Elevator', 'Auditorium', 'ATM', 'Computer Labs']
    services_available = Column(JSON, default=list, nullable=False)           # Key services offered at this location
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    coordinate_source = Column(String(100), default="CAMPUS_CENTROID_ESTIMATE", nullable=False) # OPENSTREETMAP_VERIFIED, CAMPUS_SURVEY_GPS, DIAGRAM_IMAGE_ESTIMATE
    coordinate_verification_status = Column(String(100), default="CAMPUS_CENTROID_ESTIMATE", nullable=False) # VERIFIED_MAP_PIN, APPROXIMATE_DIAGRAM_PIN
    accessibility = Column(String(255), nullable=True)                        # Legacy accessibility string
    accessibility_information = Column(String(255), nullable=True)            # Detailed accessibility e.g., 'Ramp access, braille signage, elevators'
    opening_hours = Column(String(150), nullable=True)                        # e.g., '09:00 AM - 05:00 PM (Mon-Sat)'
    nearby_places = Column(JSON, default=list, nullable=False)                # Nearby block numbers or landmark place IDs
    official_source = Column(String(255), default="Official LPU Campus Directory", nullable=False)
    source_date = Column(String(50), default="2026-11-18", nullable=False)
    verification_status = Column(String(100), default="USER_SUPPLIED_MAP_PENDING_VERIFICATION", nullable=False) # RECONCILED_UNIVERSITY_RECORD, USER_SUPPLIED_MAP_PENDING_VERIFICATION, OFFICIAL_CURRENT_VERIFIED, OFFICIAL_HISTORICAL
    official_map_url = Column(String(500), default="https://www.lpu.in/about_lpu/campus-tour.php", nullable=False)
    verified_at = Column(DateTime, default=get_utc_now, nullable=False)
    last_verified_at = Column(DateTime, default=get_utc_now, nullable=False)

    @property
    def display_name(self) -> str:
        return self.official_name or self.name

    @property
    def resolved_description(self) -> str:
        return self.building_description or self.description

    @property
    def resolved_accessibility(self) -> str:
        return self.accessibility_information or self.accessibility or "Standard pedestrian ramp access"
