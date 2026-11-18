"""
CAMPUSCONNECT AGENTIC INTELLIGENCE SYSTEM
Coordinates the 4 proprietary intelligence identities (NOVA, THEMIS, ATHENA, ORACLE)
and AEGIS orchestrator across general conversation and specialized university intelligence.
"""

import time
import uuid
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.intelligence.identity_engine import IdentityEngine, IdentitySpecification
from app.intelligence.intent_engine import IntentEngine, IntentAnalysisResult
from app.intelligence.planning_engine import PlanningEngine, ExecutionPlan
from app.intelligence.knowledge_engine import KnowledgeEngine, KnowledgeRetrievalResult
from app.intelligence.routing_engine import RoutingEngine
from app.intelligence.execution_engine import ExecutionEngine
from app.intelligence.verification_engine import VerificationEngine, VerificationResult
from app.intelligence.synthesis_engine import SynthesisEngine
from app.intelligence.conversation_engine import ConversationEngine, ConversationContext
from app.ai.cost_controller import CostController
from app.schemas.chat import ThinkingStep, Citation

logger = logging.getLogger(__name__)


class IntelligenceExecutionResult:
    def __init__(
        self,
        content: str,
        intelligence_id: str,
        intelligence_name: str,
        thinking_level: str,
        action_type: str,
        thinking_steps: List[ThinkingStep],
        citations: List[Citation],
        cards: Dict[str, Any],
        follow_ups: List[str],
        confidence_score: float,
        latency_ms: int,
        is_ai_generated: bool,
        cost_usd: float,
        routed_model: str,
        specialists_involved: List[str]
    ):
        self.content = content
        self.intelligence_id = intelligence_id
        self.intelligence_name = intelligence_name
        self.thinking_level = thinking_level
        self.action_type = action_type
        self.thinking_steps = thinking_steps
        self.citations = citations
        self.cards = cards
        self.follow_ups = follow_ups
        self.confidence_score = confidence_score
        self.latency_ms = latency_ms
        self.is_ai_generated = is_ai_generated
        self.cost_usd = cost_usd
        self.routed_model = routed_model
        self.specialists_involved = specialists_involved


