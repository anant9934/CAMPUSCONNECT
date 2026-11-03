from sqlalchemy import Column, String, Boolean, Text, JSON
from app.core.database import Base
from app.models.base import TimestampMixin, generate_uuid


class UMSServiceCatalog(Base, TimestampMixin):
    """
    UMS Service Catalog transcribed from authenticated student screenshots.
    Holds all 234 visible menu entries organized by module with navigation paths
    and execution boundaries.
    """
    __tablename__ = "ums_service_catalog"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    catalog_id = Column(String(50), unique=True, index=True, nullable=False)  # e.g., UMS-001 .. UMS-234
    module = Column(String(100), index=True, nullable=False)                  # e.g., Examination System, Residential Services
    service_label = Column(String(255), index=True, nullable=False)           # Exact menu label seen in screenshot
    action_type = Column(String(50), index=True, nullable=False)              # navigation_or_information, personal_record_or_status, etc.
    public_chatbot_support = Column(String(100), nullable=False)              # explain_and_guide, breadcrumb_and_handoff
    execution_boundary = Column(Text, nullable=False)                         # Policy boundary explanation
    ums_authentication = Column(String(100), nullable=False)                  # required_for_personal_record_or_submission
    navigation_path = Column(String(500), nullable=False)                     # e.g., UMS > Examination System > Registration for Re-Appear
    deep_link_status = Column(String(50), default="not_verified", nullable=False)  # not_verified, verified, entry_page_only
    deep_link_url = Column(String(500), default="https://ums.lpu.in/lpuums/", nullable=False)
    source_evidence = Column(String(255), default="User-provided authenticated UMS menu screenshot", nullable=False)
    verification_status = Column(String(100), default="menu_label_observed_procedure_not_verified", nullable=False)
    notes = Column(Text, nullable=True)
    keywords = Column(JSON, default=list, nullable=False)                     # Synonyms and student search tokens
    is_active = Column(Boolean, default=True, index=True, nullable=False)

