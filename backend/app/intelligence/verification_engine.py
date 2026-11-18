import re
import logging
from typing import Tuple, List, Dict, Any

from app.services.grounding_service import validate_grounded_response

logger = logging.getLogger(__name__)


class VerificationResult:
    def __init__(
        self,
        is_valid: bool,
        verified_content: str,
        violations_detected: List[str],
        policy_warnings: List[str]
    ):
        self.is_valid = is_valid
        self.verified_content = verified_content
        self.violations_detected = violations_detected
        self.policy_warnings = policy_warnings


class VerificationEngine:
    """
    LAYER 7 — VERIFICATION ENGINE
    Independent factual consistency, institutional policy compliance,
    unsupported claim interception, and citation verification.
    """

    UNAUTHORIZED_EXECUTION_PATTERNS = [
        r"i have (approved|updated|changed|submitted|cleared) your",
        r"your attendance has been (increased|updated|corrected)",
        r"fee has been paid",
        r"marks have been updated"
    ]

    HALLUCINATED_ATTENDANCE_PATTERNS = [
        r"condonation below 65%",
        r"condonation can be granted for 5\d%",
        r"attendance of 5\d% is acceptable"
    ]

    @classmethod
    def verify(
        cls,
        content: str,
        evidence_context: str,
        intelligence_id: str
    ) -> VerificationResult:
        violations: List[str] = []
        warnings: List[str] = []
        sanitized = content

        # 1. Check for unauthorized unilateral execution claims
        for pat in cls.UNAUTHORIZED_EXECUTION_PATTERNS:
            if re.search(pat, sanitized, re.IGNORECASE):
                violations.append("Unauthorized claim of unilateral transaction execution.")
                sanitized += (
                    "\n\n*Notice: As a public university intelligence assistant, this system cannot execute portal "
                    "transactions directly. Please review and complete your submission securely inside official UMS at https://ums.lpu.in.*"
                )
                break

        # 2. Check for statutory attendance condonation floor violations (< 65%)
        for pat in cls.HALLUCINATED_ATTENDANCE_PATTERNS:
            if re.search(pat, sanitized, re.IGNORECASE):
                violations.append("Violation of statutory 65% condonation floor.")
                sanitized += (
                    "\n\n⚠️ **Statutory Attendance Rule:** Under Lovely Professional University Academic Regulations, "
                    "no condonation can be approved for attendance falling below the **65% statutory floor**. "
                    "Attendance below 65% results in non-negotiable course debarment."
                )
                break

        # 3. Grounding check against official knowledge base evidence
        is_grounded, validated_text, ground_reason = validate_grounded_response(
            sanitized, evidence_context
        )
        if not is_grounded:
            warnings.append(f"Grounding variance detected: {ground_reason}")
            # Ensure safety boundary is maintained
            if len(evidence_context.strip()) > 50:
                sanitized = validated_text

        is_valid = len(violations) == 0

        return VerificationResult(
            is_valid=is_valid,
            verified_content=sanitized,
            violations_detected=violations,
            policy_warnings=warnings
        )
