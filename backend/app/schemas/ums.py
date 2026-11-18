from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class EvidenceClassification(str, Enum):
    OFFICIAL_CURRENT_VERIFIED = "OFFICIAL_CURRENT_VERIFIED"
    OFFICIAL_HISTORICAL = "OFFICIAL_HISTORICAL"
    ADMIN_CONFIRMED = "ADMIN_CONFIRMED"
    VENDOR_CONFIRMED = "VENDOR_CONFIRMED"
    USER_REPORTED = "USER_REPORTED"
    UNVERIFIED = "UNVERIFIED"
    CONFLICTING = "CONFLICTING"
    EXPIRED = "EXPIRED"


class UMSServiceCatalogOut(BaseModel):
    id: str
    catalog_id: str
    module: str
    service_label: str
    action_type: str
    public_chatbot_support: str
    execution_boundary: str
    ums_authentication: str
    navigation_path: str
    deep_link_status: str
    deep_link_url: str
    source_evidence: str
    verification_status: str
    notes: Optional[str] = None
    keywords: List[str] = Field(default_factory=list)
    is_active: bool

    class Config:
        from_attributes = True


class UMSServiceCatalogUpdate(BaseModel):
    service_label: Optional[str] = None
    navigation_path: Optional[str] = None
    verification_status: Optional[str] = None
    deep_link_status: Optional[str] = None
    deep_link_url: Optional[str] = None
    notes: Optional[str] = None
    keywords: Optional[List[str]] = None
    is_active: Optional[bool] = None


class ActionWorkflowOut(BaseModel):
    id: str
    action_id: str
    user_intent: str
    action_mode: str
    target_system: str
    ums_navigation_path: str
    chatbot_flow: str
    evidence: str
    execution_guardrail: str
    prerequisites: List[str] = Field(default_factory=list)
    steps: List[str] = Field(default_factory=list)
    handoff_url: str
    is_active: bool

    class Config:
        from_attributes = True


class CampusPlaceOut(BaseModel):
    id: str
    place_id: str
    name: str
    category: str
    building: str
    floor_room: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    opening_hours: Optional[str] = None
    accessibility: Optional[str] = None
    description: str
    services_available: List[str] = Field(default_factory=list)
    official_map_url: str
    verified_at: Optional[Any] = None

    class Config:
        from_attributes = True


# Action Card Models for Enriched Chat Response
class NavigationCard(BaseModel):
    service_title: str
    module: str
    breadcrumb: str
    instruction: str
    handoff_url: str = "https://ums.lpu.in/lpuums/"
    button_label: str = "Open Official UMS"


class BookingCard(BaseModel):
    booking_type: str
    service_title: str
    breadcrumb: str
    prerequisites: List[str] = Field(default_factory=list)
    availability_caveat: str = "Live slot availability depends on your active UMS schedule after authentication."
    handoff_url: str = "https://ums.lpu.in/lpuums/"
    button_label: str = "Continue to UMS Booking"


class ProcedureChecklist(BaseModel):
    procedure_name: str
    steps: List[str] = Field(default_factory=list)
    required_documents: List[str] = Field(default_factory=list)
    deadline_or_fees: Optional[str] = None
    breadcrumb: Optional[str] = None
    handoff_url: str = "https://ums.lpu.in/lpuums/"


class RMSCard(BaseModel):
    title: str = "Relationship Management System (RMS) Grievance Guide"
    submission_path: str = "UMS > Student Services > Relationship Management System > Log Request"
    tracking_path: str = "UMS > Student Services > Relationship Management System > View Request Status"
    stages: List[str] = Field(default_factory=lambda: [
        "Select Message Type (Complaint / Query / Suggestion)",
        "Select Relevant Department (e.g. Hostel, Academics, Examination, Transport)",
        "Select Specific Category and Subcategory",
        "Describe your issue in detail and attach supporting evidence",
        "Submit and note the generated Unique Request Tracking Number"
    ])
    privacy_notice: str = "For your confidentiality and security, do not enter sensitive grievance text in this public chatbot. Submit directly inside authenticated UMS."
    handoff_url: str = "https://ums.lpu.in/lpuums/"


class PersonalRecordCard(BaseModel):
    record_type: str
    title: str
    breadcrumb: str
    boundary_explanation: str
    handoff_url: str = "https://ums.lpu.in/lpuums/"


class CampusPlaceCard(BaseModel):
    place_id: str
    name: str
    building: str
    block_number: Optional[str] = None
    category: str = "Academic"
    building_description: Optional[str] = None
    campus_zone: str = "Central Academic Zone"
    floor_room: Optional[str] = None
    opening_hours: Optional[str] = None
    accessibility: Optional[str] = None
    accessibility_information: Optional[str] = None
    description: str = ""
    services: List[str] = Field(default_factory=list)
    verified_facilities: List[str] = Field(default_factory=list)
    nearby_landmarks: List[str] = Field(default_factory=list)
    navigation_actions: List[str] = Field(default_factory=lambda: [
        "Navigate Here",
        "View on Campus Map",
        "3D Walkthrough"
    ])
    map_url: str = "https://www.lpu.in/about_lpu/campus-tour.php"
    building_purpose: Optional[str] = None
    actual_office_service: Optional[str] = None
    room_verification_status: str = "VERIFIED_ROOM"
    coordinates_verification_status: str = "VERIFIED_MAP_PIN"
    coordinate_source: str = "CAMPUS_CENTROID_ESTIMATE"
    evidence_status: str = "OFFICIAL_CURRENT_VERIFIED"
    verification_status: str = "RECONCILED_UNIVERSITY_RECORD"
    badge: str = "RECONCILED_UNIVERSITY_RECORD"
    source_attribution: str = "Official LPU Campus Directory & 01-55 Site Plan"
    discrepancy_note: Optional[str] = None
    floors: List[str] = Field(default_factory=list)
    rooms: List[Dict[str, Any]] = Field(default_factory=list)
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class FoodOutletAlternative(BaseModel):
    outlet_id: str
    display_name: str
    location: str
    specialty: str
    opening_hours: str


