"""
EvaluationBenchmark: Domain metrics (Recall@K, Precision, RMSE, F1) for opportunity intelligence.
"""

from typing import List, Dict, Any
import math

class EvaluationBenchmark:
    def __init__(self):
        pass

    def skill_recall_at_k(self, predicted: List[str], ground_truth: List[str], k: int = 5) -> float:
        if not ground_truth:
            return 100.0
        top_k = [p.lower() for p in predicted[:k]]
        gt_lower = set(g.lower() for g in ground_truth)
        hits = sum(1 for p in top_k if p in gt_lower)
        return round((hits / len(gt_lower)) * 100.0, 2)

    def skill_precision_at_k(self, predicted: List[str], ground_truth: List[str], k: int = 5) -> float:
        top_k = [p.lower() for p in predicted[:k]]
        if not top_k:
            return 0.0
        gt_lower = set(g.lower() for g in ground_truth)
        hits = sum(1 for p in top_k if p in gt_lower)
        return round((hits / len(top_k)) * 100.0, 2)
