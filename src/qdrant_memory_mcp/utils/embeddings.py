"""
OpenAI embedding generation with caching
"""

from typing import List, Dict
import httpx
from ..config import OPENAI_API_KEY, EMBEDDING_MODEL

# Module-level cache
_embedding_cache: Dict[str, List[float]] = {}


def get_embedding(text: str) -> List[float]:
    """
    Get embedding from OpenAI with caching

    Args:
        text: Text to embed

    Returns:
        List of floats representing the embedding vector
    """
    if text in _embedding_cache:
        return _embedding_cache[text]

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "input": text,
        "model": EMBEDDING_MODEL
    }

    with httpx.Client() as client:
        response = client.post(
            "https://api.openai.com/v1/embeddings",
            headers=headers,
            json=data,
            timeout=30.0
        )
        response.raise_for_status()
        embedding = response.json()["data"][0]["embedding"]

        # Cache the result
        _embedding_cache[text] = embedding
        return embedding
