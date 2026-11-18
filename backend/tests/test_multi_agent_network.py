import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.agents.agent_registry import AgentRegistry
from app.agents.aegis_orchestrator import AEGISOrchestrator
from app.agents.specialists.themis_agent import ThemisAgent
from app.agents.specialists.hermes_agent import HermesAgent
from app.agents.specialists.argus_agent import ArgusAgent
from app.agents.specialists.athena_agent import AthenaAgent
from app.agents.specialists.mnemos_agent import MnemosAgent
from app.agents.specialists.oracle_agent import OracleAgent
from app.agents.specialists.forge_agent import ForgeAgent
from app.agents.specialists.vision_agent import VisionAgent
from app.core.database import AsyncSessionLocal


@pytest.fixture(autouse=True)
def setup_registry():
    AgentRegistry.initialize()


@pytest.mark.asyncio
async def test_agent_registry_initialization():
    """Verify all 9 agents are properly registered with complete specifications."""
    agents = AgentRegistry.list_agents()
    agent_ids = {a.id for a in agents}
    expected_ids = {"aegis", "themis", "hermes", "argus", "athena", "mnemos", "oracle", "forge", "vision"}
    
    assert expected_ids.issubset(agent_ids), f"Missing agents in registry: {expected_ids - agent_ids}"
    
    # Check specific attributes
    aegis = AgentRegistry.get_agent("aegis")
    assert aegis is not None
    assert aegis.is_orchestrator is True
    assert "parallel_agent_orchestration" in aegis.capabilities

    themis = AgentRegistry.get_agent("themis")
    assert themis is not None
    assert "attendance_condonation_analysis" in themis.capabilities
    assert themis.budget.max_output_tokens == 600

    hermes = AgentRegistry.get_agent("hermes")
    assert hermes is not None
    assert "ums_234_service_catalog_resolution" in hermes.capabilities

    argus = AgentRegistry.get_agent("argus")
    assert argus is not None
    assert "pure_veg_dining_discovery" in argus.capabilities


@pytest.mark.asyncio
async def test_themis_agent_independent_execution():
    """Verify THEMIS evaluates attendance policies and limits correctly."""
    themis = ThemisAgent()
    async with AsyncSessionLocal() as session:
        output = await themis.execute(
            query="my attendance is 68% can I get condonation?",
            context={},
            db=session
        )
        assert output.success is True
        assert output.agent_id == "themis"
        assert "75% attendance" in output.findings or "65%" in output.findings
        assert "Proctorial Board" in output.findings or "Section 12" in output.findings


@pytest.mark.asyncio
async def test_hermes_agent_independent_execution():
    """Verify HERMES resolves UMS breadcrumbs and intercepts transactions."""
    hermes = HermesAgent()
    async with AsyncSessionLocal() as session:
        # Test 1: Navigation resolution
        output_nav = await hermes.execute(
            query="how to apply for hostel leave",
            context={},
            db=session
        )
        assert output_nav.success is True
        assert "nav_card" in output_nav.cards or "Hostel" in output_nav.findings

        # Test 2: Transaction security intercept
        output_pay = await hermes.execute(
            query="pay my pending hostel fee now",
            context={},
            db=session
        )
        assert output_pay.success is True
        assert "Security Policy Boundary" in output_pay.findings or "cannot directly execute" in output_pay.findings


@pytest.mark.asyncio
async def test_argus_agent_independent_execution():
    """Verify ARGUS discovers faculty seating and consultation hours."""
    argus = ArgusAgent()
    async with AsyncSessionLocal() as session:
        output = await argus.execute(
            query="who is Dr Mohit Arora and where is his office?",
            context={},
            db=session
        )
        assert output.success is True
        assert output.agent_id == "argus"
        assert "Mohit Arora" in output.findings
        assert "3:00 PM – 5:00 PM" in output.findings or "Block 32" in output.findings


@pytest.mark.asyncio
async def test_athena_agent_independent_execution():
    """Verify ATHENA provides academic reasoning on exams and backlog rules."""
    athena = AthenaAgent()
    async with AsyncSessionLocal() as session:
        output = await athena.execute(
            query="what is the policy for re-appear exams and course equivalence?",
            context={},
            db=session
        )
        assert output.success is True
        assert output.agent_id == "athena"
        assert "Re-appear" in output.findings or "Backlog" in output.findings


@pytest.mark.asyncio
async def test_mnemos_agent_independent_execution():
    """Verify MNEMOS executes hybrid knowledge retrieval."""
    mnemos = MnemosAgent()
    async with AsyncSessionLocal() as session:
        output = await mnemos.execute(
            query="what is the passing marks criteria?",
            context={},
            db=session
        )
        assert output.success is True
        assert output.agent_id == "mnemos"
        assert len(output.findings) > 0


