from fastapi import APIRouter
from app.api.v1.endpoints import (
    chat,
    categories,
    sessions,
    conversations,
    feedback,
    admin_auth,
    admin_dashboard,
    admin_faqs,
    admin_documents,
    admin_analytics,
    admin_reindex,
    admin_knowledge_records,
    ums_routes,
    portal,
    campus_features,
    agents,
    admin_intelligence,
    opportunities,
)

api_router = APIRouter()

# Public Endpoints
api_router.include_router(chat.router, tags=["chat"])
api_router.include_router(agents.router, prefix="/agents", tags=["multi-agent"])
api_router.include_router(portal.router, tags=["student-portal"])
api_router.include_router(campus_features.router, prefix="/campus", tags=["campus-features"])
api_router.include_router(opportunities.router, tags=["opportunities"])
api_router.include_router(categories.router, tags=["categories"])
api_router.include_router(sessions.router, tags=["sessions"])
api_router.include_router(conversations.router, tags=["conversations"])
api_router.include_router(feedback.router, tags=["feedback"])
api_router.include_router(ums_routes.router, tags=["ums-actions-campus"])

# Admin Endpoints
api_router.include_router(admin_auth.router, tags=["admin-auth"])
api_router.include_router(admin_intelligence.router, prefix="/admin/intelligence", tags=["admin-intelligence"])
api_router.include_router(admin_dashboard.router, tags=["admin-dashboard"])
api_router.include_router(admin_faqs.router, tags=["admin-faqs"])
api_router.include_router(admin_documents.router, tags=["admin-documents"])
api_router.include_router(admin_knowledge_records.router, tags=["admin-knowledge-records"])
api_router.include_router(admin_analytics.router, tags=["admin-analytics"])
api_router.include_router(admin_reindex.router, tags=["admin-reindex"])

