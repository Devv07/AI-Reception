from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from core.config import ALLOWED_ORIGINS, APP_NAME
from services.ai.pipeline import chat
from services.rag.ingest import ingest_directory

app = FastAPI(title=APP_NAME)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    query: str
    org_id: str
    conversation_id: str
    channel: str = "web"
    org_name: str = "our organization"


@app.get("/")
async def root() -> dict[str, str]:
    return {"status": "ok", "app": APP_NAME}


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "healthy"}


@app.post("/api/chat")
async def api_chat(request: ChatRequest) -> dict:
    return await chat(
        query=request.query,
        org_id=request.org_id,
        conversation_id=request.conversation_id,
        channel=request.channel,
        org_name=request.org_name,
    )


@app.post("/api/ingest")
async def api_ingest(org_id: str, dir_path: str = "knowledge") -> dict:
    return await ingest_directory(dir_path, org_id)
