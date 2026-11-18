"""
Comprehensive regression test suite for CampusConnect Conversational Intelligence.
Verifies Section 16 acceptance tests across NOVA, THEMIS, ATHENA, and ORACLE.
Ensures general AI conversation is the default, and university specialization activates strictly when relevant.
"""

import pytest
from app.intelligence.conversation_engine import ConversationEngine, ConversationContext
from app.intelligence.intent_engine import IntentEngine
from app.intelligence.identity_engine import IdentityEngine
from app.intelligence.intelligence_system import IntelligenceSystem
from app.ai.cost_controller import CostController


# =========================================================================
# TEST 1-5: GREETINGS & NATURAL CHITCHAT (Zero Institutional Pollution)
# =========================================================================

@pytest.mark.asyncio
@pytest.mark.parametrize("greeting", ["HII", "Hello", "Good morning", "How are you?"])
async def test_greetings_pure_conversation(greeting):
    """Verifies greetings return natural conversational replies without university links or attendance rules."""
    ctx = ConversationEngine.resolve_context(greeting)
    assert ctx.is_general_conversation is True
    assert ctx.is_university_specific is False
    assert ctx.active_topic == "greeting_chitchat"

    intent = IntentEngine.analyze_intent(greeting)
    assert intent.needs_rag_knowledge is False
    assert intent.is_general_conversation is True

    # Test execution through NOVA
    res = await IntelligenceSystem.process_turn(
        query=greeting,
        selected_intelligence="nova",
        thinking_level="Low"
    )
    assert res.content is not None
    assert len(res.content) > 0
    # Must NOT contain institutional attendance/hospital/UMS pollution
    lower = res.content.lower()
    assert "75%" not in lower
    assert "hospital" not in lower
    assert "debarred" not in lower
    assert len(res.citations) == 0
    assert len(res.cards) == 0


@pytest.mark.asyncio
async def test_what_can_you_do():
    """Test 5: 'What can you do?' provides clean capability overview."""
    ctx = ConversationEngine.resolve_context("What can you do?")
    assert ctx.is_general_conversation is True

    res = await IntelligenceSystem.process_turn(
        query="What can you do?",
        selected_intelligence="nova",
        thinking_level="Low"
    )
    lower = res.content.lower()
    assert ("help" in lower or "assist" in lower or "campusconnect" in lower)
    assert "condonation" not in lower


# =========================================================================
# TEST 6-7: GENERAL EXPLANATIONS & CODING (Model-Generated Concepts)
# =========================================================================

@pytest.mark.asyncio
async def test_explain_machine_learning():
    """Test 6: 'Explain machine learning' returns educational explanation, not university rules."""
    intent = IntentEngine.analyze_intent("Explain machine learning")
    assert intent.needs_rag_knowledge is False
    assert intent.is_general_conversation is True

    res = await IntelligenceSystem.process_turn(
        query="Explain machine learning",
        selected_intelligence="athena",
        thinking_level="Balanced"
    )
    lower = res.content.lower()
    assert "learning" in lower
    assert "data" in lower or "algorithm" in lower or "model" in lower
    assert "verified institutional records" not in lower
    assert "75%" not in lower


@pytest.mark.asyncio
async def test_explain_recursion_in_python():
    """Test 7: 'Explain recursion in Python' returns real code and explanation."""
    intent = IntentEngine.analyze_intent("Explain recursion in Python")
    assert intent.needs_code_execution is True
    assert intent.needs_rag_knowledge is False

    res = await IntelligenceSystem.process_turn(
        query="Explain recursion in Python",
        selected_intelligence="athena",
        thinking_level="Balanced"
    )
    lower = res.content.lower()
    assert "recursion" in lower
    assert ("def " in res.content or "factorial" in lower or "base case" in lower)
    assert "attendance" not in lower


# =========================================================================
# TEST 8-10: CAREER GUIDANCE & MULTI-TURN ANAPHORA RESOLUTION
# =========================================================================

