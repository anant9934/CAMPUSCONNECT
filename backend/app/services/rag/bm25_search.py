"""
Okapi BM25 Lexical Search Engine for CampusConnect LPU Assistant.
Features:
- Field-weighted token frequencies (Title/Canonical: 2.5x, Keywords: 2.0x, Content: 1.0x)
- Exact n-gram phrase matching bonus for multi-word queries
- Normalized BM25 scoring in [0, 1] range for calibrated hybrid combination
"""
import math
import re
from typing import List, Dict, Any, Tuple, Set

STOPWORDS: Set[str] = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are",
    "aren't", "as", "at", "be", "because", "been", "before", "being", "below", "between", "both",
    "but", "by", "can", "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does",
    "doesn't", "doing", "don't", "down", "during", "each", "few", "for", "from", "further", "had",
    "hadn't", "has", "hasn't", "have", "haven't", "having", "he", "her", "here", "hers", "herself",
    "him", "himself", "his", "how", "i", "if", "in", "into", "is", "isn't", "it", "its", "itself",
    "me", "more", "most", "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only",
    "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "she", "should",
    "so", "some", "such", "than", "that", "the", "their", "theirs", "them", "themselves", "then",
    "there", "these", "they", "this", "those", "through", "to", "too", "under", "until", "up",
    "very", "was", "wasn't", "we", "were", "weren't", "what", "when", "where", "which", "while",
    "who", "whom", "why", "with", "would", "you", "your", "yours", "yourself", "yourselves",
    "tell", "know", "please", "lpu", "lovely", "university",
    "dr", "prof", "mr", "mrs", "ms"
}


def bm25_tokenize(text: str) -> List[str]:
    """Tokenize text into lowercase alpha-numeric terms, filtering stopwords."""
    cleaned = re.sub(r"[^\w\s-]", " ", text.lower())
    tokens = cleaned.split()
    return [t for t in tokens if len(t) > 1 and t not in STOPWORDS]


class BM25SearchEngine:
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.doc_ids: List[str] = []
        self.doc_lengths: List[float] = []
        self.avg_doc_length: float = 0.0
        self.doc_count: int = 0
        self.term_doc_freq: Dict[str, int] = {}
        self.doc_term_freqs: List[Dict[str, float]] = []
        self.doc_raw_texts: List[str] = []
        self.doc_titles: List[str] = []

    def fit_corpus(self, docs: List[Dict[str, Any]]) -> None:
        """Indexes corpus with field-weighted term counts."""
        self.doc_ids = []
        self.doc_lengths = []
        self.doc_term_freqs = []
        self.doc_raw_texts = []
        self.doc_titles = []
        self.term_doc_freq = {}
        self.doc_count = len(docs)

        if not docs:
            self.avg_doc_length = 0.0
            return

        total_length = 0.0

        for d in docs:
            self.doc_ids.append(d["id"])
            title = d.get("canonical_question", "")
            alts = " ".join(d.get("alternative_questions", []))
            keywords = " ".join(d.get("keywords", []))
            content = d.get("answer", "") or d.get("content", "")

            self.doc_titles.append(f"{title} {alts}".lower())
            self.doc_raw_texts.append(f"{title} {alts} {keywords} {content}".lower())

            # Tokenize fields with weights
            title_tokens = bm25_tokenize(f"{title} {alts}")
            kw_tokens = bm25_tokenize(keywords)
            content_tokens = bm25_tokenize(content)

            term_freq: Dict[str, float] = {}
            for t in title_tokens:
                term_freq[t] = term_freq.get(t, 0.0) + 2.5
            for t in kw_tokens:
                term_freq[t] = term_freq.get(t, 0.0) + 2.0
            for t in content_tokens:
                term_freq[t] = term_freq.get(t, 0.0) + 1.0

            # Virtual weighted length
            weighted_len = sum(term_freq.values())
            self.doc_lengths.append(weighted_len)
            self.doc_term_freqs.append(term_freq)
            total_length += weighted_len

            # Update document frequency for each unique term
            for term in term_freq:
                self.term_doc_freq[term] = self.term_doc_freq.get(term, 0) + 1

        self.avg_doc_length = total_length / self.doc_count if self.doc_count > 0 else 1.0

    def get_idf(self, term: str) -> float:
        """Calculate Robertson-Spärck Jones IDF."""
        df = self.term_doc_freq.get(term, 0)
        if df == 0:
            return 0.0
        return math.log(1.0 + (self.doc_count - df + 0.5) / (df + 0.5))

    def search(self, query: str) -> Dict[str, float]:
        """
        Calculates BM25 scores for all indexed documents.
        Includes exact n-gram phrase bonus and soft saturation normalization to [0, 1].
        """
        if self.doc_count == 0:
            return {}

        q_clean = query.lower().strip()
        q_tokens = bm25_tokenize(query)
        if not q_tokens:
            return {}

        raw_scores: Dict[str, float] = {}
        max_score = 0.0

        # Exact multi-token phrase detection
        phrases: List[str] = []
        if len(q_tokens) >= 2:
            for i in range(len(q_tokens) - 1):
                phrases.append(f"{q_tokens[i]} {q_tokens[i+1]}")
        if len(q_tokens) >= 3:
            for i in range(len(q_tokens) - 2):
                phrases.append(f"{q_tokens[i]} {q_tokens[i+1]} {q_tokens[i+2]}")

        for idx, doc_id in enumerate(self.doc_ids):
            score = 0.0
            tf_dict = self.doc_term_freqs[idx]
            doc_len = self.doc_lengths[idx]
            len_norm = 1.0 - self.b + self.b * (doc_len / (self.avg_doc_length or 1.0))

            matched_count = 0
            # 1. Standard BM25 term weighting
            for token in q_tokens:
                tf = tf_dict.get(token, 0.0)
                if tf <= 0:
                    continue
                matched_count += 1
                idf = self.get_idf(token)
                numerator = tf * (self.k1 + 1.0)
                denominator = tf + self.k1 * len_norm
                score += idf * (numerator / denominator)

            # 2. Exact phrase bonus (bigrams and trigrams)
            raw_text = self.doc_raw_texts[idx]
            title_text = self.doc_titles[idx]

            for phrase in phrases:
                if phrase in title_text:
                    score += 4.5  # Significant bonus for title phrase match
                elif phrase in raw_text:
                    score += 2.0  # Moderate bonus for body phrase match

            if score > 0:
                # Query term coverage penalty: if query has multiple distinct terms and only a few match, penalize
                coverage = matched_count / len(q_tokens) if q_tokens else 1.0
                score *= (coverage ** 0.75)
                raw_scores[doc_id] = score
                if score > max_score:
                    max_score = score

        if not raw_scores or max_score <= 0:
            return {}

        # Normalize to [0, 1] range using hyperbolic saturation
        # Prevents high-term documents from overwhelming semantic & authority scores
        normalized_scores: Dict[str, float] = {}
        for doc_id, sc in raw_scores.items():
            # Soft saturation curve
            norm_val = sc / (sc + 8.0)
            normalized_scores[doc_id] = float(round(norm_val, 4))

        return normalized_scores
