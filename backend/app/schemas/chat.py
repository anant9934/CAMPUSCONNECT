from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from app.schemas.ums import (
    NavigationCard,
    BookingCard,
    ProcedureChecklist,
    RMSCard,
    PersonalRecordCard,
    CampusPlaceCard,
    FoodOutletCard,
    PersonCard,
    WhoToMeetCard,
    AcademicBenefitAssessmentCard,
    EvidenceCard,
)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000, description="Student question in English")
    session_token: str = Field(..., min_length=10, description="Anonymous session identifier token")
    conversation_id: Optional[str] = Field(None, description="Existing conversation thread UUID")
    category_slug: Optional[str] = Field(None, description="Optional category filter (e.g. academics, hostel)")
    user_lat: Optional[float] = Field(None, description="User latitude (permission-gated browser location)")
    user_lon: Optional[float] = Field(None, description="User longitude (permission-gated browser location)")
    user_landmark: Optional[str] = Field(None, description="User-selected landmark if GPS denied (e.g. Block 32)")
    provider: Optional[str] = Field(None, description="Target LLM provider (gemini, bazaarlink, groq, pekpik, cohere, openrouter)")
    model: Optional[str] = Field(None, description="Specific model identifier")
    reasoning_mode: Optional[str] = Field("balanced", description="Reasoning mode: quick, balanced, deepthink, research")
    thinking_level: Optional[str] = Field("medium", description="Thinking level: low, medium, high, research")
    web_research: Optional[bool] = Field(False, description="Enable live web research")
    agent_id: Optional[str] = Field("aegis", description="Target agent: aegis, nova, athena, oracle, forge, themis, hermes, vision")


class ThinkingStep(BaseModel):
    step: int
    title: str
    description: str
    status: str = "completed"  # 'pending', 'running', 'completed'


class Citation(BaseModel):
    title: str
    url: str
    source_type: str = "Official Portal"
    verified: bool = True
    snippet: Optional[str] = None
    content_owner: Optional[str] = None


class ChatResponse(BaseModel):
    conversation_id: str
    message_id: str
    role: str = "assistant"
    content: str
    action_type: str = "ANSWER"  # ANSWER, NAVIGATE, PREPARE, BOOK_HANDOFF, PERSONAL_RECORD, ESCALATE, EXECUTE, ABSTAIN
    thinking_steps: List[ThinkingStep] = []
    citations: List[Citation] = []
    follow_ups: List[str] = []
    navigation_card: Optional[NavigationCard] = None
    booking_card: Optional[BookingCard] = None
    procedure_checklist: Optional[ProcedureChecklist] = None
    rms_card: Optional[RMSCard] = None
    personal_record_card: Optional[PersonalRecordCard] = None
    campus_place_card: Optional[CampusPlaceCard] = None
    food_outlet_card: Optional[FoodOutletCard] = None
    person_card: Optional[PersonCard] = None
    who_to_meet_card: Optional[WhoToMeetCard] = None
    academic_benefit_card: Optional[AcademicBenefitAssessmentCard] = None
    evidence_card: Optional[EvidenceCard] = None
    confidence_score: float = 0.0
    latency_ms: int = 0
    is_ai_generated: bool = False
    agent_id: Optional[str] = Field("aegis", description="Responding orchestrator or specialist agent id")
    specialists_involved: List[str] = Field(default_factory=list, description="Specialist agents coordinated for this turn")
    agent_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Execution and routing metadata")


