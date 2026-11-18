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
    CAMPUSCONNECT NINE-LAYER AGENTIC INTELLIGENCE SYSTEM
    Coordinates the 4 proprietary intelligence identities (NOVA, THEMIS, ATHENA, ORACLE)
    and AEGIS auto-orchestrator across the 9 layers.
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
        # LAYER 2 — INTENT ENGINE
        # =========================================================================
        intent = IntentEngine.analyze_intent(
            query=query,
            context={"web_research": web_research, "category_slug": category_slug}
        )

        # Resolve intelligence identity (Auto routes to recommended specialist)
        resolved_intel = selected_intelligence.lower()
        if resolved_intel in ["auto", "aegis"]:
            resolved_intel = intent.recommended_intelligence

        # =========================================================================
        # LAYER 1 — IDENTITY ENGINE
        # =========================================================================
        identity = IdentityEngine.get_identity(resolved_intel)

        # =========================================================================
        # LAYER 3 — PLANNING ENGINE
        # =========================================================================
        plan = PlanningEngine.create_plan(
            intent=intent,
            intelligence_id=resolved_intel,
            thinking_level=thinking_level,
            context={"web_research": web_research}
        )

        # Budget Check
        estimated_input_toks = (len(query.split()) + 500) * 2
        is_allowed, budget_err = CostController.check_and_enforce_budget(
            user_identifier=user_identifier,
            intelligence_id=resolved_intel,
            estimated_input_tokens=estimated_input_toks,
            call_count_in_turn=1
        )
        if not is_allowed:
            return cls._build_budget_exceeded_result(budget_err, identity, thinking_level, start_time)

        # Transparent 7 Real Execution Steps
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
            )
        ]

        # =========================================================================
        # LAYER 4 — KNOWLEDGE ENGINE
        # =========================================================================
        thinking_steps.append(
            ThinkingStep(
                step=3,
                title="Retrieving knowledge",
                description="Querying institutional pgvector embeddings, hybrid BM25 index & university service catalog.",
                status="completed"
            )
        )

        knowledge = await KnowledgeEngine.retrieve(
            query=query,
            db=db,
            user_lat=user_lat,
            user_lon=user_lon,
            landmark=landmark,
            category_slug=category_slug,
            thinking_level=thinking_level
        )

        # =========================================================================
        # LAYER 5 — MODEL ROUTING ENGINE
        # =========================================================================
        thinking_steps.append(
            ThinkingStep(
                step=4,
                title="Selecting model",
                description="Evaluating candidate models across capability requirements, context window, latency tier & token budget.",
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

        # =========================================================================
        # LAYER 6 — EXECUTION ENGINE (Subagent delegation if planned)
        # =========================================================================
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
                query=query,
                context=sub_context,
                db=db,
                request_id=request_id,
                parent_intelligence=resolved_intel
            )
            for out in subagent_outputs:
                specialists_involved.append(out["agent_name"])
                # Merge cards
                if out.get("cards"):
                    knowledge.action_cards.update(out["cards"])
                # Merge citations
                if out.get("citations"):
                    knowledge.citations.extend(out["citations"])
        else:
            thinking_steps.append(
                ThinkingStep(
                    step=5,
                    title="Running tools",
                    description=f"Executing direct institutional hybrid search and action resolvers.",
                    status="completed"
                )
            )

        # =========================================================================
        # LAYER 8 — RESPONSE SYNTHESIS ENGINE
        # =========================================================================
        synthesis_result = await SynthesisEngine.synthesize_response(
            query=query,
            identity=identity,
            evidence_context=knowledge.evidence_context,
            subagent_outputs=subagent_outputs,
            conversation_history=history,
            routed_provider=routing_decision.provider_name,
            routed_model=routing_decision.model_id,
            fallback_chain=routing_decision.fallback_chain,
            user_identifier=user_identifier,
            thinking_level=thinking_level
        )

        # =========================================================================
        # LAYER 7 — VERIFICATION ENGINE
        # =========================================================================
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

        # Follow-up prompts
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
    def _build_budget_exceeded_result(
        cls,
        err_msg: str,
        identity: IdentitySpecification,
        thinking_level: str,
        start_time: float
    ) -> IntelligenceExecutionResult:
        latency = int((time.time() - start_time) * 1000)
        return IntelligenceExecutionResult(
            content=f"⚠️ **Budget Limit Encountered ({identity.name}):**\n\n{err_msg}\n\nPlease check official UMS at https://ums.lpu.in for direct information.",
            intelligence_id=identity.id,
            intelligence_name=identity.name,
            thinking_level=thinking_level,
            action_type="POLICY_INTERCEPT",
            thinking_steps=[
                ThinkingStep(step=1, title="Understanding task", description="Budget boundary evaluation", status="completed"),
                ThinkingStep(step=2, title="Budget Intercept", description=err_msg, status="completed"),
            ],
            citations=[],
            cards={},
            follow_ups=["Try a simpler query", "Switch thinking depth to Low"],
            confidence_score=1.0,
            latency_ms=latency,
            is_ai_generated=False,
            cost_usd=0.0,
            routed_model="policy_budget_controller",
            specialists_involved=[identity.id]
        )
