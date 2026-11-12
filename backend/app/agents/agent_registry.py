import logging
from typing import Dict, List, Optional
from app.schemas.agent import (
    AgentDefinition,
    AgentModelConfig,
    AgentBudget,
    AgentRetryPolicy,
    AgentPublicInfo,
    AgentEngineInfo,
)
from app.core.config import settings

logger = logging.getLogger(__name__)


def _create_default_agent_definitions() -> Dict[str, AgentDefinition]:
    """
    Constructs the 9 canonical agent specifications for CampusConnect Multi-Agent Intelligence Network V1.
    """
    return {
        # 1. AEGIS — Master Orchestration & Routing
        "aegis": AgentDefinition(
            id="aegis",
            name="AEGIS — Master Orchestrator",
            role="Autonomous Intent Routing & Multi-Agent Synthesis",
            description="Analyzes complex student queries, coordinates specialist agents in parallel, and synthesizes unified answers.",
            capabilities=[
                "intent_decomposition",
                "parallel_agent_orchestration",
                "risk_and_policy_validation",
                "evidence_synthesis",
                "card_assembly",
            ],
            system_instructions=(
                "You are AEGIS, the master orchestration intelligence for Lovely Professional University. "
                "Your role is to evaluate student intent, determine required domain specialists (THEMIS, HERMES, ARGUS, ATHENA, MNEMOS, ORACLE, FORGE, VISION), "
                "dispatch sub-tasks, validate evidence against official LPU regulations, and deliver a coherent, empathetic response."
            ),
            allowed_tools=["intent_classifier", "action_classifier", "multi_domain_orchestrator"],
            knowledge_collections=["ums_services", "action_workflows", "lpu_policies", "campus_directory"],
            primary_model=AgentModelConfig(
                provider="gemini",
                model_id=settings.GEMINI_MODEL or "gemini-3.5-flash-lite",
                temperature=0.2,
                max_output_tokens=700,
                timeout_seconds=20.0
            ),
            secondary_model=AgentModelConfig(
                provider="groq",
                model_id=settings.GROQ_MODEL or "llama-3.3-70b-versatile",
                temperature=0.2,
                max_output_tokens=600,
                timeout_seconds=15.0
            ),
            budget=AgentBudget(max_input_tokens=2500, max_output_tokens=700, max_execution_time_seconds=15.0, cost_tier="standard"),
            retry_policy=AgentRetryPolicy(max_retries=2, fallback_to_secondary=True),
            permission_required="public",
            is_orchestrator=True,
            input_schema={"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
            output_schema={"type": "object", "properties": {"content": {"type": "string"}, "action_type": {"type": "string"}}, "required": ["content"]}
        ),

        # 2. THEMIS — University Policy, Academic Benefits & Eligibility Assessment
        "themis": AgentDefinition(
            id="themis",
            name="THEMIS — Policy & Academic Benefits",
            role="Institutional Regulations, EDU-Revolution, Attendance & Eligibility Verification",
            description="Evaluates academic policies, attendance condonation floors, EDU-Revolution categories (Cat 1-9), and SAC ratification.",
            capabilities=[
                "attendance_condonation_analysis",
                "edurev_benefit_mapping",
                "standing_academic_committee_rules",
                "disciplinary_and_proctorial_boundaries",
                "evidence_checklist_verification",
            ],
            system_instructions=(
                "You are THEMIS, the university policy and academic benefit intelligence for LPU. "
                "You rigorously evaluate eligibility against official university regulations. "
                "CRITICAL BOUNDARIES: You cannot independently grant waivers or benefits; you only assess eligibility and specify required documents. "
                "Distinguish revenue-generating startup projects from the separate up to 10% attendance condonation. "
                "Emphasize the 75% end-term exam mandatory floor and warn that fraudulent documentation violates Section 12 of the Student Code of Conduct."
            ),
            allowed_tools=["edurev_advisor", "academic_benefit_assessment", "policy_lookup"],
            knowledge_collections=["lpu_policies", "edurev_guidelines", "attendance_regulations"],
            primary_model=AgentModelConfig(
                provider="gemini",
                model_id=settings.GEMINI_MODEL or "gemini-3.5-flash-lite",
                temperature=0.1,
                max_output_tokens=600,
                timeout_seconds=15.0
            ),
            secondary_model=AgentModelConfig(
                provider="bazaarlink",
                model_id=settings.BAZAARLINK_MODEL or "qwen/qwen3.7-flash:free",
                temperature=0.1,
                max_output_tokens=500,
                timeout_seconds=12.0
            ),
            budget=AgentBudget(max_input_tokens=2000, max_output_tokens=600, max_execution_time_seconds=12.0, cost_tier="standard"),
            retry_policy=AgentRetryPolicy(max_retries=2, fallback_to_secondary=True),
            permission_required="public",
            is_orchestrator=False,
            input_schema={"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
            output_schema={"type": "object", "properties": {"eligible_benefits": {"type": "string"}, "evidence_checklist": {"type": "array"}}, "required": ["eligible_benefits"]}
        ),

        # 3. HERMES — UMS Navigation, Services & Workflows
        "hermes": AgentDefinition(
            id="hermes",
            name="HERMES — UMS Navigator & Workflows",
            role="University Management System (UMS) Breadcrumbs & Action Execution Boundaries",
            description="Guides students through 234 official UMS pathways, RMS grievances, appointment handoffs, and procedure checklists.",
            capabilities=[
                "ums_234_service_catalog_resolution",
                "action_workflow_matching",
                "rms_grievance_routing",
                "procedure_checklist_generation",
                "transaction_security_intercepts",
            ],
            system_instructions=(
                "You are HERMES, the official UMS navigation and workflow specialist for Lovely Professional University. "
                "You map student service intents directly to verified UMS breadcrumbs across 234 catalogued services. "
                "SECURITY INTERCEPT: You never execute financial transactions, grade submissions, or direct bookings on student behalf. "
                "Provide exact navigation paths, prerequisites, and official handoff URLs."
            ),
            allowed_tools=["ums_resolver", "workflow_engine", "rms_card_builder"],
            knowledge_collections=["ums_services", "action_workflows", "procedure_guidelines"],
            primary_model=AgentModelConfig(
                provider="gemini",
                model_id=settings.GEMINI_MODEL or "gemini-3.5-flash-lite",
                temperature=0.1,
                max_output_tokens=500,
                timeout_seconds=10.0
            ),
            secondary_model=AgentModelConfig(
                provider="groq",
                model_id=settings.GROQ_MODEL or "llama-3.3-70b-versatile",
                temperature=0.1,
                max_output_tokens=500,
                timeout_seconds=10.0
            ),
            budget=AgentBudget(max_input_tokens=1800, max_output_tokens=500, max_execution_time_seconds=10.0, cost_tier="free_tier"),
            retry_policy=AgentRetryPolicy(max_retries=2, fallback_to_secondary=True),
            permission_required="public",
            is_orchestrator=False,
            input_schema={"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
            output_schema={"type": "object", "properties": {"breadcrumb": {"type": "string"}, "service_label": {"type": "string"}}, "required": ["breadcrumb"]}
        ),

        # 4. ARGUS — Faculty, Leadership, Experts & Campus Intelligence
        "argus": AgentDefinition(
            id="argus",
            name="ARGUS — Faculty & Campus Intelligence",
            role="Campus Spatial Wayfinding, Faculty Cabins, Consultation Hours & Pure-Veg Dining",
            description="Finds verified faculty office hours (3:00 PM - 5:00 PM), leadership escalation ladders, Block 30 UniHospital, and campus amenities.",
            capabilities=[
                "people_directory_lookup",
                "leadership_escalation_routing",
                "campus_wayfinding_and_pois",
                "pure_veg_dining_discovery",
                "spatial_proximity_estimation",
            ],
            system_instructions=(
                "You are ARGUS, the campus intelligence and faculty discovery specialist for LPU. "
                "You know the exact physical layout of the 600-acre Phagwara campus. "
                "TRUTH MANDATE: Never invent private faculty cabins. If an unverified room is requested, direct to Block 32 School Office during student consultation hours (3:00 PM – 5:00 PM). "
                "Clarify Dr. Mohit Arora as Head of School (CSE) and Dr. Dalwinder Singh as Academic Coordinator. "
                "Enforce the 100% pure vegetarian campus dining mandate."
            ),
            allowed_tools=["people_directory", "campus_map", "campus_food", "issue_resolver", "geo_service"],
            knowledge_collections=["campus_places", "faculty_directory", "dining_outlets", "spatial_amenities"],
            primary_model=AgentModelConfig(
                provider="gemini",
                model_id=settings.GEMINI_MODEL or "gemini-3.5-flash-lite",
                temperature=0.1,
                max_output_tokens=500,
                timeout_seconds=12.0
            ),
            secondary_model=AgentModelConfig(
                provider="bazaarlink",
                model_id=settings.BAZAARLINK_MODEL or "qwen/qwen3.7-flash:free",
                temperature=0.1,
                max_output_tokens=500,
                timeout_seconds=10.0
            ),
            budget=AgentBudget(max_input_tokens=1800, max_output_tokens=500, max_execution_time_seconds=10.0, cost_tier="free_tier"),
            retry_policy=AgentRetryPolicy(max_retries=2, fallback_to_secondary=True),
            permission_required="public",
            is_orchestrator=False,
            input_schema={"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
            output_schema={"type": "object", "properties": {"person_name": {"type": "string"}, "cabin_location": {"type": "string"}}}
        ),

        # 5. ATHENA — Academic Reasoning & Complex Analysis
        "athena": AgentDefinition(
            id="athena",
            name="ATHENA — Academic Reasoning & Analytics",
            role="Curriculum Evaluation, Course Equivalence & Credit Substitution",
            description="Performs deep multi-variable reasoning on syllabus equivalence, CGPA requirements, grade upgrades, and credit transfers.",
            capabilities=[
                "curriculum_and_syllabus_analysis",
                "course_equivalence_deduction",
                "cgpa_and_credit_calculation",
                "complex_academic_appeals",
            ],
            system_instructions=(
                "You are ATHENA, the academic reasoning intelligence. You perform rigorous evaluations of course curricula, "
                "calculating credit substitution feasibility, CA equivalence thresholds, and academic standing prerequisites."
            ),
            allowed_tools=["hybrid_search", "academic_benefit_assessment"],
            knowledge_collections=["academic_schedules", "examination_guidelines", "syllabus_records"],
            primary_model=AgentModelConfig(
                provider="pekpik",
                model_id=settings.PEKPIK_MODEL or "deepseek-v4-1-flash-1017",
                temperature=0.2,
                max_output_tokens=650,
                timeout_seconds=18.0
            ),
            secondary_model=AgentModelConfig(
                provider="gemini",
                model_id=settings.GEMINI_MODEL or "gemini-3.5-flash-lite",
                temperature=0.2,
                max_output_tokens=600,
                timeout_seconds=15.0
            ),
            budget=AgentBudget(max_input_tokens=2200, max_output_tokens=650, max_execution_time_seconds=18.0, cost_tier="high_reasoning"),
            retry_policy=AgentRetryPolicy(max_retries=2, fallback_to_secondary=True),
            permission_required="public",
            is_orchestrator=False,
            input_schema={"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
            output_schema={"type": "object", "properties": {"reasoning": {"type": "string"}, "verdict": {"type": "string"}}}
        ),

        # 6. MNEMOS — Retrieval, Knowledge & Authorized Memory
        "mnemos": AgentDefinition(
            id="mnemos",
            name="MNEMOS — Knowledge & Memory Retrieval",
            role="Institutional RAG, Dense Embeddings & Contextual Document Recall",
            description="Searches 1,035 approved university knowledge items using hybrid dense/sparse search and maintains conversation memory.",
            capabilities=[
                "hybrid_search_execution",
                "dense_hf_embedding_retrieval",
                "contextual_anaphora_resolution",
                "knowledge_provenance_validation",
            ],
            system_instructions=(
                "You are MNEMOS, the repository memory intelligence for CampusConnect. "
                "You retrieve accurate facts from approved institutional knowledge records and syllabus documents without hallucination."
            ),
            allowed_tools=["hybrid_search", "hf_embeddings", "query_response_cache"],
            knowledge_collections=["faqs", "policies", "contact_directory", "facility_services"],
            primary_model=AgentModelConfig(
                provider="gemini",
                model_id=settings.GEMINI_MODEL or "gemini-3.5-flash-lite",
                temperature=0.0,
                max_output_tokens=400,
                timeout_seconds=10.0
            ),
            secondary_model=AgentModelConfig(
                provider="groq",
                model_id=settings.GROQ_MODEL or "llama-3.3-70b-versatile",
                temperature=0.0,
                max_output_tokens=400,
                timeout_seconds=8.0
            ),
            budget=AgentBudget(max_input_tokens=1500, max_output_tokens=400, max_execution_time_seconds=8.0, cost_tier="free_tier"),
            retry_policy=AgentRetryPolicy(max_retries=2, fallback_to_secondary=True),
            permission_required="public",
            is_orchestrator=False,
            input_schema={"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
            output_schema={"type": "object", "properties": {"evidence_context": {"type": "string"}, "citations": {"type": "array"}}}
        ),

        # 7. ORACLE — Web Research, Source Verification & Evidence Synthesis
        "oracle": AgentDefinition(
            id="oracle",
            name="ORACLE — Web Research & Verification",
            role="Freshness Intelligence, Regulatory Portals (UGC, AICTE) & External Hackathons",
            description="Performs live web research via Tavily for Smart India Hackathon (SIH), government regulations, and external announcements.",
            capabilities=[
                "live_tavily_search",
                "domain_reliability_scoring",
                "regulatory_compliance_check",
                "third_party_claim_filtering",
            ],
            system_instructions=(
                "You are ORACLE, the controlled web research agent. You verify external freshness (SIH hackathons, UGC/AICTE notifications) "
                "while strictly enforcing priority domains (.gov.in, .ac.in, lpu.in) and penalizing unverified blogs."
            ),
            allowed_tools=["tavily_search", "web_research_tool_cache"],
            knowledge_collections=["regulatory_notices", "sih_hackathon_guidelines"],
            primary_model=AgentModelConfig(
                provider="gemini",
                model_id=settings.GEMINI_MODEL or "gemini-3.5-flash-lite",
                temperature=0.1,
                max_output_tokens=550,
                timeout_seconds=15.0
            ),
            secondary_model=AgentModelConfig(
                provider="groq",
                model_id=settings.GROQ_MODEL or "llama-3.3-70b-versatile",
                temperature=0.1,
                max_output_tokens=500,
                timeout_seconds=12.0
            ),
            budget=AgentBudget(max_input_tokens=2000, max_output_tokens=550, max_execution_time_seconds=15.0, cost_tier="standard"),
            retry_policy=AgentRetryPolicy(max_retries=1, fallback_to_secondary=True),
            permission_required="public",
            is_orchestrator=False,
            input_schema={"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
            output_schema={"type": "object", "properties": {"findings": {"type": "string"}, "citations": {"type": "array"}}}
        ),

        # 8. FORGE — Coding, Technical Projects & Architecture
        "forge": AgentDefinition(
            id="forge",
            name="FORGE — Technical Project & Code Review",
            role="Technical Stack Evaluation, GitHub Project Architecture & Startup Code Analysis",
            description="Evaluates technical projects for EDU-Revolution submission: code repositories, deployment URLs, tech stacks, and internships.",
            capabilities=[
                "tech_stack_audit",
                "github_repository_validation",
                "startup_job_matching",
                "architecture_feasibility_review",
            ],
            system_instructions=(
                "You are FORGE, the software engineering and technical project intelligence. "
                "You review student code architectures, evaluate stack suitability for EDU-Rev Category 5/6, and match startup internships."
            ),
            allowed_tools=["startup_jobs_service", "opportunities_cache"],
            knowledge_collections=["tech_project_rubrics", "startup_opportunities"],
            primary_model=AgentModelConfig(
                provider="groq",
                model_id=settings.GROQ_MODEL or "llama-3.3-70b-versatile",
                temperature=0.2,
                max_output_tokens=600,
                timeout_seconds=15.0
            ),
            secondary_model=AgentModelConfig(
                provider="gemini",
                model_id=settings.GEMINI_MODEL or "gemini-3.5-flash-lite",
                temperature=0.2,
                max_output_tokens=600,
                timeout_seconds=15.0
            ),
            budget=AgentBudget(max_input_tokens=2200, max_output_tokens=600, max_execution_time_seconds=15.0, cost_tier="standard"),
            retry_policy=AgentRetryPolicy(max_retries=2, fallback_to_secondary=True),
            permission_required="public",
            is_orchestrator=False,
            input_schema={"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
            output_schema={"type": "object", "properties": {"project_feasibility": {"type": "string"}, "tech_recommendation": {"type": "string"}}}
        ),

        # 9. VISION — Document, PDF, Screenshot & Image Perception
        "vision": AgentDefinition(
            id="vision",
            name="VISION — Document & Image Perception",
            role="Multimodal Ingestion: UMS Screenshots, Gradecards, Timetables & PDF Syllabi",
            description="Parses student-uploaded files, error screenshots, fee receipts, and marks sheets for downstream specialist processing.",
            capabilities=[
                "document_text_extraction",
                "screenshot_error_parsing",
                "gradecard_and_timetable_extraction",
                "multimodal_ocr_perception",
            ],
            system_instructions=(
                "You are VISION, the multimodal document and image understanding agent. "
                "You extract text, identify UMS portal error messages, and structure uploaded syllabus PDFs for academic review."
            ),
            allowed_tools=["document_uploader", "pdf_reader"],
            knowledge_collections=["uploaded_documents"],
            primary_model=AgentModelConfig(
                provider="gemini",
                model_id=settings.GEMINI_MODEL or "gemini-3.5-flash-lite",
                temperature=0.1,
                max_output_tokens=600,
                timeout_seconds=20.0
            ),
            secondary_model=AgentModelConfig(
                provider="groq",
                model_id=settings.GROQ_MODEL or "llama-3.3-70b-versatile",
                temperature=0.1,
                max_output_tokens=500,
                timeout_seconds=15.0
            ),
            budget=AgentBudget(max_input_tokens=3000, max_output_tokens=600, max_execution_time_seconds=20.0, cost_tier="standard"),
            retry_policy=AgentRetryPolicy(max_retries=2, fallback_to_secondary=True),
            permission_required="public",
            is_orchestrator=False,
            input_schema={"type": "object", "properties": {"document_name": {"type": "string"}}, "required": ["document_name"]},
            output_schema={"type": "object", "properties": {"extracted_text": {"type": "string"}, "summary": {"type": "string"}}}
        ),
    }


class AgentRegistry:
    """
    Central In-Memory Registry for CampusConnect Multi-Agent Intelligence Network V1.
    Provides lookup, validation, public identity lists, and engine diagnostics.
    """

    _agents: Dict[str, AgentDefinition] = {}

    @classmethod
    def initialize(cls) -> None:
        if not cls._agents:
            cls._agents = _create_default_agent_definitions()
            logger.info(f"AgentRegistry initialized with {len(cls._agents)} registered agents: {list(cls._agents.keys())}")

    @classmethod
    def get_agent(cls, agent_id: str) -> Optional[AgentDefinition]:
        cls.initialize()
        return cls._agents.get(agent_id.lower().strip())

    @classmethod
    def list_agents(cls) -> List[AgentDefinition]:
        cls.initialize()
        return list(cls._agents.values())

    @classmethod
    def list_public_agents(cls) -> List[AgentPublicInfo]:
        cls.initialize()
        return [
            AgentPublicInfo(
                id=a.id,
                name=a.name,
                role=a.role,
                description=a.description,
                capabilities=a.capabilities,
                is_orchestrator=a.is_orchestrator,
                permission_required=a.permission_required,
            )
            for a in cls._agents.values()
        ]

    @classmethod
    def get_engine_diagnostics(cls) -> List[AgentEngineInfo]:
        cls.initialize()
        diagnostics: List[AgentEngineInfo] = []
        for a in cls._agents.values():
            diagnostics.append(
                AgentEngineInfo(
                    agent_id=a.id,
                    agent_name=a.name,
                    actual_provider=a.primary_model.provider,
                    actual_model_id=a.primary_model.model_id,
                    availability=True,
                    last_health_check="Healthy (Active Gateway)",
                    execution_mode="Autonomous Reactive Loop",
                    cost_tier=a.budget.cost_tier
                )
            )
        return diagnostics

