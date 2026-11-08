import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.models import (
    FAQ,
    KnowledgeChunk,
    KnowledgeDocument,
    Category,
    KnowledgeRecord,
    UMSServiceCatalog,
    ActionWorkflow,
    CampusPlace,
)
from app.services.rag.keyword_search import compute_keyword_score, normalize_query
from app.services.rag.bm25_search import BM25SearchEngine
from app.services.rag.tfidf_search import TfidfSearchEngine
from app.services.rag.semantic_search import SemanticSearchEngine
from app.services.rag.entity_matcher import EntityMatcher
from app.services.rag.source_validator import validate_record_for_retrieval, evaluate_source_freshness, format_citation
from app.services.rag.confidence import evaluate_confidence, ConfidenceEvaluation

logger = logging.getLogger(__name__)

AUTHORITY_WEIGHTS = {
    "policy": 1.25,
    "academic_regulation": 1.25,
    "examination_rule": 1.20,
    "attendance_policy": 1.20,
    "security_emergency_protocol": 1.25,
    "medical_health_service": 1.20,
    "fee_structure": 1.20,
    "scholarship_scheme": 1.20,
    "process_sop": 1.15,
    "action_workflow": 1.20,
    "ums_service": 1.20,
    "faculty_profile": 1.25,
    "academic_programme": 1.15,
    "hostel_rule": 1.15,
    "transport_route": 1.15,
    "placement_policy": 1.20,
    "grievance_redressal_mechanism": 1.20,
    "grading_system": 1.20,
    "library_resource": 1.10,
    "campus_facility": 1.20,
    "campus_place": 1.25,
    "student_activity": 1.15,
    "faq": 1.0,
    "chunk": 1.0,
    "unverified": 0.70
}


