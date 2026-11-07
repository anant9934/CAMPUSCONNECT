import logging
import re
from typing import List, Dict, Any, Optional
from app.services.gemini_service import gemini_service

logger = logging.getLogger(__name__)


def generate_rule_based_variants(record_type: str, title: str, content: str) -> List[str]:
    """
    Deterministic fallback to generate query variants from title and content
    without making external model calls.
    """
    variants = []
    clean_title = title.rstrip(".?")

    if record_type == "contact_directory":
        variants.extend([
            f"How do I contact {clean_title}?",
            f"Where is the office for {clean_title}?",
            f"Email address and phone number for {clean_title}",
            f"Who is {clean_title} at LPU?"
        ])
    elif record_type == "policy":
        variants.extend([
            f"What is LPU's policy on {clean_title}?",
            f"What are the rules regarding {clean_title}?",
            f"What happens if {clean_title} conditions are not met?",
            f"Official regulation for {clean_title}"
        ])
    elif record_type == "academic_schedule":
        variants.extend([
            f"When is the schedule for {clean_title}?",
            f"Important dates for {clean_title}",
            f"What is the timeline for {clean_title} at LPU?"
        ])
    elif record_type == "facility_service":
        variants.extend([
            f"Where is {clean_title} located on campus?",
            f"What are the timings for {clean_title}?",
            f"Facilities and services at {clean_title}"
        ])
    elif record_type == "placement_procedure":
        variants.extend([
            f"What are the placement procedures for {clean_title}?",
            f"Eligibility and packages for {clean_title}?",
            f"How does LPU conduct recruitment for {clean_title}?"
        ])
    elif record_type == "library_resource":
        variants.extend([
            f"How do I access {clean_title} in LPU library?",
            f"Where can I find {clean_title}?",
            f"Digital resources for {clean_title}"
        ])
    elif record_type == "grievance_procedure":
        variants.extend([
            f"How do I submit a grievance for {clean_title}?",
            f"What is the complaint procedure for {clean_title}?",
            f"Who handles {clean_title} issues at LPU?"
        ])
    else:
        variants.extend([
            f"Tell me about {clean_title} at LPU",
            f"How does {clean_title} work at Lovely Professional University?",
            f"Information on {clean_title}"
        ])

    return list(set(variants))


async def generate_searchable_variants(record: Dict[str, Any]) -> List[str]:
    """
    Generates searchable student question variants for an approved record.
    Never alters the underlying institutional facts.
    """
    title = record.get("title", "")
    content = record.get("content", "")[:600]
    record_type = record.get("record_type", "faq")

    # If Gemini is not configured or in fallback mode, use deterministic generator
    if not gemini_service.is_configured():
        return generate_rule_based_variants(record_type, title, content)

    prompt = f"""You are generating student query search variants for the university knowledge base.
Institutional Record:
Type: {record_type}
Title: {title}
Content: {content}

TASK:
Output exactly 3 to 4 realistic questions or search phrases that an LPU student might type into the search bar to find this record.
STRICT RULES:
1. Do NOT invent new facts or alter any numbers, names, or locations.
2. Only output the questions, one per line.
3. No prefixes like "1." or "- ". Just the clean questions."""

    try:
        import asyncio
        loop = asyncio.get_running_loop()
        res = await asyncio.wait_for(
            loop.run_in_executor(
                None,
                lambda: gemini_service.client.models.generate_content(
                    model=gemini_service.client._model if hasattr(gemini_service.client, '_model') else "gemini-2.5-flash",
                    contents=prompt
                )
            ),
            timeout=8.0
        )
        if res and hasattr(res, "text") and res.text:
            lines = [l.strip().lstrip("-•*123456789. ") for l in res.text.split("\n") if l.strip()]
            valid = [l for l in lines if len(l) > 5 and not l.startswith("```")]
            if valid:
                return valid[:5]
    except Exception as e:
        logger.warning(f"Gemini variant generation failed for '{title}': {e}. Using deterministic generator.")

    return generate_rule_based_variants(record_type, title, content)

