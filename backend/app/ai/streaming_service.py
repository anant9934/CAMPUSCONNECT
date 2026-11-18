import json
import asyncio
import logging
from typing import AsyncGenerator, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session import Message
from app.ai.conversation_orchestrator import ConversationOrchestrator
from app.ai.gemini_provider import GeminiProvider, circuit_breaker
from app.ai.llm_registry import LLMRegistry
from app.ai.response_generator import ResponseGenerator, CAMPUSCONNECT_V8_SYSTEM_PROMPT
from app.ai.tool_executor import ToolExecutor
from app.ai.context_manager import ContextManager
from app.ai.response_validator import ResponseValidator
from app.ai.proactive_intelligence import ProactiveStudentIntelligence

logger = logging.getLogger(__name__)


class StreamingService:
    """
    Manages Server-Sent Events (SSE) streaming for real Gemini-powered chat turns.
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
        thinking_level: Optional[str] = "medium",
    ) -> AsyncGenerator[str, None]:
        q_clean = message.strip()

        # Event 1: Thinking progression starts
        yield f"event: thinking\ndata: {json.dumps({'step': 1, 'title': 'Understanding intent', 'status': 'in_progress'})}\n\n"
        await asyncio.sleep(0.05)

        # Execute tools
        yield f"event: thinking\ndata: {json.dumps({'step': 2, 'title': 'Executing campus tools & RAG', 'status': 'in_progress'})}\n\n"

        tool_results = await ToolExecutor.execute_all_relevant_tools(
            query=q_clean,
            db=db,
            user_lat=user_lat,
            user_lon=user_lon,
            landmark=landmark,
            category_slug=category_slug
        )

        # Emit cards as soon as tools finish
        cards_payload = {
            "food_card": tool_results["food_card"].model_dump() if tool_results["food_card"] else None,
            "person_card": tool_results["person_card"].model_dump() if tool_results["person_card"] else None,
            "who_to_meet_card": tool_results["who_to_meet_card"].model_dump() if tool_results["who_to_meet_card"] else None,
            "academic_benefit_card": tool_results["academic_benefit_card"].model_dump() if tool_results["academic_benefit_card"] else None,
            "place_card": tool_results["place_card"].model_dump() if tool_results["place_card"] else None,
            "nav_card": tool_results["nav_card"].model_dump() if tool_results["nav_card"] else None,
        }
        yield f"event: cards\ndata: {json.dumps(cards_payload)}\n\n"

        # Emit citations
        if tool_results.get("citations"):
            citations_data = [c.model_dump() if hasattr(c, "model_dump") else dict(c) for c in tool_results["citations"]]
            yield f"event: citations\ndata: {json.dumps(citations_data)}\n\n"

        yield f"event: thinking\ndata: {json.dumps({'step': 3, 'title': 'Proactive Opportunity Evaluation & Token Streaming', 'status': 'in_progress'})}\n\n"

        history_turns = await ContextManager.get_conversation_history(conversation_id, db)
        history_text = "\n".join([f"{h['role'].title()}: {h['content']}" for h in history_turns]) if history_turns else "None (New Thread)"

        # Evaluate proactive opportunity intelligence
        proactive_eval = await ProactiveStudentIntelligence.evaluate_turn(
            user_message=q_clean,
            conversation_history=history_turns
        )

        full_prompt = f"""APPROVED INSTITUTIONAL EVIDENCE FROM LOVELY PROFESSIONAL UNIVERSITY:
================================================================================
{tool_results.get('evidence_context', 'No specific institutional records retrieved.')}
================================================================================

PROACTIVE OPPORTUNITY & POLICY ASSESSMENT:
--------------------------------------------------------------------------------
{proactive_eval.proactive_guidance_text}
--------------------------------------------------------------------------------

CONVERSATION CONTEXT:
{history_text}

STUDENT QUERY:
{q_clean}

TASK:
Provide a clear, accurate, and professional response to the student's query based strictly on the approved institutional evidence above."""

        target_provider_name = provider or "gemini"
        try:
            active_provider = LLMRegistry.get_provider(target_provider_name)
        except Exception:
            active_provider = GeminiProvider()

        full_generated_text = ""

        # Stream tokens
        try:
            if not active_provider.is_available() or (target_provider_name == "gemini" and circuit_breaker.is_open()):
                # Fallback to secondary or direct knowledge base
                fallback_text = (
                    f"⚠️ Notice: Provider '{target_provider_name}' currently unavailable. Displaying verified institutional records directly:\n\n"
                    + (tool_results.get("evidence_context") or "Please check https://ums.lpu.in for official details.")
                )
                for word in fallback_text.split(" "):
                    yield f"event: token\ndata: {json.dumps({'token': word + ' '})}\n\n"
                    await asyncio.sleep(0.02)
                full_generated_text = fallback_text
            else:
                async for chunk in active_provider.generate_stream(
                    prompt=full_prompt,
                    system_instruction=CAMPUSCONNECT_V8_SYSTEM_PROMPT,
                    conversation_history=history_turns
                ):
                    full_generated_text += chunk
                    yield f"event: token\ndata: {json.dumps({'token': chunk})}\n\n"

        except Exception as e:
            logger.error(f"Error during token streaming: {e}")
            err_msg = "\n\n⚠️ Encountered a temporary connection delay. Please consult https://ums.lpu.in."
            yield f"event: token\ndata: {json.dumps({'token': err_msg})}\n\n"
            full_generated_text += err_msg

        # Save assistant message to database
        sanitized_text, _, _ = ResponseValidator.validate_and_sanitize(full_generated_text)
        assistant_msg = Message(
            conversation_id=conversation_id,
            role="assistant",
            content=sanitized_text,
            thinking_steps=[],
            citations=[c.model_dump() if hasattr(c, "model_dump") else dict(c) for c in tool_results.get("citations", [])],
            confidence_score=tool_results["confidence"].score,
            latency_ms=100
        )
        db.add(assistant_msg)
        await db.commit()

        # Emit completion
        yield f"event: done\ndata: {json.dumps({'message_id': str(assistant_msg.id), 'status': 'completed'})}\n\n"
