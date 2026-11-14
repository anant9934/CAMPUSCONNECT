from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models import AdminUser, AuditLog
from app.api.v1.endpoints.admin_auth import get_current_admin
from app.services.rag.hybrid_search import hybrid_search_engine

router = APIRouter()


@router.post("/admin/reindex")
async def trigger_reindex(
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Force re-indexation of all approved knowledge base FAQs and documents into memory."""
    await hybrid_search_engine.build_index(db)

    audit = AuditLog(
        admin_id=admin.id,
        action="reindex_knowledge_base",
        resource_type="system",
        resource_id="hybrid_index",
        details={"total_indexed": len(hybrid_search_engine.corpus_cache)},
    )
    db.add(audit)
    await db.commit()

    return {
        "status": "success",
        "message": f"Successfully reindexed {len(hybrid_search_engine.corpus_cache)} approved records.",
        "total_indexed": len(hybrid_search_engine.corpus_cache),
    }

