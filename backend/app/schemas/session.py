from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas.chat import Citation, ThinkingStep


class SessionCreateRequest(BaseModel):
    user_agent: Optional[str] = None


class SessionResponse(BaseModel):
    session_token: str
    expires_at: datetime
    is_active: bool


class MessageOut(BaseModel):
    id: str
    conversation_id: str
    role: str
    content: str
    thinking_steps: List[ThinkingStep] = []
    citations: List[Citation] = []
    confidence_score: Optional[float] = None
    created_at: datetime


class ConversationSummary(BaseModel):
    id: str
    title: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    message_count: int = 0


class ConversationDetail(BaseModel):
    id: str
    session_id: str
    title: str
    is_active: bool
    created_at: datetime
    messages: List[MessageOut] = []

