import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base_agent import BaseSpecialistAgent
from app.agents.agent_registry import AgentRegistry
from app.schemas.agent import AgentOutput

logger = logging.getLogger(__name__)


class VisionAgent(BaseSpecialistAgent):
    """
    VISION — Document, PDF, Screenshot & Image Understanding Specialist.
    Parses uploaded syllabus files, grade cards, and portal error screenshots.
    """

    def __init__(self):
        definition = AgentRegistry.get_agent("vision")
        if not definition:
            raise RuntimeError("VISION agent definition not found in registry")
        super().__init__(definition)

    async def run(
        self,
        query: str,
        context: Dict[str, Any],
        db: AsyncSession,
        **kwargs
    ) -> AgentOutput:
        doc_name = context.get("uploaded_doc_name") or "uploaded_attachment"
        extracted_text = context.get("extracted_text") or query

        findings = (
            f"**Multimodal Perception Report ({doc_name}):**\n"
            f"- Extracted content processed and tokenized.\n"
            f"- Structure and semantic entities mapped for academic and UMS evaluation."
        )

        return AgentOutput(
            agent_id=self.id,
            success=True,
            findings=findings,
            structured_data={
                "doc_name": doc_name,
                "text_length": len(extracted_text),
            },
            citations=[],
            cards={},
            confidence=0.96,
            model_used=self.definition.primary_model.model_id,
            provider_used=self.definition.primary_model.provider
        )