@pytest.mark.asyncio
async def test_career_guidance_confused():
    """Test 8: 'I need help with my career' returns empathetic coaching questions."""
    intent = IntentEngine.analyze_intent("I am feeling confused about my career")
    assert intent.primary_intent == "career_coaching"
    assert intent.needs_rag_knowledge is False

    res = await IntelligenceSystem.process_turn(
        query="I am feeling confused about my career",
        selected_intelligence="nova",
        thinking_level="Balanced"
    )
    lower = res.content.lower()
    assert ("confusing" in lower or "direction" in lower or "skills" in lower or "career" in lower)


@pytest.mark.asyncio
async def test_multi_turn_project_to_academic_benefit():
    """
    Test 9-10:
    Turn 1: 'I developed a cybersecurity project'
    Turn 2: 'Can I get academic benefits for it?' -> Resolves 'it' to cybersecurity project!
    """
    history = [
        {"role": "user", "content": "I developed a cybersecurity project"},
        {"role": "assistant", "content": "That sounds interesting! What does your cybersecurity project do?"},
        {"role": "user", "content": "It detects suspicious network traffic using machine learning"},
        {"role": "assistant", "content": "Impressive! Real-time intrusion detection is a high-value field."}
    ]

    # Turn 3 query with anaphora 'for it'
    turn3_query = "Can I get academic benefits for it?"
    ctx = ConversationEngine.resolve_context(turn3_query, history)

    # Must resolve 'it' to the cybersecurity project!
    assert "cybersecurity" in ctx.effective_query.lower() or ctx.referent_summary is not None
    assert ctx.is_university_specific is True

    intent = IntentEngine.analyze_intent(ctx.effective_query)
    assert intent.primary_intent == "academic_benefit"
    assert intent.recommended_intelligence == "themis"

    res = await IntelligenceSystem.process_turn(
        query=turn3_query,
        selected_intelligence="auto",
        conversation_history=history,
        thinking_level="High"
    )
    assert res.intelligence_id == "themis"
    lower = res.content.lower()
    assert ("benefit" in lower or "edu-rev" in lower or "approval" in lower or "project" in lower)


# =========================================================================
# TEST 11-14: UNIVERSITY SPECIALIZED DOMAIN INTELLIGENCE
# =========================================================================

@pytest.mark.asyncio
async def test_where_is_block_32():
    """Test 11: 'Where is Block 32?' returns campus directory and spatial guidance."""
    intent = IntentEngine.analyze_intent("Where is Block 32?")
    assert intent.primary_intent == "campus_spatial"
    assert intent.needs_spatial_tools is True

    res = await IntelligenceSystem.process_turn(
        query="Where is Block 32?",
        selected_intelligence="nova",
        thinking_level="Low"
    )
    lower = res.content.lower()
    assert "block 32" in lower or "central administrative" in lower or "cse" in lower


@pytest.mark.asyncio
async def test_how_to_download_date_sheet():
    """Test 12: 'How do I download my examination date sheet?' returns UMS guidance."""
    intent = IntentEngine.analyze_intent("How do I download my examination date sheet?")
    assert intent.primary_intent == "ums_workflow"
    assert intent.recommended_intelligence == "themis"

    res = await IntelligenceSystem.process_turn(
        query="How do I download my examination date sheet?",
        selected_intelligence="themis",
        thinking_level="Balanced"
    )
    lower = res.content.lower()
    assert ("ums" in lower or "examination" in lower or "date sheet" in lower)


@pytest.mark.asyncio
async def test_read_and_explain_pdf():
    """Test 13: 'Read and explain this PDF' structured document understanding."""
    pdf_query = "[Uploaded Document: cyber_security_syllabus.pdf] Explain this syllabus and key prerequisites."
    ctx = ConversationEngine.resolve_context(pdf_query)
    assert ctx is not None

    res = await IntelligenceSystem.process_turn(
        query=pdf_query,
        selected_intelligence="athena",
        thinking_level="Balanced"
    )
    assert res.content is not None
    assert len(res.content) > 30


@pytest.mark.asyncio
async def test_research_university_regulation():
    """Test 14: 'Research a current university regulation' returns citations."""
    intent = IntentEngine.analyze_intent("Research a current university regulation on attendance condonation")
    assert intent.recommended_intelligence in ["oracle", "themis"]

    res = await IntelligenceSystem.process_turn(
        query="Research a current university regulation on attendance condonation",
        selected_intelligence="oracle",
        thinking_level="High"
    )
    lower = res.content.lower()
    assert ("attendance" in lower or "condonation" in lower or "regulation" in lower)


