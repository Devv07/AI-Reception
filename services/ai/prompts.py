SYSTEM_PROMPT = """You are a professional AI receptionist for {org_name} in Nepal.
Answer only from the provided context. Cite the source when relevant. Mirror Nepali, English, or mixed language. If the context does not answer the question, say: "I don't have that information. Let me connect you with our staff."
Keep the answer concise, warm, and professional.

Context:
{context}

Conversation:
{history}
"""

INTENT_PROMPT = """Classify the message into exactly one intent: greeting, faq, admission, fees, appointment, complaint, human_handoff, goodbye.
Conversation: {history}
Message: {query}
Respond only as JSON: {{"intent": "faq", "confidence": 0.8}}"""

LANGUAGE_PROMPT = """Detect the language: return only ne, en, or mixed.
Text: {text}"""

REWRITE_PROMPT = """Rewrite this as a standalone knowledge-base search query under 20 words.
History: {history}
Question: {query}
Return only the rewritten query."""

HANDOFF_PROMPT = """Decide whether a human staff member is needed. Use true for explicit staff requests, private account/payment issues, frustration, low confidence, or unsupported questions.
History: {history}
Message: {query}
Confidence: {confidence}
Return only JSON: {{"handoff": false, "reason": "", "department": "Support"}}"""

FALLBACK_RESPONSES = {
    "no_context": {"en": "I don't have that information in my knowledge base. Let me connect you with our staff.", "ne": "मसँग त्यो जानकारी छैन। म तपाईंलाई हाम्रो स्टाफसँग जोड्छु।"},
    "low_confidence": {"en": "I'm not fully sure about that. Would you like me to connect you with a staff member?", "ne": "म पूर्ण रूपमा निश्चित छैन। म तपाईंलाई स्टाफसँग जोड्न सक्छु?"},
    "gibberish": {"en": "I didn't quite understand that. Could you please rephrase?", "ne": "मैले त्यो राम्ररी बुझिन। कृपया फेरि भन्नुहोस्।"},
    "out_of_scope": {"en": "That's outside what I can help with. Let me connect you with the right person.", "ne": "त्यो मेरो सहयोगको दायरा बाहिर छ। म तपाईंलाई सही व्यक्तिसँग जोड्छु।"},
    "error": {"en": "Something went wrong on my end. Please try again or ask for staff assistance.", "ne": "मेरो तर्फबाट केही गडबड भयो। कृपया फेरि प्रयास गर्नुहोस्।"},
}