class IntelligenceSystem:
    """
    CAMPUSCONNECT AGENTIC INTELLIGENCE SYSTEM
    Distinguishes general AI conversation from university specialized tasks.
    Enforces that general conversation is the default, and university specialization
    activates strictly when relevant to the student's intent.
    """

    @classmethod
    async def process_turn(
        cls,
        query: str,
        selected_intelligence: str = "auto",
        thinking_level: str = "Balanced",
        user_identifier: str = "anonymous_student",
        conversation_history: Optional[List[Dict[str, str]]] = None,
        db: Optional[AsyncSession] = None,
        user_lat: Optional[float] = None,
        user_lon: Optional[float] = None,
        landmark: Optional[str] = None,
        category_slug: Optional[str] = None,
        web_research: bool = False
    ) -> IntelligenceExecutionResult:
        start_time = time.time()
        request_id = f"req_{uuid.uuid4().hex[:12]}"
        history = conversation_history or []

        # =========================================================================
        # 1. CONVERSATION INTELLIGENCE CORE: Context & Coreference Resolution
        # =========================================================================
        conv_context = ConversationEngine.resolve_context(query, history)

        # =========================================================================
        # 2. INTENT ENGINE: Intent & Boundary Detection
        # =========================================================================
        intent = IntentEngine.analyze_intent(
            query=conv_context.effective_query,
            context={"web_research": web_research, "category_slug": category_slug}
        )

        # Resolve intelligence identity (Auto routes to recommended specialist)
        resolved_intel = selected_intelligence.lower()
        if resolved_intel in ["auto", "aegis"]:
            resolved_intel = intent.recommended_intelligence

        # =========================================================================
        # 3. IDENTITY ENGINE: Master Prompt & Directives
        # =========================================================================
        identity = IdentityEngine.get_identity(resolved_intel)

        # =========================================================================
        # 4. PLANNING & BUDGET: Modulate based on Thinking Level
        # =========================================================================
        plan = PlanningEngine.create_plan(
            intent=intent,
            intelligence_id=resolved_intel,
            thinking_level=thinking_level,
            context={"web_research": web_research}
        )

        estimated_input_toks = (len(query.split()) + 300) * 2
        is_allowed, budget_err = CostController.check_and_enforce_budget(
            user_identifier=user_identifier,
            intelligence_id=resolved_intel,
            estimated_input_tokens=estimated_input_toks,
            call_count_in_turn=1
        )
        if not is_allowed:
            return cls._build_budget_exceeded_result(budget_err, identity, thinking_level, start_time)

        # =========================================================================
        # 5. DIVERGENT FLOW: General Conversation vs. University Specialized
        # =========================================================================
        is_general_conversation = conv_context.is_general_conversation and not intent.needs_rag_knowledge

        if is_general_conversation:
            # -----------------------------------------------------------------
            # FAST GENERAL CONVERSATION PATH (0 University Noise, 0 Fake Citations)
            # -----------------------------------------------------------------
            thinking_steps: List[ThinkingStep] = [
                ThinkingStep(
                    step=1,
                    title="Understanding conversation",
                    description=f"Identified topic: {conv_context.active_topic.replace('_', ' ').title()} ({intent.detected_language.upper()}).",
                    status="completed"
                ),
                ThinkingStep(
                    step=2,
                    title=f"Reasoning via {identity.name}",
                    description=f"Active identity: {identity.name} ({identity.subtitle}). Depth: {thinking_level.title()}.",
                    status="completed"
                )
            ]

            # Route to model
            routing_decision = await RoutingEngine.route_subtask(
                task_name=f"{resolved_intel}_general",
                intelligence_id=resolved_intel,
                thinking_level=thinking_level,
                required_capabilities=["streaming"],
                request_id=request_id,
                db=db
            )

            # Synthesize pure conversational response
            synthesis_result = await SynthesisEngine.synthesize_response(
                query=query,
                identity=identity,
                evidence_context="",
                subagent_outputs=[],
                conversation_history=history,
                routed_provider=routing_decision.provider_name,
                routed_model=routing_decision.model_id,
                fallback_chain=routing_decision.fallback_chain,
                user_identifier=user_identifier,
                thinking_level=thinking_level,
                is_university_specific=False
            )

            # Validate response relevance (Section 12)
            final_content = ConversationEngine.validate_response_relevance(
                user_query=query,
                generated_content=synthesis_result["content"],
                context=conv_context
            )

            # Contextual conversational follow-ups
            if conv_context.active_topic == "greeting_chitchat":
                follow_ups = [
                    "What can you do?",
                    "Explain machine learning",
                    "I need help with my career"
                ]
            elif conv_context.active_topic == "career_coaching":
                follow_ups = [
                    "What tech skills should I learn first?",
                    "How do I prepare for campus placement drives?",
                    "Suggest full stack projects for my resume"
                ]
            elif "recursion" in query.lower():
                follow_ups = [
                    "Show an example of recursion in Python",
                    "What is the difference between recursion and iteration?",
                    "What is stack overflow in recursion?"
                ]
            elif "machine learning" in query.lower():
                follow_ups = [
                    "What is the difference between supervised and unsupervised learning?",
                    "How does gradient descent work?",
                    "Can you suggest a beginner ML project?"
                ]
            else:
                follow_ups = [
                    "Can you explain further?",
                    "Give me a practical code example",
                    "What are the best practices for this?"
                ]

            total_latency_ms = int((time.time() - start_time) * 1000)

            return IntelligenceExecutionResult(
                content=final_content,
                intelligence_id=resolved_intel,
                intelligence_name=identity.name,
                thinking_level=thinking_level,
                action_type="ANSWER",
                thinking_steps=thinking_steps,
                citations=[],
                cards={},
                follow_ups=follow_ups,
                confidence_score=0.98,
                latency_ms=total_latency_ms,
                is_ai_generated=synthesis_result["is_ai_generated"],
                cost_usd=routing_decision.estimated_cost_usd,
                routed_model=routing_decision.key,
                specialists_involved=[resolved_intel]
            )

        # ---------------------------------------------------------------------
        # UNIVERSITY SPECIALIZED GROUNDED PATH (Institutional Evidence & Cards)
        # ---------------------------------------------------------------------
        thinking_steps: List[ThinkingStep] = [
            ThinkingStep(
                step=1,
                title="Understanding task",
                description=f"Identified goal: {intent.primary_intent.replace('_', ' ').title()} (Language: {intent.detected_language.upper()}, Complexity: {intent.complexity.title()}).",
                status="completed"
            ),
            ThinkingStep(
                step=2,
                title="Planning",
                description=f"Active identity: {identity.name} ({identity.subtitle}). Depth: {thinking_level.title()}. Budget: max {plan.max_model_calls} model call(s).",
                status="completed"
            ),
            ThinkingStep(
                step=3,
                title="Retrieving knowledge",
                description="Querying institutional records, hybrid BM25 index & university service catalog.",
                status="completed"
            )
        ]

        # Targeted institutional knowledge retrieval
        knowledge = await KnowledgeEngine.retrieve(
            query=conv_context.effective_query,
            db=db,
            user_lat=user_lat,
            user_lon=user_lon,
            landmark=landmark,
            category_slug=category_slug,
            thinking_level=thinking_level
        )

        thinking_steps.append(
            ThinkingStep(
                step=4,
                title="Selecting model",
                description="Evaluating candidate models across capability requirements, latency tier & token budget.",
                status="completed"
            )
        )

        required_caps = ["streaming", "structured_output"]
        if intent.needs_code_execution or resolved_intel == "athena":
            required_caps.append("tools")
        if thinking_level == "High":
            required_caps.append("reasoning")

        routing_decision = await RoutingEngine.route_subtask(
            task_name=f"{resolved_intel}_generation",
            intelligence_id=resolved_intel,
            thinking_level=thinking_level,
            required_capabilities=required_caps,
            request_id=request_id,
            db=db
        )

        # Execution of specialist subagents if planned
        subagent_outputs: List[Dict[str, Any]] = []
        specialists_involved: List[str] = [resolved_intel]

        if plan.required_subagents:
            thinking_steps.append(
                ThinkingStep(
                    step=5,
                    title="Running tools",
                    description=f"Invoking internal specialist subagents: {', '.join([s.upper() for s in plan.required_subagents])}.",
                    status="completed"
                )
            )
            sub_context = {
                "user_lat": user_lat,
                "user_lon": user_lon,
                "landmark": landmark,
                "category_slug": category_slug,
                "thinking_level": thinking_level
            }
            subagent_outputs = await ExecutionEngine.execute_subagents(
                subagent_names=plan.required_subagents,
                query=conv_context.effective_query,
                context=sub_context,
                db=db,
                request_id=request_id,
                parent_intelligence=resolved_intel
            )
            for out in subagent_outputs:
                specialists_involved.append(out["agent_name"])
                if out.get("cards"):
                    knowledge.action_cards.update(out["cards"])
                if out.get("citations"):
                    knowledge.citations.extend(out["citations"])
        else:
            thinking_steps.append(
                ThinkingStep(
                    step=5,
                    title="Running tools",
                    description="Executing direct institutional hybrid search and action resolvers.",
                    status="completed"
                )
            )

        # Synthesize grounded response
        synthesis_result = await SynthesisEngine.synthesize_response(
            query=conv_context.effective_query,
            identity=identity,
            evidence_context=knowledge.evidence_context,
            subagent_outputs=subagent_outputs,
            conversation_history=history,
            routed_provider=routing_decision.provider_name,
            routed_model=routing_decision.model_id,
            fallback_chain=routing_decision.fallback_chain,
            user_identifier=user_identifier,
            thinking_level=thinking_level,
            is_university_specific=True
        )

        # Verify regulatory claims if attendance or benefits involved
        thinking_steps.append(
            ThinkingStep(
                step=6,
                title="Verifying results",
                description="Cross-referencing claims against statutory regulations (75% attendance rule, 65% floor) and verifying citation integrity.",
                status="completed"
            )
        )

        verification = VerificationEngine.verify(
            content=synthesis_result["content"],
            evidence_context=knowledge.evidence_context,
            intelligence_id=resolved_intel
        )

        thinking_steps.append(
            ThinkingStep(
                step=7,
                title="Preparing response",
                description=f"Response compiled by {identity.name} via {routing_decision.key} at {thinking_level.title()} depth.",
                status="completed"
            )
        )

        total_latency_ms = int((time.time() - start_time) * 1000)

        # Format final citations
        final_citations = [
            Citation(**c) if isinstance(c, dict) else c
            for c in knowledge.citations[:4]
        ]

        follow_ups = [
            f"Ask {identity.name} about related campus procedures",
            "How do I submit this in UMS?",
            "What is the physical office location?"
        ]

        return IntelligenceExecutionResult(
            content=verification.verified_content,
            intelligence_id=resolved_intel,
            intelligence_name=identity.name,
            thinking_level=thinking_level,
            action_type="ANSWER",
            thinking_steps=thinking_steps,
            citations=final_citations,
            cards=knowledge.action_cards,
            follow_ups=follow_ups,
            confidence_score=knowledge.confidence_score,
            latency_ms=total_latency_ms,
            is_ai_generated=synthesis_result["is_ai_generated"],
            cost_usd=routing_decision.estimated_cost_usd,
            routed_model=routing_decision.key,
            specialists_involved=list(dict.fromkeys(specialists_involved))
        )

    @classmethod
    def _build_budget_exceeded_result(cls, err_msg: str, identity: IdentitySpecification, thinking_level: str, start_time: float) -> IntelligenceExecutionResult:
        return IntelligenceExecutionResult(
            content=f"⚠️ **Execution Budget Reached**: {err_msg}\n\nPlease try again shortly or switch to Low thinking depth to conserve your request budget.",
            intelligence_id=identity.id,
            intelligence_name=identity.name,
            thinking_level=thinking_level,
            action_type="BUDGET_EXCEEDED",
            thinking_steps=[],
            citations=[],
            cards={},
            follow_ups=["Try a simpler query", "Switch to Low thinking depth"],
            confidence_score=1.0,
            latency_ms=int((time.time() - start_time) * 1000),
            is_ai_generated=False,
            cost_usd=0.0,
            routed_model="system_budget_guard",
            specialists_involved=[identity.id]
        )
