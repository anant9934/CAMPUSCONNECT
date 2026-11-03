from sqlalchemy import Column, String, Boolean, Text, JSON
from app.core.database import Base
from app.models.base import TimestampMixin, generate_uuid


class ActionWorkflow(Base, TimestampMixin):
    """
    Standard Operating Procedures and Action Workflows for key campus services
    (Hostel, Doctor, Counselling, Library Discussion Rooms, Language Lab, RMS, Fees, etc.)
    """
    __tablename__ = "action_workflows"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    action_id = Column(String(50), unique=True, index=True, nullable=False)   # e.g., ACT-001 .. ACT-024
    user_intent = Column(String(255), index=True, nullable=False)             # Canonical user intent, e.g. 'Book hostel'
    action_mode = Column(String(50), index=True, nullable=False)              # BOOK_HANDOFF, NAVIGATE, PREPARE, PERSONAL_RECORD, ESCALATE, ANSWER
    target_system = Column(String(100), nullable=False)                       # UMS, LPU Touch, YourDOST, UniHospital, RMS
    ums_navigation_path = Column(String(500), nullable=False)                 # Exact menu path to navigate
    chatbot_flow = Column(Text, nullable=False)                               # Interaction workflow instructions
    evidence = Column(Text, nullable=False)                                   # Verification source evidence
    execution_guardrail = Column(Text, nullable=False)                        # Security and ERP boundary guardrail
    prerequisites = Column(JSON, default=list, nullable=False)                # Required documents/conditions
    steps = Column(JSON, default=list, nullable=False)                        # Sequential guidance steps
    handoff_url = Column(String(500), default="https://ums.lpu.in/lpuums/", nullable=False)
    is_active = Column(Boolean, default=True, index=True, nullable=False)

