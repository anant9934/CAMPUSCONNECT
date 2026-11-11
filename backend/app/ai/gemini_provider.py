import asyncio
import logging
import random
import time
from typing import Dict, Any, List, Optional, AsyncGenerator
from google import genai
from google.genai import types
from google.genai.errors import APIError

from app.core.config import settings
from app.ai.llm_provider import BaseLLMProvider

logger = logging.getLogger(__name__)


class GeminiCircuitBreaker:
    """Protects Gemini Developer API Free Tier limits by backing off when rate-limited."""
    def __init__(self):
        self.circuit_open_until: float = 0.0
        self.rate_limit_hits: int = 0
        self.total_calls: int = 0
        self.failed_calls: int = 0

    def trip(self, cooldown_seconds: int = 60) -> None:
        self.circuit_open_until = time.time() + cooldown_seconds
        self.rate_limit_hits += 1
        logger.warning(f"Gemini Circuit Breaker TRIPPED for {cooldown_seconds}s.")

    def is_open(self) -> bool:
        return time.time() < self.circuit_open_until

    def record_success(self) -> None:
        self.total_calls += 1

    def record_failure(self) -> None:
        self.total_calls += 1
        self.failed_calls += 1


circuit_breaker = GeminiCircuitBreaker()


class GeminiProvider(BaseLLMProvider):
    """
    Real Google Gemini LLM Provider using the modern official google-genai SDK.
    Configured for Gemini Developer API Free Tier.
    Supports non-streaming and streaming token generation.
    """

    def __init__(self):
        self._primary_key = settings.GEMINI_API_KEY.strip() if settings.GEMINI_API_KEY else ""
        self._secondary_key = settings.GEMINI_API_KEY_SECONDARY.strip() if settings.GEMINI_API_KEY_SECONDARY else ""
        self._active_key = self._primary_key or self._secondary_key
        self._model = settings.GEMINI_MODEL
        self._client: Optional[genai.Client] = None
        self._init_client()

    def _init_client(self) -> None:
        if self._active_key:
            try:
                self._client = genai.Client(api_key=self._active_key)
                logger.info(f"GeminiProvider initialized with model '{self._model}'")
            except Exception as e:
                logger.error(f"GeminiProvider initialization error: {e}")
                self._client = None
        else:
            logger.warning("GeminiProvider: No API key provided.")
            self._client = None

    def _rotate_key(self) -> bool:
        if self._secondary_key and self._active_key != self._secondary_key:
            try:
                self._client = genai.Client(api_key=self._secondary_key)
                self._active_key = self._secondary_key
                logger.info("Rotated to secondary Gemini API key.")
                return True
            except Exception as e:
                logger.error(f"Failed to switch to secondary Gemini key: {e}")
        return False

    @property
    def provider_name(self) -> str:
        return "gemini"

    @property
    def model_name(self) -> str:
        return self._model

    def is_available(self) -> bool:
        return self._client is not None and not circuit_breaker.is_open()

    async def generate(
        self,
        prompt: str,
        system_instruction: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        temperature: float = 0.2,
        max_output_tokens: int = 1024,
    ) -> Dict[str, Any]:
        """
        Executes a real call to Google Gemini API with retries and exponential backoff.
        """
        if not self.is_available():
            raise RuntimeError("Gemini API is currently unavailable or circuit breaker is open.")

        retries = settings.GEMINI_MAX_RETRIES
        delay = 1.0
        start_time = time.time()

        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
        )

        for attempt in range(retries + 1):
            try:
                loop = asyncio.get_running_loop()
                response = await asyncio.wait_for(
                    loop.run_in_executor(
                        None,
                        lambda: self._client.models.generate_content(
                            model=self._model,
                            contents=prompt,
                            config=config
                        )
                    ),
                    timeout=float(settings.GEMINI_TIMEOUT_SECONDS)
                )

                latency_ms = int((time.time() - start_time) * 1000)
                circuit_breaker.record_success()

                text = ""
                if response and hasattr(response, "text") and response.text:
                    text = response.text.strip()
                elif response and hasattr(response, "candidates") and response.candidates:
                    parts = response.candidates[0].content.parts
                    text = "".join(p.text for p in parts if hasattr(p, "text")).strip()

                usage = getattr(response, "usage_metadata", None)
                p_tokens = getattr(usage, "prompt_token_count", 0) or len(prompt) // 4
                c_tokens = getattr(usage, "candidates_token_count", 0) or len(text) // 4

                return {
                    "content": text,
                    "prompt_tokens": p_tokens,
                    "completion_tokens": c_tokens,
                    "total_tokens": p_tokens + c_tokens,
                    "latency_ms": latency_ms,
                    "model": self._model,
                    "finish_reason": "stop"
                }

            except (APIError, Exception) as e:
                err_str = str(e).lower()
                is_rate_limit = "429" in err_str or "quota" in err_str or "resource_exhausted" in err_str

                if is_rate_limit:
                    if self._rotate_key():
                        logger.info("Retrying with secondary Gemini API key...")
                        continue
                    circuit_breaker.trip(cooldown_seconds=60)
                    circuit_breaker.record_failure()
                    raise RuntimeError("Gemini Developer Free Tier quota exceeded. Temporary backoff active.") from e

                if attempt < retries:
                    jitter = random.uniform(0.1, 0.5)
                    await asyncio.sleep(delay + jitter)
                    delay *= 2.0
                else:
                    circuit_breaker.record_failure()
                    raise e

        raise RuntimeError("Gemini request failed after all retries.")

    async def generate_stream(
        self,
        prompt: str,
        system_instruction: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        temperature: float = 0.2,
        max_output_tokens: int = 1024,
    ) -> AsyncGenerator[str, None]:
        """
        Streams tokens incrementally from Google Gemini API.
        """
        if not self.is_available():
            raise RuntimeError("Gemini API is unavailable or circuit breaker open.")

        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
        )

        try:
            # generate_content_stream returns an iterator of response chunks
            response_stream = self._client.models.generate_content_stream(
                model=self._model,
                contents=prompt,
                config=config
            )

            for chunk in response_stream:
                chunk_text = ""
                if hasattr(chunk, "text") and chunk.text:
                    chunk_text = chunk.text
                elif hasattr(chunk, "candidates") and chunk.candidates:
                    parts = chunk.candidates[0].content.parts
                    chunk_text = "".join(p.text for p in parts if hasattr(p, "text"))

                if chunk_text:
                    yield chunk_text
                    await asyncio.sleep(0.01)  # Cooperative yield for async streaming

            circuit_breaker.record_success()

        except Exception as e:
            err_str = str(e).lower()
            if "429" in err_str or "quota" in err_str:
                circuit_breaker.trip(60)
            logger.error(f"Gemini streaming error: {e}")
            raise e
