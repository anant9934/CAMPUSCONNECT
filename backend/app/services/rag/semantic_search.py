import math
import logging
from typing import List, Dict, Any, Optional
import numpy as np

from app.services.rag.hf_embedding_service import HuggingFaceEmbeddingService

logger = logging.getLogger(__name__)

# Predefined semantic concept clusters for LPU domain
SEMANTIC_CLUSTERS = {
    "academics_attendance": [
        "attendance", "75%", "75 percent", "present", "absent", "shortage", "debarred", 
        "medical leave", "duty leave", "class", "lecture", "faculty", "minimum attendance"
    ],
    "ums_portal": [
        "ums", "portal", "login", "touch", "password", "registration number", "timetable",
        "announcement", "notices", "rms", "ticket", "student dashboard", "relationship management"
    ],
    "examination_datesheet": [
        "exam", "examination", "datesheet", "date sheet", "schedule", "timing", "ete", "end term",
        "mid term", "re-evaluation", "reappear", "backlog", "admit card", "block 34", "grade card"
    ],
    "hostel_residential": [
        "hostel", "room", "bh", "gh", "warden", "outpass", "night leave", "gate pass",
        "mess", "food", "laundry", "allotment", "curfew", "night out", "resident"
    ],
    "transportation": [
        "transport", "bus", "route", "bus pass", "timing", "pickup", "drop", "jalandhar",
        "phagwara", "ludhiana", "shuttle", "commute", "travel"
    ],
    "fees_financial": [
        "fee", "tuition", "payment", "challan", "receipt", "due", "fine", "late fee",
        "scholarship", "online payment", "net banking", "upi", "installment"
    ],
    "campus_facilities": [
        "unihospital", "hospital", "doctor", "medical", "ambulance", "emergency", "medicine",
        "unimall", "atm", "mall", "canteen", "stationary", "bank", "block 13", "dsa", "clubs"
    ],
    "library": [
        "library", "book", "issue", "return", "block 37", "dr radhakrishnan", "opac",
        "journal", "ieee", "reading room", "rfid"
    ]
}


def create_dense_semantic_vector(text: str) -> np.ndarray:
    """
    Creates a dense semantic representation by projecting text across domain semantic clusters,
    subword n-grams, and length features.
    """
    text_lower = text.lower()
    vector = []

    # 1. Cluster affinity features
    for cluster_name, terms in SEMANTIC_CLUSTERS.items():
        score = 0.0
        for term in terms:
            if term in text_lower:
                score += 1.0 + (len(term) / 10.0)
        vector.append(score)

    # 2. Subword character n-gram hashing (3-grams and 4-grams)
    char_dim = 48
    char_features = [0.0] * char_dim
    for n in (3, 4):
        for i in range(len(text_lower) - n + 1):
            sub = text_lower[i:i+n]
            idx = hash(sub) % char_dim
            char_features[idx] += 1.0

    vector.extend(char_features)
    vec_arr = np.array(vector, dtype=float)
    norm = np.linalg.norm(vec_arr)
    if norm > 0:
        vec_arr = vec_arr / norm
    return vec_arr


class SemanticSearchEngine:
    def __init__(self):
        self.doc_vectors: Dict[str, np.ndarray] = {}
        self.hf_doc_vectors: Dict[str, np.ndarray] = {}

    def index_documents(self, docs: List[Dict[str, Any]]) -> None:
        """Precompute and store dense semantic vectors for approved knowledge records."""
        self.doc_vectors.clear()
        self.hf_doc_vectors.clear()

        for doc in docs:
            parts = [
                doc.get("canonical_question", ""),
                " ".join(doc.get("alternative_questions", [])),
                " ".join(doc.get("keywords", [])),
                doc.get("answer", "")[:300],
                doc.get("content", "")[:300],
            ]
            full_text = " ".join(filter(None, parts))
            self.doc_vectors[doc["id"]] = create_dense_semantic_vector(full_text)

    def search(self, query: str) -> Dict[str, float]:
        """Compute cosine similarity of query against all indexed documents."""
        # 1. Try Serverless Hugging Face 384-d dense embeddings if available
        if self.hf_doc_vectors:
            hf_q_vec = HuggingFaceEmbeddingService.generate_embeddings(query)
            if hf_q_vec is not None and isinstance(hf_q_vec, np.ndarray):
                q_norm = np.linalg.norm(hf_q_vec)
                if q_norm > 0:
                    results = {}
                    for doc_id, d_vec in self.hf_doc_vectors.items():
                        d_norm = np.linalg.norm(d_vec)
                        if d_norm == 0:
                            results[doc_id] = 0.0
                        else:
                            cos_sim = float(np.dot(hf_q_vec, d_vec) / (q_norm * d_norm))
                            results[doc_id] = max(0.0, min(1.0, cos_sim))
                    return results

        # 2. Resilient local semantic cluster vector projection
        q_vec = create_dense_semantic_vector(query)
        q_norm = np.linalg.norm(q_vec)
        if q_norm == 0:
            return {}

        # If query has zero LPU domain terms, downscale character n-gram artifact
        has_domain_terms = any(term in query.lower() for terms in SEMANTIC_CLUSTERS.values() for term in terms)

        results = {}
        for doc_id, d_vec in self.doc_vectors.items():
            d_norm = np.linalg.norm(d_vec)
            if d_norm == 0:
                results[doc_id] = 0.0
                continue
            cos_sim = float(np.dot(q_vec, d_vec) / (q_norm * d_norm))
            if not has_domain_terms:
                cos_sim *= 0.35
            # Bound within 0.0 and 1.0
            results[doc_id] = max(0.0, min(1.0, cos_sim))

        return results

