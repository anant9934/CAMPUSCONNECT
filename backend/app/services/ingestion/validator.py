import hashlib
import re
from datetime import datetime, timezone
from typing import Dict, Any, Tuple, Optional, List
from app.schemas.typed_knowledge import KnowledgeType

# Support all 30 standardized knowledge types plus backward-compatible legacy aliases
VALID_RECORD_TYPES = {t.value for t in KnowledgeType}
VALID_RECORD_TYPES.update({
    "academic_schedule",
    "contact_directory",
    "facility_service",
    "placement_procedure",
    "international_programme",
    "research_facility",
    "student_activity",
    "grievance_procedure",
    "official_notice"
})

SENSITIVE_TYPES = {
    KnowledgeType.POLICY.value,
    KnowledgeType.ACADEMIC_REGULATION.value,
    KnowledgeType.FEE_STRUCTURE.value,
    KnowledgeType.PLACEMENT_POLICY.value,
    KnowledgeType.SECURITY_EMERGENCY_PROTOCOL.value,
    KnowledgeType.MEDICAL_HEALTH_SERVICE.value,
    "placement_procedure",
    "grievance_procedure"
}

SENSITIVE_KEYWORDS = {
    "fee", "tuition", "scholarship", "attendance", "75%", "debarred", 
    "placement", "package", "salary", "emergency", "unihospital", "ambulance",
    "fine", "penalty", "harassment", "police", "expulsion"
}


class KnowledgeValidationError(Exception):
    pass


def compute_content_hash(title: str, content: str, record_type: str) -> str:
    """Computes a SHA-256 fingerprint for duplicate detection."""
    normalized = f"{record_type.strip().lower()}::{title.strip().lower()}::{content.strip()}"
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def is_record_sensitive(record_type: str, title: str, content: str) -> bool:
    """
    Determines if record covers sensitive policies, fees, attendance,
    placement, or emergency details that require dedicated administrative review.
    """
    if record_type in SENSITIVE_TYPES:
        return True
    combined = f"{title.lower()} {content.lower()}"
    return any(k in combined for k in SENSITIVE_KEYWORDS)


def is_record_expired(review_expiry_date: Optional[datetime]) -> bool:
    """Checks whether the record has passed its review or validity expiry date."""
    if not review_expiry_date:
        return False
    now = datetime.now(timezone.utc)
    if review_expiry_date.tzinfo is None:
        review_expiry_date = review_expiry_date.replace(tzinfo=timezone.utc)
    return now > review_expiry_date


def validate_and_normalize_record(record_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validates institutional record compliance against SRS requirements:
    - Record ID presence
    - Record Type in the 30 approved types
    - Title & Content non-empty
    - URL structure
    - Date sanity checks
    - Duplicate hash computation
    - Sensitivity marking
    - Expiration marking
    """
    record_id = record_data.get("record_id", "").strip()
    if not record_id:
        raise KnowledgeValidationError("Missing required 'record_id'.")

    record_type = record_data.get("record_type", "").strip().lower()
    if record_type not in VALID_RECORD_TYPES:
        raise KnowledgeValidationError(
            f"Invalid record_type '{record_type}'. Allowed types: {sorted(list(VALID_RECORD_TYPES))}"
        )

    title = record_data.get("title", "").strip()
    if not title:
        raise KnowledgeValidationError("Missing required 'title'.")

    content = record_data.get("content", "").strip()
    if not content:
        raise KnowledgeValidationError("Missing required 'content'.")

    source_url = record_data.get("original_source_url", "").strip()
    if not source_url or not (source_url.startswith("http://") or source_url.startswith("https://")):
        raise KnowledgeValidationError(f"Invalid original_source_url: '{source_url}'. Must start with http:// or https://")

    # Dates validation
    now_utc = datetime.now(timezone.utc)
    last_verified = record_data.get("last_verified_at") or record_data.get("last_verified_date") or now_utc
    effective_from = record_data.get("effective_from") or record_data.get("effective_date")
    review_expiry = record_data.get("review_due_at") or record_data.get("review_expiry_date")

    if effective_from and review_expiry and effective_from > review_expiry:
        raise KnowledgeValidationError("effective_from cannot be later than review_due_at.")

    content_hash = compute_content_hash(title, content, record_type)
    sensitive = is_record_sensitive(record_type, title, content)
    expired = is_record_expired(review_expiry)

    # Status determination
    initial_status = record_data.get("approval_status", "approved")
    if expired:
        approval_status = "expired"
        is_approved = False
    elif sensitive and record_data.get("requires_admin_review", False):
        approval_status = "pending_review"
        is_approved = False
    else:
        approval_status = initial_status
        is_approved = (approval_status == "approved")

    return {
        "record_id": record_id,
        "record_type": record_type,
        "title": title,
        "content": content,
        "category_id": record_data.get("category_id"),
        "category_name": record_data.get("category_name", "General"),
        "tags": record_data.get("tags", []),
        "institution": record_data.get("institution", "Lovely Professional University"),
        "campus": record_data.get("campus", "Phagwara, Punjab"),
        "original_source_url": source_url,
        "source_id": record_data.get("source_id"),
        "source_title": record_data.get("source_title", "Official LPU Portal"),
        "source_type": record_data.get("source_type", "web_page"),
        "source_document": record_data.get("source_document"),
        "source_page": record_data.get("source_page"),
        "source_section": record_data.get("source_section"),
        "clause_reference": record_data.get("clause_reference"),
        "publication_date": record_data.get("publication_date"),
        "last_verified_date": last_verified,
        "last_verified_at": last_verified,
        "effective_date": effective_from,
        "effective_from": effective_from,
        "effective_to": record_data.get("effective_to"),
        "review_expiry_date": review_expiry,
        "review_due_at": review_expiry,
        "approval_status": approval_status,
        "verification_status": record_data.get("verification_status", "verified"),
        "verified_by": record_data.get("verified_by", "system"),
        "confidentiality": record_data.get("confidentiality", "public"),
        "language": record_data.get("language", "en"),
        "is_approved": is_approved,
        "is_active": record_data.get("is_active", True),
        "is_sensitive": sensitive,
        "requires_admin_review": sensitive and not is_approved,
        "version": record_data.get("version", 1),
        "content_hash": content_hash,
        "searchable_variants": record_data.get("searchable_variants", []),
        "type_metadata": record_data.get("type_metadata", {}),
        "audit_trail": record_data.get("audit_trail", [
            {
                "timestamp": now_utc.isoformat(),
                "action": "ingested_v4",
                "actor": "system",
                "notes": "Validated and normalized in Data Quality v4.0 pipeline"
            }
        ])
    }
