from __future__ import annotations

from functools import lru_cache

from sentence_transformers import SentenceTransformer

from core.config import EMBEDDING_MODEL


@lru_cache(maxsize=1)
def _get_model() -> SentenceTransformer:
    return SentenceTransformer(EMBEDDING_MODEL)


def get_embedding(text: str) -> list[float]:
    return _get_model().encode(text, normalize_embeddings=True).tolist()


def get_embeddings(texts: list[str]) -> list[list[float]]:
    return _get_model().encode(texts, normalize_embeddings=True).tolist()