import pytest
import asyncio
import time
from unittest.mock import AsyncMock, patch, MagicMock

from app.ai.llm_registry import LLMRegistry
from app.ai.response_generator import ResponseGenerator
from app.ai.router_policy import RouterPolicy
from app.ai.gemini_provider import GeminiProvider, circuit_breaker
from app.ai.fallback_manager import FallbackManager
from app.ai.openai_compatible_provider import BazaarLinkLLMProvider, GroqLLMProvider


@pytest.mark.asyncio
async def test_1_primary_gemini_success():
    """Verify primary Gemini succeeds and returns valid response structure."""
    mock_gemini = AsyncMock()
    mock_gemini.provider_name = "gemini"
    mock_gemini.model_name = "gemini-3.5-flash-lite"
    mock_gemini.is_available.return_value = True
    mock_gemini.generate.return_value = {
        "content": "CampusConnect: The AI & ML coordinator is Dr. Dalwinder Singh in Block 32.",
        "prompt_tokens": 120,
        "completion_tokens": 30,
        "total_tokens": 150,
        "latency_ms": 350,
        "model": "gemini-3.5-flash-lite",
        "finish_reason": "stop"
    }

    with patch.object(LLMRegistry, "get_provider", side_effect=lambda name: mock_gemini if name == "gemini" else MagicMock(is_available=lambda: False)):
        with patch.object(RouterPolicy, "select_provider_cascade", return_value=[("gemini", mock_gemini)]):
            res = await ResponseGenerator.generate_response(
                user_message="Who is the AI ML lead?",
                evidence_context="Dr. Dalwinder Singh is the Academic Coordinator for AI & ML in Block 32.",
                conversation_history=[]
            )
            assert res["provider"] == "gemini"
            assert "Dr. Dalwinder Singh" in res["content"]
            assert res["latency_ms"] == 350


@pytest.mark.asyncio
async def test_2_primary_gemini_429_failover_to_secondary():
    """Verify when primary Gemini returns 429 quota exhausted, secondary provider takes over successfully."""
    # 1. Primary throws 429 quota exception
    mock_gemini = AsyncMock()
    mock_gemini.provider_name = "gemini"
    mock_gemini.model_name = "gemini-3.5-flash-lite"
    mock_gemini.is_available.return_value = True
    mock_gemini.generate.side_effect = RuntimeError("429 Resource Exhausted: Gemini Developer Free Tier quota exceeded")

    # 2. Secondary BazaarLink succeeds
    mock_secondary = AsyncMock()
    mock_secondary.provider_name = "bazaarlink"
    mock_secondary.model_name = "qwen/qwen3.7-flash:free"
    mock_secondary.is_available.return_value = True
    mock_secondary.generate.return_value = {
        "content": "BazaarLink Failover: Pure vegetarian food stalls are open at Uni-Centre.",
        "prompt_tokens": 90,
        "completion_tokens": 25,
        "total_tokens": 115,
        "latency_ms": 420,
        "model": "qwen/qwen3.7-flash:free",
        "finish_reason": "stop"
    }

    cascade = [("gemini", mock_gemini), ("bazaarlink", mock_secondary)]
    with patch.object(RouterPolicy, "select_provider_cascade", return_value=cascade):
        res = await ResponseGenerator.generate_response(
            user_message="Where can I find pure veg food?",
            evidence_context="Uni-Centre food court has 100% vegetarian stalls.",
            conversation_history=[]
        )
        assert res["provider"] == "bazaarlink"
        assert "BazaarLink Failover" in res["content"]
        assert mock_gemini.generate.called
        assert mock_secondary.generate.called


@pytest.mark.asyncio
async def test_3_primary_gemini_timeout_failover_to_secondary():
    """Verify when primary Gemini times out, secondary provider takes over seamlessly."""
    mock_gemini = AsyncMock()
    mock_gemini.provider_name = "gemini"
    mock_gemini.model_name = "gemini-3.5-flash-lite"
    mock_gemini.is_available.return_value = True
    mock_gemini.generate.side_effect = asyncio.TimeoutError("Gemini request timed out after 30s")

    mock_secondary = AsyncMock()
    mock_secondary.provider_name = "groq"
    mock_secondary.model_name = "llama-3.3-70b-versatile"
    mock_secondary.is_available.return_value = True
    mock_secondary.generate.return_value = {
        "content": "Groq Failover: Attendance condonation up to 10% requires medical/duty leave proof.",
        "prompt_tokens": 80,
        "completion_tokens": 20,
        "total_tokens": 100,
        "latency_ms": 190,
        "model": "llama-3.3-70b-versatile",
        "finish_reason": "stop"
    }

    cascade = [("gemini", mock_gemini), ("groq", mock_secondary)]
    with patch.object(RouterPolicy, "select_provider_cascade", return_value=cascade):
        res = await ResponseGenerator.generate_response(
            user_message="How do I get attendance condonation?",
            evidence_context="10% institutional attendance condonation requires verified medical or duty leave.",
            conversation_history=[]
        )
        assert res["provider"] == "groq"
        assert "Groq Failover" in res["content"]


