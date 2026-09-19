from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


APP_NAME = os.getenv("APP_NAME", "AI Reception")
APP_ENV = os.getenv("APP_ENV", "development")

DEBUG = os.getenv("DEBUG", "false").lower() in {
    "1",
    "true",
    "yes",
    "on",
}


# ============================================================
# GROQ
# ============================================================

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip().strip('"').strip("'")

if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY is required in the project .env file"
    )


# Current Groq models
#
# Main model:
# Used for knowledge-based receptionist responses.
#
# Fast model:
# Used for lightweight tasks such as intent/language detection.

GROQ_MODEL = os.getenv(
    "GROQ_MODEL",
    "openai/gpt-oss-120b",
)

GROQ_FAST_MODEL = os.getenv(
    "GROQ_FAST_MODEL",
    "openai/gpt-oss-20b",
)


# ============================================================
# RAG
# ============================================================

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "all-MiniLM-L6-v2",
)

CHROMA_DB_PATH = BASE_DIR / "storage" / "chroma_db"


# ============================================================
# DATABASE
# ============================================================

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./storage/ai_reception.db",
)


# ============================================================
# AUTH
# ============================================================

JWT_SECRET = os.getenv(
    "JWT_SECRET",
    "change-me-in-development",
)

JWT_ALGORITHM = os.getenv(
    "JWT_ALGORITHM",
    "HS256",
)

ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv(
        "ACCESS_TOKEN_EXPIRE_MINUTES",
        "30",
    )
)


# ============================================================
# CORS
# ============================================================

ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:3000,http://localhost:5173",
    ).split(",")
    if origin.strip()
]