from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class FAQBase(BaseModel):
    category_id: str
    canonical_question: str
    alternative_questions: List[str] = []
    answer: str
    keywords: List[str] = []
    source_url: Optional[str] = "https://ums.lpu.in"
    source_title: Optional[str] = "LPU Official Information"
    source_type: str = "Official Portal"
    content_owner: str = "Division of Student Affairs"


class FAQCreate(FAQBase):
    is_approved: bool = True
    approval_status: str = "approved"


class FAQUpdate(BaseModel):
    category_id: Optional[str] = None
    canonical_question: Optional[str] = None
    alternative_questions: Optional[List[str]] = None
    answer: Optional[str] = None
    keywords: Optional[List[str]] = None
    source_url: Optional[str] = None
    source_title: Optional[str] = None
    source_type: Optional[str] = None
    content_owner: Optional[str] = None
    is_approved: Optional[bool] = None
    approval_status: Optional[str] = None


class FAQOut(FAQBase):
    id: str
    category_name: Optional[str] = None
    approval_status: str
    is_approved: bool
    version: int
    last_reviewed: datetime
    created_at: datetime
    updated_at: datetime

