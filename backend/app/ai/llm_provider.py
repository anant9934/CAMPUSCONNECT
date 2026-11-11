from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, AsyncGenerator


class BaseLLMProvider(ABC):
    """
    Abstract Base Class for Real LLM Providers in CampusConnect.
    Enforces server-side execution, streaming support, and usage tracking.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Identifier name of the LLM provider (e.g. 'gemini', 'groq', 'mock')."""
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Model identifier (e.g. 'gemini-2.5-flash', 'gemini-1.5-flash')."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Returns True if the provider is properly configured and healthy."""
        pass

    @property
    def supports_tools(self) -> bool:
        """Indicates whether this provider supports function calling."""
        return True

    @property
    def supports_streaming(self) -> bool:
        """Indicates whether this provider supports streaming output."""
        return True

    async def health_check(self) -> Dict[str, Any]:
        """Performs a lightweight health check of provider availability."""
        return {
            "provider": self.provider_name,
            "model": self.model_name,
            "available": self.is_available(),
            "supports_tools": self.supports_tools,
            "supports_streaming": self.supports_streaming,
        }

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_instruction: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        temperature: float = 0.2,
        max_output_tokens: int = 1024,
    ) -> Dict[str, Any]:
        """
        Generate a complete response using the real LLM.
        Returns dict with:
        - content: str
        - prompt_tokens: int
        - completion_tokens: int
        - total_tokens: int
        - latency_ms: int
        - model: str
        - finish_reason: str
        """
        pass

    @abstractmethod
    async def generate_stream(
        self,
        prompt: str,
        system_instruction: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        temperature: float = 0.2,
        max_output_tokens: int = 1024,
    ) -> AsyncGenerator[str, None]:
        """
        Yields tokens incrementally as they are produced by the LLM.
        """
        pass