@pytest.mark.asyncio
async def test_4_primary_gemini_network_failure_failover_to_secondary():
    """Verify when primary Gemini suffers network/connection failure, secondary provider takes over."""
    mock_gemini = AsyncMock()
    mock_gemini.provider_name = "gemini"
    mock_gemini.model_name = "gemini-3.5-flash-lite"
    mock_gemini.is_available.return_value = True
    mock_gemini.generate.side_effect = ConnectionError("Failed to establish a new connection to generativelanguage.googleapis.com")

    mock_secondary = AsyncMock()
    mock_secondary.provider_name = "pekpik"
    mock_secondary.model_name = "deepseek-v4-1-flash-1017"
    mock_secondary.is_available.return_value = True
    mock_secondary.generate.return_value = {
        "content": "Pekpik Failover: Proctorial Board hearings are held in Block 30 Division of Student Welfare.",
        "prompt_tokens": 85,
        "completion_tokens": 22,
        "total_tokens": 107,
        "latency_ms": 510,
        "model": "deepseek-v4-1-flash-1017",
        "finish_reason": "stop"
    }

    cascade = [("gemini", mock_gemini), ("pekpik", mock_secondary)]
    with patch.object(RouterPolicy, "select_provider_cascade", return_value=cascade):
        res = await ResponseGenerator.generate_response(
            user_message="Where is Proctorial Board?",
            evidence_context="Proctorial Board is located in Block 30 Division of Student Welfare.",
            conversation_history=[]
        )
        assert res["provider"] == "pekpik"
        assert "Pekpik Failover" in res["content"]


@pytest.mark.asyncio
async def test_5_all_providers_unavailable_handled_safely():
    """Verify when all providers in cascade fail, system raises and FallbackManager produces safe verified response."""
    mock_p1 = AsyncMock()
    mock_p1.generate.side_effect = RuntimeError("Primary failure")

    mock_p2 = AsyncMock()
    mock_p2.generate.side_effect = RuntimeError("Secondary failure")

    cascade = [("gemini", mock_p1), ("bazaarlink", mock_p2)]
    with patch.object(RouterPolicy, "select_provider_cascade", return_value=cascade):
        with pytest.raises(RuntimeError) as exc_info:
            await ResponseGenerator.generate_response(
                user_message="Test query",
                evidence_context="Test evidence",
                conversation_history=[]
            )
        assert "All LLM providers in cascade failed" in str(exc_info.value)

    # Test FallbackManager produces safe structured response without crashing
    mock_tool_results = {
        "evidence_context": "Block 32 houses the School of Computer Science & Engineering.",
        "citations": [{"title": "LPU Campus Map", "url": "https://www.lpu.in"}],
        "confidence": MagicMock(score=0.88),
    }
    fb = FallbackManager.get_service_error_response("All LLM providers in cascade failed", mock_tool_results)
    assert fb["finish_reason"] == "error_fallback"
    assert fb["model"] == "verified-institutional-fallback"
    assert "Block 32" in fb["content"]
    assert "⚠️" in fb["content"]


@pytest.mark.asyncio
async def test_6_circuit_breaker_recovery():
    """Verify circuit breaker trips on 429 and restores availability after cooldown."""
    cb = GeminiProvider.__init__
    # Test circuit breaker behavior directly
    cb_inst = circuit_breaker
    cb_inst.circuit_open_until = 0.0  # Reset
    assert not cb_inst.is_open()

    # Trip breaker
    cb_inst.trip(cooldown_seconds=1)
    assert cb_inst.is_open()

    # Wait for cooldown to expire
    await asyncio.sleep(1.05)
    assert not cb_inst.is_open()
    cb_inst.record_success()
    assert cb_inst.total_calls >= 1
