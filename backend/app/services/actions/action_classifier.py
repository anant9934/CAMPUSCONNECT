import re
from typing import Tuple, Dict, Any, Optional

# SRS v3.0 Core Product Modes
MODE_ANSWER = "ANSWER"
MODE_NAVIGATE = "NAVIGATE"
MODE_PREPARE = "PREPARE"
MODE_BOOK_HANDOFF = "BOOK_HANDOFF"
MODE_PERSONAL_RECORD = "PERSONAL_RECORD"
MODE_ESCALATE = "ESCALATE"
MODE_EXECUTE = "EXECUTE"
MODE_ABSTAIN = "ABSTAIN"


class ActionMode:
    ANSWER = MODE_ANSWER
    NAVIGATE = MODE_NAVIGATE
    PREPARE = MODE_PREPARE
    BOOK_HANDOFF = MODE_BOOK_HANDOFF
    PERSONAL_RECORD = MODE_PERSONAL_RECORD
    ESCALATE = MODE_ESCALATE
    EXECUTE = MODE_EXECUTE
    ABSTAIN = MODE_ABSTAIN


# Lexical patterns for action classification
EXECUTE_PATTERNS = [
    r"\bpay my\b",
    r"\bpay the fee\b",
    r"\bpay.*fee\b",
    r"\bpay.*for me\b",
    r"\bbook.*for me\b",
    r"\bbook.*right now\b",
    r"\bbook.*immediately\b",
    r"\bdeduct fee\b",
    r"\bbook my slot\b",
    r"\bcancel my booking\b",
    r"\bsubmit my grievance\b",
    r"\bsubmit this complaint\b",
    r"\bupload my assignment\b",
    r"\bregister me\b",
    r"\btransfer my money\b",
    r"\bmark my attendance\b",
    r"\bchange my marks\b",
]

PERSONAL_RECORD_PATTERNS = [
    r"\bmy (?:current )?attendance\b",
    r"\bmy.*attendance\b",
    r"\battendance percentage\b",
    r"\bview attendance\b",
    r"\bcheck my attendance\b",
    r"\bmy marks\b",
    r"\bmy.*marks\b",
    r"\bmy result\b",
    r"\bmy.*result\b",
    r"\bmy cgpa\b",
    r"\bmy.*cgpa\b",
    r"\bmy sgpa\b",
    r"\bmy.*sgpa\b",
    r"\bmy fee statement\b",
    r"\bmy fee receipt\b",
    r"\bmy.*fee\b",
    r"\bview fee receipt\b",
    r"\bview fee status\b",
    r"\bmy dues\b",
    r"\bmy balance\b",
    r"\bfee balance\b",
    r"\bmy timetable\b",
    r"\bmy time table\b",
    r"\bmy.*timetable\b",
    r"\bmy admit card\b",
    r"\bmy leave status\b",
    r"\bmy grade\b",
    r"\bmy grades\b",
    r"\bmy.*grades?\b",
    r"\bcgpa\b",
    r"\bsgpa\b",
    r"\bregistration number\b",
    r"\bexam marks\b",
    r"\bmarks of\b",
    r"\bcgpa of\b",
    r"\bstudent.*marks\b",
    r"\bstudent.*cgpa\b",
    r"\bstudent.*record\b",
]

BOOKING_PATTERNS = [
    r"\bbook.*hostel\b",
    r"\bhostel.*booking\b",
    r"\bhostel.*allotment\b",
    r"\bbook.*room\b",
    r"\bdoctor.*appointment\b",
    r"\bbook.*doctor\b",
    r"\bmedical.*appointment\b",
    r"\bsee.*doctor\b",
    r"\bcounseling\b",
    r"\bcounselling\b",
    r"\bpsychologist\b",
    r"\byourdost\b",
    r"\bdiscussion.*room\b",
    r"\blibrary.*room\b",
    r"\blanguage.*lab\b",
    r"\bappointment.*with\b",
    r"\bbook.*slot\b",
]

ESCALATE_PATTERNS = [
    r"\bfile complaint\b",
    r"\bgrievance\b",
    r"\brms\b",
    r"\blog request\b",
    r"\bcomplain about\b",
    r"\bwi-fi complaint\b",
    r"\bmess complaint\b",
    r"\bwarden complaint\b",
    r"\bharassment\b",
    r"\bragging\b",
    r"\bescalate\b",
    r"\btrack grievance\b",
    r"\btrack request\b",
    r"\bemergency\b",
    r"\bambulance\b",
    r"\bmedical emergency\b",
    r"\bchest pain\b",
    r"\bcollapsed\b",
]

