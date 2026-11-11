import logging
from typing import List, Dict, Any, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.session import Message

logger = logging.getLogger(__name__)


class ContextManager:
    """
    Manages isolated conversation context and history window for real LLM reasoning.
    Prevents token blowout while preserving conversational continuity.
    """

    MAX_HISTORY_TURNS = 6  # Last 3 user + 3 assistant turns

    @classmethod
    async def get_conversation_history(
        cls,
        conversation_id: str,
        db: AsyncSession
    ) -> List[Dict[str, str]]:
        """
        Retrieves recent turns for a specific conversation in chronological order.
        """
        stmt = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
        )
        res = await db.execute(stmt)
        messages = res.scalars().all()

        turns = []
        for m in messages:
            # Skip system messages or empty content
            if m.role in ("user", "assistant") and m.content:
                turns.append({
                    "role": m.role,
                    "content": m.content.strip()
                })

        # Return only the most recent turns within context budget
        return turns[-cls.MAX_HISTORY_TURNS:]

    @classmethod
    def format_history_for_prompt(cls, history: List[Dict[str, str]]) -> str:
        """
        Formats history into a clean multi-turn dialogue string.
        """
        if not history:
            return "No prior context. (First turn in this conversation)"

        formatted = []
        for h in history:
            speaker = "Student" if h["role"] == "user" else "CampusConnect Assistant"
            formatted.append(f"{speaker}: {h['content']}")
        return "\n".join(formatted)
