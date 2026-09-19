from __future__ import annotations

from app.schemas import AIResponse
from app.services.ai.member1.intent import detect_intent
from app.services.ai.member1.llm import call
from app.services.ai.member1.prompts import FALLBACK_ERROR, FALLBACK_NO_CONTEXT, FALLBACK_UNKNOWN, SYSTEM_PROMPT
from app.services.ai.member1.rag import retrieve

INTENT_MAP = {
    "greeting": "general_information",
    "faq": "general_information",
    "admission": "admission_information",
    "fees": "fee_information",
    "appointment": "appointment",
    "complaint": "complaint",
    "human_handoff": "human_assistance",
    "goodbye": "general_information",
}


def _history(context: list[dict[str, str]]) -> tuple[str, str, str]:
    organization_id = ""
    lines: list[str] = []
    latest_user_message = ""
    for item in context:
        if item.get("organization_id"):
            organization_id = item["organization_id"]
            continue
        role = item.get("role", "user")
        content = item.get("content", "")
        if role == "user":
            latest_user_message = content
            lines.append(f"Visitor: {content}")
        elif role == "assistant":
            lines.append(f"Receptionist: {content}")
    return organization_id, latest_user_message, "\n".join(lines[-10:]) or "No previous conversation."


async def respond(message: str, context: list[dict[str, str]]) -> dict[str, object]:
    organization_id, _, history = _history(context)
    result = await detect_intent(message, history)
    source_matches: list[dict[str, str | float]] = []
    intent = str(result["intent"])
    confidence = float(result["confidence"])
    answer = ""
    action = None
    needs_human = False

    if intent == "greeting":
        answer = "Welcome to our reception. How can I help you today?"
    elif intent == "goodbye":
        answer = "Thank you for contacting us. Have a great day."
    elif intent == "appointment":
        answer = "Which department or person would you like to meet?"
        action = "book_appointment"
    elif intent == "complaint":
        answer = "I am sorry you experienced a problem. I can create a support ticket for you."
        action = "create_ticket"
    elif intent == "human_handoff":
        answer = "Certainly. I will connect you with a staff member."
        action = "human_handoff"
        needs_human = True
    elif intent in {"faq", "admission", "fees"}:
        try:
            if organization_id:
                source_matches = retrieve(message, organization_id)
        except Exception:
            source_matches = []
        if not source_matches or float(source_matches[0]["score"]) < 0.35:
            answer = FALLBACK_NO_CONTEXT
            action = "human_handoff"
            needs_human = True
            confidence = min(confidence, 0.5)
        else:
            context_text = "\n\n---\n\n".join(
                f"Source: {match['source']}\n{match['text']}" for match in source_matches
            )
            try:
                answer = (await call(
                    message,
                    system=SYSTEM_PROMPT.format(context=context_text, history=history),
                )).strip()
            except Exception:
                answer = FALLBACK_ERROR
                action = "human_handoff"
                needs_human = True
    else:
        answer = FALLBACK_UNKNOWN
        confidence = min(confidence, 0.5)
        action = "human_handoff"
        needs_human = True

    sources = []
    for match in source_matches:
        source = {key: str(value) for key, value in match.items() if key != "text"}
        source["title"] = source.get("source", "Verified knowledge source")
        sources.append(source)
    return AIResponse(
        answer=answer or FALLBACK_ERROR,
        intent=INTENT_MAP[intent],
        confidence=confidence,
        action=action,
        needs_human=needs_human,
        language="en",
        sources=sources,
    ).model_dump()
