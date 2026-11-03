from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, Integer, Text, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin, generate_uuid, get_utc_now


class KnowledgeRecord(Base, TimestampMixin):
    """
    Unified Institutional Knowledge Repository supporting 30 typed knowledge schemas (v4.0):
    1. FAQ (faq)
    2. Policy (policy)
    3. Rule (rule)
    4. Academic Regulation (academic_regulation)
    5. Process / SOP (process_sop)
    6. UMS Service (ums_service)
    7. Action Workflow (action_workflow)
    8. Fee Structure (fee_structure)
    9. Scholarship Scheme (scholarship_scheme)
    10. Examination Rule (examination_rule)
    11. Grading System (grading_system)
    12. Attendance Policy (attendance_policy)
    13. Hostel Rule (hostel_rule)
    14. Transport Route (transport_route)
    15. Campus Facility (campus_facility)
    16. Office Directory (office_directory)
    17. Faculty Profile (faculty_profile)
    18. Academic Programme (academic_programme)
    19. Course / Subject (course_subject)
    20. Placement Statistic (placement_statistic)
    21. Placement Policy (placement_policy)
    22. Event / Activity (event_activity)
    23. Student Club (student_club)
    24. Grievance Redressal Mechanism (grievance_redressal_mechanism)
    25. Medical / Health Service (medical_health_service)
    26. Security / Emergency Protocol (security_emergency_protocol)
    27. Library Resource (library_resource)
    28. Research Centre / Lab (research_centre_lab)
    29. International Exchange Programme (international_exchange_programme)
    30. Important Date / Academic Calendar (important_date_academic_calendar)
    """
    __tablename__ = "knowledge_records"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    record_id = Column(String(50), unique=True, index=True, nullable=False)  # e.g., LPU-FAQ-001, LPU-POL-001
    record_type = Column(String(50), index=True, nullable=False)  # One of the 30 record types
    title = Column(String(255), index=True, nullable=False)
    content = Column(Text, nullable=False)
    
    category_id = Column(String(36), ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True)
    category_name = Column(String(100), nullable=True)
    tags = Column(JSON, default=list, nullable=False)

    # Institutional Scope
    institution = Column(String(100), default="Lovely Professional University", nullable=False)
    campus = Column(String(100), default="Phagwara, Punjab", nullable=False)

    # Provenance & Source Metadata
    original_source_url = Column(String(500), nullable=False)
    source_id = Column(String(100), nullable=True)
    source_title = Column(String(255), nullable=True)
    source_type = Column(String(50), nullable=True)  # pdf, html, web_page, notice, etc.
    source_document = Column(String(255), nullable=True)
    source_page = Column(String(50), nullable=True)
    source_section = Column(String(100), nullable=True)
    clause_reference = Column(String(100), nullable=True)

    # Lifecycle & Temporal Metadata
    publication_date = Column(DateTime, nullable=True)
    effective_date = Column(DateTime, nullable=True)
    effective_from = Column(DateTime, nullable=True)
    effective_to = Column(DateTime, nullable=True)
    review_expiry_date = Column(DateTime, nullable=True, index=True)
    review_due_at = Column(DateTime, nullable=True)
    last_verified_date = Column(DateTime, default=get_utc_now, nullable=False)
    last_verified_at = Column(DateTime, default=get_utc_now, nullable=False)

    # Governance, Verification & Privacy
    approval_status = Column(String(30), default="approved", index=True, nullable=False)  # 'approved', 'pending_review', 'rejected', 'expired'
    verification_status = Column(String(50), default="verified", index=True, nullable=False)  # 'verified', 'unverified', 'pending_review'
    verified_by = Column(String(100), default="system", nullable=False)
    confidentiality = Column(String(50), default="public", index=True, nullable=False)  # 'public', 'internal', 'restricted'
    language = Column(String(10), default="en", nullable=False)

    is_approved = Column(Boolean, default=True, index=True, nullable=False)
    is_active = Column(Boolean, default=True, index=True, nullable=False)
    is_sensitive = Column(Boolean, default=False, index=True, nullable=False)
    requires_admin_review = Column(Boolean, default=False, nullable=False)

    version = Column(Integer, default=1, nullable=False)
    content_hash = Column(String(64), index=True, nullable=False)

    # Search Variants & Typed Dynamic Metadata
    searchable_variants = Column(JSON, default=list, nullable=False)
    type_metadata = Column(JSON, default=dict, nullable=False)
    audit_trail = Column(JSON, default=list, nullable=False)

    category = relationship("Category")
