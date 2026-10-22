"""
InterviewEvaluator: Technical and HR behavioral question bank and evaluator.
"""

from typing import List, Dict, Any

class InterviewEvaluator:
    def get_standard_behavioral_questions(self) -> List[Dict[str, str]]:
        return [
            {"q": "Tell me about a challenging bug you solved.", "framework": "STAR (Situation, Task, Action, Result)"},
            {"q": "Why do you want to join our engineering team?", "framework": "Company alignment + Technical curiosity"},
            {"q": "How do you handle disagreement in code reviews?", "framework": "Constructive communication + Data-driven decisions"}
        ]
