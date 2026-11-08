import logging
from typing import List, Dict, Any, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)


class TfidfSearchEngine:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            sublinear_tf=True,
            min_df=1,
            stop_words='english'
        )
        self.corpus_matrix = None
        self.doc_ids: List[str] = []

    def fit_corpus(self, docs: List[Dict[str, Any]]) -> None:
        """Fit the vectorizer on the collection of approved knowledge records."""
        if not docs:
            self.corpus_matrix = None
            self.doc_ids = []
            return

        texts = []
        self.doc_ids = []
        for d in docs:
            # Combine canonical question, paraphrases, keywords, and text
            parts = [
                d.get("canonical_question", ""),
                " ".join(d.get("alternative_questions", [])),
                " ".join(d.get("keywords", [])),
                d.get("answer", ""),
                d.get("content", ""),
            ]
            texts.append(" ".join(filter(None, parts)))
            self.doc_ids.append(d["id"])

        try:
            self.corpus_matrix = self.vectorizer.fit_transform(texts)
        except Exception as e:
            logger.error(f"Error fitting TF-IDF matrix: {e}")
            self.corpus_matrix = None

    def search(self, query: str, top_k: int = 10) -> Dict[str, float]:
        """Returns a mapping of doc_id -> tfidf_similarity_score."""
        if self.corpus_matrix is None or not self.doc_ids:
            return {}

        try:
            query_vec = self.vectorizer.transform([query])
            similarities = cosine_similarity(query_vec, self.corpus_matrix)[0]
            
            results = {}
            for idx, score in enumerate(similarities):
                doc_id = self.doc_ids[idx]
                results[doc_id] = float(max(0.0, score))
            return results
        except Exception as e:
            logger.error(f"Error during TF-IDF query transformation: {e}")
            return {}

