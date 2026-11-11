from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ModelCapability:
    model_id: str
    provider: str
    display_name: str
    context_window: int
    supports_tools: bool = True
    supports_streaming: bool = True
    supports_structured_output: bool = True
    is_free_tier: bool = False
    speed_tier: str = "balanced"  # "fast", "balanced", "deep"
    cost_per_1m_input_usd: float = 0.0
    cost_per_1m_output_usd: float = 0.0
    recommended_tasks: List[str] = field(default_factory=list)


class ModelCapabilityRegistry:
    """
    Central registry of model capabilities, context limits, and routing recommendations.
    Enforces that high-complexity student queries (e.g. multi-step academic benefits, disciplinary appeals)
    route to capable models, while fast lookups use low-latency models.
    """

    _MODELS: Dict[str, ModelCapability] = {
        # Google Gemini
        "gemini-2.5-flash": ModelCapability(
            model_id="gemini-2.5-flash",
            provider="gemini",
            display_name="Gemini 2.5 Flash (Free Tier)",
            context_window=1000000,
            supports_tools=True,
            supports_streaming=True,
            supports_structured_output=True,
            is_free_tier=True,
            speed_tier="fast",
            cost_per_1m_input_usd=0.0,
            cost_per_1m_output_usd=0.0,
            recommended_tasks=["general_qa", "food_search", "places", "quick_guidance", "people_lookup"],
        ),
        "gemini-2.5-pro": ModelCapability(
            model_id="gemini-2.5-pro",
            provider="gemini",
            display_name="Gemini 2.5 Pro (Deep Reasoning)",
            context_window=2000000,
            supports_tools=True,
            supports_streaming=True,
            supports_structured_output=True,
            is_free_tier=True,
            speed_tier="deep",
            cost_per_1m_input_usd=0.0,
            cost_per_1m_output_usd=0.0,
            recommended_tasks=["complex_benefits", "attendance_solver", "appeals", "multi_turn_assessment"],
        ),
        # OpenRouter
        "meta-llama/llama-3.3-70b-instruct:free": ModelCapability(
            model_id="meta-llama/llama-3.3-70b-instruct:free",
            provider="openrouter",
            display_name="Llama 3.3 70B Instruct (Free)",
            context_window=131072,
            supports_tools=True,
            supports_streaming=True,
            supports_structured_output=True,
            is_free_tier=True,
            speed_tier="balanced",
            cost_per_1m_input_usd=0.0,
            cost_per_1m_output_usd=0.0,
            recommended_tasks=["general_qa", "attendance_solver", "project_mapping"],
        ),
        # Mistral
        "mistral-small-latest": ModelCapability(
            model_id="mistral-small-latest",
            provider="mistral",
            display_name="Mistral Small Latest",
            context_window=32768,
            supports_tools=True,
            supports_streaming=True,
            supports_structured_output=True,
            is_free_tier=False,
            speed_tier="fast",
            cost_per_1m_input_usd=0.20,
            cost_per_1m_output_usd=0.60,
            recommended_tasks=["general_qa", "ums_search", "quick_lookup"],
        ),
        # xAI Grok
        "grok-beta": ModelCapability(
            model_id="grok-beta",
            provider="xai",
            display_name="xAI Grok Beta",
            context_window=131072,
            supports_tools=True,
            supports_streaming=True,
            supports_structured_output=True,
            is_free_tier=False,
            speed_tier="balanced",
            cost_per_1m_input_usd=5.0,
            cost_per_1m_output_usd=15.0,
            recommended_tasks=["complex_dialogue", "real_time_reasoning"],
        ),
        # Generic OpenAI
        "gpt-4o-mini": ModelCapability(
            model_id="gpt-4o-mini",
            provider="openai",
            display_name="OpenAI GPT-4o Mini",
            context_window=128000,
            supports_tools=True,
            supports_streaming=True,
            supports_structured_output=True,
            is_free_tier=False,
            speed_tier="fast",
            cost_per_1m_input_usd=0.15,
            cost_per_1m_output_usd=0.60,
            recommended_tasks=["general_qa", "benefit_assessment"],
        ),
    }

    @classmethod
    def get_capability(cls, model_id: str) -> Optional[ModelCapability]:
        return cls._MODELS.get(model_id)

    @classmethod
    def list_all_models(cls) -> List[ModelCapability]:
        return list(cls._MODELS.values())

    @classmethod
    def list_free_tier_models(cls) -> List[ModelCapability]:
        return [m for m in cls._MODELS.values() if m.is_free_tier]

    @classmethod
    def register_model(cls, capability: ModelCapability) -> None:
        cls._MODELS[capability.model_id] = capability

