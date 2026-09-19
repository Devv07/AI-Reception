from __future__ import annotations

from pathlib import Path

from services.rag.embedder import get_embeddings
from services.rag.vectorstore import get_collection


def extract_text(path: str | Path) -> str:
    file_path = Path(path)
    suffix = file_path.suffix.lower()
    if suffix in {".md", ".txt"}:
        return file_path.read_text(encoding="utf-8")
    if suffix == ".pdf":
        from pypdf import PdfReader

        return "\n".join(page.extract_text() or "" for page in PdfReader(str(file_path)).pages)
    if suffix == ".docx":
        from docx import Document

        return "\n".join(paragraph.text for paragraph in Document(str(file_path)).paragraphs if paragraph.text.strip())
    return ""


def chunk_text(text: str, chunk_size: int = 400, overlap: int = 50) -> list[str]:
    words = text.split()
    if len(words) < 20:
        return []
    chunks: list[str] = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end]).strip()
        if chunk:
            chunks.append(chunk)
        if end == len(words):
            break
        start = max(end - overlap, start + 1)
    return chunks


async def ingest_document(file_path: str | Path, org_id: str, doc_name: str | None = None) -> dict:
    path = Path(file_path)
    name = doc_name or path.name
    chunks = chunk_text(extract_text(path))
    if not chunks:
        return {"source": str(path), "chunks": 0}

    embeddings = get_embeddings(chunks)
    collection = get_collection()
    collection.upsert(
        ids=[f"{org_id}__{name}__{index}" for index in range(len(chunks))],
        embeddings=embeddings,
        documents=chunks,
        metadatas=[{"org_id": org_id, "source": name, "chunk_index": index} for index in range(len(chunks))],
    )
    print(f"📚 Indexed {len(chunks)} chunks from {name}")
    return {"source": str(path), "chunks": len(chunks)}


async def ingest_directory(dir_path: str | Path, org_id: str) -> dict:
    root = Path(dir_path)
    supported = {".md", ".txt", ".pdf", ".docx"}
    files = [path for path in root.rglob("*") if path.is_file() and path.suffix.lower() in supported]
    results = [await ingest_document(path, org_id) for path in files]
    return {"org_id": org_id, "documents": len(results), "chunks": sum(item["chunks"] for item in results), "files": results}