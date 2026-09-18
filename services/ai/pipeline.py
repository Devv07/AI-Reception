from __future__ import annotations

from services.ai.intent import detect_intent
from services.ai.language import detect_language
from services.ai.llm import MAIN_MODEL, llm_call
from services.ai.memory import get_memory, save_memory
from services.ai.prompts import FALLBACK_RESPONSES, SYSTEM_PROMPT
from services.rag.retriever import retrieve


def _history_text(history: list[dict[str, str]]) -> str:
    if not history:
        return "No previous conversation."
    return "\n".join(f"Visitor: {item['user']}\nReceptionist: {item['assistant']}" for item in history)


async def chat(query: str, org_id: str, conversation_id: str, channel: str = "web", org_name: str = "our organization") -> dict:
    history = await get_memory(conversation_id)
    language = await detect_language(query)
    intent_result = await detect_intent(query, history)
    intent = str(intent_result["intent"])
    confidence = float(intent_result["confidence"])
    sources: list[str] = []
    handoff_required = False
    handoff_department = ""

    if intent == "greeting":
        response = "नमस्ते! हाम्रो संस्थामा स्वागत छ। म तपाईंलाई कसरी सहयोग गर्न सक्छु?" if language == "ne" else "Namaste! Welcome to our organization. How can I help you today?"
    elif intent in {"faq", "admission", "fees"}:
        matches = await retrieve(query, org_id)
        score = float(matches[0]["score"]) if matches else 0.0
        if not matches or score < 0.35:
            response = FALLBACK_RESPONSES["no_context"]["ne" if language == "ne" else "en"]
            handoff_required = True
            handoff_department = "General"
        else:
            sources = list(dict.fromkeys(str(match["source"]) for match in matches))
            context = "\n\n---\n\n".join(f"Source: {match['source']}\n{match['text']}" for match in matches)
            prompt = SYSTEM_PROMPT.format(org_name=org_name, context=context, history=_history_text(history))
            try:
                response = await llm_call(query, system=prompt, model=MAIN_MODEL, temperature=0.3, max_tokens=1024)
            except Exception:
                response = FALLBACK_RESPONSES["error"]["ne" if language == "ne" else "en"]
                handoff_required = True
                handoff_department = "General"
    elif intent == "appointment":
        response = "Which department or person would you like to meet?" if language != "ne" else "तपाईं कुन विभाग वा व्यक्तिलाई भेट्न चाहनुहुन्छ?"
    elif intent == "complaint":
        response = "I am sorry you experienced a problem. Please share the details so our Support team can help." if language != "ne" else "तपाईंले समस्या भोग्नुभएकोमा म क्षमाप्रार्थी छु। कृपया विवरण दिनुहोस्, हाम्रो Support टोलीले सहयोग गर्नेछ।"
        handoff_required = True
        handoff_department = "Support"
    elif intent == "human_handoff":
        response = "Certainly. I will connect you with a staff member." if language != "ne" else "अवश्य। म तपाईंलाई हाम्रो कर्मचारीसँग जोड्छु।"
        handoff_required = True
        handoff_department = "General"
    elif intent == "goodbye":
        response = "Thank you for contacting us. Have a great day!" if language != "ne" else "सम्पर्क गर्नुभएकोमा धन्यवाद। तपाईंको दिन शुभ रहोस्!"
    else:
        response = FALLBACK_RESPONSES["gibberish"]["ne" if language == "ne" else "en"]

    await save_memory(conversation_id, query, response)
    return {
        "response": response,
        "intent": intent,
        "confidence": confidence,
        "language": language,
        "sources": sources,
        "handoff_required": handoff_required,
        "handoff_department": handoff_department,
        "conversation_id": conversation_id,
    }
