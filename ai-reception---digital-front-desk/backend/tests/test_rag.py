import asyncio
from pathlib import Path

from app.services.ai.member1 import pipeline, rag


class FakeEmbeddingModel:
    def encode(self, values, normalize_embeddings=True):
        if isinstance(values, str):
            values = [values]
        return [[float(len(value))] for value in values]


class FakeCollection:
    def __init__(self, documents=None, metadatas=None, distances=None):
        self.documents = documents or []
        self.metadatas = metadatas or []
        self.distances = distances or []
        self.last_query = None
        self.upserted = None

    def count(self):
        return len(self.documents)

    def upsert(self, **kwargs):
        self.upserted = kwargs

    def query(self, **kwargs):
        self.last_query = kwargs
        return {
            "documents": [self.documents],
            "metadatas": [self.metadatas],
            "distances": [self.distances],
        }


def test_ingest_uses_stable_org_scoped_ids_and_metadata(tmp_path, monkeypatch):
    source = tmp_path / "programs.md"
    source.write_text("BIT programs and tuition fees are documented here.", encoding="utf-8")
    collection = FakeCollection()
    monkeypatch.setattr(rag, "_embedding_model", lambda: FakeEmbeddingModel())
    monkeypatch.setattr(rag, "get_collection", lambda: collection)

    result = rag.ingest_document(source, "org-123")

    assert result == {"source": "programs.md", "chunks": 1}
    assert collection.upserted["ids"] == ["org-123__programs.md__0"]
    assert collection.upserted["metadatas"] == [{"org_id": "org-123", "source": "programs.md", "chunk_index": "0"}]


def test_retrieve_filters_by_organization_and_preserves_source_metadata(monkeypatch):
    collection = FakeCollection(
        documents=["BIT, BCS, BBA, and BHM programs are offered."],
        metadatas=[{"org_id": "org-123", "source": "texas_college_programs_fees.md", "chunk_index": "0"}],
        distances=[0.12],
    )
    monkeypatch.setattr(rag, "_embedding_model", lambda: FakeEmbeddingModel())
    monkeypatch.setattr(rag, "get_collection", lambda: collection)

    matches = rag.retrieve("What programs does Texas College offer?", "org-123")

    assert matches[0]["source"] == "texas_college_programs_fees.md"
    assert matches[0]["chunk_index"] == "0"
    assert matches[0]["score"] == 0.88
    assert collection.last_query["where"] == {"org_id": "org-123"}


def test_pipeline_generates_grounded_english_answer_with_sources(monkeypatch):
    async def fake_detect_intent(query, history):
        return {"intent": "faq", "confidence": 0.96}

    def fake_retrieve(query, organization_id):
        return [{
            "text": "BIT, BCS, BBA, and BHM programs are offered.",
            "source": "texas_college_programs_fees.md",
            "chunk_index": "0",
            "score": 0.91,
        }]

    async def fake_call(prompt, system=None, fast=False):
        assert "BIT, BCS, BBA, and BHM" in system
        assert "Use English only" in system
        return "Texas College offers BIT, BCS, BBA, and BHM programs."

    monkeypatch.setattr(pipeline, "detect_intent", fake_detect_intent)
    monkeypatch.setattr(pipeline, "retrieve", fake_retrieve)
    monkeypatch.setattr(pipeline, "call", fake_call)

    response = asyncio.run(pipeline.respond(
        "What programs does Texas College offer?",
        [{"role": "user", "content": "What programs does Texas College offer?"}, {"organization_id": "org-123"}],
    ))

    assert response["answer"] == "Texas College offers BIT, BCS, BBA, and BHM programs."
    assert response["language"] == "en"
    assert response["intent"] == "general_information"
    assert response["sources"] == [{
        "source": "texas_college_programs_fees.md",
        "chunk_index": "0",
        "score": "0.91",
        "title": "texas_college_programs_fees.md",
    }]


def test_pipeline_offers_human_assistance_when_knowledge_is_unavailable(monkeypatch):
    async def fake_detect_intent(query, history):
        return {"intent": "faq", "confidence": 0.96}

    monkeypatch.setattr(pipeline, "detect_intent", fake_detect_intent)
    monkeypatch.setattr(pipeline, "retrieve", lambda query, organization_id: [])

    response = asyncio.run(pipeline.respond(
        "What are the college office hours?",
        [{"role": "user", "content": "What are the college office hours?"}, {"organization_id": "org-123"}],
    ))

    assert response["needs_human"] is True
    assert response["action"] == "human_handoff"
    assert response["sources"] == []
    assert "don't have that information" in response["answer"].lower()
    assert response["language"] == "en"
