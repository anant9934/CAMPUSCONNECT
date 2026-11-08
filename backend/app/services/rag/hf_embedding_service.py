import os
import logging
from typing import List, Optional, Union
import numpy as np

from app.core.config import settings

logger = logging.getLogger(__name__)


class HuggingFaceEmbeddingService:
    """
    Serverless dense embeddings via Hugging Face API using the official huggingface_hub client.
    Generates 384-dimensional dense vector representations for LPU knowledge retrieval
    without downloading model weights locally.
    Default models:
    - BAAI/bge-small-en-v1.5 (384-d)
    - sentence-transformers/all-MiniLM-L6-v2 (384-d)
    """

    _client = None

    @classmethod
    def get_token(cls) -> str:
        return (
            os.environ.get("HF_TOKEN")
            or settings.HF_TOKEN
            or settings.HF_TOKEN_READ
            or ""
        ).strip()

    @classmethod
    def get_client(cls):
        if cls._client is not None:
            return cls._client

        token = cls.get_token()
        if not token:
            logger.warning("HF_TOKEN is not configured. Serverless embeddings unavailable.")
            return None

        try:
            from huggingface_hub import InferenceClient
            cls._client = InferenceClient(
                provider="hf-inference",
                api_key=token,
            )
            return cls._client
        except Exception as e:
            logger.warning(f"Failed to initialize huggingface_hub InferenceClient: {e}")
            return None

    @classmethod
    def is_available(cls) -> bool:
        return bool(cls.get_token())

    @classmethod
    def generate_embeddings(
        cls,
        texts: Union[str, List[str]],
        model: Optional[str] = None
    ) -> Optional[np.ndarray]:
        """
        Generates 384-d dense embeddings for text or list of texts.
        Returns numpy array of shape (N, 384) or (384,) normalized to unit norm.
        """
        input_list = [texts] if isinstance(texts, str) else texts
        if not input_list:
            return None

        client = cls.get_client()
        if not client:
            return None

        target_model = model or settings.HF_EMBEDDING_MODEL or "BAAI/bge-small-en-v1.5"

        try:
            raw_embeddings = client.feature_extraction(
                input_list,
                model=target_model,
            )
            arr = np.array(raw_embeddings, dtype=np.float32)

            # Ensure 2D shape (N, dimension)
            if arr.ndim == 1:
                arr = np.expand_dims(arr, axis=0)
            elif arr.ndim == 3:
                # If model returns token-level embeddings (N, tokens, dim), average pool across tokens
                arr = np.mean(arr, axis=1)

            # Normalize rows to unit length for cosine similarity
            norms = np.linalg.norm(arr, axis=1, keepdims=True)
            norms[norms == 0] = 1.0
            norm_arr = arr / norms

            if isinstance(texts, str):
                return norm_arr[0]
            return norm_arr

        except Exception as e:
            logger.debug(f"HF serverless embedding call encountered: {e}. Graceful fallback available.")
            return None

