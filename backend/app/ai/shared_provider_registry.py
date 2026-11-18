import os
import time
import logging
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from app.core.config import settings

logger = logging.getLogger(__name__)


class ModelCapabilities(BaseModel):
    streaming: bool = True
    structured_output: bool = True
    tool_calling: bool = True
    image_input: bool = False
    reasoning_mode: bool = False
    context_window: int = 128000
    max_output_tokens: int = 4096


class TokenPricing(BaseModel):
    input_usd_per_1m: float = 0.0
    output_usd_per_1m: float = 0.0


class RateLimitConfig(BaseModel):
    max_requests_per_minute: int = 60
    max_tokens_per_minute: int = 100000


class ProviderHealthState(BaseModel):
    is_healthy: bool = True
    consecutive_failures: int = 0
    circuit_state: str = "closed"  # closed, open, half_open
    avg_latency_ms: float = 120.0
    last_checked_at: float = Field(default_factory=time.time)
    last_error: Optional[str] = None


class ProviderModelDescriptor(BaseModel):
    provider_name: str
    model_id: str
    display_name: str
    capabilities: ModelCapabilities
    pricing: TokenPricing
    rate_limits: RateLimitConfig = Field(default_factory=RateLimitConfig)
    health: ProviderHealthState = Field(default_factory=ProviderHealthState)
    timeout_seconds: float = 20.0
    is_available: bool = True
    latency_tier: str = "fast"  # ultra_fast, fast, standard, deep_reasoning
    fallback_compatibles: List[str] = Field(default_factory=list)


