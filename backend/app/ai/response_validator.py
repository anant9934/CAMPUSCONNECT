import re
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

# Permitted domain whitelist for Lovely Professional University
PERMITTED_DOMAINS = [
    "ums.lpu.in",
    "lpu.in",
    "www.lpu.in",
    "play.google.com",
    "apps.apple.com",
    "github.com",
]


class ResponseValidator:
    """
    Validates LLM-generated output against university safety, privacy,
    and grounding guardrails before delivering to the student.
    """

    @classmethod
    def validate_and_sanitize(cls, text: str) -> Tuple[str, bool, str]:
        """
        Validates generated response.
        Returns (sanitized_text, is_valid, rationale).
        """
        if not text or not text.strip():
            return (
                "I apologize, but I could not formulate a complete answer based on verified university records. Please check the official UMS portal at https://ums.lpu.in for current information.",
                False,
                "empty_generation"
            )

        sanitized = text

        # 1. Guard against fabricated private academic record claims
        fabricated_record_patterns = [
            r"your attendance is (?:currently\s+)?\d{1,2}(?:\.\d+)?%",
            r"your (?:cgpa|gpa) is \d\.\d{1,2}",
            r"your fee balance is ₹?\s*\d+",
        ]
        for pat in fabricated_record_patterns:
            if re.search(pat, sanitized, re.IGNORECASE):
                logger.warning(f"Validator detected potential fabricated student record claim: {pat}")
                sanitized = re.sub(
                    pat,
                    "[Personal record: Please log in to official UMS to inspect your individual records]",
                    sanitized,
                    flags=re.IGNORECASE
                )

        # 2. Sanitize unapproved external URLs
        urls = re.findall(r'https?://[^\s<>"\')]+', sanitized)
        for url in urls:
            domain_match = re.search(r'https?://([^/:]+)', url)
            if domain_match:
                domain = domain_match.group(1).lower()
                is_allowed = any(domain == p or domain.endswith("." + p) for p in PERMITTED_DOMAINS)
                if not is_allowed:
                    logger.warning(f"Sanitizing unapproved external URL: {url}")
                    sanitized = sanitized.replace(url, "https://ums.lpu.in/lpuums/")

        return sanitized, True, "validated"
