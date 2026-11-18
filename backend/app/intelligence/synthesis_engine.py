import logging
from typing import Dict, Any, List, Optional

from app.intelligence.identity_engine import IdentitySpecification
from app.intelligence.execution_engine import ExecutionEngine

logger = logging.getLogger(__name__)


class SynthesisEngine:
    """
    LAYER 8 — RESPONSE SYNTHESIS ENGINE
    Produces one unified, coherent student response in the selected intelligence's voice,
    integrating specialist subagent findings, action cards, and citations.
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
        thinking_level: str = "Balanced"
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

        combined_context = f"{evidence_context}\n\n{findings_text}".strip()
        if not combined_context:
            combined_context = "Approved Lovely Professional University institutional regulations and campus guidelines."

        # Modulate instructions based on thinking level and intelligence persona
        level_instruction = (
            "Provide a fast, concise, direct answer in 2-4 sentences."
            if thinking_level == "Low"
            else (
                "Provide an evidence-intensive investigation with granular breakdown and official citations."
                if thinking_level == "High"
                else "Provide a balanced, structured, and clear response grounded strictly in official records."
            )
        )

        full_prompt = f"""OFFICIAL INSTITUTIONAL EVIDENCE:
================================================================================
{combined_context[:3000]}
================================================================================

STUDENT QUERY:
{query}

INTELLIGENCE IDENTITY: {identity.name} ({identity.subtitle})
VOICE & TONE DIRECTIVE: {identity.voice_and_tone}
THINKING DEPTH: {thinking_level.upper()}
{level_instruction}

TASK:
Respond as {identity.name}. Ground all factual statements in the approved evidence above. Structure your output cleanly with markdown formatting."""

        # Determine token budget based on thinking level
        max_tokens = 350 if thinking_level == "Low" else (1000 if thinking_level == "High" else 600)
        temp = 0.1 if thinking_level == "Low" else (0.25 if thinking_level == "High" else 0.2)

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
            logger.warning(f"Synthesis LLM call failed ({e}). Assembling directly from verified knowledge records.")
            fallback_content = combined_context[:800]
            return {
                "content": f"Verified institutional records ({identity.name}):\n\n{fallback_content}",
                "provider_used": "deterministic_knowledge",
                "model_used": "offline_verified_kb",
                "tokens": 0,
                "latency_ms": 10,
                "is_ai_generated": False
            }
