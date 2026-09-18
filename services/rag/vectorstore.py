from __future__ import annotations

from functools import lru_cache

import chromadb

from core.config import CHROMA_DB_PATH


@lru_cache(maxsize=1)
def get_client() -> chromadb.PersistentClient:
    return chromadb.PersistentClient(path=str(CHROMA_DB_PATH))


def get_collection() -> chromadb.Collection:
    return get_client().get_or_create_collection(
        name="org_knowledge",
        metadata={"hnsw:space": "cosine"},
    )


def reset_collection() -> None:
    client = get_client()
    try:
        client.delete_collection("org_knowledge")
    except Exception:
        pass
    get_collection()