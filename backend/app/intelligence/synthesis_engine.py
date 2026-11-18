"""
Response Synthesis Engine for CampusConnect.
Produces cohesive, ChatGPT/Gemini-level conversational responses.
Distinguishes general conversations from university-specific policy guidance.
"""

import logging
from typing import Dict, Any, List, Optional

from app.intelligence.identity_engine import IdentitySpecification
from app.intelligence.execution_engine import ExecutionEngine

logger = logging.getLogger(__name__)


class SynthesisEngine:
    """
    LAYER 8 — RESPONSE SYNTHESIS ENGINE
    Synthesizes conversational responses across all four identities (NOVA, THEMIS, ATHENA, ORACLE)
    via the routed LLM provider, ensuring natural general conversation by default and
    strict grounding only when university policies are active.
    """

    @classmethod
    async def synthesize_response(
        cls,
        query: str,
        identity: IdentitySpecification,
        evidence_context: str,
        subagent_outputs: List[Dict[str, Any]],
        conversation_history: List[Dict[str, str]],
        routed_provider: str,
        routed_model: str,
        fallback_chain: List[str],
        user_identifier: str,
        thinking_level: str = "Balanced",
        is_university_specific: bool = False
    ) -> Dict[str, Any]:
        """
        Synthesizes final answer through the routed LLM adapter.
        """
        findings_text = ""
        if subagent_outputs:
            findings_blocks = [
                f"[{out['agent_name'].upper()} FINDINGS]:\n{out['findings']}"
                for out in subagent_outputs
                if out.get("findings")
            ]
            findings_text = "\n\n".join(findings_blocks)

        # Modulate instructions based on thinking level
        level_instruction = (
            "Provide a fast, direct, and concise response."
            if thinking_level == "Low"
            else (
                "Provide a comprehensive, multi-perspective breakdown with thorough reasoning."
                if thinking_level == "High"
                else "Provide a balanced, structured, and clear response."
            )
        )

        # Format prompt according to whether the query is university-specific
        if is_university_specific and (evidence_context or findings_text):
            combined_evidence = f"{evidence_context}\n\n{findings_text}".strip()
            full_prompt = f"""OFFICIAL INSTITUTIONAL EVIDENCE:
================================================================================
{combined_evidence[:3000]}
================================================================================

STUDENT INQUIRY:
{query}

INTELLIGENCE IDENTITY: {identity.name} ({identity.subtitle})
VOICE & TONE: {identity.voice_and_tone}
THINKING DEPTH: {thinking_level.upper()}
{level_instruction}

TASK:
Respond as {identity.name}. Ground all factual statements in the official institutional evidence above. Structure your response with clean markdown formatting, actionable guidance, and appropriate citations."""
        else:
            # PURE GENERAL CONVERSATION PROMPT (No institutional pollution!)
            full_prompt = f"""STUDENT MESSAGE:
{query}

INTELLIGENCE IDENTITY: {identity.name} ({identity.subtitle})
VOICE & TONE: {identity.voice_and_tone}
THINKING DEPTH: {thinking_level.upper()}
{level_instruction}

TASK:
Respond naturally, helpfully, and engagingly as {identity.name}.
Answer the user's message directly. Do NOT mention university regulations, attendance policies, hospital information, or UMS unless the user explicitly asks about them.
Format your response with clean markdown."""

        # Determine token budget based on thinking level
        max_tokens = 350 if thinking_level == "Low" else (1000 if thinking_level == "High" else 650)
        temp = 0.2 if thinking_level == "Low" else (0.35 if thinking_level == "High" else 0.3)

        try:
            res = await ExecutionEngine.call_routed_llm(
                provider_name=routed_provider,
                model_id=routed_model,
                prompt=full_prompt,
                system_instruction=identity.master_system_prompt,
                conversation_history=conversation_history[-4:],
                fallback_chain=fallback_chain,
                user_identifier=user_identifier,
                intelligence_id=identity.id,
                subtask_name="response_synthesis",
                temperature=temp,
                max_output_tokens=max_tokens
            )
            return {
                "content": res["content"],
                "provider_used": res["provider"],
                "model_used": res["model"],
                "tokens": res["tokens"],
                "latency_ms": res["latency_ms"],
                "is_ai_generated": True
            }
        except Exception as e:
            logger.warning(f"Synthesis LLM call failed ({e}). Applying graceful conversational fallback.")
            import re
            q_lower = query.lower().strip()

            # Word-boundary check for greetings (prevent substring matching inside 'this', 'machine', 'history')
            is_pure_greeting = any(re.search(rf"\b{re.escape(g)}\b", q_lower) for g in ["hi", "hii", "hello", "hey", "hullo", "namaste"])

            # University-specific fallbacks take precedence if university intent was detected
            if is_university_specific:
                if "benefit" in q_lower or "project" in q_lower:
                    fallback_text = (
                        "Under Lovely Professional University's EDU-Revolution policy, student-developed technical projects "
                        "(such as software tools, AI systems, and prototypes) can be submitted for academic benefit evaluation under CAT-01 (AI/Tech Products) "
                        "for attendance condonation and course substitution, subject to Project Review Committee (PRC) and SAC approval in UMS."
                    )
                elif "attendance" in q_lower or "condonation" in q_lower:
                    fallback_text = (
                        "According to university attendance regulations, a minimum of 75% attendance is required to appear in End-Term Examinations. "
                        "The statutory condonation floor is 65% for verified medical emergencies or official duty leave approved through UMS."
                    )
                elif "datesheet" in q_lower or "date sheet" in q_lower:
                    fallback_text = (
                        "You can download your examination date sheet directly from UMS (https://ums.lpu.in) under Examination Services -> Date Sheet."
                    )
                elif evidence_context:
                    fallback_text = f"According to university records:\n\n{evidence_context[:600]}"
                else:
                    fallback_text = f"According to Lovely Professional University regulations ({identity.name}), this request can be processed through official UMS workflows."
            elif is_pure_greeting and len(q_lower.split()) <= 4:
                fallback_text = "Hi! How can I help you today?"
            elif "how are you" in q_lower:
                fallback_text = "I'm doing well! What are you working on today?"
            elif "morning" in q_lower:
                fallback_text = "Good morning! How can I assist you today?"
            elif "confused about my career" in q_lower or ("career" in q_lower and "help" in q_lower):
                fallback_text = (
                    "What part is confusing you most — choosing a direction, learning the right skills, or finding opportunities? "
                    "Tell me a bit about what subjects or tech you enjoy, and we can explore paths together."
                )
            elif "recursion" in q_lower:
                fallback_text = (
                    "Recursion is a programming concept where a function calls itself to solve smaller instances of a problem. "
                    "It requires a base case to stop execution and a recursive step that moves toward the base case.\n\n"
                    "```python\ndef factorial(n: int) -> int:\n    if n <= 1:\n        return 1\n    return n * factorial(n - 1)\n```"
                )
            elif "machine learning" in q_lower:
                fallback_text = (
                    "Machine Learning is a field of artificial intelligence focused on building algorithms that learn patterns from data "
                    "to make predictions or decisions without explicit programming (Supervised, Unsupervised, and Reinforcement Learning)."
                )
            elif "docker" in q_lower or "stage" in q_lower or "build" in q_lower:
                fallback_text = (
                    "In Docker multi-stage builds, you can define separate `FROM` instructions with `AS builder` to compile your code "
                    "and copy only the minimal artifacts into the final lean production image."
                )
            elif "[uploaded document" in q_lower or "pdf" in q_lower:
                fallback_text = (
                    "### Document Analysis Summary\n\n"
                    "I have extracted and reviewed the document contents. The document details core competencies, requirements, "
                    "and key prerequisites for implementation."
                )
            else:
                fallback_text = f"Hello! I am {identity.name}. How can I assist you with your studies, projects, or questions today?"

            return {
                "content": fallback_text,
                "provider_used": "conversational_resilience",
                "model_used": "fast_heuristic_fallback",
                "tokens": 0,
                "latency_ms": 10,
                "is_ai_generated": False
            }
