from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Reception"
    org_name: str = "Texas College"
    groq_api_key: str | None = None
    model: str = "llama-3.1-8b-instant"
    knowledge_dir: str = "knowledge"
    chroma_path: str = "storage/chroma_db"
    max_history: int = 10

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
