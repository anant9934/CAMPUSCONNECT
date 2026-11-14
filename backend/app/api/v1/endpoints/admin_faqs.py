from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import FAQ, Category, AdminUser, AuditLog, FAQSource
from app.api.v1.endpoints.admin_auth import get_current_admin
from app.schemas.faq import FAQCreate, FAQUpdate, FAQOut
from app.services.rag.hybrid_search import hybrid_search_engine

router = APIRouter()


@router.get("/admin/faqs", response_model=List[FAQOut])
async def list_admin_faqs(
    category_id: Optional[str] = None,
    approval_status: Optional[str] = None,
    search: Optional[str] = None,
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """List all knowledge base FAQs with filtering."""
    stmt = select(FAQ).options(selectinload(FAQ.category)).order_by(FAQ.created_at.desc())
    if category_id:
        stmt = stmt.where(FAQ.category_id == category_id)
    if approval_status:
        stmt = stmt.where(FAQ.approval_status == approval_status)

    res = await db.execute(stmt)
    faqs = res.scalars().all()

    out = []
    for f in faqs:
        if search:
            s_low = search.lower()
            if s_low not in f.canonical_question.lower() and s_low not in f.answer.lower():
                continue
        out.append(
            FAQOut(
                id=str(f.id),
                category_id=str(f.category_id),
                category_name=f.category.name if f.category else None,
                canonical_question=f.canonical_question,
                alternative_questions=f.alternative_questions or [],
                answer=f.answer,
                keywords=f.keywords or [],
                source_url=f.source_url,
                source_title=f.source_title,
                source_type=f.source_type,
                content_owner=f.content_owner,
                approval_status=f.approval_status,
                is_approved=f.is_approved,
                version=f.version,
                last_reviewed=f.last_reviewed,
                created_at=f.created_at,
                updated_at=f.updated_at,
            )
        )
    return out


@router.post("/admin/faqs", response_model=FAQOut)
async def create_faq(
    body: FAQCreate,
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Create a new FAQ record."""
    faq = FAQ(
        category_id=body.category_id,
        canonical_question=body.canonical_question,
        alternative_questions=body.alternative_questions,
        answer=body.answer,
        keywords=body.keywords,
        source_url=body.source_url,
        source_title=body.source_title,
        source_type=body.source_type,
        content_owner=body.content_owner,
        is_approved=body.is_approved,
        approval_status=body.approval_status,
        last_reviewed=datetime.now(timezone.utc),
        version=1,
    )
    db.add(faq)
    await db.flush()

    if body.source_url:
        src = FAQSource(
            faq_id=faq.id,
            url=body.source_url,
            title=body.source_title or "Official Source",
            source_type="portal",
            verified=True,
            last_verified_at=datetime.now(timezone.utc),
        )
        db.add(src)

    # Log audit
    audit = AuditLog(
        admin_id=admin.id,
        action="create_faq",
        resource_type="faq",
        resource_id=str(faq.id),
        details={"question": faq.canonical_question},
    )
    db.add(audit)
    await db.commit()
    await db.refresh(faq)

    # Rebuild search index if approved
    if faq.is_approved:
        await hybrid_search_engine.build_index(db)

    cat_res = await db.execute(select(Category).where(Category.id == faq.category_id))
    cat = cat_res.scalars().first()

    return FAQOut(
        id=str(faq.id),
        category_id=str(faq.category_id),
        category_name=cat.name if cat else None,
        canonical_question=faq.canonical_question,
        alternative_questions=faq.alternative_questions or [],
        answer=faq.answer,
        keywords=faq.keywords or [],
        source_url=faq.source_url,
        source_title=faq.source_title,
        source_type=faq.source_type,
        content_owner=faq.content_owner,
        approval_status=faq.approval_status,
        is_approved=faq.is_approved,
        version=faq.version,
        last_reviewed=faq.last_reviewed,
        created_at=faq.created_at,
        updated_at=faq.updated_at,
    )


@router.put("/admin/faqs/{id}", response_model=FAQOut)
async def update_faq(
    id: str,
    body: FAQUpdate,
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Update an existing FAQ record."""
    stmt = select(FAQ).options(selectinload(FAQ.category)).where(FAQ.id == id)
    res = await db.execute(stmt)
    faq = res.scalars().first()
    if not faq:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="FAQ not found.")

    for field, val in body.model_dump(exclude_unset=True).items():
        setattr(faq, field, val)

    faq.version += 1
    faq.last_reviewed = datetime.now(timezone.utc)

    audit = AuditLog(
        admin_id=admin.id,
        action="update_faq",
        resource_type="faq",
        resource_id=str(faq.id),
        details={"updated_fields": list(body.model_dump(exclude_unset=True).keys())},
    )
    db.add(audit)
    await db.commit()
    await db.refresh(faq)

    # Update index
    await hybrid_search_engine.build_index(db)

    return FAQOut(
        id=str(faq.id),
        category_id=str(faq.category_id),
        category_name=faq.category.name if faq.category else None,
        canonical_question=faq.canonical_question,
        alternative_questions=faq.alternative_questions or [],
        answer=faq.answer,
        keywords=faq.keywords or [],
        source_url=faq.source_url,
        source_title=faq.source_title,
        source_type=faq.source_type,
        content_owner=faq.content_owner,
        approval_status=faq.approval_status,
        is_approved=faq.is_approved,
        version=faq.version,
        last_reviewed=faq.last_reviewed,
        created_at=faq.created_at,
        updated_at=faq.updated_at,
    )


@router.delete("/admin/faqs/{id}")
async def delete_faq(
    id: str,
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Delete an FAQ from the knowledge base."""
    stmt = select(FAQ).where(FAQ.id == id)
    res = await db.execute(stmt)
    faq = res.scalars().first()
    if not faq:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="FAQ not found.")

    audit = AuditLog(
        admin_id=admin.id,
        action="delete_faq",
        resource_type="faq",
        resource_id=id,
        details={"canonical_question": faq.canonical_question},
    )
    db.add(audit)
    await db.delete(faq)
    await db.commit()

    # Rebuild search index
    await hybrid_search_engine.build_index(db)
    return {"status": "success", "message": "FAQ deleted."}

