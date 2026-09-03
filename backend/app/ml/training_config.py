"""
TrainingConfig: Hyperparameters and PEFT/LoRA configuration dataclass.
"""

from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class TrainingConfig:
    base_model_name_or_path: str = "meta-llama/Llama-3-8B-Instruct"
    lora_r: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.05
    target_modules: List[str] = field(default_factory=lambda: ["q_proj", "v_proj", "k_proj", "o_proj"])
    learning_rate: float = 2e-4
    num_train_epochs: int = 3
    per_device_train_batch_size: int = 4
    gradient_accumulation_steps: int = 4
    warmup_ratio: float = 0.03
    weight_decay: float = 0.01
    max_seq_length: int = 1024
    load_in_4bit: bool = True
    bnb_4bit_quant_type: str = "nf4"
    bnb_4bit_compute_dtype: str = "bfloat16"
    output_dir: str = "checkpoints/naukri_career_adapter"

    def to_peft_config_dict(self) -> dict:
        return {
            "r": self.lora_r,
            "lora_alpha": self.lora_alpha,
            "lora_dropout": self.lora_dropout,
            "target_modules": self.target_modules,
            "bias": "none",
            "task_type": "CAUSAL_LM"
        }
