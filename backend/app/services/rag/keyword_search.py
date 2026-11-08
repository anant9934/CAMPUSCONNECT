import re
import math
from typing import List, Dict, Any, Set

# LPU Institutional Term Boosts
LPU_KEYWORD_BOOSTS = {
    "ums": 3.0,
    "rms": 2.5,
    "ete": 2.5,
    "ca": 2.0,
    "block 34": 3.5,
    "block34": 3.5,
    "block 13": 3.5,
    "block13": 3.5,
    "block 37": 3.5,
    "block37": 3.5,
    "unihospital": 3.5,
    "uni-hospital": 3.5,
    "unimall": 3.0,
    "datesheet": 2.5,
    "date sheet": 2.5,
    "attendance": 2.5,
    "75%": 3.0,
    "75 percent": 3.0,
    "debarred": 2.5,
    "outpass": 2.5,
    "night leave": 2.5,
    "warden": 2.0,
    "challan": 2.0,
    "lpunest": 2.5,
    "transport": 2.0,
    "bus": 2.0,
    "hostel": 2.0,
    "library": 2.0,
}

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


def normalize_query(query: str) -> str:
    """Normalize input query text."""
    query = query.lower().strip()
    query = re.sub(r'[^\w\s%]', ' ', query)
    query = re.sub(r'\s+', ' ', query)
    return query


def tokenize(text: str) -> List[str]:
    """Tokenize and filter stopwords."""
    norm = normalize_query(text)
    tokens = norm.split()
    return [t for t in tokens if t and t not in STOPWORDS]


def compute_keyword_score(query: str, target_doc: Dict[str, Any]) -> float:
    """
    Computes an enhanced lexical/keyword matching score using token frequencies,
    exact phrase matches, and LPU-specific term boosting.
    """
    query_norm = normalize_query(query)
    q_tokens = tokenize(query)
    if not q_tokens:
        return 0.0

    # Extract target text fields
    canonical = target_doc.get("canonical_question", "").lower()
    alternatives = [a.lower() for a in target_doc.get("alternative_questions", [])]
    answer = target_doc.get("answer", "").lower()
    keywords = [k.lower() for k in target_doc.get("keywords", [])]
    chunk_content = target_doc.get("content", "").lower()

    combined_text = f"{canonical} {' '.join(alternatives)} {' '.join(keywords)} {answer} {chunk_content}"

    # 1. Exact canonical or alternative match gets instant high score
    if query_norm == normalize_query(canonical):
        return 1.0
    for alt in alternatives:
        if query_norm == normalize_query(alt):
            return 0.98

    # 2. Check phrase boost
    score = 0.0
    total_weight = 0.0

    for term, boost in LPU_KEYWORD_BOOSTS.items():
        if term in query_norm:
            weight = boost * 1.5
            total_weight += weight
            if term in combined_text:
                score += weight

    # 3. Token-level matching
    matched_tokens_count = 0
    for token in q_tokens:
        weight = 1.0
        # Boost specific tokens
        if token in LPU_KEYWORD_BOOSTS:
            weight = LPU_KEYWORD_BOOSTS[token]
        total_weight += weight

        # High priority matches
        matched = False
        if token in canonical:
            score += weight * 1.2
            matched = True
        elif any(token in alt for alt in alternatives):
            score += weight * 1.0
            matched = True
        elif any(token == kw or token in kw for kw in keywords):
            score += weight * 1.1
            matched = True
        elif token in answer or token in chunk_content:
            score += weight * 0.7
            matched = True

        if matched:
            matched_tokens_count += 1

    if total_weight <= 0:
        return 0.0

    # Normalize between 0 and 1 scaled by query coverage
    raw_ratio = score / total_weight
    coverage = (matched_tokens_count / len(q_tokens)) if q_tokens else 1.0
    return min(1.0, raw_ratio * (coverage ** 0.5))

