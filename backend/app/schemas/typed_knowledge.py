from __future__ import annotations
from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl


class KnowledgeType(str, Enum):
    FAQ = "faq"
    POLICY = "policy"
    RULE = "rule"
    ACADEMIC_REGULATION = "academic_regulation"
    PROCESS_SOP = "process_sop"
    UMS_SERVICE = "ums_service"
    ACTION_WORKFLOW = "action_workflow"
    FEE_STRUCTURE = "fee_structure"
    SCHOLARSHIP_SCHEME = "scholarship_scheme"
    EXAMINATION_RULE = "examination_rule"
    GRADING_SYSTEM = "grading_system"
    ATTENDANCE_POLICY = "attendance_policy"
    HOSTEL_RULE = "hostel_rule"
    TRANSPORT_ROUTE = "transport_route"
    CAMPUS_FACILITY = "campus_facility"
    OFFICE_DIRECTORY = "office_directory"
    FACULTY_PROFILE = "faculty_profile"
    ACADEMIC_PROGRAMME = "academic_programme"
    COURSE_SUBJECT = "course_subject"
    PLACEMENT_STATISTIC = "placement_statistic"
    PLACEMENT_POLICY = "placement_policy"
    EVENT_ACTIVITY = "event_activity"
    STUDENT_CLUB = "student_club"
    GRIEVANCE_REDRESSAL_MECHANISM = "grievance_redressal_mechanism"
    MEDICAL_HEALTH_SERVICE = "medical_health_service"
    SECURITY_EMERGENCY_PROTOCOL = "security_emergency_protocol"
    LIBRARY_RESOURCE = "library_resource"
    RESEARCH_CENTRE_LAB = "research_centre_lab"
    INTERNATIONAL_EXCHANGE_PROGRAMME = "international_exchange_programme"
    IMPORTANT_DATE_ACADEMIC_CALENDAR = "important_date_academic_calendar"


# --- Common Metadata Schemas ---

class TypedKnowledgeBase(BaseModel):
    record_id: str = Field(..., description="Unique institutional identifier (e.g., LPU-FAQ-001, LPU-POL-002)")
    record_type: KnowledgeType = Field(..., description="One of the 30 standardized knowledge types")
    title: str = Field(..., min_length=3, max_length=255)
    content: str = Field(..., min_length=10)
    category_name: Optional[str] = None
    tags: List[str] = Field(default_factory=list)

    institution: str = "Lovely Professional University"
    campus: str = "Phagwara, Punjab"

    original_source_url: str = Field(..., description="Authoritative reference URL or document path")
    source_id: Optional[str] = None
    source_title: Optional[str] = None
    source_type: Optional[str] = "web_page"  # pdf, html, web_page, official_notice, screenshot
    source_document: Optional[str] = None
    source_page: Optional[str] = None
    source_section: Optional[str] = None
    clause_reference: Optional[str] = None

    publication_date: Optional[datetime] = None
    effective_from: Optional[datetime] = None
    effective_to: Optional[datetime] = None
    review_due_at: Optional[datetime] = None
    last_verified_at: Optional[datetime] = None

    verification_status: str = "verified"  # verified, unverified, pending_review
    verified_by: str = "system"
    confidentiality: str = "public"  # public, internal, restricted
    language: str = "en"

    is_approved: bool = True
    is_active: bool = True
    is_sensitive: bool = False
    requires_admin_review: bool = False
    version: int = 1

    searchable_variants: List[str] = Field(default_factory=list)
    type_metadata: Dict[str, Any] = Field(default_factory=dict)


class TypedKnowledgeCreate(TypedKnowledgeBase):
    pass


class TypedKnowledgeRead(TypedKnowledgeBase):
    id: str
    content_hash: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# --- Specialized Type-Metadata Models for All 30 Types ---

class FAQMetadata(BaseModel):
    canonical_question: str
    answer: str
    category: str
    paraphrases: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)

class PolicyMetadata(BaseModel):
    policy_name: str
    clause_number: Optional[str] = None
    applicability: str = "All students"
    penalty_or_consequence: Optional[str] = None
    exceptions: Optional[str] = None

class RuleMetadata(BaseModel):
    rule_name: str
    scope: str
    mandatory_flag: bool = True
    violation_penalty: Optional[str] = None

class AcademicRegulationMetadata(BaseModel):
    regulation_code: str
    governing_body: str = "Academic Council"
    program_applicability: str = "All regular degree programmes"
    minimum_cgpa: Optional[float] = None
    credit_requirements: Optional[int] = None

class ProcessSOPMetadata(BaseModel):
    sop_name: str
    preconditions: List[str] = Field(default_factory=list)
    sequential_steps: List[str] = Field(default_factory=list)
    required_documents: List[str] = Field(default_factory=list)
    fee_required: bool = False
    processing_sla_days: Optional[int] = None

class UMSServiceMetadata(BaseModel):
    catalog_id: str
    module: str
    menu_path: str
    action_type: str
    auth_required: bool = True
    verification_status: str = "menu_label_observed"
    deep_link_available: bool = False

class ActionWorkflowMetadata(BaseModel):
    action_id: str
    user_intent: str
    trigger_utterances: List[str] = Field(default_factory=list)
    entry_path: str
    required_fields: List[str] = Field(default_factory=list)
    handoff_url: str = "https://ums.lpu.in/lpuums/"
    guardrails: str

