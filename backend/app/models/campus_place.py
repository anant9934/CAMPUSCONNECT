from sqlalchemy import Column, String, Float, Text, JSON, DateTime
from app.core.database import Base
from app.models.base import TimestampMixin, generate_uuid, get_utc_now


class CampusPlace(Base, TimestampMixin):
    """
    Campus Place and Wayfinding Directory for Lovely Professional University.
    Holds verified locations for blocks, departments, amenities, and health facilities.
    """
    __tablename__ = "campus_places"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    place_id = Column(String(50), unique=True, index=True, nullable=False)    # e.g., LOC-001 .. LOC-020
    name = Column(String(255), index=True, nullable=False)                    # e.g., 'Block 34 - Division of Examination'
    category = Column(String(100), index=True, nullable=False)                # Administration, Academics, Healthcare, etc.
    building = Column(String(100), index=True, nullable=False)                # e.g., 'Block 34'
    floor_room = Column(String(100), nullable=True)                           # e.g., '2nd Floor, Room 201'
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    opening_hours = Column(String(150), nullable=True)                        # e.g., '09:00 AM - 05:00 PM (Mon-Sat)'
    accessibility = Column(String(255), nullable=True)                        # e.g., 'Elevator & wheelchair ramp available'
    description = Column(Text, nullable=False)                                # Detailed description & landmarks
    services_available = Column(JSON, default=list, nullable=False)           # Key services offered at this location
    official_map_url = Column(String(500), default="https://www.lpu.in/about_lpu/campus-tour.php", nullable=False)
    verified_at = Column(DateTime, default=get_utc_now, nullable=False)

