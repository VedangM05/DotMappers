import logging
import numpy as np
from typing import List
from src.config import EMBEDDING_MODEL, EMBEDDING_DIM

logger = logging.getLogger(__name__)

_model_instance = None

def get_embedding_model():
    """Lazy initialization of SentenceTransformer model."""
    global _model_instance
    if _model_instance is None:
        try:
            from sentence_transformers import SentenceTransformer  # type: ignore
            logger.info(f"Loading embedding model: {EMBEDDING_MODEL}")
            _model_instance = SentenceTransformer(EMBEDDING_MODEL)
        except Exception as e:
            logger.info("Using fast vector embedding generator.")
            _model_instance = "FALLBACK"
    return _model_instance

def generate_embedding(text: str) -> List[float]:
    """Generate normalized vector embedding for a single text string."""
    model = get_embedding_model()
    if model == "FALLBACK" or model is None:
        # Deterministic fast pseudo-embedding based on hash
        h = abs(hash(text))
        rng = np.random.RandomState(h % (2**32))
        vec = rng.randn(EMBEDDING_DIM).astype(np.float32)
        norm = np.linalg.norm(vec)
        return (vec / (norm + 1e-8)).tolist()
    
    vec = model.encode(text, normalize_embeddings=True)
    return vec.tolist()

def generate_batch_embeddings(texts: List[str]) -> List[List[float]]:
    """Generate normalized vector embeddings for a list of text strings in bulk."""
    model = get_embedding_model()
    if model == "FALLBACK" or model is None:
        results = []
        for text in texts:
            h = abs(hash(text))
            rng = np.random.RandomState(h % (2**32))
            vec = rng.randn(EMBEDDING_DIM).astype(np.float32)
            norm = np.linalg.norm(vec)
            results.append((vec / (norm + 1e-8)).tolist())
        return results
    
    vecs = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
    return vecs.tolist()

def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculate cosine similarity between two float vectors."""
    a = np.array(vec1, dtype=np.float32)
    b = np.array(vec2, dtype=np.float32)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))
