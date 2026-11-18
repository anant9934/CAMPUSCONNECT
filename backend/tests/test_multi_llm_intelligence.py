import pytest
import pytest_asyncio
from typing import Dict, Any
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.intelligence.identity_engine import IdentityEngine
from app.intelligence.intent_engine import IntentEngine
from app.intelligence.planning_engine import PlanningEngine
from app.intelligence.verification_engine import VerificationEngine
from app.intelligence.intelligence_system import IntelligenceSystem
from app.intelligence.evaluation_engine import EvaluationEngine
from app.ai.shared_provider_registry import SharedProviderRegistry
from app.ai.cost_controller import CostController, IntelligenceBudgetConfig
from app.ai.model_router import ModelRouter


class TestIdentityEngine:
    def test_four_core_identities_exist(self):
        identities = IdentityEngine.list_identities()
        id_keys = [i.id for i in identities]
        assert "nova" in id_keys
        assert "themis" in id_keys
        assert "athena" in id_keys
        assert "oracle" in id_keys

    def test_themis_identity_specifications(self):
        themis = IdentityEngine.get_identity("themis")
        assert themis.name == "THEMIS"
        assert "University" in themis.subtitle
        assert "attendance" in themis.master_system_prompt.lower()
        assert "65%" in themis.master_system_prompt
        assert "hermes" in themis.allowed_subagents

    def test_athena_identity_specifications(self):
        athena = IdentityEngine.get_identity("athena")
        assert athena.name == "ATHENA"
        assert "Advanced" in athena.subtitle
        assert athena.default_thinking_level == "High"
        assert "forge" in athena.allowed_subagents

    def test_nova_identity_specifications(self):
        nova = IdentityEngine.get_identity("nova")
        assert nova.name == "NOVA"
        assert "Everyday" in nova.subtitle
        assert "hindi" in nova.role.lower() or "hinglish" in nova.role.lower()

    def test_oracle_identity_specifications(self):
        oracle = IdentityEngine.get_identity("oracle")
        assert oracle.name == "ORACLE"
        assert "Research" in oracle.subtitle
        assert "citation" in oracle.role.lower() or "research" in oracle.role.lower()


class TestIntentEngine:
    def test_language_detection(self):
        res_en = IntentEngine.analyze_intent("How can I download my admit card?")
        assert res_en.detected_language == "en"

        res_hi = IntentEngine.analyze_intent("kya main kal hostel ja sakta hu attendance kam hai")
        assert res_hi.detected_language in ["hi", "hinglish", "en"]

    def test_themis_routing_for_attendance(self):
        res = IntentEngine.analyze_intent("My attendance is 68%, can I get medical condonation at LPU?")
        assert res.recommended_intelligence == "themis"
        assert res.complexity in ["simple", "moderate", "complex"]

    def test_athena_routing_for_code(self):
        res = IntentEngine.analyze_intent("Write a Python script for Dijkstra algorithm and analyze time complexity")
        assert res.recommended_intelligence == "athena"
        assert res.needs_code_execution is True

    def test_oracle_routing_for_research(self):
        res = IntentEngine.analyze_intent("Find primary IEEE research papers on multi-agent LLM systems")
        assert res.recommended_intelligence == "oracle"
        assert res.needs_web_search is True

    def test_nova_routing_for_campus_life(self):
        res = IntentEngine.analyze_intent("Where can I find pure vegetarian dosa near UniMall?")
        assert res.recommended_intelligence == "nova"


class TestPlanningEngine:
    def test_plan_depth_by_thinking_level(self):
        intent = IntentEngine.analyze_intent("Attendance query")
        plan_low = PlanningEngine.create_plan(intent, "nova", "Low")
        assert plan_low.max_model_calls <= 2

        plan_high = PlanningEngine.create_plan(intent, "themis", "High")
        assert plan_high.max_model_calls >= 2
        assert len(plan_high.steps) >= 3


class TestSharedProviderRegistry:
    def test_registered_providers_and_models(self):
        models = SharedProviderRegistry.list_models(active_only=False)
        assert len(models) >= 7

        providers = {m.provider_name for m in models}
        assert "gemini" in providers
        assert "groq" in providers
        assert "openrouter" in providers
        assert "mistral" in providers
        assert "cohere" in providers
        assert "bazaarlink" in providers
        assert "pekpik" in providers

    def test_model_capabilities_descriptor(self):
        gemini_flash = SharedProviderRegistry.get_model("gemini", "gemini-2.5-flash")
        assert gemini_flash is not None
        assert gemini_flash.capabilities.streaming is True
        assert gemini_flash.capabilities.structured_output is True

    def test_circuit_breaker_behavior(self):
        model = SharedProviderRegistry.get_model("groq", "llama-3.3-70b-versatile")
        assert model is not None

        # Simulate failures
        SharedProviderRegistry.update_health("groq", "llama-3.3-70b-versatile", success=False, error_msg="Network error")
        SharedProviderRegistry.update_health("groq", "llama-3.3-70b-versatile", success=False, error_msg="Network error")
        SharedProviderRegistry.update_health("groq", "llama-3.3-70b-versatile", success=False, error_msg="Network error")
        assert model.health.circuit_state == "open"

        # Record success resets failure count
        SharedProviderRegistry.update_health("groq", "llama-3.3-70b-versatile", success=True)
        assert model.health.circuit_state == "closed"