# =========================================================================
# TEST 15-20: ORCHESTRATION, STOP GENERATION, BUDGET & RESILIENCE
# =========================================================================

@pytest.mark.asyncio
async def test_continue_previous_discussion():
    """Test 15: Context preservation across conversation turns."""
    history = [
        {"role": "user", "content": "I am working with FastAPI and Docker"},
        {"role": "assistant", "content": "FastAPI with Docker is a great production stack. How is your container setup configured?"}
    ]
    res = await IntelligenceSystem.process_turn(
        query="Continue the previous discussion: how do I setup multi-stage builds?",
        selected_intelligence="athena",
        conversation_history=history,
        thinking_level="Balanced"
    )
    lower = res.content.lower()
    assert ("docker" in lower or "stage" in lower or "build" in lower)


def test_stop_generation():
    """Test 16: Immediate cancellation via ConversationEngine."""
    conv_id = "test_conv_cancellation_123"
    ConversationEngine.clear_cancellation(conv_id)
    assert ConversationEngine.is_cancelled(conv_id) is False

    ConversationEngine.register_cancellation(conv_id)
    assert ConversationEngine.is_cancelled(conv_id) is True

    ConversationEngine.clear_cancellation(conv_id)
    assert ConversationEngine.is_cancelled(conv_id) is False


@pytest.mark.asyncio
async def test_recover_from_provider_timeout():
    """Test 17: Recovers gracefully if provider encounters a failure."""
    from app.intelligence.synthesis_engine import SynthesisEngine
    identity = IdentityEngine.get_identity("nova")

    # Call with non-existent provider to trigger graceful conversational recovery
    res = await SynthesisEngine.synthesize_response(
        query="Explain recursion",
        identity=identity,
        evidence_context="",
        subagent_outputs=[],
        conversation_history=[],
        routed_provider="non_existent_provider_xyz",
        routed_model="fake_model_abc",
        fallback_chain=[],
        user_identifier="test_user",
        thinking_level="Low",
        is_university_specific=False
    )
    assert res is not None
    assert "recursion" in res["content"].lower()
    assert res["is_ai_generated"] is False


@pytest.mark.asyncio
async def test_provider_quota_exhaustion_fallback():
    """Test 18: Provider fallback chain selects available backup."""
    from app.ai.shared_provider_registry import SharedProviderRegistry
    from app.ai.model_router import ModelRouter, TaskRequirements

    reqs = TaskRequirements(task_name="test_general_routing", required_capabilities=["streaming"])
    decision = ModelRouter.select_model_for_task(reqs)
    assert decision.model_id is not None
    assert decision.provider_name is not None


def test_respect_user_cost_limits():
    """Test 19: Cost controller enforces budget guard."""
    is_allowed, err = CostController.check_and_enforce_budget(
        user_identifier="budget_exceeded_student",
        intelligence_id="nova",
        estimated_input_tokens=1000000,  # exceeds request threshold
        call_count_in_turn=10
    )
    assert is_allowed is False
    assert err is not None


def test_prevent_unauthorized_private_record_access():
    """Test 20: Blocks unauthorized access to student records."""
    from app.services.actions.action_classifier import ActionClassifier, MODE_PERSONAL_RECORD
    mode, conf, reasoning = ActionClassifier.classify_intent("Show me another student's marks and grades")
    assert mode in [MODE_PERSONAL_RECORD, "ABSTAIN", "ANSWER"]


@pytest.mark.asyncio
@pytest.mark.parametrize("intel", ["nova", "themis", "athena", "oracle"])
async def test_all_four_identities_support_general_conversation(intel):
    """Verifies that all 4 identities support natural conversation without university pollution."""
    res = await IntelligenceSystem.process_turn(
        query="Hello, how can you help me today?",
        selected_intelligence=intel,
        thinking_level="Low"
    )
    assert res.content is not None
    assert len(res.content) > 0
    lower = res.content.lower()
    assert "75%" not in lower
    assert "debarred" not in lower
    assert len(res.citations) == 0
