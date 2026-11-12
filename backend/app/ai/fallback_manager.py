import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class FallbackManager:
    """
    Manages graceful degradation when LLM services encounter quota limits,
    timeouts, or temporary connectivity issues, ensuring verified information
    is never withheld while maintaining transparency.
    """

    @classmethod
    def get_quota_exhausted_response(cls, tool_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Returned when Gemini Free Tier quota is reached and circuit breaker is open.
        """
        content = (
            "⚠️ **Notice: High AI Service Demand (Gemini Free Tier Quota)**\n\n"
            "The Google Gemini API free-tier quota is temporarily exhausted or rate-limited. "
            "Our automated circuit breaker is backing off to protect API allocations.\n\n"
            "Below is the verified institutional data retrieved by our campus RAG search for your query:\n\n"
        )

        # Append tool facts directly so student is not left empty-handed
        if tool_results.get("evidence_context"):
            content += tool_results["evidence_context"]
        else:
            content += "Please consult the official LPU UMS portal at https://ums.lpu.in or visit the respective administrative desk in Block 32/34."

        return {
            "content": content,
            "prompt_tokens": 0,
            "completion_tokens": len(content) // 4,
            "total_tokens": len(content) // 4,
            "latency_ms": 50,
            "model": "verified-institutional-fallback",
            "finish_reason": "quota_fallback"
        }

    @classmethod
    def get_service_error_response(cls, error_msg: str, tool_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Returned when an unexpected provider error occurs.
        """
        logger.error(f"FallbackManager handling provider error: {error_msg}")
        content = (
            "⚠️ **AI Service Notice:**\n\n"
            "We encountered a temporary connection delay with the AI generation provider. "
            "However, verified institutional evidence was successfully retrieved from the university knowledge base:\n\n"
        )
        if tool_results.get("evidence_context"):
            content += tool_results["evidence_context"]
        else:
            content += "Please try your request again in a few moments, or check https://ums.lpu.in."

        return {
            "content": content,
            "prompt_tokens": 0,
            "completion_tokens": len(content) // 4,
            "total_tokens": len(content) // 4,
            "latency_ms": 50,
            "model": "verified-institutional-fallback",
            "finish_reason": "error_fallback"
        }
