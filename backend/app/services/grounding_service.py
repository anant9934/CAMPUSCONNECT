import re
import logging
from typing import List, Dict, Any, Tuple, Optional

logger = logging.getLogger(__name__)

# Allowed official domains for LPU
ALLOWED_DOMAINS = [
    "ums.lpu.in",
    "lpu.in",
    "www.lpu.in",
    "nest.lpu.in",
    "touch.lpu.in"
]

FORBIDDEN_PATTERNS = [
    r"accessed (?:your )?(?:private|personal|student) record",
    r"checked (?:your )?(?:private|personal|student) (?:account|record)",
    r"updated (?:your )?attendance",
    r"processed (?:your )?fee",
    r"paid (?:your )?fee",
    r"your password is",
    r"send (?:me )?your password",
    r"enter your (?:password|pin|otp)",
    r"provide your (?:credit|debit) card",
    r"charged your (?:credit|debit) card",
    r"deducted from your (?:credit|debit) card",
]

CATEGORY_FOLLOW_UPS = {
    "academics": [
        "How do I apply for duty leave or medical leave on UMS?",
        "Where can I view my Continuous Assessment (CA) scores?",
        "Where is the official academic calendar published?"
    ],
    "examinations": [
        "Where is the Block 34 examination cell located?",
        "How do I submit an exam re-evaluation request?",
        "Where can I download my admit card for end term exams?"
    ],
    "hostel": [
        "What is the outpass procedure for night leave?",
        "How do I contact my hostel warden or maintenance?",
        "What are the hostel mess timings?"
    ],
    "transport": [
        "Does LPU provide bus service from Jalandhar or Ludhiana?",
        "How can I apply for a semester bus pass?",
        "Where is the university transport office located?"
    ],
    "fees": [
        "How do I download my fee receipt on UMS?",
        "What payment options are available for semester fees?",
        "Where is the university accounts division?"
    ],
    "campus-services": [
        "What emergency services are available at UniHospital?",
        "Where is Block 13 and the Division of Student Affairs?",
        "What facilities are inside UniMall?"
    ],
    "library": [
        "Where is the Central Library (Block 37) located?",
        "How do I access IEEE e-journals on UMS?",
        "Can I issue books with my student smart card?"
    ]
}


class GroundingValidationError(Exception):
    pass


def validate_grounded_response(
    response_text: str,
    evidence_context: str
) -> Tuple[bool, str, str]:
    """
    Validates that the generated response does not contain forbidden assertions,
    fake URLs, or claims of ERP/financial transactions.
    Returns: (is_valid, sanitized_or_fallback_text, reason)
    """
    text_lower = response_text.lower()

    # 1. Check for forbidden transaction or privacy-violating claims
    for pattern in FORBIDDEN_PATTERNS:
        if re.search(pattern, text_lower):
            logger.warning(f"Grounding validation failed: matched forbidden pattern '{pattern}'")
            return False, "", f"Forbidden assertion detected: '{pattern}'"

    # 2. Check for unauthorized external URLs
    urls_found = re.findall(r'https?://[^\s)\]"]+', response_text)
    for url in urls_found:
        domain_match = False
        for allowed in ALLOWED_DOMAINS:
            if allowed in url.lower():
                domain_match = True
                break
        if not domain_match:
            logger.warning(f"Grounding validation detected unverified URL: {url}")
            # Replace suspicious URL with official UMS portal
            response_text = response_text.replace(url, "https://ums.lpu.in")

    return True, response_text, "Valid and grounded"


def generate_follow_up_suggestions(
    category_slug: Optional[str] = None,
    query: str = ""
) -> List[str]:
    """Generates 2-3 relevant follow-up prompt suggestions."""
    if category_slug and category_slug in CATEGORY_FOLLOW_UPS:
        return CATEGORY_FOLLOW_UPS[category_slug][:3]

    # Default general follow-ups
    return [
        "How do I download my examination date sheet?",
        "Where can I find LPU bus routes?",
        "How do I contact hostel support?"
    ]
