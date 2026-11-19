import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy import (
    Column,
    String,
    Boolean,
    Integer,
    Float,
    DateTime,
    Text,
    JSON,
    ForeignKey,
    Index,
)
from sqlalchemy.orm import relationship

from app.models.base import Base


class Provider(Base):
    """
    Model Provider registration (e.g. Gemini, Groq, OpenRouter, Mistral, Cohere).
    """
    __tablename__ = "providers"

    id = Column(String(64), primary_key=True)  # e.g. "gemini", "groq", "openrouter", "mistral", "cohere"
    name = Column(String(128), nullable=False)
    display_name = Column(String(128), nullable=False)
    api_base = Column(String(256), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    priority = Column(Integer, default=10, nullable=False)  # Lower is higher priority
    supported_tasks = Column(JSON, default=list)  # ["chat", "embedding", "rerank", "vision"]
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    models = relationship("ProviderModel", back_populates="provider", cascade="all, delete-orphan")


class ProviderModel(Base):
    """
    Specific model ID exposed by a provider with capabilities and pricing.
    """
    __tablename__ = "provider_models"

    id = Column(String(128), primary_key=True)  # e.g. "gemini::gemini-2.5-flash", "groq::llama-3.3-70b-versatile"
    provider_id = Column(String(64), ForeignKey("providers.id", ondelete="CASCADE"), nullable=False)
    model_id = Column(String(128), nullable=False)  # exact upstream identifier e.g. "gemini-2.5-flash"
    display_name = Column(String(128), nullable=False)
    context_window = Column(Integer, default=128000, nullable=False)
    max_output_tokens = Column(Integer, default=4096, nullable=False)
    supports_streaming = Column(Boolean, default=True, nullable=False)
    supports_tools = Column(Boolean, default=True, nullable=False)
    supports_vision = Column(Boolean, default=False, nullable=False)
    supports_structured_output = Column(Boolean, default=True, nullable=False)
    supports_reasoning = Column(Boolean, default=False, nullable=False)
    input_price_per_1m = Column(Float, default=0.0, nullable=False)  # USD per 1M tokens
    output_price_per_1m = Column(Float, default=0.0, nullable=False)  # USD per 1M tokens
    latency_tier = Column(String(32), default="fast")  # ultra_fast, fast, medium, slow
    quality_benchmark = Column(Float, default=85.0)  # 0.0 - 100.0 score
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    provider = relationship("Provider", back_populates="models")
    capabilities = relationship("ModelCapability", back_populates="model", cascade="all, delete-orphan")


class ModelCapability(Base):
    """
    Granular capability tagging and benchmarks per model.
    """
    __tablename__ = "model_capabilities"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    model_id = Column(String(128), ForeignKey("provider_models.id", ondelete="CASCADE"), nullable=False)
    capability_name = Column(String(64), nullable=False)  # reasoning, coding, fast_chat, multilingual, search_synthesis
    benchmark_score = Column(Float, default=80.0)

    model = relationship("ProviderModel", back_populates="capabilities")


class IntelligenceProfile(Base):
    """
    The 4 proprietary intelligence identities: NOVA, THEMIS, ATHENA, ORACLE.
    """
    __tablename__ = "intelligence_profiles"

    id = Column(String(64), primary_key=True)  # "nova", "themis", "athena", "oracle"
    name = Column(String(128), nullable=False)
    title = Column(String(128), nullable=False)
    domain_description = Column(Text, nullable=False)
    voice_and_tone = Column(Text, nullable=False)
    default_thinking_level = Column(String(32), default="Balanced", nullable=False)
    allowed_subagents = Column(JSON, default=list)  # ["argus", "hermes", "forge", "vision", "mnemos"]
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    prompt_versions = relationship("IntelligencePromptVersion", back_populates="intelligence", cascade="all, delete-orphan")
    routing_policies = relationship("IntelligenceRoutingPolicy", back_populates="intelligence", cascade="all, delete-orphan")


class IntelligencePromptVersion(Base):
    """
    Versioned system instructions and instruction hierarchy stored independently of code.
    """
    __tablename__ = "intelligence_prompt_versions"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    intelligence_id = Column(String(64), ForeignKey("intelligence_profiles.id", ondelete="CASCADE"), nullable=False)
    version = Column(Integer, default=1, nullable=False)
    system_prompt = Column(Text, nullable=False)
    instruction_hierarchy = Column(JSON, default=dict)  # structured layers of constraints & instructions
    changelog = Column(Text, default="Initial release")
    is_active = Column(Boolean, default=True, nullable=False)
    created_by = Column(String(64), default="system")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    intelligence = relationship("IntelligenceProfile", back_populates="prompt_versions")


class IntelligenceRoutingPolicy(Base):
    """
    Configurable routing policy and budget per intelligence.
    """
    __tablename__ = "intelligence_routing_policies"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    intelligence_id = Column(String(64), ForeignKey("intelligence_profiles.id", ondelete="CASCADE"), nullable=False)
    thinking_level = Column(String(32), default="Balanced", nullable=False)  # "Low", "Balanced", "High"
    primary_capability = Column(String(64), nullable=False)
    preferred_providers = Column(JSON, default=list)  # ["gemini", "groq", "openrouter"]
    max_calls_per_turn = Column(Integer, default=2)
    max_input_tokens = Column(Integer, default=3000)
    max_output_tokens = Column(Integer, default=800)
    max_cost_usd_per_request = Column(Float, default=0.01)
    max_parallel_agents = Column(Integer, default=2)
    max_retries = Column(Integer, default=2)
    requires_verification = Column(Boolean, default=True)
    fallback_chain = Column(JSON, default=list)

    intelligence = relationship("IntelligenceProfile", back_populates="routing_policies")


class RoutingDecision(Base):
    """
    Observability ledger recording every dynamic model routing event.
    """
    __tablename__ = "routing_decisions"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    request_id = Column(String(64), nullable=False, index=True)
    intelligence_id = Column(String(64), nullable=False, index=True)
    subtask_name = Column(String(128), nullable=False)  # e.g. "intent_planning", "technical_synthesis", "grounding_verification"
    selected_provider = Column(String(64), nullable=False)
    selected_model = Column(String(128), nullable=False)
    rationale = Column(Text, nullable=False)
    latency_ms = Column(Integer, default=0)
    cost_usd = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class AgentExecution(Base):
    """
    Subagent execution record (ARGUS, HERMES, FORGE, VISION, MNEMOS).
    """
    __tablename__ = "agent_executions"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    request_id = Column(String(64), nullable=False, index=True)
    parent_intelligence = Column(String(64), nullable=False)  # NOVA, THEMIS, ATHENA, ORACLE, AEGIS
    agent_name = Column(String(64), nullable=False)  # ARGUS, HERMES, FORGE, VISION, MNEMOS
    status = Column(String(32), default="completed")  # running, completed, failed
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    latency_ms = Column(Integer, default=0)
    findings = Column(Text, nullable=True)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class ToolExecution(Base):
    """
    Detailed tool execution logging.
    """
    __tablename__ = "tool_executions"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    execution_id = Column(String(64), nullable=False, index=True)
    tool_name = Column(String(64), nullable=False)
    status = Column(String(32), default="success")  # success, error, fallback
    input_args = Column(JSON, default=dict)
    output_preview = Column(Text, nullable=True)
    latency_ms = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class ModelUsage(Base):
    """
    Per-call token consumption tracking.
    """
    __tablename__ = "model_usage"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(64), nullable=True, index=True)
    user_identifier = Column(String(128), nullable=True, index=True)
    intelligence_id = Column(String(64), nullable=False, index=True)
    provider = Column(String(64), nullable=False)
    model_id = Column(String(128), nullable=False)
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    latency_ms = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class ModelCost(Base):
    """
    Financial cost attribution per call and intelligence.
    """
    __tablename__ = "model_costs"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    usage_id = Column(String(64), nullable=True)
    intelligence_id = Column(String(64), nullable=False, index=True)
    provider = Column(String(64), nullable=False)
    model_id = Column(String(128), nullable=False)
    cost_usd = Column(Float, default=0.0, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class UserAIQuota(Base):
    """
    Daily quota enforcement per student/session.
    """
    __tablename__ = "user_ai_quotas"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_identifier = Column(String(128), nullable=False, unique=True, index=True)
    daily_token_budget = Column(Integer, default=50000, nullable=False)
    tokens_used_today = Column(Integer, default=0, nullable=False)
    daily_cost_limit_usd = Column(Float, default=0.50, nullable=False)
    cost_incurred_today = Column(Float, default=0.0, nullable=False)
    reset_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class ProviderHealth(Base):
    """
    Real-time health, latency, and circuit breaker status per provider/model.
    """
    __tablename__ = "provider_health"

    id = Column(String(128), primary_key=True)  # e.g. "gemini::gemini-2.5-flash"
    provider = Column(String(64), nullable=False)
    model_id = Column(String(128), nullable=False)
    is_healthy = Column(Boolean, default=True, nullable=False)
    error_count = Column(Integer, default=0)
    consecutive_failures = Column(Integer, default=0)
    circuit_state = Column(String(32), default="closed")  # closed, open, half_open
    avg_latency_ms = Column(Float, default=150.0)
    last_check_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    last_error_message = Column(Text, nullable=True)


class EvaluationRun(Base):
    """
    Domain-specific evaluation runs measuring intelligence performance.
    """
    __tablename__ = "evaluation_runs"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    run_name = Column(String(128), nullable=False)
    intelligence_id = Column(String(64), nullable=False, index=True)
    status = Column(String(32), default="completed")  # running, completed, failed
    total_cases = Column(Integer, default=0)
    passed_cases = Column(Integer, default=0)
    avg_score = Column(Float, default=0.0)  # 0 - 100
    avg_latency_ms = Column(Float, default=0.0)
    total_cost_usd = Column(Float, default=0.0)
    started_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    results = relationship("EvaluationResult", back_populates="run", cascade="all, delete-orphan")


class EvaluationResult(Base):
    """
    Individual test case result within an evaluation run.
    """
    __tablename__ = "evaluation_results"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id = Column(String(64), ForeignKey("evaluation_runs.id", ondelete="CASCADE"), nullable=False)
    test_case_id = Column(String(64), nullable=False)
    prompt = Column(Text, nullable=False)
    expected_behavior = Column(Text, nullable=False)
    actual_output = Column(Text, nullable=True)
    score = Column(Float, default=0.0)
    is_pass = Column(Boolean, default=True)
    latency_ms = Column(Integer, default=0)
    cost_usd = Column(Float, default=0.0)
    metric_breakdown = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    run = relationship("EvaluationRun", back_populates="results")