NAVIGATE_PATTERNS = [
    r"\bnavigate\b",
    r"\bnavigation\b",
    r"\bwhere is\b",
    r"\bwhere can i find\b",
    r"\bwhich menu\b",
    r"\bhow to find\b",
    r"\bnavigation path\b",
    r"\bbreadcrumb\b",
    r"\bums menu\b",
    r"\bwhere to see\b",
    r"\bwhere do i check\b",
    r"\bwhere to apply\b",
    r"\blost property\b",
    r"\blost and found\b",
    r"\bwhere is block\b",
    r"\bwhich block\b",
    r"\bcampus map\b",
    r"\bhow to reach\b",
    r"\bfind.*menu\b",
]

PREPARE_PATTERNS = [
    r"\bhow to apply\b",
    r"\bhow do i apply\b",
    r"\bdocuments? required\b",
    r"\bwhat documents?\b",
    r"\bdocuments? (?:do i )?need\b",
    r"\bdocuments? for\b",
    r"\bprerequisites\b",
    r"\beligibility for\b",
    r"\bprocedure for\b",
    r"\bsteps to\b",
    r"\bhow to register\b",
    r"\bre-evaluation\b",
    r"\breappear\b",
    r"\bre-appear\b",
    r"\bbacklog\b",
    r"\brfid application\b",
    r"\bparent pass\b",
    r"\bduplicate id\b",
    r"\bfee refund\b",
    r"\bsemester exchange\b",
]


class ActionClassifier:
    """
    Classifies student request into one of the 8 core SRS v3.0 operational modes.
    Enforces strict security boundaries to prevent unauthorized transactional claims.
    """

    @classmethod
    def classify_intent(cls, query: str) -> Tuple[str, float, str]:
        """
        Returns:
            (action_mode, confidence_score, rationale)
        """
        q = query.lower().strip()

        # 1. Check for transactional EXECUTE requests (Highest priority boundary enforcement)
        for pat in EXECUTE_PATTERNS:
            if re.search(pat, q):
                return (
                    MODE_EXECUTE,
                    0.95,
                    "User is requesting automated completion of a consequential transaction. Policy refuses direct execution in public chatbot."
                )

        # 2. Check for PERSONAL_RECORD inquiries (unless query is an issue/procedure/routing request)
        is_issue_or_procedure = any(
            w in q for w in [
                "incorrect", "wrong", "discrepancy", "shortage",
                "explain the procedure", "procedure to", "whom should i meet",
                "who to meet", "first contact", "how to resolve", "how to correct",
                "both ums pathways", "hostel and fee problem", "both pathways"
            ]
        )
        if not is_issue_or_procedure:
            for pat in PERSONAL_RECORD_PATTERNS:
                if re.search(pat, q):
                    return (
                        MODE_PERSONAL_RECORD,
                        0.92,
                        "User is requesting private authenticated student data (attendance, result, marks, fee receipt). Directed to UMS self-service."
                    )

        # 3. Check for ESCALATE / RMS Grievance
        for pat in ESCALATE_PATTERNS:
            if re.search(pat, q):
                return (
                    MODE_ESCALATE,
                    0.90,
                    "User needs formal dispute resolution or official grievance submission via Relationship Management System (RMS)."
                )

        # 4. Check for BOOKING & APPOINTMENT HANDOFF
        for pat in BOOKING_PATTERNS:
            if re.search(pat, q):
                return (
                    MODE_BOOK_HANDOFF,
                    0.90,
                    "User wants to reserve a campus amenity, clinic slot, counselling session, or discussion room."
                )

        # 5. Check for PREPARE (SOP & procedural guidance)
        for pat in PREPARE_PATTERNS:
            if re.search(pat, q):
                return (
                    MODE_PREPARE,
                    0.85,
                    "User is asking for procedural steps, required documents, or application guidelines."
                )

        # 6. Check for NAVIGATE (wayfinding or UMS menu search)
        for pat in NAVIGATE_PATTERNS:
            if re.search(pat, q):
                return (
                    MODE_NAVIGATE,
                    0.85,
                    "User is inquiring about the location of a service in UMS or a physical block on campus."
                )

        # 7. Check for obvious non-LPU / off-topic queries for ABSTAIN
        non_lpu_signals = [
            "bitcoin", "cryptocurrency", "stock market", "weather in tokyo",
            "cook pasta", "recipe", "write python code", "movie review", "quantum warp drive",
            "cricket", "world cup", "football match", "quicksort", "binary tree"
        ]
        if any(sig in q for sig in non_lpu_signals):
            return (
                MODE_ABSTAIN,
                0.95,
                "Query is outside the institutional boundary of Lovely Professional University."
            )

        # Default mode is ANSWER (standard RAG retrieval over institutional evidence)
        return (
            MODE_ANSWER,
            0.75,
            "User is requesting factual campus information answerable from approved LPU knowledge records."
        )
