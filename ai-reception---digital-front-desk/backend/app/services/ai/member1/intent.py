from __future__ import annotations

import json

from app.services.ai.member1.llm import call
from app.services.ai.member1.prompts import INTENT_PROMPT

VALID_INTENTS = {"greeting", "faq", "admission", "fees", "appointment", "complaint", "human_handoff", "goodbye"}


async def detect_intent(query: str, history: str) -> dict[str, str | float]:
    raw = await call(INTENT_PROMPT.format(history=history, query=query), fast=True)
    data = json.loads(raw)
    intent = str(data.get("intent", "faq"))
    confidence = float(data.get("confidence", 0.5))
    if intent not in VALID_INTENTS or not 0 <= confidence <= 1:
        raise ValueError("invalid intent result")
    return {"intent": intent, "confidence": confidence}