class FeeStructureMetadata(BaseModel):
    programme: str
    batch_session: str
    semester_fee: Optional[float] = None
    annual_fee: Optional[float] = None
    scholarship_applicable: bool = True
    late_fee_rules: Optional[str] = None

class ScholarshipSchemeMetadata(BaseModel):
    scholarship_name: str
    eligibility_criteria: str
    benefit_percentage_or_amount: str
    maintaining_criteria: Optional[str] = None
    application_window: Optional[str] = None

class ExaminationRuleMetadata(BaseModel):
    exam_type: str  # Mid-term, End-term, Reappear, Make-up
    eligibility_attendance_percent: float = 75.0
    admit_card_requirement: str = "Mandatory printed admit card and University ID card"
    unfair_means_code: Optional[str] = None

class GradingSystemMetadata(BaseModel):
    grade_letter: str
    grade_point: float
    percentage_range: Optional[str] = None
    description: str
    pass_fail_status: str = "Pass"

class AttendancePolicyMetadata(BaseModel):
    minimum_percentage: float = 75.0
    condonation_limit_percent: float = 65.0
    medical_leave_benefit: str
    duty_leave_benefit: str
    debarment_criteria: str

class HostelRuleMetadata(BaseModel):
    hostel_block: Optional[str] = None
    curfew_timing: str = "10:00 PM (subject to seasonal warden circulars)"
    prohibited_items: List[str] = Field(default_factory=list)
    electrical_appliances_allowed: List[str] = Field(default_factory=list)
    vacation_notice_days: Optional[int] = None

class TransportRouteMetadata(BaseModel):
    route_number: str
    origin: str
    destination: str = "LPU Campus, Phagwara"
    key_pickup_points: List[str] = Field(default_factory=list)
    morning_arrival_time: Optional[str] = None
    evening_departure_time: Optional[str] = None

class CampusFacilityMetadata(BaseModel):
    facility_name: str
    building_block: str
    floor: Optional[str] = None
    operating_hours: Optional[str] = None
    accessible_features: Optional[str] = None

class OfficeDirectoryMetadata(BaseModel):
    department_office: str
    room_number: Optional[str] = None
    building_block: Optional[str] = None
    official_email: Optional[str] = None
    phone_extension: Optional[str] = None

class FacultyProfileMetadata(BaseModel):
    faculty_name: str
    emp_code: Optional[str] = None
    designation: str
    department: str = "Computer Science and Engineering"
    specialization: Optional[str] = None
    research_areas: List[str] = Field(default_factory=list)

class AcademicProgrammeMetadata(BaseModel):
    degree: str
    programme_name: str
    duration_years: int
    total_credits: Optional[int] = None
    eligibility: str

class CourseSubjectMetadata(BaseModel):
    course_code: str
    course_title: str
    credits: float
    prerequisites: Optional[str] = None
    syllabus_summary: Optional[str] = None

class PlacementStatisticMetadata(BaseModel):
    academic_year: str
    highest_package: Optional[str] = None
    average_package: Optional[str] = None
    recruiting_companies_count: Optional[int] = None
    marquee_recruiters: List[str] = Field(default_factory=list)

class PlacementPolicyMetadata(BaseModel):
    eligibility_cgpa: float
    max_active_backlogs: int = 0
    dream_offer_policy: Optional[str] = None
    drive_attendance_rule: str

class EventActivityMetadata(BaseModel):
    event_name: str
    organizer: str
    event_type: str
    venue: str
    dates: Optional[str] = None

class StudentClubMetadata(BaseModel):
    club_name: str
    category: str  # Cultural, Technical, Literary, Sports, Social
    faculty_advisor: Optional[str] = None
    activities_summary: str

class GrievanceRedressalMetadata(BaseModel):
    grievance_type: str
    rms_portal_category: str
    escalation_level_1: str
    escalation_level_2: Optional[str] = None
    resolution_sla_days: int = 7

class MedicalHealthServiceMetadata(BaseModel):
    hospital_name: str = "Uni-Hospital (Block 30)"
    emergency_contact: str = "+91-1824-517000"
    ambulance_service: str = "24x7 Available on Campus"
    opd_timings: str = "8:00 AM - 8:00 PM"

class SecurityEmergencyProtocolMetadata(BaseModel):
    protocol_type: str
    emergency_number: str = "+91-1824-517100 / Internal Ext 100"
    evacuation_assembly_points: List[str] = Field(default_factory=list)
    warden_contact_path: str = "UMS -> Hostel -> Warden Directory"

class LibraryResourceMetadata(BaseModel):
    central_library_block: str = "Block 14"
    opac_catalog_url: str = "http://opac.lpu.in/"
    digital_library_access: str = "IEEE, ACM, Springer, ScienceDirect accessible via Campus WiFi"
    borrowing_limit_books: int = 4

class ResearchCentreLabMetadata(BaseModel):
    lab_name: str
    block_location: str
    specialized_equipment: List[str] = Field(default_factory=list)
    research_focus: str

class InternationalExchangeMetadata(BaseModel):
    partner_institution: str
    country: str
    programme_type: str  # Semester Exchange, Dual Degree, Summer School
    credit_transfer_allowed: bool = True

class ImportantDateAcademicCalendarMetadata(BaseModel):
    academic_session: str
    term: str
    event_title: str
    start_date: str
    end_date: Optional[str] = None
    is_tentative: bool = False

