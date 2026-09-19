from __future__ import annotations

from app.core.config import get_settings


async def call(prompt: str, *, system: str | None = None, fast: bool = False) -> str:
    settings = get_settings()
    if not settings.ai_api_key:
        raise RuntimeError("AI_API_KEY is not configured")

    from groq import AsyncGroq

    messages = ([{"role": "system", "content": system}] if system else [])
    messages.append({"role": "user", "content": prompt})
    request = {
        "model": settings.ai_fast_model if fast else settings.ai_model,
        "messages": messages,
        "temperature": 0.1 if fast else 0.3,
        "max_tokens": 1024,
    }
    if fast:
        request["response_format"] = {"type": "json_object"}
    response = await AsyncGroq(api_key=settings.ai_api_key).chat.completions.create(**request)
    return response.choices[0].message.content or ""
