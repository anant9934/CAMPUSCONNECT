import re
import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class IntentAnalysisResult(BaseModel):
    primary_intent: str  # everyday_query, policy_compliance, academic_benefit, ums_workflow, technical_reasoning, research_investigation, campus_spatial, emergency_medical
    detected_language: str  # "en", "hi", "hinglish"
    complexity: str  # "simple", "moderate", "complex"
    recommended_intelligence: str  # "nova", "themis", "athena", "oracle"
    needs_web_search: bool = False
    needs_rag_knowledge: bool = True
    needs_spatial_tools: bool = False
    needs_code_execution: bool = False
    is_emergency: bool = False
    rationale: str = ""


class IntentEngine:
    """
    LAYER 2 — INTENT ENGINE
    Deterministic, zero-latency intent understanding and language detection.
    Prevents unnecessary LLM calls for straightforward intent classification.
    """

    HINDI_HINGLISH_KEYWORDS = [
        "kya", "kaise", "kab", "kaha", "kahan", "kitna", "bhai", "yaar", "chahiye", "hoga", "karo", "mera", "meri", "mujhe", "batao", "attendance kam hai", "leave kaise milegi"
    ]

    EMERGENCY_KEYWORDS = [
        "emergency", "ambulance", "collapsed", "heart attack", "bleeding", "severe accident", "unconscious", "hospital urgently"
    ]

    POLICY_KEYWORDS = [
        "attendance", "condonation", "shortage", "debarred", "75%", "65%", "medical leave", "duty leave", "hospitalization", "exam debar"
    ]

    BENEFIT_KEYWORDS = [
        "edurev", "edu-revolution", "academic benefit", "ai project", "built a project", "startup revenue", "patent", "hackathon exemption"
    ]

    TECHNICAL_KEYWORDS = [
        "code", "function", "debug", "bug", "algorithm", "time complexity", "big o", "python", "typescript", "c++", "java", "sql query", "system design", "neural network", "database schema"
    ]

    RESEARCH_KEYWORDS = [
        "research paper", "ieee", "springer", "citations", "literature review", "web research", "sih 2026", "smart india hackathon", "verify source"
    ]

    SPATIAL_KEYWORDS = [
        "where is", "how to reach", "block 32", "block 34", "block 30", "uni-hospital", "uni-centre", "food court", "cabin", "dean office"
    ]

    @classmethod
    def analyze_intent(cls, query: str, context: Optional[Dict[str, Any]] = None) -> IntentAnalysisResult:
        q_clean = query.strip()
        q_lower = q_clean.lower()

        # 1. Language detection
        is_hinglish = any(re.search(rf"\b{re.escape(k)}\b", q_lower) for k in cls.HINDI_HINGLISH_KEYWORDS)
        has_devanagari = any('\u0900' <= char <= '\u097f' for char in q_clean)
        lang = "hi" if has_devanagari else ("hinglish" if is_hinglish else "en")

        # 2. Emergency check
        if any(k in q_lower for k in cls.EMERGENCY_KEYWORDS):
            return IntentAnalysisResult(
                primary_intent="emergency_medical",
                detected_language=lang,
                complexity="simple",
                recommended_intelligence="nova",
                needs_spatial_tools=True,
                is_emergency=True,
                rationale="Critical campus health or medical emergency detected."
            )

        # 3. Policy & Attendance check
        if any(k in q_lower for k in cls.POLICY_KEYWORDS):
            return IntentAnalysisResult(
                primary_intent="policy_compliance",
                detected_language=lang,
                complexity="complex" if any(num in q_lower for num in ["%", "percent", "6", "7"]) else "moderate",
                recommended_intelligence="themis",
                needs_rag_knowledge=True,
                rationale="Institutional academic regulation and attendance policy evaluation."
            )

        # 4. Academic Benefit / EDU-Revolution check
        if any(k in q_lower for k in cls.BENEFIT_KEYWORDS):
            return IntentAnalysisResult(
                primary_intent="academic_benefit",
                detected_language=lang,
                complexity="complex",
                recommended_intelligence="themis",
                needs_rag_knowledge=True,
                rationale="Student innovation and EDU-Revolution academic benefit mapping."
            )

        # 5. Technical & Coding check
        if any(k in q_lower for k in cls.TECHNICAL_KEYWORDS):
            return IntentAnalysisResult(
                primary_intent="technical_reasoning",
                detected_language=lang,
                complexity="complex" if any(k in q_lower for k in ["architecture", "optimize", "debug", "algorithm"]) else "moderate",
                recommended_intelligence="athena",
                needs_code_execution=True,
                rationale="Software engineering, mathematics, or technical code reasoning."
            )

        # 6. Research & Web search check
        if any(k in q_lower for k in cls.RESEARCH_KEYWORDS) or context and context.get("web_research"):
            return IntentAnalysisResult(
                primary_intent="research_investigation",
                detected_language=lang,
                complexity="complex",
                recommended_intelligence="oracle",
                needs_web_search=True,
                rationale="External academic research, web investigation, and source verification."
            )

        # 7. Spatial & Dining check
        if any(k in q_lower for k in cls.SPATIAL_KEYWORDS):
            return IntentAnalysisResult(
                primary_intent="campus_spatial",
                detected_language=lang,
                complexity="simple",
                recommended_intelligence="themis",
                needs_spatial_tools=True,
                rationale="Campus POI, building wayfinding, or food outlet inquiry."
            )

        # 8. Default: Everyday general query
        return IntentAnalysisResult(
            primary_intent="everyday_query",
            detected_language=lang,
            complexity="simple",
            recommended_intelligence="nova",
            needs_rag_knowledge=True,
            rationale="General campus routine or everyday student conversation."
        )
