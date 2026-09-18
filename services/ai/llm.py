from __future__ import annotations

from groq import AsyncGroq

from core.config import GROQ_API_KEY, GROQ_FAST_MODEL, GROQ_MODEL

client = AsyncGroq(api_key=GROQ_API_KEY)
MAIN_MODEL = GROQ_MODEL
FAST_MODEL = GROQ_FAST_MODEL


async def llm_call(prompt: str, system: str | None = None, model: str = MAIN_MODEL, temperature: float = 0.3, max_tokens: int = 1024, json_mode: bool = False) -> str:
    messages = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": prompt}]
    return await llm_chat(messages, model, temperature, max_tokens, json_mode)


async def llm_chat(messages: list[dict[str, str]], model: str = MAIN_MODEL, temperature: float = 0.3, max_tokens: int = 1024, json_mode: bool = False) -> str:
    kwargs = {"model": model, "messages": messages, "temperature": temperature, "max_tokens": max_tokens}
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    response = await client.chat.completions.create(**kwargs)
    return response.choices[0].message.content or ""
