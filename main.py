from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from core.config import settings
from services.ai.reception import build_answer, detect_intent, get_time_of_day, should_handoff
from services.rag.knowledge_base import knowledge_base

app = FastAPI(title=settings.app_name)


class ChatRequest(BaseModel):
    query: str
    history: list[str] | None = None


class ChatResponse(BaseModel):
    answer: str
    intent: str
    confidence: float
    handoff: bool
    department: str
    source: str


@app.on_event("startup")
def startup_event() -> None:
    knowledge_base.index_documents()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    intent_info = detect_intent(request.query, request.history)
    answer, source = build_answer(request.query, request.history, settings.org_name)
    handoff_info = should_handoff(request.query, request.history, intent_info["confidence"])

    return ChatResponse(
        answer=answer,
        intent=intent_info["intent"],
        confidence=intent_info["confidence"],
        handoff=handoff_info["handoff"],
        department=handoff_info["department"],
        source=source,
    )


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "AI Reception API is running", "time_of_day": get_time_of_day()}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
