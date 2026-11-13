import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.admin_user import AdminUser
from app.models.audit import AuditLog
from app.models.ums_catalog import UMSServiceCatalog
from app.models.action_workflow import ActionWorkflow
from app.models.campus_place import CampusPlace
from app.api.v1.endpoints.admin_auth import get_current_admin
from app.schemas.ums import (
    UMSServiceCatalogOut,
    UMSServiceCatalogUpdate,
    ActionWorkflowOut,
    CampusPlaceOut,
)
from app.services.rag.hybrid_search import hybrid_search_engine

logger = logging.getLogger(__name__)

router = APIRouter()


# ==========================================
# PUBLIC UMS & CAMPUS ENDPOINTS
# ==========================================

@router.get("/ums/services", response_model=List[UMSServiceCatalogOut])
async def list_ums_services(
    query: Optional[str] = Query(None, description="Search query across service label and keywords"),
    module: Optional[str] = Query(None, description="Filter by UMS module"),
    action_type: Optional[str] = Query(None, description="Filter by action type"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=250),
    db: AsyncSession = Depends(get_db)
):
    """List and search across all 234 UMS menu entries from authenticated student screenshots."""
    stmt = select(UMSServiceCatalog).where(UMSServiceCatalog.is_active == True)

    if module:
        stmt = stmt.where(UMSServiceCatalog.module.ilike(f"%{module}%"))
    if action_type:
        stmt = stmt.where(UMSServiceCatalog.action_type == action_type)
    if query:
        q_wild = f"%{query.strip()}%"
        stmt = stmt.where(
            or_(
                UMSServiceCatalog.service_label.ilike(q_wild),
                UMSServiceCatalog.navigation_path.ilike(q_wild),
                UMSServiceCatalog.catalog_id.ilike(q_wild),
                UMSServiceCatalog.execution_boundary.ilike(q_wild),
            )
        )

    stmt = stmt.order_by(UMSServiceCatalog.catalog_id.asc()).offset(skip).limit(limit)
    res = await db.execute(stmt)
    return res.scalars().all()


@router.get("/ums/services/{catalog_id_or_id}", response_model=UMSServiceCatalogOut)
async def get_ums_service(
    catalog_id_or_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get details and breadcrumb path for a specific UMS service by catalog_id (e.g. UMS-001) or UUID."""
    stmt = select(UMSServiceCatalog).where(
        or_(
            UMSServiceCatalog.catalog_id == catalog_id_or_id,
            UMSServiceCatalog.id == catalog_id_or_id
        )
    )
    res = await db.execute(stmt)
    service = res.scalars().first()
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"UMS service '{catalog_id_or_id}' not found"
        )
    return service


@router.get("/ums/workflows", response_model=List[ActionWorkflowOut])
async def list_action_workflows(
    intent: Optional[str] = Query(None, description="Filter by user intent"),
    action_mode: Optional[str] = Query(None, description="Filter by action mode"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """List guided action workflows (Doctor, Hostel, Counselling, Library room, RMS, etc.)."""
    stmt = select(ActionWorkflow).where(ActionWorkflow.is_active == True)

    if intent:
        stmt = stmt.where(ActionWorkflow.user_intent.ilike(f"%{intent}%"))
    if action_mode:
        stmt = stmt.where(ActionWorkflow.action_mode == action_mode)

    stmt = stmt.order_by(ActionWorkflow.action_id.asc()).offset(skip).limit(limit)
    res = await db.execute(stmt)
    return res.scalars().all()


@router.get("/ums/workflows/{action_id_or_id}", response_model=ActionWorkflowOut)
async def get_action_workflow(
    action_id_or_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific action workflow by action_id (e.g. ACT-001) or UUID."""
    stmt = select(ActionWorkflow).where(
        or_(
            ActionWorkflow.action_id == action_id_or_id,
            ActionWorkflow.id == action_id_or_id
        )
    )
    res = await db.execute(stmt)
    wf = res.scalars().first()
    if not wf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Action workflow '{action_id_or_id}' not found"
        )
    return wf


