from __future__ import annotations

import json

from services.ai.llm import FAST_MODEL, llm_call
from services.ai.prompts import INTENT_PROMPT

VALID_INTENTS = {"greeting", "faq", "admission", "fees", "appointment", "complaint", "human_handoff", "goodbye"}


async def detect_intent(query: str, history: list[dict] | None = None) -> dict[str, str | float]:
    try:
        raw = await llm_call(INTENT_PROMPT.format(history=history or [], query=query), model=FAST_MODEL, temperature=0.1, max_tokens=100, json_mode=True)
        data = json.loads(raw)
        intent = str(data.get("intent", "faq"))
        confidence = float(data.get("confidence", 0.5))
        if intent not in VALID_INTENTS or not 0 <= confidence <= 1:
            raise ValueError("invalid intent result")
        return {"intent": intent, "confidence": confidence}
    except Exception:
        return {"intent": "faq", "confidence": 0.5}