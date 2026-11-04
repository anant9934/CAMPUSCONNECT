from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class KnowledgeRecordBase(BaseModel):
    record_id: str = Field(..., description="Unique record identifier, e.g. LPU-POL-001")
    record_type: str = Field(..., description="One of the 12 record types")
    title: str = Field(..., min_length=2, max_length=255)
    content: str = Field(..., min_length=5)
    category_id: Optional[str] = None
    category_name: Optional[str] = "General"
    original_source_url: str = Field("https://ums.lpu.in", description="Authoritative portal URL")
    source_document: Optional[str] = None
    source_page: Optional[str] = None
    clause_reference: Optional[str] = None
    publication_date: Optional[datetime] = None
    effective_date: Optional[datetime] = None
    review_expiry_date: Optional[datetime] = None
    is_approved: bool = True
    approval_status: str = "approved"
    is_sensitive: bool = False
    requires_admin_review: bool = False
    searchable_variants: List[str] = []
    type_metadata: Dict[str, Any] = {}


class KnowledgeRecordCreate(KnowledgeRecordBase):
    pass


class KnowledgeRecordUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category_id: Optional[str] = None
    category_name: Optional[str] = None
    original_source_url: Optional[str] = None
    source_document: Optional[str] = None
    source_page: Optional[str] = None
    clause_reference: Optional[str] = None
    publication_date: Optional[datetime] = None
    effective_date: Optional[datetime] = None
    review_expiry_date: Optional[datetime] = None
    is_approved: Optional[bool] = None
    approval_status: Optional[str] = None
    is_sensitive: Optional[bool] = None
    requires_admin_review: Optional[bool] = None
    searchable_variants: Optional[List[str]] = None
    type_metadata: Optional[Dict[str, Any]] = None


class KnowledgeRecordOut(KnowledgeRecordBase):
    id: str
    version: int
    content_hash: str
    last_verified_date: datetime
    audit_trail: List[Dict[str, Any]] = []
    created_at: datetime
    updated_at: datetime