class SharedProviderRegistry:
    """
    Central Multi-Provider Model Registry:
    Tracks model descriptors, pricing, capabilities, health states, and circuit breakers.
    No intelligence identity is permanently bound to any single provider.
    """

    _models: Dict[str, ProviderModelDescriptor] = {}
    _initialized: bool = False

    @classmethod
    def initialize(cls) -> None:
        if cls._initialized:
            return

        # 1. Google Gemini
        has_gemini = bool(settings.GEMINI_API_KEY)
        cls.register_model(
            ProviderModelDescriptor(
                provider_name="gemini",
                model_id="gemini-2.5-flash",
                display_name="Google Gemini 2.5 Flash",
                capabilities=ModelCapabilities(
                    streaming=True,
                    structured_output=True,
                    tool_calling=True,
                    image_input=True,
                    reasoning_mode=True,
                    context_window=1000000,
                    max_output_tokens=8192,
                ),
                pricing=TokenPricing(input_usd_per_1m=0.075, output_usd_per_1m=0.30),
                rate_limits=RateLimitConfig(max_requests_per_minute=15, max_tokens_per_minute=1000000),
                timeout_seconds=25.0,
                is_available=has_gemini,
                latency_tier="fast",
                fallback_compatibles=["groq::llama-3.3-70b-versatile", "openrouter::meta-llama/llama-3.3-70b-instruct"],
            )
        )
        cls.register_model(
            ProviderModelDescriptor(
                provider_name="gemini",
                model_id="gemini-1.5-pro",
                display_name="Google Gemini 1.5 Pro",
                capabilities=ModelCapabilities(
                    streaming=True,
                    structured_output=True,
                    tool_calling=True,
                    image_input=True,
                    reasoning_mode=True,
                    context_window=2000000,
                    max_output_tokens=8192,
                ),
                pricing=TokenPricing(input_usd_per_1m=1.25, output_usd_per_1m=5.00),
                rate_limits=RateLimitConfig(max_requests_per_minute=5, max_tokens_per_minute=500000),
                timeout_seconds=35.0,
                is_available=has_gemini,
                latency_tier="deep_reasoning",
                fallback_compatibles=["gemini::gemini-2.5-flash", "groq::llama-3.3-70b-versatile"],
            )
        )

        # 2. Groq (High-speed inference)
        has_groq = bool(settings.GROQ_API_KEY)
        cls.register_model(
            ProviderModelDescriptor(
                provider_name="groq",
                model_id="llama-3.3-70b-versatile",
                display_name="Groq Llama 3.3 70B Versatile",
                capabilities=ModelCapabilities(
                    streaming=True,
                    structured_output=True,
                    tool_calling=True,
                    image_input=False,
                    reasoning_mode=True,
                    context_window=128000,
                    max_output_tokens=4096,
                ),
                pricing=TokenPricing(input_usd_per_1m=0.59, output_usd_per_1m=0.79),
                rate_limits=RateLimitConfig(max_requests_per_minute=30, max_tokens_per_minute=6000),
                timeout_seconds=15.0,
                is_available=has_groq,
                latency_tier="ultra_fast",
                fallback_compatibles=["gemini::gemini-2.5-flash", "openrouter::meta-llama/llama-3.3-70b-instruct"],
            )
        )
        cls.register_model(
            ProviderModelDescriptor(
                provider_name="groq",
                model_id="mixtral-8x7b-32768",
                display_name="Groq Mixtral 8x7B",
                capabilities=ModelCapabilities(
                    streaming=True,
                    structured_output=True,
                    tool_calling=True,
                    image_input=False,
                    reasoning_mode=False,
                    context_window=32768,
                    max_output_tokens=4096,
                ),
                pricing=TokenPricing(input_usd_per_1m=0.24, output_usd_per_1m=0.24),
                rate_limits=RateLimitConfig(max_requests_per_minute=30, max_tokens_per_minute=5000),
                timeout_seconds=12.0,
                is_available=has_groq,
                latency_tier="ultra_fast",
                fallback_compatibles=["groq::llama-3.3-70b-versatile", "gemini::gemini-2.5-flash"],
            )
        )

        # 3. OpenRouter (Multi-model gateway)
        has_openrouter = bool(settings.OPENROUTER_API_KEY)
        cls.register_model(
            ProviderModelDescriptor(
                provider_name="openrouter",
                model_id="meta-llama/llama-3.3-70b-instruct",
                display_name="OpenRouter Llama 3.3 70B Instruct",
                capabilities=ModelCapabilities(
                    streaming=True,
                    structured_output=True,
                    tool_calling=True,
                    image_input=False,
                    reasoning_mode=True,
                    context_window=128000,
                    max_output_tokens=4096,
                ),
                pricing=TokenPricing(input_usd_per_1m=0.12, output_usd_per_1m=0.30),
                rate_limits=RateLimitConfig(max_requests_per_minute=60, max_tokens_per_minute=100000),
                timeout_seconds=20.0,
                is_available=has_openrouter,
                latency_tier="fast",
                fallback_compatibles=["gemini::gemini-2.5-flash", "groq::llama-3.3-70b-versatile"],
            )
        )

        # 4. Mistral AI
        has_mistral = bool(settings.MISTRAL_API_KEY)
        cls.register_model(
            ProviderModelDescriptor(
                provider_name="mistral",
                model_id="mistral-small-latest",
                display_name="Mistral Small Latest",
                capabilities=ModelCapabilities(
                    streaming=True,
                    structured_output=True,
                    tool_calling=True,
                    image_input=False,
                    reasoning_mode=False,
                    context_window=32000,
                    max_output_tokens=4096,
                ),
                pricing=TokenPricing(input_usd_per_1m=0.20, output_usd_per_1m=0.60),
                rate_limits=RateLimitConfig(max_requests_per_minute=60, max_tokens_per_minute=100000),
                timeout_seconds=20.0,
                is_available=has_mistral,
                latency_tier="fast",
                fallback_compatibles=["gemini::gemini-2.5-flash", "groq::llama-3.3-70b-versatile"],
            )
        )

        # 5. Cohere (Retrieval & Reranking specialized provider)
        has_cohere = bool(settings.COHERE_API_KEY)
        cls.register_model(
            ProviderModelDescriptor(
                provider_name="cohere",
                model_id="command-r-plus",
                display_name="Cohere Command R+",
                capabilities=ModelCapabilities(
                    streaming=True,
                    structured_output=True,
                    tool_calling=True,
                    image_input=False,
                    reasoning_mode=True,
                    context_window=128000,
                    max_output_tokens=4096,
                ),
                pricing=TokenPricing(input_usd_per_1m=2.50, output_usd_per_1m=10.00),
                rate_limits=RateLimitConfig(max_requests_per_minute=20, max_tokens_per_minute=50000),
                timeout_seconds=25.0,
                is_available=has_cohere,
                latency_tier="standard",
                fallback_compatibles=["gemini::gemini-2.5-flash"],
            )
        )

        # 6. BazaarLink (AI Agent LLM Gateway)
        has_bazaarlink = bool(settings.BAZAARLINK_API_KEY)
        cls.register_model(
            ProviderModelDescriptor(
                provider_name="bazaarlink",
                model_id="qwen/qwen3.7-flash:free",
                display_name="BazaarLink Qwen 3.7 Flash (Free)",
                capabilities=ModelCapabilities(
                    streaming=True,
                    structured_output=True,
                    tool_calling=True,
                    image_input=False,
                    reasoning_mode=False,
                    context_window=32768,
                    max_output_tokens=2048,
                ),
                pricing=TokenPricing(input_usd_per_1m=0.0, output_usd_per_1m=0.0),
                rate_limits=RateLimitConfig(max_requests_per_minute=20, max_tokens_per_minute=50000),
                timeout_seconds=18.0,
                is_available=has_bazaarlink,
                latency_tier="fast",
                fallback_compatibles=["gemini::gemini-2.5-flash"],
            )
        )

        # 7. PEKPIK LLM (DeepSeek reasoning gateway)
        has_pekpik = bool(getattr(settings, "PEKPIK_DEEPSEEK_API_KEY", "") or getattr(settings, "PEKPIK_GPT_API_KEY", ""))
        cls.register_model(
            ProviderModelDescriptor(
                provider_name="pekpik",
                model_id="deepseek-flash",
                display_name="PEKPIK DeepSeek Flash",
                capabilities=ModelCapabilities(
                    streaming=True,
                    structured_output=True,
                    tool_calling=True,
                    image_input=False,
                    reasoning_mode=True,
                    context_window=64000,
                    max_output_tokens=4096,
                ),
                pricing=TokenPricing(input_usd_per_1m=0.0, output_usd_per_1m=0.0),
                rate_limits=RateLimitConfig(max_requests_per_minute=30, max_tokens_per_minute=60000),
                timeout_seconds=25.0,
                is_available=has_pekpik,
                latency_tier="standard",
                fallback_compatibles=["groq::llama-3.3-70b-versatile", "gemini::gemini-2.5-flash"],
            )
        )

        cls._initialized = True
        logger.info(f"SharedProviderRegistry initialized with {len(cls._models)} models across 7 provider adapters.")

    @classmethod
    def register_model(cls, descriptor: ProviderModelDescriptor) -> None:
        key = f"{descriptor.provider_name}::{descriptor.model_id}"
        cls._models[key] = descriptor

    @classmethod
    def get_model(cls, provider_name: str, model_id: str) -> Optional[ProviderModelDescriptor]:
        cls.initialize()
        return cls._models.get(f"{provider_name}::{model_id}")

    @classmethod
    def get_by_key(cls, key: str) -> Optional[ProviderModelDescriptor]:
        cls.initialize()
        return cls._models.get(key)

    @classmethod
    def list_models(cls, active_only: bool = True) -> List[ProviderModelDescriptor]:
        cls.initialize()
        if active_only:
            return [m for m in cls._models.values() if m.is_available and m.health.is_healthy]
        return list(cls._models.values())

    @classmethod
    def update_health(
        cls,
        provider_name: str,
        model_id: str,
        success: bool,
        latency_ms: float = 0.0,
        error_msg: Optional[str] = None
    ) -> None:
        cls.initialize()
        key = f"{provider_name}::{model_id}"
        m = cls._models.get(key)
        if not m:
            return

        h = m.health
        h.last_checked_at = time.time()
        if success:
            h.consecutive_failures = 0
            h.circuit_state = "closed"
            h.is_healthy = True
            h.avg_latency_ms = (h.avg_latency_ms * 0.8) + (latency_ms * 0.2)
        else:
            h.consecutive_failures += 1
            h.last_error = error_msg
            if h.consecutive_failures >= 3:
                h.circuit_state = "open"
                h.is_healthy = False
                logger.warning(f"Circuit breaker opened for model {key}: {error_msg}")
