"""
DatasetLoader: Loads and validates JSONL instruction fine-tuning datasets.
"""

import json
from typing import List, Dict, Any, Tuple

class DatasetLoader:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.data: List[Dict[str, str]] = []

    def load_dataset(self) -> List[Dict[str, str]]:
        self.data = []
        with open(self.filepath, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    entry = json.loads(line)
                    if "instruction" in entry and "response" in entry:
                        self.data.append(entry)
        return self.data

    def profile_token_lengths(self) -> Dict[str, float]:
        if not self.data:
            self.load_dataset()
        lens = [len(d["instruction"].split()) + len(d["response"].split()) for d in self.data]
        return {
            "count": len(lens),
            "avg_words": sum(lens) / len(lens) if lens else 0.0,
            "max_words": max(lens) if lens else 0,
            "min_words": min(lens) if lens else 0
        }

    def format_for_alpaca(self, entry: Dict[str, str]) -> str:
        sys_prompt = entry.get("system", "You are CampusConnect Career Advisor.")
        return f"### System:\n{sys_prompt}\n\n### Instruction:\n{entry['instruction']}\n\n### Response:\n{entry['response']}"

    def train_val_test_split(self, train_ratio=0.8, val_ratio=0.1) -> Tuple[List[Dict], List[Dict], List[Dict]]:
        if not self.data:
            self.load_dataset()
        n = len(self.data)
        n_train = int(n * train_ratio)
        n_val = int(n * val_ratio)
        return self.data[:n_train], self.data[n_train:n_train+n_val], self.data[n_train+n_val:]
