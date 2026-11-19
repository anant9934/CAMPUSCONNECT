"""
Intent Analysis Engine for CampusConnect.
Classifies query intent, detected language, complexity, and resource requirements.
Ensures zero unnecessary RAG or multi-agent calls for general chitchat or explanations.
"""

import re
import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class IntentAnalysisResult(BaseModel):
    primary_intent: str  # greeting_chitchat, general_knowledge, career_coaching, technical_coding, policy_compliance, academic_benefit, ums_workflow, campus_spatial, research_investigation, emergency_medical
    detected_language: str  # "en", "hi", "hinglish"
    complexity: str  # "simple", "moderate", "complex"
    recommended_intelligence: str  # "nova", "themis", "athena", "oracle"
    is_general_conversation: bool = True
    needs_web_search: bool = False
    needs_rag_knowledge: bool = False
    needs_spatial_tools: bool = False
    needs_code_execution: bool = False
    is_emergency: bool = False
    rationale: str = ""


class IntentEngine:
    """
    LAYER 2 — INTENT ENGINE
    Deterministic, zero-latency intent understanding and language detection.
    Guarantees that general conversations, greetings, and conceptual questions
    never trigger unnecessary institutional vector searches or multi-agent bloat.
    """

    HINDI_HINGLISH_KEYWORDS = [
        "kya", "kaise", "kab", "kaha", "kahan", "kitna", "bhai", "yaar", "chahiye", "hoga", "karo", "mera", "meri", "mujhe", "batao", "attendance kam hai", "leave kaise milegi"
    ]

    EMERGENCY_KEYWORDS = [
        "emergency", "ambulance", "collapsed", "heart attack", "bleeding", "severe accident", "unconscious", "hospital urgently"
    ]

    GREETING_KEYWORDS = [
        "hi", "hii", "hiii", "hello", "hey", "good morning", "good afternoon", "good evening", "how are you", "who are you", "what can you do", "thank you", "thanks", "bye"
    ]

    POLICY_KEYWORDS = [
        "attendance", "condonation", "shortage", "debarred", "75%", "65%", "medical leave", "duty leave", "hospitalization", "exam debar", "attendance criteria", "grade improvement", "re-appear", "reappear", "backlog"
    ]

    BENEFIT_KEYWORDS = [
        "edurev", "edu-revolution", "academic benefit", "ai project", "built a project", "startup revenue", "patent", "hackathon exemption", "academic benefits for it", "grade upgradation", "credit transfer", "nptel", "swayam", "course equivalence", "credit substitution"
    ]

    TECHNICAL_KEYWORDS = [
        "code", "function", "debug", "bug", "algorithm", "time complexity", "big o", "python", "typescript", "c++", "java", "sql query", "system design", "neural network", "database schema", "recursion", "compiler"
    ]

    RESEARCH_KEYWORDS = [
        "research paper", "ieee", "springer", "citations", "literature review", "web research", "sih 2026", "smart india hackathon", "verify source", "university regulation"
    ]

    SPATIAL_KEYWORDS = [
        "where is", "how to reach", "take me to", "take me from", "directions to", "route to",
        "navigate to", "walk to", "walking distance", "block 32", "block 34", "block 30",
        "block 14", "block 53", "block 01", "block", "hostel", "boys hostel", "girls hostel",
        "campus map", "pedestrian", "uni-hospital", "unihospital", "uni-centre", "unimall",
        "food court", "cabin", "dean office", "chancellor office", "academic block"
    ]

    UMS_WORKFLOW_KEYWORDS = [
        "datesheet", "date sheet", "hall ticket", "admit card", "download", "ums", "fee payment", "fee slip", "hostel leave", "rms", "grade card"
    ]

    CAREER_KEYWORDS = [
        "career", "confused about my career", "job advice", "which path should i choose", "software engineering vs data science", "placement preparation"
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
                is_general_conversation=False,
                needs_spatial_tools=True,
                needs_rag_knowledge=True,
                is_emergency=True,
                rationale="Critical campus health or medical emergency detected."
            )

        # 3. Pure Greetings & Chitchat Check
        tokens = q_lower.split()
        if len(tokens) <= 5 and any(k in q_lower for k in cls.GREETING_KEYWORDS):
            return IntentAnalysisResult(
                primary_intent="greeting_chitchat",
                detected_language=lang,
                complexity="simple",
                recommended_intelligence="nova",
                is_general_conversation=True,
                needs_rag_knowledge=False,
                rationale="Natural conversational greeting or chitchat."
            )

        # 4. Career Guidance & Brainstorming
        if any(k in q_lower for k in cls.CAREER_KEYWORDS) and not any(k in q_lower for k in ["placement drive", "t&p"]):
            return IntentAnalysisResult(
                primary_intent="career_coaching",
                detected_language=lang,
                complexity="moderate",
                recommended_intelligence="nova",
                is_general_conversation=True,
                needs_rag_knowledge=False,
                rationale="General career exploration, advising, and brainstorming."
            )

        # 5. University Policy & Attendance check
        if any(k in q_lower for k in cls.POLICY_KEYWORDS):
            return IntentAnalysisResult(
                primary_intent="policy_compliance",
                detected_language=lang,
                complexity="complex" if any(num in q_lower for num in ["%", "percent", "6", "7"]) else "moderate",
                recommended_intelligence="themis",
                is_general_conversation=False,
                needs_rag_knowledge=True,
                rationale="Attendance regulations, debarment, or medical condonation."
            )

        # 6. Academic Benefits & Project Innovation check
        if any(k in q_lower for k in cls.BENEFIT_KEYWORDS) or ("benefit" in q_lower and any(p in q_lower for p in ["project", "it", "patent", "hackathon"])):
            return IntentAnalysisResult(
                primary_intent="academic_benefit",
                detected_language=lang,
                complexity="complex",
                recommended_intelligence="themis",
                is_general_conversation=False,
                needs_rag_knowledge=True,
                rationale="Student innovation and EDU-Revolution academic benefit evaluation."
            )

        # 7. UMS Workflow check
        if any(k in q_lower for k in cls.UMS_WORKFLOW_KEYWORDS):
            return IntentAnalysisResult(
                primary_intent="ums_workflow",
                detected_language=lang,
                complexity="simple",
                recommended_intelligence="themis",
                is_general_conversation=False,
                needs_rag_knowledge=True,
                rationale="UMS self-service navigation, datesheet download, or administrative workflow."
            )

        # 8. Spatial & Wayfinding check
        if any(k in q_lower for k in cls.SPATIAL_KEYWORDS):
            rec_intel = "themis" if any(w in q_lower for w in ["office", "dean", "chancellor", "admin"]) else "nova"
            return IntentAnalysisResult(
                primary_intent="campus_spatial",
                detected_language=lang,
                complexity="simple",
                recommended_intelligence=rec_intel,
                is_general_conversation=False,
                needs_spatial_tools=True,
                needs_rag_knowledge=True,
                rationale="Campus block discovery, wayfinding, or pedestrian navigation."
            )

        # 9. Research & Source Verification check
        if any(k in q_lower for k in cls.RESEARCH_KEYWORDS) or (context and context.get("web_research")):
            return IntentAnalysisResult(
                primary_intent="research_investigation",
                detected_language=lang,
                complexity="complex",
                recommended_intelligence="oracle",
                is_general_conversation=False,
                needs_web_search=True,
                needs_rag_knowledge=True,
                rationale="External academic research, web investigation, and source verification."
            )

        # 10. Technical & Coding check
        if any(k in q_lower for k in cls.TECHNICAL_KEYWORDS) or any(k in q_lower for k in ["recursion", "machine learning", "compiler", "algorithm"]):
            return IntentAnalysisResult(
                primary_intent="technical_coding",
                detected_language=lang,
                complexity="complex" if any(k in q_lower for k in ["architecture", "optimize", "debug", "algorithm"]) else "moderate",
                recommended_intelligence="athena",
                is_general_conversation=True,
                needs_code_execution=True,
                needs_rag_knowledge=False,
                rationale="Software engineering, mathematics, or conceptual technical explanation."
            )

        # 11. Default: Everyday General Conversation
        return IntentAnalysisResult(
            primary_intent="general_knowledge",
            detected_language=lang,
            complexity="simple",
            recommended_intelligence="nova",
            is_general_conversation=True,
            needs_rag_knowledge=False,
            rationale="General everyday conversational query."
        )
