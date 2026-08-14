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
