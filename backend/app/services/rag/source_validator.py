import re
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional


class SourceValidationError(Exception):
    pass


def is_valid_source_url(url: Optional[str]) -> bool:
    """Validate that source URL is a well-formed HTTP/HTTPS URL."""
    if not url:
        return False
    url_pattern = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' # domain...
        r'localhost|' # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return bool(url_pattern.match(url.strip()))


def evaluate_source_freshness(last_reviewed: Optional[datetime]) -> float:
    """
    Evaluates freshness of the source.
    Returns a multiplier from 0.85 (outdated > 365 days) to 1.0 (reviewed within 90 days).
    """
    if not last_reviewed:
        return 0.90
    
    # Handle timezone awareness
    now = datetime.now(timezone.utc)
    if last_reviewed.tzinfo is None:
        last_reviewed = last_reviewed.replace(tzinfo=timezone.utc)
    
    age_days = (now - last_reviewed).days
    if age_days <= 90:
        return 1.0
    elif age_days <= 180:
        return 0.98
    elif age_days <= 365:
        return 0.92
    else:
        return 0.85  # Outdated penalty


def validate_record_for_retrieval(record: Dict[str, Any]) -> bool:
    """
    Strict gatekeeper: checks that the record is fully approved for student retrieval.
    Unapproved, pending, review-required, or expired records must NEVER be returned to the student.
    """
    if not record.get("is_approved", False):
        return False
    if record.get("approval_status", "").lower() != "approved":
        return False
    if record.get("requires_admin_review", False):
        return False

    # Exclude expired records from authoritative student answers
    expiry = record.get("review_expiry_date")
    if expiry:
        now = datetime.now(timezone.utc)
        if hasattr(expiry, "tzinfo") and expiry.tzinfo is None:
            expiry = expiry.replace(tzinfo=timezone.utc)
        if isinstance(expiry, datetime) and now > expiry:
            return False

    return True


def format_citation(source_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Format citation metadata into a clean structure for frontend rendering."""
    title = source_dict.get("source_title") or source_dict.get("title") or "LPU Official Information"
    source_type = source_dict.get("source_type") or "Official Portal"
    clause = source_dict.get("clause_reference")
    page = source_dict.get("source_page")
    meta = source_dict.get("type_metadata") or {}

    # Build rich type-specific details
    provenance_parts = []
    if clause:
        provenance_parts.append(f"Ref: {clause}")
    if page:
        provenance_parts.append(f"Page: {page}")
    if meta.get("official_email"):
        provenance_parts.append(f"Email: {meta['official_email']}")
    if meta.get("verified_phone"):
        provenance_parts.append(f"Tel: {meta['verified_phone']}")
    if meta.get("operating_hours"):
        provenance_parts.append(f"Hours: {meta['operating_hours']}")
    if meta.get("academic_session"):
        provenance_parts.append(f"Session: {meta['academic_session']}")

    provenance_str = " | ".join(provenance_parts)

    raw_snippet = source_dict.get("answer") or source_dict.get("content") or ""
    snippet = raw_snippet[:220] + ("..." if len(raw_snippet) > 220 else "")
    if provenance_str:
        snippet = f"[{provenance_str}]\n{snippet}"

    return {
        "title": title,
        "url": source_dict.get("source_url") or source_dict.get("url") or source_dict.get("original_source_url") or "https://ums.lpu.in",
        "source_type": source_type,
        "verified": source_dict.get("verified", True),
        "content_owner": source_dict.get("content_owner") or source_dict.get("category_name") or "Lovely Professional University",
        "snippet": snippet,
        "clause_reference": clause,
        "source_page": page,
        "type_metadata": meta,
    }

