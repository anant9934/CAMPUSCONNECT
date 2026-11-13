from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models import Category
from app.schemas.category import CategoryOut

router = APIRouter()


@router.get("/categories", response_model=List[CategoryOut])
async def list_categories(db: AsyncSession = Depends(get_db)):
    """List active LPU campus categories for navigation and service cards."""
    stmt = (
        select(Category)
        .where(Category.is_active == True)
        .order_by(Category.display_order.asc())
    )
    result = await db.execute(stmt)
    categories = result.scalars().all()
    return categories

