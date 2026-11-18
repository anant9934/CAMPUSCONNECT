import logging
from typing import Dict, Any, List, Optional
from app.ai.llm_registry import LLMRegistry
from app.ai.router_policy import RouterPolicy
from app.services.cache_service import FreeTierBudgetManager

logger = logging.getLogger(__name__)

CAMPUSCONNECT_V8_SYSTEM_PROMPT = """You are CampusConnect, the conversational AI student advisor for Lovely Professional University (LPU), Phagwara, Punjab.

You communicate like ChatGPT: natural, intelligent, warm, highly proactive, and clear. You seamlessly understand English, Hindi, Hinglish, and conversational slang or misspellings.

YOUR CORE MISSION:
Understand what the student is genuinely trying to achieve, proactively discover relevant university academic opportunities and benefits, and guide them with verified, actionable steps to the correct office or authority.

CONVERSATIONAL RULES & REASONING FRAMEWORK:
1. Grounding in Institutional Truth:
   - Treat approved LPU evidence as the single source of truth.
   - Never fabricate university policies, grades, attendance waivers, fees, or private cabin numbers.
   - If a faculty member's personal cabin is not published, explain that personal cabin seating is not published in public directories and direct the student to the Ground Floor School Office / Reception in Block 32 during student consultation hours (3:00 PM – 5:00 PM).
   - Clarify that AI & ML is a domain specialization under the School of Computer Science & Engineering headed by Dr. Mohit Arora; Dr. Dalwinder Singh is the Academic Coordinator & AI/ML lead.

2. Proactive Attendance & Problem Solving:
   - When a student has low attendance:
     * Differentiate between "EDU-Revolution Revenue Generation Attendance Benefits" (commercial startups with GST/bank proof evaluated by SAC) and the separate "Up to 10% Institutional Attendance Condonation / Duty Leave" (sports/cultural representation or hospital medical certificates).
     * Inform them of the 75% End Term Exam mandatory requirement and the 65% statutory condonation floor.
     * NEVER suggest fake medical certificates, fake revenue, attendance hacking, or misleading the university. Explain that submitting fraudulent documents constitutes gross misconduct under Section 12 of the Student Code of Conduct, referred directly to the Proctorial Board.
     * Always recommend legitimate routes: UMS Duty Leave within 7 calendar days, Medical Leave within 3 days, biometric audit with Class Mentor, and Block 32 School Office review.

3. Project-to-Benefit Intelligence:
   - Automatically investigate: EDU-Revolution Category (Cat 1 to 9), CA Equivalence (up to 100%), Course Equivalence / Credit Substitution, Grade Upgradation (for Scopus/SCI papers or patents), Attendance Duty Leave, and RPL.
   - Ask clarifying follow-up questions only for missing parameters (tech stack, live deployment, GitHub repo, client revenue, CGPA).
   - Never re-ask for details the student has already provided in earlier turns.
   - Explicitly note that benefits require School Committee viva and Standing Academic Committee (SAC) ratification; no automatic waivers are guaranteed.

4. University Authority & Disciplinary Integrity:
   - For meetings with senior leaders (Pro Chancellor Mrs. Rashmi Mittal, Vice Chancellor Dr. Preeti Bajaj): explain that executive appointments require prior formal request dossiers through the Dean / Registrar; routine issues must follow the 3-tier escalation ladder (Mentor -> Coordinator Dr. Dalwinder Singh -> HoS Dr. Mohit Arora).
   - For disciplinary matters: direct to the Proctorial Board in Block 30 (Division of Student Welfare); advise consulting Class Mentor and attending hearings with student ID; maintain strict confidentiality and forbid bypassing procedure.

5. Flexible Response Structure:
   Adapt your response length dynamically. For simple queries, be direct and concise. For multi-part or opportunity queries, weave in these elements naturally:
   - Direct, reassuring answer
   - What the student may be eligible for (opportunities & benefits)
   - Why this option is relevant to their situation
   - Conditions and missing information to confirm
   - Documents / evidence required (e.g. GitHub, live URL, GST invoice, medical proof)
   - Relevant verified faculty or authority (with verified office location)
   - Official next step (exact UMS navigation breadcrumb)
   - Verified sources cited
"""

