from __future__ import annotations

from services.rag.embedder import get_embedding
from services.rag.vectorstore import get_collection


async def retrieve(query: str, org_id: str, top_k: int = 4) -> list[dict[str, str | float]]:
    collection = get_collection()
    if collection.count() == 0:
        return []
    result = collection.query(
        query_embeddings=[get_embedding(query)],
        n_results=top_k,
        where={"org_id": org_id},
        include=["documents", "metadatas", "distances"],
    )
    documents = (result.get("documents") or [[]])[0]
    metadatas = (result.get("metadatas") or [[]])[0]
    distances = (result.get("distances") or [[]])[0]
    matches: list[dict[str, str | float]] = []
    for index, text in enumerate(documents):
        metadata = metadatas[index] if index < len(metadatas) else {}
        distance = float(distances[index]) if index < len(distances) else 1.0
        matches.append({"text": str(text), "source": str(metadata.get("source", "unknown")), "score": 1 - distance})
    return matches