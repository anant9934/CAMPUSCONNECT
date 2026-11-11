import logging
from typing import Dict, Any, Optional, List
from app.core.config import settings
from app.ai.llm_provider import BaseLLMProvider
from app.ai.gemini_provider import GeminiProvider
from app.ai.openai_compatible_provider import (
    OpenRouterLLMProvider,
    MistralLLMProvider,
    XAIGrokLLMProvider,
    GenericOpenAILLMProvider,
    GroqLLMProvider,
    BazaarLinkLLMProvider,
    PekpikLLMProvider,
    AionLabsLLMProvider,
    CohereLLMProvider,
)

logger = logging.getLogger(__name__)


class LLMRegistry:
    """
    Registry for configured Multi-Provider LLMs in CampusConnect V8:
    - Google Gemini (Gemini 2.5 Flash / Pro)
    - OpenRouter (Llama 3.3 70B, etc.)
    - Mistral AI (Mistral Small / Medium)
    - xAI Grok (Grok Beta)
    - OpenAI / Generic OpenAI-Compatible
    """

    _providers: Dict[str, BaseLLMProvider] = {}
    _default_provider_name: str = "gemini"

    @classmethod
    def register(cls, name: str, provider: BaseLLMProvider, set_default: bool = False) -> None:
        cls._providers[name] = provider
        if set_default or not cls._default_provider_name:
            cls._default_provider_name = name
        logger.info(f"Registered LLM provider '{name}' ({provider.model_name}) - Available: {provider.is_available()}")

    @classmethod
    def get_provider(cls, name: Optional[str] = None) -> BaseLLMProvider:
        key = name or cls._default_provider_name
        if key not in cls._providers:
            cls._lazy_register(key)
        if key not in cls._providers:
            raise ValueError(f"LLM provider '{key}' not found in registry.")
        return cls._providers[key]

    @classmethod
    def get_default_provider(cls) -> BaseLLMProvider:
        return cls.get_provider(cls._default_provider_name)

    @classmethod
    def list_providers(cls) -> List[Dict[str, Any]]:
        return [
            {
                "name": name,
                "model": prov.model_name,
                "available": prov.is_available(),
                "supports_tools": prov.supports_tools,
                "supports_streaming": prov.supports_streaming,
                "is_default": (name == cls._default_provider_name),
            }
            for name, prov in cls._providers.items()
        ]

    @classmethod
    def _lazy_register(cls, name: str) -> None:
        if name == "gemini":
            cls.register("gemini", GeminiProvider(), set_default=(cls._default_provider_name == "gemini"))
        elif name == "openrouter":
            cls.register("openrouter", OpenRouterLLMProvider(
                api_key=settings.OPENROUTER_API_KEY,
                model_name=settings.OPENROUTER_MODEL,
                base_url=settings.OPENROUTER_BASE_URL
            ))
        elif name == "mistral":
            cls.register("mistral", MistralLLMProvider(
                api_key=settings.MISTRAL_API_KEY,
                model_name=settings.MISTRAL_MODEL,
                base_url=settings.MISTRAL_BASE_URL
            ))
        elif name == "xai":
            cls.register("xai", XAIGrokLLMProvider(
                api_key=settings.XAI_API_KEY,
                model_name=settings.XAI_MODEL,
                base_url=settings.XAI_BASE_URL
            ))
        elif name == "openai":
            cls.register("openai", GenericOpenAILLMProvider(
                api_key=settings.OPENAI_API_KEY,
                model_name=settings.OPENAI_MODEL,
                base_url=settings.OPENAI_BASE_URL
            ))


        elif name == "groq":
            cls.register("groq", GroqLLMProvider(
                api_key=settings.GROQ_API_KEY,
                model_name=settings.GROQ_MODEL,
                base_url=settings.GROQ_BASE_URL
            ))
        elif name == "bazaarlink":
            cls.register("bazaarlink", BazaarLinkLLMProvider(
                api_key=settings.BAZAARLINK_API_KEY,
                model_name=settings.BAZAARLINK_MODEL,
                base_url=settings.BAZAARLINK_BASE_URL
            ))
        elif name == "pekpik":
            cls.register("pekpik", PekpikLLMProvider(
                api_key=settings.PEKPIK_DEEPSEEK_API_KEY or settings.PEKPIK_GPT_API_KEY,
                model_name=settings.PEKPIK_MODEL,
                base_url=settings.PEKPIK_BASE_URL
            ))
        elif name == "aionlabs":
            cls.register("aionlabs", AionLabsLLMProvider(
                api_key=settings.AIONLABS_API_KEY,
                base_url=settings.AIONLABS_BASE_URL
            ))
        elif name == "cohere":
            cls.register("cohere", CohereLLMProvider(
                api_key=settings.COHERE_API_KEY,
                model_name=settings.COHERE_MODEL,
                base_url=settings.COHERE_BASE_URL
            ))


# Auto-register all providers on startup
ALL_PROVIDER_IDS = [
    "gemini",
    "bazaarlink",
    "pekpik",
    "groq",
    "openrouter",
    "cohere",
    "aionlabs",
    "mistral",
    "xai",
    "openai",
]
for provider_id in ALL_PROVIDER_IDS:
    try:
        LLMRegistry._lazy_register(provider_id)
    except Exception as e:
        logger.warning(f"Error initializing provider '{provider_id}': {e}")
