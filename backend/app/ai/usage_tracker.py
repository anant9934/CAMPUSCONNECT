import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.portal import LLMUsageLog

logger = logging.getLogger(__name__)


class UsageTracker:
    """
    Tracks and logs LLM token consumption, latencies, and status
    for auditability and quota management.
    """

    @classmethod
    async def log_usage(
        cls,
        db: AsyncSession,
        model_name: str,
        prompt_tokens: int,
        completion_tokens: int,
        latency_ms: int,
        status: str = "success",
        session_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> None:
        try:
            log_entry = LLMUsageLog(
                session_id=session_id,
                conversation_id=conversation_id,
                model_name=model_name,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
                latency_ms=latency_ms,
                status=status,
                error_message=error_message
            )
            db.add(log_entry)
            await db.commit()
        except Exception as e:
            logger.error(f"Failed to log LLM usage: {e}")
