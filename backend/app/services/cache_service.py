import time
import hashlib
import re
import logging
from typing import Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)


class QueryResponseCache:
    """
    High-performance in-memory semantic & query response cache.
    Prevents duplicate LLM invocations and free-tier quota exhaustion.
    Stores cached responses with TTL (Time-To-Live).
    """

    _cache: Dict[str, Dict[str, Any]] = {}
    DEFAULT_TTL_SECONDS = 7200  # 2 Hours

    @classmethod
    def _normalize_query(cls, query: str) -> str:
        """Normalizes query text to maximize cache hit rate on equivalent questions."""
        q = query.lower().strip()
        # Remove extra punctuation and whitespace
        q = re.sub(r"[^\w\s]", " ", q)
        q = re.sub(r"\s+", " ", q).strip()
        return q

    @classmethod
    def make_cache_key(cls, query: str, context_prefix: str = "") -> str:
        norm = cls._normalize_query(query)
        raw = f"{context_prefix}:{norm}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    @classmethod
    def get(cls, query: str, context_prefix: str = "") -> Optional[Dict[str, Any]]:
        key = cls.make_cache_key(query, context_prefix)
        entry = cls._cache.get(key)
        if not entry:
            return None

        # Check TTL
        now = time.time()
        if now - entry["cached_at"] > entry["ttl"]:
            del cls._cache[key]
            return None

        logger.info(f"Cache HIT for query: '{query[:40]}...' (0 LLM cost)")
        return entry["data"]

    @classmethod
    def set(
        cls,
        query: str,
        response_data: Dict[str, Any],
        context_prefix: str = "",
        ttl_seconds: Optional[int] = None
    ) -> None:
        key = cls.make_cache_key(query, context_prefix)
        # Cap cache size at 1000 items (FIFO eviction)
        if len(cls._cache) > 1000:
            oldest_key = min(cls._cache.keys(), key=lambda k: cls._cache[k]["cached_at"])
            del cls._cache[oldest_key]

        cls._cache[key] = {
            "cached_at": time.time(),
            "ttl": ttl_seconds or cls.DEFAULT_TTL_SECONDS,
            "data": response_data
        }

    @classmethod
    def clear(cls) -> None:
        cls._cache.clear()


class ToolCache:
    """
    In-memory caching for external tool APIs (Open-Meteo, Geoapify, Startup.Jobs, Tavily).
    Ensures free-tier API quotas are preserved and network calls are minimized.
    """

    _tool_cache: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def get(cls, tool_name: str, cache_key: str) -> Optional[Any]:
        composite_key = f"{tool_name}:{cache_key}"
        entry = cls._tool_cache.get(composite_key)
        if not entry:
            return None

        if time.time() - entry["cached_at"] > entry["ttl"]:
            del cls._tool_cache[composite_key]
            return None

        return entry["data"]

    @classmethod
    def set(cls, tool_name: str, cache_key: str, data: Any, ttl_seconds: int = 1800) -> None:
        composite_key = f"{tool_name}:{cache_key}"
        cls._tool_cache[composite_key] = {
            "cached_at": time.time(),
            "ttl": ttl_seconds,
            "data": data
        }


class FreeTierBudgetManager:
    """
    Proactively manages free-tier rate limits (RPM / RPD) across all registered providers.
    Soft-throttles a provider when approaching RPM ceiling to avoid HTTP 429 exhaustion.
    """

    # Provider RPM safety thresholds (80% of published free-tier caps)
    PROVIDER_RPM_LIMITS = {
        "gemini": 12,       # Free tier cap is 15 RPM
        "groq": 25,         # Free tier cap is 30 RPM
        "bazaarlink": 15,   # Free tier cap is 20 RPM
        "pekpik": 15,       # Free tier cap is 20 RPM
        "openrouter": 15,   # Free tier cap is 20 RPM
        "cohere": 8,        # Free trial cap is 10 RPM
    }

    _request_log: Dict[str, list] = {}

    @classmethod
    def is_provider_safe(cls, provider_name: str) -> bool:
        """
        Returns True if the provider is currently within safe RPM bounds.
        If near the RPM threshold, returns False so the router shifts to the next tier.
        """
        now = time.time()
        window = 60.0  # 1 minute

        timestamps = cls._request_log.get(provider_name, [])
        # Prune older than 60s
        timestamps = [t for t in timestamps if now - t < window]
        cls._request_log[provider_name] = timestamps

        limit = cls.PROVIDER_RPM_LIMITS.get(provider_name.lower(), 15)
        if len(timestamps) >= limit:
            logger.warning(
                f"Provider '{provider_name}' approaching free-tier limit ({len(timestamps)}/{limit} RPM). "
                f"Soft-shifting to secondary provider to preserve quota."
            )
            return False
        return True

    @classmethod
    def record_call(cls, provider_name: str) -> None:
        now = time.time()
        timestamps = cls._request_log.get(provider_name, [])
        timestamps.append(now)
        cls._request_log[provider_name] = timestamps

