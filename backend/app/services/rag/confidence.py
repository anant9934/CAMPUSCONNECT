from enum import Enum
from typing import Dict, Any, List, Optional
from app.core.config import settings


class ConfidenceLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"


class ConfidenceEvaluation:
    def __init__(
        self,
        score: float,
        level: ConfidenceLevel,
        margin: float,
        should_generate_ai: bool,
        explanation: str
    ):
        self.score = score
        self.level = level
        self.margin = margin
        self.should_generate_ai = should_generate_ai
        self.explanation = explanation

    def to_dict(self) -> Dict[str, Any]:
        return {
            "score": round(self.score, 4),
            "level": self.level.value,
            "margin": round(self.margin, 4),
            "should_generate_ai": self.should_generate_ai,
            "explanation": self.explanation
        }


def evaluate_confidence(ranked_candidates: List[Dict[str, Any]]) -> ConfidenceEvaluation:
    """
    Calibrates confidence score from ranked retrieval candidates.
    Evaluates absolute score and the margin of victory between top candidates.
    """
    if not ranked_candidates:
        return ConfidenceEvaluation(
            score=0.0,
            level=ConfidenceLevel.NONE,
            margin=0.0,
            should_generate_ai=False,
            explanation="No matching approved records found in the LPU knowledge base."
        )

    top_candidate = ranked_candidates[0]
    top_score = float(top_candidate.get("hybrid_score", 0.0))

    runner_up_score = 0.0
    if len(ranked_candidates) > 1:
        runner_up_score = float(ranked_candidates[1].get("hybrid_score", 0.0))

    margin = max(0.0, top_score - runner_up_score)

    if top_score >= settings.CONFIDENCE_HIGH_THRESHOLD:
        level = ConfidenceLevel.HIGH
        should_generate = True
        explanation = "Strong institutional evidence found with high semantic and lexical agreement."
    elif top_score >= settings.CONFIDENCE_MEDIUM_THRESHOLD:
        level = ConfidenceLevel.MEDIUM
        should_generate = True
        explanation = "Relevant institutional knowledge retrieved with acceptable confidence."
    elif top_score >= settings.CONFIDENCE_LOW_THRESHOLD:
        level = ConfidenceLevel.LOW
        # Low confidence does not meet grounding standards
        should_generate = False
        explanation = "Marginal match found, but confidence is insufficient to guarantee accurate institutional facts."
    else:
        level = ConfidenceLevel.NONE
        should_generate = False
        explanation = "Retrieved score is below threshold; abstaining from speculative answer generation."

    return ConfidenceEvaluation(
        score=top_score,
        level=level,
        margin=margin,
        should_generate_ai=should_generate,
        explanation=explanation
    )

