from app.ml.training_config import TrainingConfig
from app.ml.domain_fine_tuner import LoRADomainFineTuner
from app.ml.evaluation_benchmark import EvaluationBenchmark

def test_training_config():
    cfg = TrainingConfig()
    assert cfg.lora_r == 16
    assert "q_proj" in cfg.target_modules

def test_evaluation_benchmark():
    b = EvaluationBenchmark()
    recall = b.skill_recall_at_k(["Python", "SQL", "React"], ["Python", "SQL"])
    assert recall == 100.0
