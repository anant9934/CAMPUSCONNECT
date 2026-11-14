from typing import List
from fastapi import APIRouter, HTTPException, status

from app.schemas.agent import AgentPublicInfo, AgentEngineInfo, AgentDefinition
from app.agents.agent_registry import AgentRegistry

router = APIRouter()


@router.get("", response_model=List[AgentPublicInfo], tags=["multi-agent"])
async def list_available_agents():
    """
    Returns list of named specialist agents in CampusConnect Multi-Agent Intelligence Network V1:
    AEGIS, ATHENA, THEMIS, HERMES, ARGUS, MNEMOS, ORACLE, FORGE, VISION.
    """
    return AgentRegistry.list_public_agents()


@router.get("/diagnostics", response_model=List[AgentEngineInfo], tags=["multi-agent"])
async def get_agent_engine_diagnostics():
    """
    Expandable Engine Information for Settings modal:
    Shows actual provider, actual model ID, availability, health check, and execution mode per agent.
    """
    return AgentRegistry.get_engine_diagnostics()


@router.get("/{agent_id}", response_model=AgentDefinition, tags=["multi-agent"])
async def get_agent_details(agent_id: str):
    """
    Returns granular configuration, tools, and budget parameters for a specific agent.
    """
    agent = AgentRegistry.get_agent(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent '{agent_id}' not found in registry."
        )
    return agent

