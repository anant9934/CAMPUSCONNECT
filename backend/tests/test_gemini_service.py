import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from app.services.gemini_service import GeminiService, quota_manager
from app.services.grounding_service import validate_grounded_response
from google.genai.errors import APIError


@pytest.mark.asyncio
async def test_gemini_verified_fallback_when_unconfigured():
    from app.core.config import settings
    with patch.object(settings, "GEMINI_API_KEY", ""), patch.object(settings, "GEMINI_API_KEY_SECONDARY", ""):
        service = GeminiService()
        service.client = None  # Simulate unconfigured API key

        sample_faq = {
            "canonical_question": "How do I download my examination date sheet at LPU?",
            "answer": "Log in to UMS and click on Examination -> Date Sheet.",
            "source_url": "https://ums.lpu.in",
            "source_title": "LPU Examination Division Guidelines"
        }

        result = await service.generate_grounded_response(
            query="Where is my date sheet?",
            evidence_context="Sample verified evidence",
            top_faq_match=sample_faq
        )

        assert result["is_ai_generated"] is False
        assert "Log in to UMS" in result["text"]
        assert "verified_fallback" in result["status"]


@pytest.mark.asyncio
async def test_gemini_quota_exhausted_trips_circuit_breaker():
    from app.core.config import settings
    with patch.object(settings, "GEMINI_API_KEY", "dummy_test_api_key"), patch.object(settings, "GEMINI_API_KEY_SECONDARY", ""):
        service = GeminiService()
        mock_client = MagicMock()
        service.client = mock_client

        sample_faq = {
            "canonical_question": "What is the mandatory attendance requirement at LPU?",
            "answer": "Minimum 75% attendance is required.",
            "source_url": "https://ums.lpu.in",
            "source_title": "LPU Academic Regulations"
        }

        # Simulate HTTP 429 Resource Exhausted APIError
        api_error = APIError(429, {"error": {"message": "Resource exhausted: daily quota limit reached"}})
        mock_client.models.generate_content.side_effect = api_error

        result = await service.generate_grounded_response(
            query="What attendance is needed?",
            evidence_context="Evidence context",
            top_faq_match=sample_faq
        )

        # Must fall back gracefully to verified FAQ without crashing or lying
        assert result["is_ai_generated"] is False
        assert "Minimum 75% attendance" in result["text"]
        assert "quota" in result["status"] or "verified_fallback" in result["status"]
        assert quota_manager.is_circuit_open() is True


def test_grounding_validation_detects_forbidden_claims():
    bad_text = "I have accessed your private record and updated your attendance to 85%."
    is_valid, text, reason = validate_grounded_response(bad_text, "Evidence context")
    assert is_valid is False
    assert "Forbidden assertion" in reason


def test_grounding_validation_sanitizes_unapproved_urls():
    text_with_fake_url = "You can download it at https://fake-exam-portal-cheat.com/sheet or https://ums.lpu.in"
    is_valid, sanitized, reason = validate_grounded_response(text_with_fake_url, "Evidence context")
    assert is_valid is True
    assert "fake-exam-portal-cheat.com" not in sanitized
    assert "ums.lpu.in" in sanitized
