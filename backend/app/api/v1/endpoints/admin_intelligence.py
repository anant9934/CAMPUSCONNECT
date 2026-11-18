import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.ai.shared_provider_registry import SharedProviderRegistry, ProviderModelDescriptor, ModelCapabilities, TokenPricing
from app.ai.cost_controller import CostController, INTELLIGENCE_BUDGETS
from app.intelligence.identity_engine import IdentityEngine
from app.intelligence.evaluation_engine import EvaluationEngine
from app.intelligence.intelligence_system import IntelligenceSystem

logger = logging.getLogger(__name__)
router = APIRouter()


class UpdateModelCapabilityPayload(BaseModel):
    provider_name: str
    model_id: str
    is_available: Optional[bool] = None
    input_price_per_1m: Optional[float] = None
    output_price_per_1m: Optional[float] = None
    latency_tier: Optional[str] = None
    timeout_seconds: Optional[float] = None


class UpdateBudgetPayload(BaseModel):
    intelligence_id: str
    max_calls_per_turn: Optional[int] = None
    max_input_tokens: Optional[int] = None
    max_output_tokens: Optional[int] = None
    max_request_cost_usd: Optional[float] = None
    max_parallel_agents: Optional[int] = None


@router.get("/providers", tags=["admin-intelligence"])
async def list_providers_and_models():
    """
    Returns registered models, health states, pricing, and capabilities across all providers.
    Never exposes API secrets.
    """
    models = SharedProviderRegistry.list_models(active_only=False)
    return [m.model_dump() for m in models]


@router.post("/providers/configure", tags=["admin-intelligence"])
async def configure_model_settings(payload: UpdateModelCapabilityPayload):
    """
    Updates model capabilities, availability, pricing, or latency tier.
    """
    model = SharedProviderRegistry.get_model(payload.provider_name, payload.model_id)
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Model {payload.provider_name}::{payload.model_id} not found."
        )

    if payload.is_available is not None:
        model.is_available = payload.is_available
    if payload.input_price_per_1m is not None:
        model.pricing.input_usd_per_1m = payload.input_price_per_1m
    if payload.output_price_per_1m is not None:
        model.pricing.output_usd_per_1m = payload.output_price_per_1m
    if payload.latency_tier is not None:
        model.latency_tier = payload.latency_tier
    if payload.timeout_seconds is not None:
        model.timeout_seconds = payload.timeout_seconds

    return {
        "status": "success",
        "message": f"Updated {payload.provider_name}::{payload.model_id} successfully.",
        "model": model.model_dump()
    }


@router.get("/costs", tags=["admin-intelligence"])
async def get_cost_and_usage_attribution():
    """
    Returns cost attribution, token consumption, and call counts by intelligence identity.
    """
    return {
        "attribution_by_intelligence": CostController.get_attribution_summary(),
        "configured_budgets": {
            intel: {
                "max_calls_per_turn": b.max_calls_per_turn,
                "max_input_tokens": b.max_input_tokens,
                "max_output_tokens": b.max_output_tokens,
                "max_request_cost_usd": b.max_request_cost_usd,
                "max_parallel_agents": b.max_parallel_agents,
                "daily_user_quota_tokens": b.daily_user_quota_tokens,
            }
            for intel, b in INTELLIGENCE_BUDGETS.items()
        }
    }


@router.post("/budgets/configure", tags=["admin-intelligence"])
async def configure_intelligence_budget(payload: UpdateBudgetPayload):
    """
    Configures resource ceilings and cost limits per intelligence identity.
    """
    budget = CostController.get_budget(payload.intelligence_id)
    if payload.max_calls_per_turn is not None:
        budget.max_calls_per_turn = payload.max_calls_per_turn
    if payload.max_input_tokens is not None:
        budget.max_input_tokens = payload.max_input_tokens
    if payload.max_output_tokens is not None:
        budget.max_output_tokens = payload.max_output_tokens
    if payload.max_request_cost_usd is not None:
        budget.max_request_cost_usd = payload.max_request_cost_usd
    if payload.max_parallel_agents is not None:
        budget.max_parallel_agents = payload.max_parallel_agents

    return {
        "status": "success",
        "intelligence_id": payload.intelligence_id,
        "updated_budget": budget.__dict__
    }


@router.get("/identities", tags=["admin-intelligence"])
async def list_intelligence_identities():
    """
    Lists the 4 proprietary intelligence identities (NOVA, THEMIS, ATHENA, ORACLE)
    and their active prompt configurations.
    """
    return [
        {
            "id": ident.id,
            "name": ident.name,
            "subtitle": ident.subtitle,
            "role": ident.role,
            "voice_and_tone": ident.voice_and_tone,
            "default_thinking_level": ident.default_thinking_level,
            "allowed_subagents": ident.allowed_subagents,
            "prompt_length_chars": len(ident.master_system_prompt),
        }
        for ident in IdentityEngine.list_identities()
    ]


@router.post("/evaluations/run/{intelligence_id}", tags=["admin-intelligence"])
async def run_domain_evaluation(intelligence_id: str):
    """
    Triggers domain-specific benchmark evaluation suite measuring correctness,
    latency, token consumption, and cost across test cases.
    """
    async def invoke_fn(query: str, intelligence_id: str, thinking_level: str):
        res = await IntelligenceSystem.process_turn(
            query=query,
            selected_intelligence=intelligence_id,
            thinking_level=thinking_level
        )
        return {
            "content": res.content,
            "cost_usd": res.cost_usd,
            "latency_ms": res.latency_ms
        }

    summary = await EvaluationEngine.run_benchmark_for_intelligence(
        intelligence_id=intelligence_id,
        system_invoker_fn=invoke_fn
    )
    return summary