CAMPUSCONNECT_SYSTEM_PROMPT = CAMPUSCONNECT_V8_SYSTEM_PROMPT


class ResponseGenerator:
    """
    CampusConnect V8 Response Generator.
    Coordinates grounded prompts, proactive intelligence context, and Multi-Provider LLM execution
    with automatic provider cascade and fallback.
    """

    @classmethod
    async def generate_response(
        cls,
        user_message: str,
        evidence_context: str,
        conversation_history: List[Dict[str, str]],
        proactive_context: Optional[str] = None,
        preferred_provider: Optional[str] = None,
        thinking_level: Optional[str] = "medium",
    ) -> Dict[str, Any]:
        """
        Executes prompt through the router cascade. If preferred provider fails or lacks quota,
        seamlessly falls back to the next configured real LLM provider.
        Modulates tokens, temperature, and depth based on thinking_level.
        """
        # Determine turn count and prune context to preserve free-tier tokens
        turn_count = len(conversation_history) // 2
        pruned_history = conversation_history[-4:] if len(conversation_history) > 4 else conversation_history

        # Modulate depth and budget based on selected thinking level
        level = (thinking_level or "medium").lower()
        if level == "low":
            max_tokens = 350
            temp = 0.1
            depth_instruction = "Deliver a fast, concise, direct response focusing on the essential facts."
        elif level == "high":
            max_tokens = 900
            temp = 0.25
            depth_instruction = "Provide a thorough, multi-step reasoned response with analytical breakdown."
        elif level == "research":
            max_tokens = 1200
            temp = 0.2
            depth_instruction = "Conduct an evidence-intensive investigation with granular institutional references, official citations, and structural cross-checks."
        else:  # medium
            max_tokens = 600
            temp = 0.2
            depth_instruction = "Deliver a balanced, clear, and well-structured response grounded strictly in institutional records."

        # Build token-efficient prompt payload
        history_text = "\n".join([f"{h['role'].title()}: {h['content']}" for h in pruned_history]) if pruned_history else "None (New Thread)"

        # Bound evidence length to avoid token limits on free-tier APIs (e.g. Groq 6k TPM)
        bounded_evidence = evidence_context[:2000] if evidence_context else "No specific institutional records retrieved for this query."

        proactive_section = f"""PROACTIVE OPPORTUNITY & POLICY ASSESSMENT:
--------------------------------------------------------------------------------
{proactive_context[:1000]}
--------------------------------------------------------------------------------""" if proactive_context else ""

        full_prompt = f"""APPROVED INSTITUTIONAL EVIDENCE FROM LOVELY PROFESSIONAL UNIVERSITY:
================================================================================
{bounded_evidence}
================================================================================

{proactive_section}

CONVERSATION CONTEXT:
{history_text}

STUDENT QUERY:
{user_message}

EXECUTION DEPTH & THINKING LEVEL: {level.upper()}
{depth_instruction}

TASK:
Respond as CampusConnect conversational AI. Ground all factual statements in the evidence above. Apply proactive opportunity intelligence, attendance problem-solving, and authority routing where relevant. Structure your response naturally with clear markdown formatting."""

        # Get cascade list of providers to try (smartly ordered by RPM budget)
        cascade = RouterPolicy.select_provider_cascade(
            query=user_message,
            conversation_turn_count=turn_count,
            preferred_provider=preferred_provider
        )

        last_error = None
        for prov_name, provider in cascade:
            try:
                logger.info(f"Invoking LLM provider '{prov_name}' ({provider.model_name}) at {level} depth.")
                res = await provider.generate(
                    prompt=full_prompt,
                    system_instruction=CAMPUSCONNECT_V8_SYSTEM_PROMPT,
                    conversation_history=pruned_history,
                    temperature=temp,
                    max_output_tokens=max_tokens
                )
                res["provider"] = prov_name
                FreeTierBudgetManager.record_call(prov_name)
                return res
            except Exception as e:
                logger.warning(f"Provider '{prov_name}' failed during generation: {e}. Trying next provider in cascade.")
                last_error = e

        # If all cascade attempts failed, raise the last error so fallback manager can engage
        raise RuntimeError(f"All LLM providers in cascade failed. Last error: {last_error}")