class TestCostController:
    def test_cost_calculation(self):
        cost = CostController.calculate_cost("gemini", "gemini-2.5-flash", 10000, 2000)
        assert cost > 0.0
        assert cost < 0.01

    def test_free_tier_zero_cost(self):
        cost_bz = CostController.calculate_cost("bazaarlink", "qwen/qwen3.7-flash:free", 5000, 1000)
        assert cost_bz == 0.0

    def test_budget_enforcement(self):
        is_ok, err = CostController.check_and_enforce_budget("student_123", "nova", 500, 1)
        assert is_ok is True
        assert err is None

        is_ok_excess, err_excess = CostController.check_and_enforce_budget("student_123", "nova", 500, 5)
        assert is_ok_excess is False
        assert "exceeded" in err_excess.lower()


class TestVerificationEngine:
    def test_statutory_65_percent_attendance_floor(self):
        res = VerificationEngine.verify(
            content="Your application is approved with condonation below 65%.",
            evidence_context="",
            intelligence_id="themis"
        )
        assert res.is_valid is False
        assert "65%" in res.verified_content
        assert any("65%" in v for v in res.violations_detected)

    def test_statutory_compliant_condonation(self):
        res = VerificationEngine.verify(
            content="Under Lovely Professional University policy, medical condonation can only be considered if attendance remains at or above the 65% statutory floor.",
            evidence_context="LPU Academic Policy: 75% attendance requirement, 65% condonation floor.",
            intelligence_id="themis"
        )
        assert res.is_valid is True

    def test_non_unilateral_execution_block(self):
        res = VerificationEngine.verify(
            content="I have updated your attendance and fee has been paid.",
            evidence_context="",
            intelligence_id="themis"
        )
        assert res.is_valid is False
        assert "cannot execute portal transactions directly" in res.verified_content


@pytest.mark.asyncio
class TestIntelligenceSystemEndToEnd:
    async def test_full_turn_7_real_steps(self):
        res = await IntelligenceSystem.process_turn(
            query="What is the policy for medical leave attendance at LPU?",
            selected_intelligence="themis",
            thinking_level="Balanced"
        )
        assert res.intelligence_id == "themis"
        assert res.intelligence_name == "THEMIS"
        assert len(res.thinking_steps) == 7

        expected_titles = [
            "Understanding task",
            "Planning",
            "Retrieving knowledge",
            "Selecting model",
            "Running tools",
            "Verifying results",
            "Preparing response"
        ]
        actual_titles = [s.title for s in res.thinking_steps]
        assert actual_titles == expected_titles

        assert len(res.content) > 50
        assert res.confidence_score > 0.0

    async def test_auto_orchestrator_turn(self):
        res = await IntelligenceSystem.process_turn(
            query="How can I implement a binary search tree in C++?",
            selected_intelligence="auto",
            thinking_level="Balanced"
        )
        assert res.intelligence_id == "athena"
        assert len(res.thinking_steps) >= 2

        # University-specific policy routes to THEMIS with full 7-step RAG pipeline
        res_univ = await IntelligenceSystem.process_turn(
            query="What is the LPU attendance condonation policy?",
            selected_intelligence="auto",
            thinking_level="Balanced"
        )
        assert res_univ.intelligence_id == "themis"
        assert len(res_univ.thinking_steps) == 7


@pytest.mark.asyncio
class TestAdminIntelligenceEndpoints:
    async def test_list_providers(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/v1/admin/intelligence/providers")
            assert resp.status_code == 200
            data = resp.json()
            assert isinstance(data, list)
            assert len(data) >= 7

    async def test_list_identities(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/v1/admin/intelligence/identities")
            assert resp.status_code == 200
            data = resp.json()
            assert len(data) >= 4
            names = [d["name"] for d in data]
            assert "THEMIS" in names
            assert "ATHENA" in names
            assert "NOVA" in names
            assert "ORACLE" in names

    async def test_get_costs_and_budgets(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/v1/admin/intelligence/costs")
            assert resp.status_code == 200
            data = resp.json()
            assert "attribution_by_intelligence" in data
            assert "configured_budgets" in data
            assert "themis" in data["configured_budgets"]

    async def test_run_themis_evaluation(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post("/api/v1/admin/intelligence/evaluations/run/themis")
            assert resp.status_code == 200
            data = resp.json()
            assert data["intelligence_id"] == "themis"
            assert data["total_cases"] >= 2
            assert "pass_rate_percent" in data
            assert "avg_latency_ms" in data