@router.get("/campus/places", response_model=List[CampusPlaceOut])
async def list_campus_places(
    query: Optional[str] = Query(None, description="Search building, name, or service"),
    category: Optional[str] = Query(None, description="Filter by category"),
    building: Optional[str] = Query(None, description="Filter by building"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """List and search verified campus places, blocks, amenities, and medical facilities."""
    stmt = select(CampusPlace)

    if category:
        stmt = stmt.where(CampusPlace.category.ilike(f"%{category}%"))
    if building:
        stmt = stmt.where(CampusPlace.building.ilike(f"%{building}%"))
    if query:
        q_wild = f"%{query.strip()}%"
        stmt = stmt.where(
            or_(
                CampusPlace.name.ilike(q_wild),
                CampusPlace.building.ilike(q_wild),
                CampusPlace.description.ilike(q_wild),
                CampusPlace.place_id.ilike(q_wild),
            )
        )

    stmt = stmt.order_by(CampusPlace.place_id.asc()).offset(skip).limit(limit)
    res = await db.execute(stmt)
    return res.scalars().all()


@router.get("/campus/places/{place_id_or_id}", response_model=CampusPlaceOut)
async def get_campus_place(
    place_id_or_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get verified place details and coordinates by place_id (e.g. LOC-001) or UUID."""
    stmt = select(CampusPlace).where(
        or_(
            CampusPlace.place_id == place_id_or_id,
            CampusPlace.id == place_id_or_id
        )
    )
    res = await db.execute(stmt)
    place = res.scalars().first()
    if not place:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campus place '{place_id_or_id}' not found"
        )
    return place


# ==========================================
# ADMIN MANAGEMENT ENDPOINTS
# ==========================================

@router.get("/admin/ums-catalog", response_model=List[UMSServiceCatalogOut])
async def admin_list_ums_catalog(
    module: Optional[str] = None,
    verification_status: Optional[str] = None,
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=300),
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Admin inspection of all 234 UMS menu items with verification status and boundaries."""
    stmt = select(UMSServiceCatalog)

    if module:
        stmt = stmt.where(UMSServiceCatalog.module.ilike(f"%{module}%"))
    if verification_status:
        stmt = stmt.where(UMSServiceCatalog.verification_status == verification_status)
    if is_active is not None:
        stmt = stmt.where(UMSServiceCatalog.is_active == is_active)
    if search:
        q_wild = f"%{search.strip()}%"
        stmt = stmt.where(
            or_(
                UMSServiceCatalog.service_label.ilike(q_wild),
                UMSServiceCatalog.catalog_id.ilike(q_wild),
                UMSServiceCatalog.navigation_path.ilike(q_wild),
                UMSServiceCatalog.module.ilike(q_wild),
            )
        )

    stmt = stmt.order_by(UMSServiceCatalog.catalog_id.asc()).offset(skip).limit(limit)
    res = await db.execute(stmt)
    return res.scalars().all()


@router.get("/admin/ums-catalog/{id}", response_model=UMSServiceCatalogOut)
async def admin_get_ums_service(
    id: str,
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Admin inspect specific UMS service entry by ID."""
    stmt = select(UMSServiceCatalog).where(
        or_(
            UMSServiceCatalog.id == id,
            UMSServiceCatalog.catalog_id == id
        )
    )
    res = await db.execute(stmt)
    service = res.scalars().first()
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"UMS service entry '{id}' not found"
        )
    return service


@router.put("/admin/ums-catalog/{id}", response_model=UMSServiceCatalogOut)
async def admin_update_ums_service(
    id: str,
    body: UMSServiceCatalogUpdate,
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Admin update breadcrumbs, verification status, deep link status, notes, or active state."""
    stmt = select(UMSServiceCatalog).where(
        or_(
            UMSServiceCatalog.id == id,
            UMSServiceCatalog.catalog_id == id
        )
    )
    res = await db.execute(stmt)
    service = res.scalars().first()
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"UMS service entry '{id}' not found"
        )

    changes = {}
    for field, val in body.model_dump(exclude_unset=True).items():
        old_val = getattr(service, field)
        if old_val != val:
            changes[field] = {"old": old_val, "new": val}
            setattr(service, field, val)

    if changes:
        audit = AuditLog(
            admin_id=admin.id,
            action="update_ums_catalog_entry",
            resource_type="ums_catalog",
            resource_id=service.catalog_id,
            details=changes,
        )
        db.add(audit)
        await db.commit()
        await db.refresh(service)

        # Refresh hybrid search index
        try:
            await hybrid_search_engine.sync_with_db(db)
        except Exception as e:
            logger.warning(f"Error resyncing hybrid search engine after UMS catalog update: {e}")

    return service


@router.get("/admin/action-workflows", response_model=List[ActionWorkflowOut])
async def admin_list_action_workflows(
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Admin inspect all 24 action workflows."""
    stmt = select(ActionWorkflow).order_by(ActionWorkflow.action_id.asc())
    res = await db.execute(stmt)
    return res.scalars().all()


@router.get("/admin/campus-places", response_model=List[CampusPlaceOut])
async def admin_list_campus_places(
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Admin inspect verified campus places and wayfinding locations."""
    stmt = select(CampusPlace).order_by(CampusPlace.place_id.asc())
    res = await db.execute(stmt)
    return res.scalars().all()

