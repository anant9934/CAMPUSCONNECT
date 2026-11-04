from typing import Optional
from pydantic import BaseModel


class CategoryOut(BaseModel):
    id: str
    name: str
    slug: str
    description: Optional[str] = None
    icon: str = "Folder"
    display_order: int = 0
    is_active: bool = True