class HybridSearchEngine:
    def __init__(self):
        self.bm25_engine = BM25SearchEngine()
        self.tfidf_engine = TfidfSearchEngine()
        self.semantic_engine = SemanticSearchEngine()
        self.corpus_cache: List[Dict[str, Any]] = []
        self._is_indexed = False

    async def build_index(self, db: AsyncSession) -> None:
        """Fetch all approved FAQs, document chunks, and typed knowledge records into search indices."""
        records: List[Dict[str, Any]] = []

        # 1. Fetch Approved FAQs
        faq_stmt = (
            select(FAQ)
            .options(selectinload(FAQ.category), selectinload(FAQ.sources))
            .where(FAQ.is_approved == True, FAQ.approval_status == "approved")
        )
        faq_result = await db.execute(faq_stmt)
        faqs = faq_result.scalars().all()

        for f in faqs:
            records.append({
                "id": str(f.id),
                "record_id": f.faq_id if hasattr(f, "faq_id") else str(f.id),
                "type": "faq",
                "category_id": str(f.category_id),
                "category_name": f.category.name if f.category else "General",
                "category_slug": f.category.slug if f.category else "general",
                "canonical_question": f.canonical_question,
                "alternative_questions": f.alternative_questions or [],
                "answer": f.answer,
                "content": f.answer,
                "keywords": f.keywords or [],
                "source_url": f.source_url or "https://ums.lpu.in",
                "source_title": f.source_title or "LPU Official Information",
                "source_type": f.source_type or "Official FAQ",
                "content_owner": f.content_owner or "Lovely Professional University",
                "last_reviewed": f.last_reviewed,
                "is_approved": f.is_approved,
                "approval_status": f.approval_status,
                "is_active": True,
                "version": f.version,
            })

        # 2. Fetch Approved Document Chunks
        chunk_stmt = (
            select(KnowledgeChunk)
            .join(KnowledgeDocument)
            .options(selectinload(KnowledgeChunk.document).selectinload(KnowledgeDocument.category))
            .where(KnowledgeDocument.is_approved == True, KnowledgeDocument.status == "approved")
        )
        chunk_result = await db.execute(chunk_stmt)
        chunks = chunk_result.scalars().all()

        for c in chunks:
            doc = c.document
            records.append({
                "id": str(c.id),
                "record_id": str(c.id),
                "type": "chunk",
                "category_id": str(doc.category_id) if doc.category_id else None,
                "category_name": doc.category.name if doc.category else "General",
                "category_slug": doc.category.slug if doc.category else "general",
                "canonical_question": doc.title,
                "alternative_questions": [],
                "answer": c.content,
                "content": c.content,
                "keywords": [],
                "source_url": f"https://ums.lpu.in/docs/{doc.filename}",
                "source_title": f"{doc.title} (Page {c.page_number or 1})",
                "source_type": "Approved Handbook",
                "content_owner": "LPU Administration",
                "last_reviewed": doc.updated_at,
                "is_approved": doc.is_approved,
                "approval_status": doc.status,
                "is_active": True,
                "version": 1,
            })

        # 3. Fetch Approved Multi-Type Knowledge Records (30 Types v4.0)
        now_utc = datetime.now(timezone.utc)
        kr_stmt = (
            select(KnowledgeRecord)
            .options(selectinload(KnowledgeRecord.category))
            .where(
                KnowledgeRecord.is_approved == True,
                KnowledgeRecord.is_active == True,
                KnowledgeRecord.approval_status == "approved"
            )
        )
        kr_result = await db.execute(kr_stmt)
        krs = kr_result.scalars().all()

        for k in krs:
            # Exclude expired records from authoritative index
            if k.review_expiry_date or k.review_due_at:
                exp = k.review_due_at or k.review_expiry_date
                if exp.tzinfo is None:
                    exp = exp.replace(tzinfo=timezone.utc)
                if now_utc > exp:
                    continue

            if k.requires_admin_review and not k.is_approved:
                continue

            type_label = k.record_type.replace('_', ' ').title()
            meta_keywords = []
            if isinstance(k.type_metadata, dict):
                for val in k.type_metadata.values():
                    if isinstance(val, str):
                        meta_keywords.append(val)
                    elif isinstance(val, list):
                        meta_keywords.extend([str(x) for x in val if isinstance(x, str)])

            records.append({
                "id": str(k.id),
                "record_id": k.record_id,
                "type": k.record_type,
                "category_id": str(k.category_id) if k.category_id else None,
                "category_name": k.category_name or (k.category.name if k.category else "General"),
                "category_slug": (k.category.slug if k.category else (k.category_name or "general").lower().replace(" ", "-")),
                "canonical_question": k.title,
                "alternative_questions": k.searchable_variants or [],
                "answer": k.content,
                "content": k.content,
                "keywords": [k.record_type, k.category_name or "", k.clause_reference or ""] + (k.tags or []) + meta_keywords,
                "source_url": k.original_source_url,
                "source_title": f"[{type_label.upper()}] {k.source_title or k.source_document or 'LPU Official Directory'}",
                "source_type": type_label,
                "source_document": k.source_document,
                "source_page": k.source_page,
                "clause_reference": k.clause_reference,
                "content_owner": k.verified_by or "Lovely Professional University",
                "last_reviewed": k.last_verified_at or k.last_verified_date,
                "effective_from": k.effective_from or k.effective_date,
                "review_expiry_date": k.review_due_at or k.review_expiry_date,
                "is_approved": k.is_approved,
                "approval_status": k.approval_status,
                "is_active": k.is_active,
                "version": k.version,
                "type_metadata": k.type_metadata,
            })

        # 4. Fetch Active UMS Service Catalog (234 services)
        ums_stmt = select(UMSServiceCatalog).where(UMSServiceCatalog.is_active == True)
        ums_res = await db.execute(ums_stmt)
        ums_services = ums_res.scalars().all()
        for svc in ums_services:
            records.append({
                "id": str(svc.id),
                "record_id": svc.catalog_id,
                "type": "ums_service",
                "category_id": None,
                "category_name": svc.module,
                "category_slug": "ums-services",
                "canonical_question": f"How to find {svc.service_label} in UMS?",
                "alternative_questions": [f"Where is {svc.service_label}?", f"{svc.service_label} in {svc.module}"],
                "answer": f"To access {svc.service_label}, open UMS and navigate to: {svc.navigation_path}. Execution boundary: {svc.execution_boundary}.",
                "content": f"Service: {svc.service_label}. Module: {svc.module}. Path: {svc.navigation_path}. Boundary: {svc.execution_boundary}.",
                "keywords": [svc.service_label, svc.module, "ums", "portal"] + (svc.keywords or []),
                "source_url": svc.deep_link_url or "https://ums.lpu.in/lpuums/",
                "source_title": f"[UMS SERVICE] {svc.module} > {svc.service_label}",
                "source_type": "UMS Service Catalog",
                "content_owner": "LPU University Management System",
                "last_reviewed": svc.updated_at,
                "is_approved": True,
                "approval_status": "approved",
                "is_active": True,
                "version": 1,
                "type_metadata": {
                    "module": svc.module,
                    "service_label": svc.service_label,
                    "navigation_path": svc.navigation_path,
                    "execution_boundary": svc.execution_boundary,
                    "ums_authentication": svc.ums_authentication,
                }
            })

        # 5. Fetch Active Action Workflows (24 workflows)
        wf_stmt = select(ActionWorkflow).where(ActionWorkflow.is_active == True)
        wf_res = await db.execute(wf_stmt)
        workflows = wf_res.scalars().all()
        for wf in workflows:
            records.append({
                "id": str(wf.id),
                "record_id": wf.action_id,
                "type": "action_workflow",
                "category_id": None,
                "category_name": wf.target_system,
                "category_slug": "action-workflows",
                "canonical_question": f"How to {wf.user_intent}?",
                "alternative_questions": [wf.user_intent, f"Steps for {wf.user_intent}", f"Where to {wf.user_intent}"],
                "answer": f"{wf.chatbot_flow}. Navigation path: {wf.ums_navigation_path}. Prerequisites: {', '.join(wf.prerequisites or [])}. Guardrail: {wf.execution_guardrail}.",
                "content": f"{wf.user_intent}. Path: {wf.ums_navigation_path}. Flow: {wf.chatbot_flow}. Guardrail: {wf.execution_guardrail}.",
                "keywords": [wf.user_intent, wf.target_system, "workflow", "booking"] + (wf.prerequisites or []),
                "source_url": wf.handoff_url or "https://ums.lpu.in/lpuums/",
                "source_title": f"[UMS WORKFLOW] {wf.user_intent}",
                "source_type": "UMS Action Workflow",
                "content_owner": "Lovely Professional University",
                "last_reviewed": wf.updated_at,
                "is_approved": True,
                "approval_status": "approved",
                "is_active": True,
                "version": 1,
                "type_metadata": {
                    "user_intent": wf.user_intent,
                    "target_system": wf.target_system,
                    "ums_navigation_path": wf.ums_navigation_path,
                    "action_mode": wf.action_mode,
                }
            })

        # 6. Fetch Verified Campus Places
        place_stmt = select(CampusPlace)
        place_res = await db.execute(place_stmt)
        places = place_res.scalars().all()
        for p in places:
            records.append({
                "id": str(p.id),
                "record_id": p.place_id,
                "type": "campus_place",
                "category_id": None,
                "category_name": p.category,
                "category_slug": "campus-places",
                "canonical_question": f"Where is {p.name} located?",
                "alternative_questions": [f"Location of {p.building}", f"Where to find {p.name}", p.building],
                "answer": f"{p.name} is located at {p.building} ({p.floor_room or 'Campus'}). {p.description} Available services: {', '.join(p.services_available or [])}. Hours: {p.opening_hours or 'N/A'}. Accessibility: {p.accessibility or 'N/A'}.",
                "content": f"{p.name} ({p.building}). {p.description}. Services: {', '.join(p.services_available or [])}.",
                "keywords": [p.name, p.building, p.category, "location", "map", "directions"] + (p.services_available or []),
                "source_url": p.official_map_url or "https://www.lpu.in/about_lpu/campus-tour.php",
                "source_title": f"[CAMPUS WAYFINDING] {p.building}",
                "source_type": "Campus Place Directory",
                "content_owner": "LPU Campus Infrastructure & Security",
                "last_reviewed": p.verified_at,
                "is_approved": True,
                "approval_status": "approved",
                "is_active": True,
                "version": 1,
                "type_metadata": {
                    "building": p.building,
                    "floor_room": p.floor_room,
                    "opening_hours": p.opening_hours,
                    "accessibility": p.accessibility,
                }
            })

        self.corpus_cache = records
        self.bm25_engine.fit_corpus(records)
        self.tfidf_engine.fit_corpus(records)
        self.semantic_engine.index_documents(records)
        self._is_indexed = True
        logger.info(f"Hybrid search index updated with {len(records)} approved knowledge items.")

    async def search(
        self,
        query: str,
        db: AsyncSession,
        category_slug: Optional[str] = None,
        record_type: Optional[str] = None,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """
        Execute calibrated hybrid search over approved records with BM25, TF-IDF,
        Dense Semantic embeddings, Exact Entity Matching, and Authority weighting.
        """
        if not self._is_indexed or not self.corpus_cache:
            await self.build_index(db)

        if not self.corpus_cache:
            eval_result = evaluate_confidence([])
            return {
                "candidates": [],
                "confidence": eval_result,
                "citations": [],
                "evidence_context": ""
            }

        norm_q = normalize_query(query)
        bm25_scores = self.bm25_engine.search(query)
        tfidf_scores = self.tfidf_engine.search(norm_q)
        semantic_scores = self.semantic_engine.search(norm_q)

        # Entity resolution & intent detection
        entity_match = EntityMatcher.match_entity(query)
        target_rec_id = entity_match["record_id"] if entity_match else None
        entity_boost = entity_match["boost"] if entity_match else 0.0

        q_lower = query.lower()
        is_wayfinding = any(w in q_lower for w in ["where is", "where's", "location of", "how to reach", "directions to"])
        is_ums = any(w in q_lower for w in ["on ums", "in ums", "ums portal", "navigation path", "service path", "how to find on ums"])

        now_utc = datetime.now(timezone.utc)
        ranked = []

        for doc in self.corpus_cache:
            # 1. Pre-retrieval safety check: only approved and active
            if not validate_record_for_retrieval(doc):
                continue
            if not doc.get("is_active", True):
                continue

            # 2. Metadata filtering
            if record_type and doc.get("type") != record_type:
                continue

            doc_id = doc["id"]
            rec_id = doc.get("record_id", doc_id)
            rtype = doc.get("type", "faq")

            bm_score = bm25_scores.get(doc_id, 0.0)
            tf_score = tfidf_scores.get(doc_id, 0.0)
            sem_score = semantic_scores.get(doc_id, 0.0)
            kw_score = compute_keyword_score(norm_q, doc)
            freshness = evaluate_source_freshness(doc.get("last_reviewed"))

            # 3. Base Calibrated Score: BM25 (0.35) + TFIDF (0.20) + Semantic (0.25) + Keyword (0.20)
            raw_hybrid = (
                0.35 * bm_score +
                0.20 * tf_score +
                0.25 * sem_score +
                0.20 * kw_score
            ) * freshness

            # 4. Curated Record vs Raw UUID FAQ Weighting
            # Deprecate un-curated raw UUID FAQs when competing with curated records
            is_raw_uuid = len(rec_id) == 36 and "-" in rec_id
            if is_raw_uuid:
                raw_hybrid *= 0.80

            # 5. Authority Multiplier (applied when candidate exhibits genuine relevance)
            if (kw_score >= 0.25 and (bm_score >= 0.20 or tf_score >= 0.20)) or sem_score >= 0.35:
                auth_weight = AUTHORITY_WEIGHTS.get(rtype, 1.0)
                raw_hybrid *= auth_weight

            # 6. Intent-to-Record-Type Alignment
            if kw_score >= 0.20 or bm_score >= 0.20:
                if is_wayfinding and rtype in ("campus_place", "campus_facility"):
                    raw_hybrid *= 1.30
                elif is_ums and rtype in ("ums_service", "action_workflow"):
                    raw_hybrid *= 1.30

            # 7. Exact Entity Matcher Direct Boost
            if target_rec_id and (rec_id == target_rec_id or doc_id == target_rec_id):
                raw_hybrid += entity_boost

            # 8. Recency weighting for time-sensitive records
            if rtype in ("important_date_academic_calendar", "academic_schedule", "official_notice"):
                eff = doc.get("effective_from") or doc.get("last_reviewed")
                if eff:
                    if eff.tzinfo is None:
                        eff = eff.replace(tzinfo=timezone.utc)
                    days_diff = (now_utc - eff).days
                    if days_diff <= 90:
                        raw_hybrid *= 1.10
                    elif days_diff > 365:
                        raw_hybrid *= 0.85

            # 9. Category affinity bonus
            if category_slug and doc.get("category_slug") == category_slug:
                raw_hybrid = min(1.0, raw_hybrid * 1.15)

            # 10. Canonical question match bonus (additive to preserve relative ranking)
            if kw_score >= 0.98 or bm_score >= 0.90:
                raw_hybrid += 0.15

            if raw_hybrid > 0.05:
                item = dict(doc)
                item["bm25_score"] = round(bm_score, 4)
                item["keyword_score"] = round(kw_score, 4)
                item["tfidf_score"] = round(tf_score, 4)
                item["semantic_score"] = round(sem_score, 4)
                item["hybrid_score"] = round(raw_hybrid, 4)
                ranked.append(item)

        # Sort descending by hybrid_score
        ranked.sort(key=lambda x: x["hybrid_score"], reverse=True)
        top_candidates = ranked[:top_k]

        # Evaluate calibrated confidence
        confidence_eval = evaluate_confidence(top_candidates)

        # Build citations & evidence context
        citations = []
        evidence_lines = []
        for idx, cand in enumerate(top_candidates):
            citations.append(format_citation(cand))
            evidence_lines.append(
                f"[Source {idx+1}: {cand.get('source_title', 'LPU')} ({cand.get('source_url', '')})]\n"
                f"Record ID: {cand.get('record_id', '')} | Type: {cand.get('type', '')}\n"
                f"Question/Topic: {cand.get('canonical_question', '')}\n"
                f"Verified Answer/Content: {cand.get('answer', cand.get('content', ''))}\n"
            )

        evidence_context = "\n\n".join(evidence_lines)

        return {
            "candidates": top_candidates,
            "confidence": confidence_eval,
            "citations": citations,
            "evidence_context": evidence_context
        }


# Global singleton instance
hybrid_search_engine = HybridSearchEngine()
