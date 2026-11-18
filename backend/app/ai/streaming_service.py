"""
Streaming Service for CampusConnect.
Manages Server-Sent Events (SSE) streaming for real conversational turns.
Supports cancellation via ConversationEngine, token-level streaming,
thinking step progress, and action card delivery.
"""

import json
import asyncio
import logging
from typing import AsyncGenerator, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.intelligence.conversation_engine import ConversationEngine
from app.schemas.chat import ThinkingStep, Citation

logger = logging.getLogger(__name__)


class StreamingService:
    """
    Manages Server-Sent Events (SSE) streaming for real chat turns.
    Yields JSON event blocks conforming to SSE protocol:
    event: <event_name>\ndata: <json_payload>\n\n
    """

    @classmethod
    async def stream_chat_turn(
        cls,
        message: str,
        conversation_id: str,
        session_id: str,
        db: AsyncSession,
        user_lat: Optional[float] = None,
        user_lon: Optional[float] = None,
        landmark: Optional[str] = None,
        category_slug: Optional[str] = None,
        provider: Optional[str] = None,
        reasoning_mode: Optional[str] = "balanced",
        thinking_level: Optional[str] = "Balanced",
        selected_intelligence: str = "auto",
        conversation_history: Optional[list] = None,
        web_research: bool = False
    ) -> AsyncGenerator[str, None]:
        q_clean = message.strip()
        ConversationEngine.clear_cancellation(conversation_id)

        # Map thinking level string cleanly
        th_level = thinking_level.title() if thinking_level else "Balanced"
        if th_level not in ["Low", "Balanced", "High"]:
            th_level = "Balanced"

        # Emit initial thinking step
        yield f"event: thinking\ndata: {json.dumps({'step': 1, 'title': 'Understanding conversation', 'status': 'in_progress'})}\n\n"
        await asyncio.sleep(0.01)

        # Check early cancellation
        if ConversationEngine.is_cancelled(conversation_id):
            yield f"event: done\ndata: {json.dumps({'cancelled': True})}\n\n"
            return

        try:
            from app.intelligence.intelligence_system import IntelligenceSystem
            intel_res = await IntelligenceSystem.process_turn(
                query=q_clean,
                selected_intelligence=selected_intelligence,
                thinking_level=th_level,
                user_identifier=session_id,
                conversation_history=conversation_history,
                db=db,
                user_lat=user_lat,
                user_lon=user_lon,
                landmark=landmark,
                category_slug=category_slug,
                web_research=web_research
            )
        except Exception as e:
            logger.error(f"Error executing intelligence turn: {e}", exc_info=True)
            yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"
            return

        # Stream the thinking steps
        for step in intel_res.thinking_steps:
            if ConversationEngine.is_cancelled(conversation_id):
                yield f"event: done\ndata: {json.dumps({'cancelled': True})}\n\n"
                return
            yield f"event: thinking\ndata: {json.dumps(step.model_dump())}\n\n"
            await asyncio.sleep(0.01)

        # Stream content tokens (chunked for realistic natural typing cadence)
        full_text = intel_res.content
        words = full_text.split(" ")
        chunk_size = 4  # 4 words per chunk

        for i in range(0, len(words), chunk_size):
            if ConversationEngine.is_cancelled(conversation_id):
                logger.info(f"Generation cancelled mid-stream for {conversation_id}")
                yield f"event: done\ndata: {json.dumps({'cancelled': True, 'interrupted': True})}\n\n"
                return

            chunk = " ".join(words[i:i + chunk_size])
            if i + chunk_size < len(words):
                chunk += " "
            yield f"event: token\ndata: {json.dumps({'token': chunk})}\n\n"
            await asyncio.sleep(0.02)

        # Emit cards if present
        if intel_res.cards:
            for card_type, card_data in intel_res.cards.items():
                if card_data:
                    yield f"event: card\ndata: {json.dumps({'type': card_type, 'data': card_data if isinstance(card_data, dict) else getattr(card_data, 'model_dump', lambda: str(card_data))()})}\n\n"

        # Emit citations if present
        if intel_res.citations:
            citations_data = [c.model_dump() if hasattr(c, "model_dump") else c for c in intel_res.citations]
            yield f"event: citations\ndata: {json.dumps({'citations': citations_data})}\n\n"

        # Final done event
        done_payload = {
            "content": full_text,
            "intelligence_id": intel_res.intelligence_id,
            "intelligence_name": intel_res.intelligence_name,
            "follow_ups": intel_res.follow_ups,
            "latency_ms": intel_res.latency_ms,
            "confidence_score": intel_res.confidence_score,
            "is_ai_generated": intel_res.is_ai_generated
        }
        yield f"event: done\ndata: {json.dumps(done_payload)}\n\n"