class FoodOutletCard(BaseModel):
    outlet_id: str
    display_name: str
    outlet_type: str
    zone: str
    location_description: str
    distance_meters: Optional[int] = None  # Preserved for backward compatibility
    walking_minutes: Optional[int] = None  # Preserved for backward compatibility
    estimated_straight_line_distance_meters: Optional[int] = None
    distance_type: str = "straight_line_estimate"
    open_status: str = "open"  # "open", "closed", "unknown"
    opening_hours: str
    matched_items: List[str] = Field(default_factory=list)
    price_sample: Optional[str] = None
    evidence_type: str = "official"  # "official", "vendor-confirmed", "student-reported"
    evidence_status: str = "OFFICIAL_CURRENT_VERIFIED"
    verification_notice: Optional[str] = None
    is_vegetarian: bool = True
    alternatives: List[FoodOutletAlternative] = Field(default_factory=list)
    query_match_status: str = "exact"  # "exact", "unmatched_alternative", "dietary_fallback"


class PersonCard(BaseModel):
    person_id: str
    full_name: str
    designation: str
    school_division: str
    building_block: str
    room_cabin: str
    email: Optional[str] = None
    profile_source: str
    verification_date: str
    notes: Optional[str] = None
    revalidation_advisory: Optional[str] = None
    role_category: Optional[str] = None
    school_hod: Optional[str] = None
    department_hod: Optional[str] = None
    executive_dean: Optional[str] = None
    senior_dean: Optional[str] = None
    associate_dean: Optional[str] = None
    academic_coordinator: Optional[str] = None
    programme_coordinator: Optional[str] = None
    course_instructor: Optional[str] = None
    faculty_mentor: Optional[str] = None
    office_location: Optional[str] = None
    office_seating_verified: bool = False
    verification_timestamp: str = "2026-11-18T00:00:00Z"
    evidence_status: str = "OFFICIAL_CURRENT_VERIFIED"


class WhoToMeetCard(BaseModel):
    issue_key: str
    category_title: str
    primary_contact_role: str
    named_contact_person: Optional[str] = None
    office_location: str
    room_details: str
    ums_navigation_path: str
    prerequisite_action: str
    required_documents: List[str] = Field(default_factory=list)
    escalation_ladder: List[str] = Field(default_factory=list)
    revalidation_notice: Optional[str] = None
    evidence_status: str = "OFFICIAL_CURRENT_VERIFIED"


class AcademicBenefitAssessmentCard(BaseModel):
    category_id: str
    category_name: str
    portal_stage_name: str = "Select Category"
    matched_criteria: str
    eligible_academic_benefits: str
    missing_evidence: List[str] = Field(default_factory=list)
    evidence_checklist: List[str] = Field(default_factory=list)
    technical_originality_check: str = "Must be student's original engineering output; tutorial clones or plagiarized submissions disqualified."
    limitations_and_caveats: List[str] = Field(default_factory=list)
    course_mapping_window: str = "First 4 weeks of active academic semester"
    approval_prerequisite: str = "School Evaluation Committee viva & Standing Academic Committee ratification"
    submission_route: str = "UMS > Relationship Management System (RMS) > Edu-Revolution: Be the change > Apply for EDU Revolution"
    physical_helpdesk: str = "Block 27 Room 102 (Query & Assistance Zone)"
    guarantee_disclaimer: str = "Benefits require Standing Academic Committee approval and active term course mapping. No automatic grades, marks, or attendance waivers are guaranteed."
    scrgm_distinction: str = "Student-Centric Revenue Generation Model (SCRGM) is a commercial revenue framework and does NOT convert money/sales into academic marks or credits."
    eligibility_vs_approval_notice: str = "POTENTIAL ELIGIBILITY ONLY: Assessment indicates preliminary alignment. Formal benefit approval requires syllabus matching with your course instructor in the first 4 weeks, demonstration before the School Evaluation Committee, and ratification by the Standing Academic Committee. No marks, grades, or attendance dispensations are guaranteed without formal SAC ratification."
    evidence_status: str = "OFFICIAL_CURRENT_VERIFIED"


class EvidenceCard(BaseModel):
    source_title: str
    source_type: str
    document_name: Optional[str] = None
    clause_or_page: Optional[str] = None
    verification_date: str
    is_official: bool = True
    evidence_status: str = "OFFICIAL_CURRENT_VERIFIED"
    revalidation_advisory: Optional[str] = None