@pytest.mark.asyncio
async def test_oracle_agent_independent_execution():
    """Verify ORACLE handles research and scores source domains."""
    oracle = OracleAgent()
    async with AsyncSessionLocal() as session:
        output = await oracle.execute(
            query="what is Smart India Hackathon participation guidelines for LPU?",
            context={},
            db=session
        )
        assert output.success is True
        assert output.agent_id == "oracle"
        assert len(output.citations) > 0


@pytest.mark.asyncio
async def test_forge_agent_independent_execution():
    """Verify FORGE audits tech stack and finds startup opportunities."""
    forge = ForgeAgent()
    async with AsyncSessionLocal() as session:
        output = await forge.execute(
            query="AI full-stack internship and python project evaluation",
            context={},
            db=session
        )
        assert output.success is True
        assert output.agent_id == "forge"
        assert "Technical Project Evaluation" in output.findings


@pytest.mark.asyncio
async def test_vision_agent_independent_execution():
    """Verify VISION handles document extraction context."""
    vision = VisionAgent()
    async with AsyncSessionLocal() as session:
        output = await vision.execute(
            query="analyze grade sheet error",
            context={"uploaded_doc_name": "marks_card.pdf", "extracted_text": "Error in registration"},
            db=session
        )
        assert output.success is True
        assert output.agent_id == "vision"
        assert "marks_card.pdf" in output.findings


@pytest.mark.asyncio
async def test_aegis_routing_plans():
    """Verify AEGIS accurately routes different student intents to specific specialist teams."""
    # 1. Attendance -> THEMIS + MNEMOS
    plan_att = AEGISOrchestrator.plan_routing("my attendance is 64% can I write exams?")
    assert "themis" in plan_att.specialist_agents
    assert "mnemos" in plan_att.specialist_agents

    # 2. EDU-Rev Project -> THEMIS + ATHENA + MNEMOS
    plan_proj = AEGISOrchestrator.plan_routing("I built an AI project, can I get academic benefit under edurev?")
    assert "themis" in plan_proj.specialist_agents
    assert "athena" in plan_proj.specialist_agents

    # 3. Faculty Seating -> ARGUS
    plan_fac = AEGISOrchestrator.plan_routing("where is Dr Dalwinder Singh cabin?")
    assert "argus" in plan_fac.specialist_agents

    # 4. UMS Navigation -> HERMES
    plan_ums = AEGISOrchestrator.plan_routing("how to apply for hostel leave on ums?")
    assert "hermes" in plan_ums.specialist_agents

    # 5. SIH Hackathon -> ORACLE + ATHENA
    plan_sih = AEGISOrchestrator.plan_routing("what are external sih hackathon rules?")
    assert "oracle" in plan_sih.specialist_agents

    # 6. Coding / Tech -> FORGE + THEMIS
    plan_code = AEGISOrchestrator.plan_routing("review my react and fastapi coding project for startup revenue")
    assert "forge" in plan_code.specialist_agents


@pytest.mark.asyncio
async def test_aegis_multi_agent_coordinated_turn():
    """Verify AEGIS coordinates multiple specialists concurrently and synthesizes a unified turn."""
    async with AsyncSessionLocal() as session:
        result = await AEGISOrchestrator.orchestrate_turn(
            query="I have 68% attendance but I built a live revenue startup project. What can I do?",
            conversation_history=[],
            db=session,
            session_token="test_sess_multi_agent_001",
            explicit_agent_id="aegis"
        )
        assert result is not None
        assert result["agent_id"] == "aegis"
        assert len(result["specialists_involved"]) >= 2
        assert "themis" in result["specialists_involved"]
        assert len(result["thinking_steps"]) >= 4
        assert len(result["content"]) > 50


@pytest.mark.asyncio
async def test_api_agents_endpoints():
    """Verify API endpoints for agent listing and engine diagnostics."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # 1. List available agents
        res = await ac.get("/api/v1/agents")
        assert res.status_code == 200
        data = res.json()
        assert len(data) == 8
        names = [a["id"] for a in data]
        assert "aegis" in names
        assert "nova" in names
        assert "athena" in names
        assert "themis" in names
        assert "hermes" in names
        assert "oracle" in names
        assert "forge" in names
        assert "vision" in names

        # 2. Get engine diagnostics
        diag_res = await ac.get("/api/v1/agents/diagnostics")
        assert diag_res.status_code == 200
        diag_data = diag_res.json()
        assert len(diag_data) >= 8
        for item in diag_data:
            assert "actual_provider" in item
            assert "actual_model_id" in item
            assert "last_health_check" in item
            assert "execution_mode" in item

        # 3. Get single agent details
        themis_res = await ac.get("/api/v1/agents/themis")
        assert themis_res.status_code == 200
        themis_data = themis_res.json()
        assert themis_data["id"] == "themis"
        assert "THEMIS" in themis_data["name"]
        assert themis_data["budget"]["max_output_tokens"] == 600

