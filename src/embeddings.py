import numpy as np
from typing import List
from src.config import EMBEDDING_DIM

def generate_embedding(text: str) -> List[float]:
    """Deterministic hash-based embedding (zero-cost)."""
    h = abs(hash(text))
    rng = np.random.RandomState(h % (2**32))
    vec = rng.randn(EMBEDDING_DIM).astype(np.float32)
    norm = np.linalg.norm(vec)
    return (vec / (norm + 1e-8)).tolist()

def generate_batch_embeddings(texts: List[str]) -> List[List[float]]:
    """Generate deterministic embeddings for a list of texts."""
    return [generate_embedding(text) for text in texts]

def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    a = np.array(vec1, dtype=np.float32)
    b = np.array(vec2, dtype=np.float32)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    return 0.0 if norm_a == 0 or norm_b == 0 else float(np.dot(a, b) / (norm_a * norm_b))
