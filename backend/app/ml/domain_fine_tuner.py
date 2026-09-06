"""
LoRADomainFineTuner: Domain adaptation fine-tuning harness for opportunity intelligence.
"""

import math
import json
from typing import Dict, Any, List
from app.ml.training_config import TrainingConfig
from app.ml.dataset_loader import DatasetLoader

class LoRADomainFineTuner:
    def __init__(self, config: TrainingConfig = None):
        self.config = config or TrainingConfig()
        self.training_logs: List[Dict[str, Any]] = []
