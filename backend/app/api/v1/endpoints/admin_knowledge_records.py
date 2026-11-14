from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import KnowledgeRecord, AdminUser, AuditLog
from app.api.v1.endpoints.admin_auth import get_current_admin
from app.schemas.knowledge_record import KnowledgeRecordCreate, KnowledgeRecordUpdate, KnowledgeRecordOut
from app.services.ingestion.validator import validate_and_normalize_record, compute_content_hash, KnowledgeValidationError
from app.services.ingestion.variant_generator import generate_searchable_variants
from app.services.rag.hybrid_search import hybrid_search_engine

router = APIRouter()


@router.get("/admin/knowledge-records/statistics")
async def get_knowledge_records_statistics(
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Returns distribution of records across all 30 types and approval statuses."""
    total_stmt = select(func.count(KnowledgeRecord.id))
    total_count = (await db.execute(total_stmt)).scalar() or 0

    approved_stmt = select(func.count(KnowledgeRecord.id)).where(KnowledgeRecord.is_approved == True)
    approved_count = (await db.execute(approved_stmt)).scalar() or 0

    pending_stmt = select(func.count(KnowledgeRecord.id)).where(
        or_(KnowledgeRecord.approval_status == "pending_review", KnowledgeRecord.requires_admin_review == True)
    )
    pending_count = (await db.execute(pending_stmt)).scalar() or 0

    sensitive_stmt = select(func.count(KnowledgeRecord.id)).where(KnowledgeRecord.is_sensitive == True)
    sensitive_count = (await db.execute(sensitive_stmt)).scalar() or 0

    type_stmt = select(KnowledgeRecord.record_type, func.count(KnowledgeRecord.id)).group_by(KnowledgeRecord.record_type)
    type_res = await db.execute(type_stmt)
    type_counts = {r[0]: r[1] for r in type_res.all()}

    return {
        "total_records": total_count,
        "approved_records": approved_count,
        "pending_review_records": pending_count,
        "sensitive_records": sensitive_count,
        "type_distribution": type_counts
    }


@router.get("/admin/knowledge-records/conflicts")
async def list_conflicting_and_review_records(
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Lists records that require admin intervention due to sensitivity, expiry, or conflicts."""
    stmt = select(KnowledgeRecord).where(
        or_(
            KnowledgeRecord.requires_admin_review == True,
            KnowledgeRecord.approval_status == "pending_review",
            KnowledgeRecord.approval_status == "conflict"
        )
    ).order_by(KnowledgeRecord.updated_at.desc())

    res = await db.execute(stmt)
    records = res.scalars().all()

    return [
        {
            "id": str(r.id),
            "record_id": r.record_id,
            "record_type": r.record_type,
            "title": r.title,
            "category_name": r.category_name,
            "approval_status": r.approval_status,
            "is_sensitive": r.is_sensitive,
            "requires_admin_review": r.requires_admin_review,
            "last_verified_at": r.last_verified_at.isoformat() if r.last_verified_at else None,
            "source_document": r.source_document or r.original_source_url
        }
        for r in records
    ]


@router.get("/admin/knowledge-records", response_model=List[KnowledgeRecordOut])
async def list_knowledge_records(
    record_type: Optional[str] = None,
    approval_status: Optional[str] = None,
    is_sensitive: Optional[bool] = None,
    search: Optional[str] = None,
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """List unified knowledge repository records across all 30 types with rich filters."""
    stmt = select(KnowledgeRecord).order_by(KnowledgeRecord.updated_at.desc())

    if record_type:
        stmt = stmt.where(KnowledgeRecord.record_type == record_type)
    if approval_status:
        stmt = stmt.where(KnowledgeRecord.approval_status == approval_status)
    if is_sensitive is not None:
        stmt = stmt.where(KnowledgeRecord.is_sensitive == is_sensitive)

    res = await db.execute(stmt)
    records = res.scalars().all()

    out = []
    for r in records:
        if search:
            s_low = search.lower()
            if s_low not in r.title.lower() and s_low not in r.content.lower() and s_low not in r.record_id.lower():
                continue
        out.append(
            KnowledgeRecordOut(
                id=str(r.id),
                record_id=r.record_id,
                record_type=r.record_type,
                title=r.title,
                content=r.content,
                category_id=str(r.category_id) if r.category_id else None,
                category_name=r.category_name,
                original_source_url=r.original_source_url,
                source_document=r.source_document,
                source_page=r.source_page,
                clause_reference=r.clause_reference,
                publication_date=r.publication_date,
                last_verified_date=r.last_verified_date,
                effective_date=r.effective_date,
                review_expiry_date=r.review_expiry_date,
                approval_status=r.approval_status,
                is_approved=r.is_approved,
                is_sensitive=r.is_sensitive,
                requires_admin_review=r.requires_admin_review,
                version=r.version,
                content_hash=r.content_hash,
                searchable_variants=r.searchable_variants or [],
                type_metadata=r.type_metadata or {},
                audit_trail=r.audit_trail or [],
                created_at=r.created_at,
                updated_at=r.updated_at,
            )
        )
    return out


@router.post("/admin/knowledge-records", response_model=KnowledgeRecordOut)
async def create_knowledge_record(
    body: KnowledgeRecordCreate,
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Create a new record in the unified knowledge repository with validation."""
    try:
        norm = validate_and_normalize_record(body.model_dump())
    except KnowledgeValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    # Duplicate check
    existing = (await db.execute(
        select(KnowledgeRecord).where(
            or_(
                KnowledgeRecord.record_id == norm["record_id"],
                KnowledgeRecord.content_hash == norm["content_hash"]
            )
        )
    )).scalars().first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Duplicate detected: record with ID '{norm['record_id']}' or identical content hash already exists."
        )

    # Generate variants if empty
    if not norm["searchable_variants"]:
        norm["searchable_variants"] = await generate_searchable_variants(norm)

    rec = KnowledgeRecord(
        record_id=norm["record_id"],
        record_type=norm["record_type"],
        title=norm["title"],
        content=norm["content"],
        category_id=norm["category_id"],
        category_name=norm["category_name"],
        original_source_url=norm["original_source_url"],
        source_document=norm["source_document"],
        source_page=norm["source_page"],
        clause_reference=norm["clause_reference"],
        publication_date=norm["publication_date"],
        last_verified_date=norm["last_verified_date"],
        effective_date=norm["effective_date"],
        review_expiry_date=norm["review_expiry_date"],
        approval_status=norm["approval_status"],
        is_approved=norm["is_approved"],
        is_sensitive=norm["is_sensitive"],
        requires_admin_review=norm["requires_admin_review"],
        version=1,
        content_hash=norm["content_hash"],
        searchable_variants=norm["searchable_variants"],
        type_metadata=norm["type_metadata"],
        audit_trail=[
            {
                "action": "created",
                "admin": admin.username,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "note": "Manual creation via Admin Portal"
            }
        ],
    )
    db.add(rec)

    audit = AuditLog(
        admin_id=admin.id,
        action="create_knowledge_record",
        resource_type="knowledge_record",
        resource_id=rec.record_id,
        details={"title": rec.title, "record_type": rec.record_type},
    )
    db.add(audit)
    await db.commit()
    await db.refresh(rec)

    # Rebuild search index
    await hybrid_search_engine.build_index(db)

    return KnowledgeRecordOut(
        id=str(rec.id),
        record_id=rec.record_id,
        record_type=rec.record_type,
        title=rec.title,
        content=rec.content,
        category_id=str(rec.category_id) if rec.category_id else None,
        category_name=rec.category_name,
        original_source_url=rec.original_source_url,
        source_document=rec.source_document,
        source_page=rec.source_page,
        clause_reference=rec.clause_reference,
        publication_date=rec.publication_date,
        last_verified_date=rec.last_verified_date,
        effective_date=rec.effective_date,
        review_expiry_date=rec.review_expiry_date,
        approval_status=rec.approval_status,
        is_approved=rec.is_approved,
        is_sensitive=rec.is_sensitive,
        requires_admin_review=rec.requires_admin_review,
        version=rec.version,
        content_hash=rec.content_hash,
        searchable_variants=rec.searchable_variants or [],
        type_metadata=rec.type_metadata or {},
        audit_trail=rec.audit_trail or [],
        created_at=rec.created_at,
        updated_at=rec.updated_at,
    )


@router.get("/admin/knowledge-records/{id}", response_model=KnowledgeRecordOut)
async def get_knowledge_record(
    id: str,
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get a single record from the unified repository by UUID or institutional record_id."""
    stmt = select(KnowledgeRecord).where(
        or_(KnowledgeRecord.id == id, KnowledgeRecord.record_id == id)
    )
    res = await db.execute(stmt)
    rec = res.scalars().first()
    if not rec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found.")

    return KnowledgeRecordOut(
        id=str(rec.id),
        record_id=rec.record_id,
        record_type=rec.record_type,
        title=rec.title,
        content=rec.content,
        category_id=str(rec.category_id) if rec.category_id else None,
        category_name=rec.category_name,
        original_source_url=rec.original_source_url,
        source_document=rec.source_document,
        source_page=rec.source_page,
        clause_reference=rec.clause_reference,
        publication_date=rec.publication_date,
        last_verified_date=rec.last_verified_date,
        effective_date=rec.effective_date,
        review_expiry_date=rec.review_expiry_date,
        approval_status=rec.approval_status,
        is_approved=rec.is_approved,
        is_sensitive=rec.is_sensitive,
        requires_admin_review=rec.requires_admin_review,
        version=rec.version,
        content_hash=rec.content_hash,
        searchable_variants=rec.searchable_variants or [],
        type_metadata=rec.type_metadata or {},
        audit_trail=rec.audit_trail or [],
        created_at=rec.created_at,
        updated_at=rec.updated_at,
    )


@router.put("/admin/knowledge-records/{id}", response_model=KnowledgeRecordOut)
async def update_knowledge_record(
    id: str,
    body: KnowledgeRecordUpdate,
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Update an existing knowledge record with version bump and audit ledger."""
    stmt = select(KnowledgeRecord).where(
        or_(KnowledgeRecord.id == id, KnowledgeRecord.record_id == id)
    )
    res = await db.execute(stmt)
    rec = res.scalars().first()
    if not rec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found.")

    updates = body.model_dump(exclude_unset=True)
    for field, val in updates.items():
        setattr(rec, field, val)

    # Bump version and refresh hash
    rec.version += 1
    rec.last_verified_date = datetime.now(timezone.utc)
    rec.content_hash = compute_content_hash(rec.title, rec.content, rec.record_type)

    trail = list(rec.audit_trail or [])
    trail.append({
        "action": "updated",
        "admin": admin.username,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "fields": list(updates.keys()),
        "version": rec.version
    })
    rec.audit_trail = trail

    audit = AuditLog(
        admin_id=admin.id,
        action="update_knowledge_record",
        resource_type="knowledge_record",
        resource_id=rec.record_id,
        details={"version": rec.version, "fields": list(updates.keys())},
    )
    db.add(audit)
    await db.commit()
    await db.refresh(rec)

    # Rebuild search index
    await hybrid_search_engine.build_index(db)

    return KnowledgeRecordOut(
        id=str(rec.id),
        record_id=rec.record_id,
        record_type=rec.record_type,
        title=rec.title,
        content=rec.content,
        category_id=str(rec.category_id) if rec.category_id else None,
        category_name=rec.category_name,
        original_source_url=rec.original_source_url,
        source_document=rec.source_document,
        source_page=rec.source_page,
        clause_reference=rec.clause_reference,
        publication_date=rec.publication_date,
        last_verified_date=rec.last_verified_date,
        effective_date=rec.effective_date,
        review_expiry_date=rec.review_expiry_date,
        approval_status=rec.approval_status,
        is_approved=rec.is_approved,
        is_sensitive=rec.is_sensitive,
        requires_admin_review=rec.requires_admin_review,
        version=rec.version,
        content_hash=rec.content_hash,
        searchable_variants=rec.searchable_variants or [],
        type_metadata=rec.type_metadata or {},
        audit_trail=rec.audit_trail or [],
        created_at=rec.created_at,
        updated_at=rec.updated_at,
    )


@router.post("/admin/knowledge-records/{id}/approve")
async def approve_knowledge_record(
    id: str,
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Approve record, clearing review flags and activating for public student search."""
    stmt = select(KnowledgeRecord).where(
        or_(KnowledgeRecord.id == id, KnowledgeRecord.record_id == id)
    )
    res = await db.execute(stmt)
    rec = res.scalars().first()
    if not rec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found.")

    rec.approval_status = "approved"
    rec.is_approved = True
    rec.requires_admin_review = False
    rec.last_verified_date = datetime.now(timezone.utc)

    trail = list(rec.audit_trail or [])
    trail.append({
        "action": "approved",
        "admin": admin.username,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "note": "Approved by administrator for public RAG retrieval"
    })
    rec.audit_trail = trail

    audit = AuditLog(
        admin_id=admin.id,
        action="approve_knowledge_record",
        resource_type="knowledge_record",
        resource_id=rec.record_id,
        details={"record_type": rec.record_type, "is_sensitive": rec.is_sensitive},
    )
    db.add(audit)
    await db.commit()

    # Rebuild search index
    await hybrid_search_engine.build_index(db)
    return {"status": "success", "message": f"Record '{rec.record_id}' approved and indexed."}


@router.post("/admin/knowledge-records/{id}/reject")
async def reject_knowledge_record(
    id: str,
    reason: Optional[str] = None,
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Reject or deprecate record, preventing it from appearing in student search results."""
    stmt = select(KnowledgeRecord).where(
        or_(KnowledgeRecord.id == id, KnowledgeRecord.record_id == id)
    )
    res = await db.execute(stmt)
    rec = res.scalars().first()
    if not rec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found.")

    rec.approval_status = "rejected"
    rec.is_approved = False
    rec.requires_admin_review = False
    rec.last_verified_date = datetime.now(timezone.utc)

    trail = list(rec.audit_trail or [])
    trail.append({
        "action": "rejected",
        "admin": admin.username,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "note": reason or "Rejected by administrator during knowledge curation review"
    })
    rec.audit_trail = trail

    audit = AuditLog(
        admin_id=admin.id,
        action="reject_knowledge_record",
        resource_type="knowledge_record",
        resource_id=rec.record_id,
        details={"record_type": rec.record_type, "reason": reason},
    )
    db.add(audit)
    await db.commit()

    # Rebuild search index
    await hybrid_search_engine.build_index(db)
    return {"status": "success", "message": f"Record '{rec.record_id}' marked as rejected."}


@router.delete("/admin/knowledge-records/{id}")
async def delete_knowledge_record(
    id: str,
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Delete record from repository and search index."""
    stmt = select(KnowledgeRecord).where(
        or_(KnowledgeRecord.id == id, KnowledgeRecord.record_id == id)
    )
    res = await db.execute(stmt)
    rec = res.scalars().first()
    if not rec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found.")

    audit = AuditLog(
        admin_id=admin.id,
        action="delete_knowledge_record",
        resource_type="knowledge_record",
        resource_id=rec.record_id,
        details={"title": rec.title, "record_type": rec.record_type},
    )
    db.add(audit)
    await db.delete(rec)
    await db.commit()

    # Rebuild search index
    await hybrid_search_engine.build_index(db)
    return {"status": "success", "message": "Record deleted."}


@router.post("/admin/knowledge-records/{id}/generate-variants")
async def generate_variants_for_record(
    id: str,
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Generate or refresh question variants without altering facts."""
    stmt = select(KnowledgeRecord).where(
        or_(KnowledgeRecord.id == id, KnowledgeRecord.record_id == id)
    )
    res = await db.execute(stmt)
    rec = res.scalars().first()
    if not rec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found.")

    variants = await generate_searchable_variants({
        "title": rec.title,
        "content": rec.content,
        "record_type": rec.record_type
    })
    rec.searchable_variants = variants

    trail = list(rec.audit_trail or [])
    trail.append({
        "action": "generated_variants",
        "admin": admin.username,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "variants_count": len(variants)
    })
    rec.audit_trail = trail

    await db.commit()
    await hybrid_search_engine.build_index(db)

    return {
        "status": "success",
        "record_id": rec.record_id,
        "searchable_variants": variants
    }
