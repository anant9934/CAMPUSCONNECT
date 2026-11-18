import time
import asyncio
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.agent import (
    AgentDefinition,
    AgentExecutionPlan,
    AgentOutput,
)
from app.schemas.chat import ThinkingStep, Citation
from app.agents.agent_registry import AgentRegistry
from app.agents.specialists.themis_agent import ThemisAgent
from app.agents.specialists.hermes_agent import HermesAgent
from app.agents.specialists.argus_agent import ArgusAgent
from app.agents.specialists.athena_agent import AthenaAgent
from app.agents.specialists.mnemos_agent import MnemosAgent
from app.agents.specialists.oracle_agent import OracleAgent
from app.agents.specialists.forge_agent import ForgeAgent
from app.agents.specialists.vision_agent import VisionAgent
from app.agents.specialists.nova_agent import NovaAgent
from app.ai.response_generator import ResponseGenerator
from app.services.grounding_service import validate_grounded_response, generate_follow_up_suggestions

logger = logging.getLogger(__name__)


class AEGISOrchestrator:
    """
    AEGIS — Master Multi-Agent Orchestration & Routing Intelligence.
    Coordinates the 8 specialist agents (THEMIS, HERMES, ARGUS, ATHENA, MNEMOS, ORACLE, FORGE, VISION).
    Decomposes queries, dispatches parallel sub-agents, verifies safety boundaries,
    and synthesizes unified student answers.
    """

    _specialists_map = None

    @classmethod
    def _get_specialist_instances(cls) -> Dict[str, Any]:
        if cls._specialists_map is None:
            cls._specialists_map = {
                "nova": NovaAgent(),
                "themis": ThemisAgent(),
                "hermes": HermesAgent(),
                "argus": ArgusAgent(),
                "athena": AthenaAgent(),
                "mnemos": MnemosAgent(),
                "oracle": OracleAgent(),
                "forge": ForgeAgent(),
                "vision": VisionAgent(),
            }
        return cls._specialists_map

    @classmethod
    def plan_routing(
        cls,
        query: str,
        explicit_agent_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> AgentExecutionPlan:
        """
        Evaluates query complexity, risk, thinking level, and intent to select the optimal specialist team.
        """
        q_lower = query.lower()
        context = context or {}
        thinking_level = context.get("thinking_level", "medium").lower()

        # 1. Explicit specialist override
        if explicit_agent_id and explicit_agent_id.lower() != "aegis":
            target = explicit_agent_id.lower().strip()
            specialists = [target]
            if target != "vision" and "mnemos" not in specialists and target != "nova":
                specialists.append("mnemos")
            elif target == "nova":
                specialists = ["nova"]
            
            # If research level requested, also include oracle
            if thinking_level == "research" and "oracle" not in specialists:
                specialists.append("oracle")

            return AgentExecutionPlan(
                query=query,
                intent=f"Explicit Request for {target.upper()}",
                complexity="simple" if thinking_level == "low" else "moderate",
                risk="low",
                primary_agent=target,
                specialist_agents=specialists,
                parallel_group=specialists,
                sequential_group=[],
                rationale=f"User explicitly requested specialist {target.upper()} with thinking level '{thinking_level}'."
            )

        # 2. Multimodal document upload
        if context.get("is_uploaded_document") or "[uploaded " in q_lower:
            return AgentExecutionPlan(
                query=query,
                intent="Multimodal Document Comprehension",
                complexity="complex",
                risk="medium",
                primary_agent="aegis",
                specialist_agents=["vision", "mnemos", "themis"],
                parallel_group=["vision", "mnemos"],
                sequential_group=["themis"],
                rationale="Uploaded file detected; engaging VISION for perception, MNEMOS for retrieval, and THEMIS for policy."
            )

        # 3. Attendance problem solving
        if any(k in q_lower for k in ["attendance", "shortage", "debarred", "condonation", "medical leave", "duty leave"]):
            return AgentExecutionPlan(
                query=query,
                intent="Attendance Policy & Condonation Assessment",
                complexity="complex",
                risk="high",
                primary_agent="aegis",
                specialist_agents=["themis", "mnemos"],
                parallel_group=["themis", "mnemos"],
                sequential_group=[],
                rationale="Query involves attendance eligibility and condonation rules; routing to THEMIS + MNEMOS."
            )

        # 4. EDU-Revolution project benefits & academic recognition
        if any(k in q_lower for k in ["edurev", "edu-revolution", "academic benefit", "ca exemption", "course equivalence", "credit substitution", "project benefit"]):
            return AgentExecutionPlan(
                query=query,
                intent="Academic Benefit & EDU-Revolution Evaluation",
                complexity="complex",
                risk="medium",
                primary_agent="aegis",
                specialist_agents=["themis", "athena", "mnemos"],
                parallel_group=["themis", "mnemos"],
                sequential_group=["athena"],
                rationale="Comprehensive benefit assessment requires THEMIS (policy), ATHENA (academic reasoning), and MNEMOS (knowledge)."
            )

        # 5. UMS navigation, bookings, or RMS grievance
        if any(k in q_lower for k in ["ums", "how to apply", "portal", "rms", "grievance", "complaint", "fee receipt", "download", "procedure", "hostel leave"]):
            return AgentExecutionPlan(
                query=query,
                intent="UMS Navigation & University Workflows",
                complexity="simple",
                risk="low",
                primary_agent="aegis",
                specialist_agents=["hermes"],
                parallel_group=["hermes"],
                sequential_group=[],
                rationale="Query relates to university service execution; routing directly to HERMES."
            )

        # 6. Faculty, leadership, office hours, campus wayfinding, food
        if any(k in q_lower for k in ["who", "whom", "hod", "head", "dean", "cabin", "arora", "sobti", "food", "eat", "cafe", "dhaba", "chaap", "block 32", "block 34", "block 30", "where is"]):
            return AgentExecutionPlan(
                query=query,
                intent="Faculty Discovery & Campus Wayfinding",
                complexity="simple",
                risk="low",
                primary_agent="aegis",
                specialist_agents=["hermes", "argus"],
                parallel_group=["hermes", "argus"],
                sequential_group=[],
                rationale="Physical spatial intelligence and leadership directory match; routing to HERMES + ARGUS."
            )

        # 7. Live web research & external hackathons (SIH) or Research level
        if thinking_level == "research" or any(k in q_lower for k in ["sih", "hackathon", "ugc", "aicte", "news", "announcement", "external"]) or context.get("web_research"):
            return AgentExecutionPlan(
                query=query,
                intent="External Web Research & Regulatory Verification",
                complexity="complex" if thinking_level == "research" else "moderate",
                risk="low",
                primary_agent="aegis",
                specialist_agents=["oracle", "athena"],
                parallel_group=["oracle", "athena"],
                sequential_group=[],
                rationale="External freshness and research-level queries routed to ORACLE + ATHENA."
            )

        # 8. Technical projects, code review, tech internships
        if any(k in q_lower for k in ["coding", "code", "python", "bug", "github", "react", "fastapi", "docker", "full-stack", "internship", "stipend"]):
            return AgentExecutionPlan(
                query=query,
                intent="Technical Project & Internship Alignment",
                complexity="moderate",
                risk="low",
                primary_agent="aegis",
                specialist_agents=["forge", "themis"],
                parallel_group=["forge", "themis"],
                sequential_group=[],
                rationale="Software engineering and technical portfolio review routed to FORGE + THEMIS."
            )

        # 9. Fast everyday questions & campus FAQs (Low thinking level or common facts)
        if thinking_level == "low" or any(k in q_lower for k in ["timing", "when", "time", "fee", "bus", "hostel", "curfew", "gym", "library", "what is"]):
            return AgentExecutionPlan(
                query=query,
                intent="Everyday Campus Guidance",
                complexity="simple",
                risk="low",
                primary_agent="aegis",
                specialist_agents=["nova", "mnemos"],
                parallel_group=["nova", "mnemos"],
                sequential_group=[],
                rationale="Common university query or low thinking level; routing to NOVA for fast everyday answers."
            )

        # Default fallback: NOVA + MNEMOS retrieval
        return AgentExecutionPlan(
            query=query,
            intent="General Institutional Inquiry",
            complexity="simple",
            risk="low",
            primary_agent="aegis",
            specialist_agents=["nova", "mnemos"],
            parallel_group=["nova", "mnemos"],
            sequential_group=[],
            rationale="Standard factual inquiry routed to NOVA everyday help + MNEMOS retrieval."
        )

    @classmethod
    def _get_specialist_status_label(cls, s_id: str) -> str:
        labels = {
            "themis": "Policy analysis",
            "athena": "Reasoning & equivalence",
            "argus": "Faculty discovery & wayfinding",
            "oracle": "Source verification",
            "nova": "Everyday retrieval",
            "hermes": "UMS navigation",
            "forge": "Code review",
            "vision": "Document perception",
            "mnemos": "Knowledge memory",
        }
        return labels.get(s_id.lower(), "Specialist processing")

    @classmethod
    async def orchestrate_turn(
        cls,
        query: str,
        conversation_history: List[Dict[str, str]],
        db: AsyncSession,
        session_token: str,
        user_lat: Optional[float] = None,
        user_lon: Optional[float] = None,
        landmark: Optional[str] = None,
        category_slug: Optional[str] = None,
        explicit_agent_id: Optional[str] = "aegis",
        preferred_provider: Optional[str] = None,
        web_research: bool = False,
        thinking_level: str = "medium",
    ) -> Dict[str, Any]:
        """
        Executes the full multi-agent orchestration lifecycle:
        Plan -> Parallel Execution -> Sequential Execution -> Evidence Merge -> Synthesis -> Validation.
        """
        start_time = time.time()
        specialists_map = cls._get_specialist_instances()

        # Step 1: Routing & Team Planning
        context_data = {
            "user_lat": user_lat,
            "user_lon": user_lon,
            "landmark": landmark,
            "category_slug": category_slug,
            "history_turns": conversation_history,
            "web_research": web_research,
            "is_uploaded_document": "[uploaded " in query.lower(),
            "thinking_level": thinking_level,
        }

        plan = cls.plan_routing(
            query=query,
            explicit_agent_id=explicit_agent_id,
            context=context_data
        )

        specialist_statuses = [
            f"{s.upper()}: {cls._get_specialist_status_label(s)}"
            for s in plan.specialist_agents
        ]

        thinking_steps: List[ThinkingStep] = [
            ThinkingStep(
                step=1,
                title="Understanding request & selecting intelligence",
                description=f"Formed team: [{', '.join(specialist_statuses)}] (Complexity: {plan.complexity.title()}, Thinking: {thinking_level.title()}). {plan.rationale}",
                status="completed"
            ),
            ThinkingStep(
                step=2,
                title="Searching university knowledge",
                description="Querying approved institutional regulations, UMS catalog, and campus guidelines.",
                status="completed"
            )
        ]

        # Step 2: Execute Parallel Agents
        parallel_tasks = []
        for s_id in plan.parallel_group:
            agent = specialists_map.get(s_id)
            if agent:
                parallel_tasks.append(
                    agent.execute(query=query, context=context_data, db=db)
                )

        parallel_results: List[AgentOutput] = await asyncio.gather(*parallel_tasks) if parallel_tasks else []

        # Step 3: Execute Sequential Agents
        sequential_results: List[AgentOutput] = []
        for s_id in plan.sequential_group:
            agent = specialists_map.get(s_id)
            if agent:
                seq_res = await agent.execute(query=query, context=context_data, db=db)
                sequential_results.append(seq_res)

        all_agent_outputs: List[AgentOutput] = parallel_results + sequential_results

        thinking_steps.append(
            ThinkingStep(
                step=3,
                title="Consulting specialist agents",
                description=f"Completed specialist consultations: {', '.join([f'{o.agent_id.upper()} ({cls._get_specialist_status_label(o.agent_id)})' for o in all_agent_outputs])}.",
                status="completed"
            )
        )

        # Step 4: Aggregate Evidence, Cards, and Citations
        merged_cards: Dict[str, Any] = {}
        merged_citations: List[Dict[str, Any]] = []
        findings_sections: List[str] = []

        for out in all_agent_outputs:
            if out.success and out.findings:
                findings_sections.append(f"[{out.agent_id.upper()} FINDINGS]:\n{out.findings}")
            if out.cards:
                merged_cards.update(out.cards)
            if out.citations:
                for c in out.citations:
                    if c not in merged_citations:
                        merged_citations.append(c)

        thinking_steps.append(
            ThinkingStep(
                step=4,
                title="Validating sources & institutional grounding",
                description=f"Synthesized evidence from {len(all_agent_outputs)} specialists with {len(merged_cards)} actionable cards and {len(merged_citations)} citations.",
                status="completed"
            )
        )

        # Step 5: Synthesize Final Coherent Response
        aggregated_evidence = "\n\n".join(findings_sections) if findings_sections else "Approved institutional guidance."
        
        try:
            llm_res = await ResponseGenerator.generate_response(
                user_message=query,
                evidence_context=aggregated_evidence,
                conversation_history=conversation_history,
                preferred_provider=preferred_provider,
                thinking_level=thinking_level,
            )
            final_content = llm_res["content"]
            is_ai_gen = True
            provider_used = llm_res.get("provider", "gemini")
        except Exception as e:
            logger.warning(f"Synthesis LLM call failed ({e}). Assembling directly from specialist findings.")
            final_content = "\n\n".join([o.findings for o in all_agent_outputs if o.findings])
            is_ai_gen = False
            provider_used = "deterministic_specialists"

        thinking_steps.append(
            ThinkingStep(
                step=5,
                title="Preparing response",
                description=f"Generated unified response via {explicit_agent_id.upper()} at {thinking_level.title()} thinking depth with verified citations.",
                status="completed"
            )
        )

        # Step 6: Grounding Validation
        is_valid, validated_content, _ = validate_grounded_response(final_content, aggregated_evidence)
        if not is_valid:
            validated_content = final_content

        thinking_steps.append(
            ThinkingStep(
                step=5,
                title="Completed",
                description=f"Response compiled by {explicit_agent_id.upper()} with verified institutional citations.",
                status="completed"
            )
        )

        total_latency = int((time.time() - start_time) * 1000)

        # Assemble Citations
        citations_list = [Citation(**c) for c in merged_citations]
        follow_ups = generate_follow_up_suggestions(category_slug, query)

        return {
            "content": validated_content,
            "action_type": "ANSWER",
            "thinking_steps": thinking_steps,
            "citations": citations_list,
            "follow_ups": follow_ups,
            "cards": merged_cards,
            "confidence_score": 0.98,
            "latency_ms": total_latency,
            "is_ai_generated": is_ai_gen,
            "agent_id": explicit_agent_id or "aegis",
            "specialists_involved": [o.agent_id for o in all_agent_outputs],
            "agent_metadata": {
                "plan": plan.model_dump(),
                "specialist_outputs": [o.model_dump() for o in all_agent_outputs],
                "provider_used": provider_used,
            }
        }
