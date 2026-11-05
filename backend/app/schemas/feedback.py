from typing import Optional, Literal
from pydantic import BaseModel, Field


class FeedbackCreate(BaseModel):
    conversation_id: str
    message_id: str
    rating: Literal["helpful", "unhelpful"]
    comment: Optional[str] = Field(None, max_length=500)
    session_token: Optional[str] = None


class FeedbackOut(BaseModel):
    id: str
    conversation_id: str
    message_id: str
    rating: str
    comment: Optional[str]

