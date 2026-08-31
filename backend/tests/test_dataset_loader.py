from app.ml.dataset_loader import DatasetLoader

def test_dataset_loader():
    loader = DatasetLoader("data/naukri_corpus/fine_tuning_instructions.jsonl")
    data = loader.load_dataset()
    assert len(data) >= 10
    profile = loader.profile_token_lengths()
    assert profile["count"] >= 10
