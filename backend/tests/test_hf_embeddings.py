import pytest
import numpy as np

from app.core.config import settings
from app.services.rag.hf_embedding_service import HuggingFaceEmbeddingService
from app.services.rag.semantic_search import SemanticSearchEngine, create_dense_semantic_vector


def test_hf_embedding_service_config():
    """Verify Hugging Face token and model configuration."""
    token = HuggingFaceEmbeddingService.get_token()
    assert token != ""
    assert token.startswith("hf_")
    assert HuggingFaceEmbeddingService.is_available() is True
    assert settings.HF_EMBEDDING_MODEL == "BAAI/bge-small-en-v1.5"
    assert settings.HF_EMBEDDING_DIMENSION == 384


def test_local_dense_semantic_vector():
    """Verify local semantic vector projection."""
    vec = create_dense_semantic_vector("How to check attendance and datesheet on UMS?")
    assert isinstance(vec, np.ndarray)
    assert len(vec) > 0
    # Vector is normalized
    norm = np.linalg.norm(vec)
    assert abs(norm - 1.0) < 1e-4


def test_semantic_search_engine_integration():
    """Verify SemanticSearchEngine indexes and searches with fallback resilience."""
    engine = SemanticSearchEngine()
    sample_docs = [
        {
            "id": "doc-1",
            "canonical_question": "What is the minimum attendance requirement at LPU?",
            "alternative_questions": ["attendance bar", "75% criteria"],
            "keywords": ["attendance", "rules"],
            "answer": "Minimum attendance is 75% for ETE.",
            "content": "75% attendance policy."
        },
        {
            "id": "doc-2",
            "canonical_question": "Where is the Uni-Hospital located?",
            "alternative_questions": ["hospital block", "doctor appointment"],
            "keywords": ["hospital", "medical"],
            "answer": "Uni-Hospital is located in Block 30.",
            "content": "Block 30 hospital."
        }
    ]

    engine.index_documents(sample_docs)
    assert len(engine.doc_vectors) == 2

    # Query attendance
    scores = engine.search("attendance percentage shortage")
    assert len(scores) == 2
    assert scores["doc-1"] > scores["doc-2"]

