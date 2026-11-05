from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class AgentModelConfig(BaseModel):
    provider: str = Field(..., description="LLM provider: gemini, groq, bazaarlink, pekpik, openrouter, cohere, local")
    model_id: str = Field(..., description="Exact model identifier")
    temperature: float = Field(0.2, ge=0.0, le=1.0)
    max_output_tokens: int = Field(600, ge=100, le=4096)
    timeout_seconds: float = Field(15.0, ge=1.0, le=60.0)


class AgentBudget(BaseModel):
    max_input_tokens: int = Field(2000, description="Max input context length in tokens")
    max_output_tokens: int = Field(600, description="Max output tokens for this specialist")
    max_execution_time_seconds: float = Field(10.0, description="Timeout ceiling for agent execution")
    cost_tier: str = Field("free_tier", description="Budget tier: free_tier, standard, high_reasoning")


class AgentRetryPolicy(BaseModel):
    max_retries: int = Field(2, ge=0, le=5)
    backoff_factor: float = Field(0.5, ge=0.1, le=3.0)
    fallback_to_secondary: bool = Field(True, description="Failover to secondary provider on failure")


class AgentDefinition(BaseModel):
    id: str = Field(..., description="Unique agent slug: aegis, athena, themis, hermes, argus, mnemos, oracle, forge, vision")
    name: str = Field(..., description="Display title: e.g. AEGIS — Master Orchestrator")
    role: str = Field(..., description="Domain specialization summary")
    description: str = Field(..., description="User-facing concise description of capabilities")
    capabilities: List[str] = Field(default_factory=list, description="List of granular capability tags")
    system_instructions: str = Field(..., description="Specialist persona and institutional directives")
    allowed_tools: List[str] = Field(default_factory=list, description="Tool names this agent is authorized to call")
    knowledge_collections: List[str] = Field(default_factory=list, description="Target knowledge domains")
    primary_model: AgentModelConfig
    secondary_model: AgentModelConfig
    budget: AgentBudget
    retry_policy: AgentRetryPolicy = Field(default_factory=AgentRetryPolicy)
    permission_required: str = Field("public", description="public, authenticated_student, administrative")
    is_orchestrator: bool = Field(False)
    input_schema: Dict[str, Any] = Field(default_factory=dict)
    output_schema: Dict[str, Any] = Field(default_factory=dict)


class AgentPublicInfo(BaseModel):
    id: str
    name: str
    role: str
    description: str
    capabilities: List[str]
    is_orchestrator: bool
    permission_required: str


class AgentEngineInfo(BaseModel):
    agent_id: str
    agent_name: str
    actual_provider: str
    actual_model_id: str
    availability: bool
    last_health_check: str
    execution_mode: str
    cost_tier: str


class AgentExecutionPlan(BaseModel):
    query: str
    intent: str
    complexity: str  # simple, moderate, complex
    risk: str        # low, medium, high
    primary_agent: str
    specialist_agents: List[str] = []
    parallel_group: List[str] = []
    sequential_group: List[str] = []
    rationale: str


class AgentOutput(BaseModel):
    agent_id: str
    success: bool
    findings: str
    structured_data: Dict[str, Any] = Field(default_factory=dict)
    citations: List[Dict[str, Any]] = Field(default_factory=list)
    cards: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = 1.0
    latency_ms: int = 0
    tokens_used: int = 0
    model_used: str = ""
    provider_used: str = ""
    error: Optional[str] = None

