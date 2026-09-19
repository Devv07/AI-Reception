from __future__ import annotations

from services.ai.llm import FAST_MODEL, llm_call
from services.ai.prompts import LANGUAGE_PROMPT


async def detect_language(text: str) -> str:
    devanagari = sum(1 for character in text if "\u0900" <= character <= "\u097f")
    letters = sum(1 for character in text if character.isalpha())
    if letters and devanagari / letters > 0.3:
        return "ne"
    if text and all(ord(character) < 128 for character in text):
        return "en"
    try:
        result = (await llm_call(LANGUAGE_PROMPT.format(text=text), model=FAST_MODEL, temperature=0, max_tokens=10)).strip().lower()
        return result if result in {"ne", "en", "mixed"} else "en"
    except Exception:
        return "en"