import json
import logging
import time
from typing import Dict, Any, List, Optional, AsyncGenerator
import httpx

from app.ai.llm_provider import BaseLLMProvider

logger = logging.getLogger(__name__)


class OpenAICompatibleProvider(BaseLLMProvider):
    """
    Generic provider for any OpenAI-compatible API:
    - OpenAI (api.openai.com)
    - OpenRouter (openrouter.ai)
    - Mistral AI (api.mistral.ai)
    - xAI Grok (api.x.ai)
    - Local models via Ollama / vLLM / LocalAI
    """

    def __init__(
        self,
        provider_name: str,
        model_name: str,
        api_key: str,
        base_url: str = "https://api.openai.com/v1",
        extra_headers: Optional[Dict[str, str]] = None,
        timeout_seconds: int = 30,
    ):
        self._provider_name = provider_name
        self._model_name = model_name
        self._api_key = api_key.strip() if api_key else ""
        self._base_url = base_url.rstrip("/")
        self._extra_headers = extra_headers or {}
        self._timeout_seconds = timeout_seconds

    @property
    def provider_name(self) -> str:
        return self._provider_name

    @property
    def model_name(self) -> str:
        return self._model_name

    def is_available(self) -> bool:
        return bool(self._api_key)

    def _get_headers(self) -> Dict[str, str]:
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        headers.update(self._extra_headers)
        return headers

    def _build_messages(
        self,
        prompt: str,
        system_instruction: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> List[Dict[str, str]]:
        messages = [{"role": "system", "content": system_instruction}]
        if conversation_history:
            for turn in conversation_history:
                role = "assistant" if turn.get("role") in ("model", "assistant") else "user"
                messages.append({"role": role, "content": turn.get("content", "")})
        messages.append({"role": "user", "content": prompt})
        return messages

    async def generate(
        self,
        prompt: str,
        system_instruction: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        temperature: float = 0.2,
        max_output_tokens: int = 1024,
    ) -> Dict[str, Any]:
        if not self.is_available():
            raise ValueError(f"Provider '{self._provider_name}' is not configured with an API key.")

        url = f"{self._base_url}/chat/completions"
        headers = self._get_headers()
        messages = self._build_messages(prompt, system_instruction, conversation_history)
        payload = {
            "model": self._model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_output_tokens,
            "stream": False,
        }

        start_time = time.time()
        async with httpx.AsyncClient(timeout=self._timeout_seconds) as client:
            response = await client.post(url, headers=headers, json=payload)
            if response.status_code != 200:
                raise RuntimeError(
                    f"{self._provider_name} API returned {response.status_code}: {response.text}"
                )
            data = response.json()

        latency_ms = int((time.time() - start_time) * 1000)
        choices = data.get("choices", [])
        if not choices:
            raise RuntimeError(f"{self._provider_name} returned empty choices array.")

        content = choices[0].get("message", {}).get("content", "").strip()
        usage = data.get("usage", {})

        return {
            "content": content,
            "prompt_tokens": usage.get("prompt_tokens", len(prompt) // 4),
            "completion_tokens": usage.get("completion_tokens", len(content) // 4),
            "total_tokens": usage.get("total_tokens", (len(prompt) + len(content)) // 4),
            "latency_ms": latency_ms,
            "model": self._model_name,
            "finish_reason": choices[0].get("finish_reason", "stop"),
        }

    async def generate_stream(
        self,
        prompt: str,
        system_instruction: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        temperature: float = 0.2,
        max_output_tokens: int = 1024,
    ) -> AsyncGenerator[str, None]:
        if not self.is_available():
            raise ValueError(f"Provider '{self._provider_name}' is not configured with an API key.")

        url = f"{self._base_url}/chat/completions"
        headers = self._get_headers()
        messages = self._build_messages(prompt, system_instruction, conversation_history)
        payload = {
            "model": self._model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_output_tokens,
            "stream": True,
        }

        async with httpx.AsyncClient(timeout=self._timeout_seconds) as client:
            async with client.stream("POST", url, headers=headers, json=payload) as response:
                if response.status_code != 200:
                    err_body = await response.aread()
                    raise RuntimeError(
                        f"{self._provider_name} streaming error {response.status_code}: {err_body.decode('utf-8')}"
                    )
                async for line in response.aiter_lines():
                    line = line.strip()
                    if not line or line.startswith(":"):
                        continue
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data_str)
                            delta = chunk.get("choices", [{}])[0].get("delta", {})
                            token = delta.get("content")
                            if token:
                                yield token
                        except json.JSONDecodeError:
                            continue


class OpenRouterLLMProvider(OpenAICompatibleProvider):
    """OpenRouter adapter with site referral headers."""

    def __init__(self, api_key: str, model_name: str = "meta-llama/llama-3.3-70b-instruct:free", base_url: str = "https://openrouter.ai/api/v1"):
        super().__init__(
            provider_name="openrouter",
            model_name=model_name,
            api_key=api_key,
            base_url=base_url,
            extra_headers={
                "HTTP-Referer": "https://campusconnect.lpu.in",
                "X-Title": "LPU CampusConnect AI Student Portal",
            },
        )


class MistralLLMProvider(OpenAICompatibleProvider):
    """Mistral AI adapter."""

    def __init__(self, api_key: str, model_name: str = "mistral-small-latest", base_url: str = "https://api.mistral.ai/v1"):
        super().__init__(
            provider_name="mistral",
            model_name=model_name,
            api_key=api_key,
            base_url=base_url,
        )


class XAIGrokLLMProvider(OpenAICompatibleProvider):
    """xAI Grok adapter."""

    def __init__(self, api_key: str, model_name: str = "grok-beta", base_url: str = "https://api.x.ai/v1"):
        super().__init__(
            provider_name="xai",
            model_name=model_name,
            api_key=api_key,
            base_url=base_url,
        )


class GenericOpenAILLMProvider(OpenAICompatibleProvider):
    """Generic OpenAI-compatible adapter."""

    def __init__(self, api_key: str, model_name: str = "gpt-4o-mini", base_url: str = "https://api.openai.com/v1"):
        super().__init__(
            provider_name="openai",
            model_name=model_name,
            api_key=api_key,
            base_url=base_url,
        )


class GroqLLMProvider(OpenAICompatibleProvider):
    """Groq ultra-fast inference adapter."""

    def __init__(
        self,
        api_key: str,
        model_name: str = "llama-3.3-70b-versatile",
        base_url: str = "https://api.groq.com/openai/v1",
    ):
        super().__init__(
            provider_name="groq",
            model_name=model_name,
            api_key=api_key,
            base_url=base_url,
        )


class BazaarLinkLLMProvider(OpenAICompatibleProvider):
    """BazaarLink AI Gateway adapter (e.g. qwen/qwen3.7-flash:free)."""

    def __init__(
        self,
        api_key: str,
        model_name: str = "qwen/qwen3.7-flash:free",
        base_url: str = "https://api.bazaarlink.ai/v1",
    ):
        super().__init__(
            provider_name="bazaarlink",
            model_name=model_name,
            api_key=api_key,
            base_url=base_url,
        )


class PekpikLLMProvider(OpenAICompatibleProvider):
    """Pekpik LLM adapter (DeepSeek Flash & GPT models)."""

    def __init__(
        self,
        api_key: str,
        model_name: str = "deepseek-v4-1-flash-1017",
        base_url: str = "https://aiapiv2.pekpik.com/v1",
    ):
        super().__init__(
            provider_name="pekpik",
            model_name=model_name,
            api_key=api_key,
            base_url=base_url,
        )


class AionLabsLLMProvider(OpenAICompatibleProvider):
    """Aion Labs API adapter."""

    def __init__(
        self,
        api_key: str,
        model_name: str = "default",
        base_url: str = "https://api.aionlabs.ai/v1",
    ):
        super().__init__(
            provider_name="aionlabs",
            model_name=model_name,
            api_key=api_key,
            base_url=base_url,
        )


class CohereLLMProvider(OpenAICompatibleProvider):
    """Cohere v2 / OpenAI-compatible adapter."""

    def __init__(
        self,
        api_key: str,
        model_name: str = "command-a-03-2025",
        base_url: str = "https://api.cohere.com/compatibility/v1",
    ):
        super().__init__(
            provider_name="cohere",
            model_name=model_name,
            api_key=api_key,
            base_url=base_url,
        )


