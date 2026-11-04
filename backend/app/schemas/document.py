from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class DocumentOut(BaseModel):
    id: str
    category_id: Optional[str]
    category_name: Optional[str] = None
    title: str
    filename: str
    file_size: int
    mime_type: str
    status: str
    is_approved: bool
    total_chunks: int
    created_at: datetime
    updated_at: datetime


class ChunkOut(BaseModel):
    id: str
    chunk_index: int
    content: str
    page_number: Optional[int]
    token_count: int

