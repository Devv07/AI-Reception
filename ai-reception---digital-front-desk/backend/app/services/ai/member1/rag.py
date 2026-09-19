from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from app.core.config import get_settings


@lru_cache(maxsize=1)
def _embedding_model():
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(get_settings().embedding_model)


def _storage_path() -> Path:
    path = Path(get_settings().chroma_db_path)
    return path if path.is_absolute() else Path(__file__).resolve().parents[4] / path


def get_collection():
    import chromadb

    client = chromadb.PersistentClient(path=str(_storage_path()))
    return client.get_or_create_collection(name="org_knowledge", metadata={"hnsw:space": "cosine"})


def chunk_text(text: str, chunk_size: int = 400, overlap: int = 50) -> list[str]:
    words = text.split()
    if not words:
        return []
    chunks: list[str] = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunks.append(" ".join(words[start:end]))
        if end == len(words):
            break
        start = max(end - overlap, start + 1)
    return chunks


def ingest_document(file_path: str | Path, organization_id: str, document_name: str | None = None) -> dict[str, object]:
    path = Path(file_path)
    text = path.read_text(encoding="utf-8")
    chunks = chunk_text(text)
    if not chunks:
        return {"source": path.name, "chunks": 0}

    encoded = _embedding_model().encode(chunks, normalize_embeddings=True)
    embeddings = encoded.tolist() if hasattr(encoded, "tolist") else encoded
    collection = get_collection()
    name = document_name or path.name
    collection.upsert(
        ids=[f"{organization_id}__{name}__{index}" for index in range(len(chunks))],
        embeddings=embeddings,
        documents=chunks,
        metadatas=[
            {"org_id": organization_id, "source": name, "chunk_index": str(index)}
            for index in range(len(chunks))
        ],
    )
    return {"source": name, "chunks": len(chunks)}


def ingest_directory(directory: str | Path, organization_id: str) -> dict[str, object]:
    root = Path(directory)
    files = sorted(path for path in root.rglob("*") if path.is_file() and path.suffix.lower() in {".md", ".txt"})
    results = [ingest_document(path, organization_id) for path in files]
    return {
        "organization_id": organization_id,
        "documents": len(results),
        "chunks": sum(int(result["chunks"]) for result in results),
        "files": results,
    }


def retrieve(query: str, organization_id: str, top_k: int = 4) -> list[dict[str, str | float]]:
    collection = get_collection()
    if collection.count() == 0:
        return []

    encoded = _embedding_model().encode(query, normalize_embeddings=True)
    embedding = encoded.tolist() if hasattr(encoded, "tolist") else encoded
    result = collection.query(
        query_embeddings=[embedding],
        n_results=top_k,
        where={"org_id": organization_id},
        include=["documents", "metadatas", "distances"],
    )
    documents = (result.get("documents") or [[]])[0]
    metadatas = (result.get("metadatas") or [[]])[0]
    distances = (result.get("distances") or [[]])[0]
    matches = []
    for index, document in enumerate(documents):
        metadata = metadatas[index] if index < len(metadatas) else {}
        distance = float(distances[index]) if index < len(distances) else 1.0
        match = {"text": str(document), "score": 1 - distance}
        match.update({str(key): str(value) for key, value in metadata.items()})
        match["source"] = str(metadata.get("source", "unknown"))
        matches.append(match)
    return matches
