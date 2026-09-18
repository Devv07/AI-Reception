from abc import ABC, abstractmethod

from app.schemas import AIResponse


class AIProvider(ABC):
    @abstractmethod
    def respond(self, message: str, language: str, context: list[dict[str, str]]) -> AIResponse:
        raise NotImplementedError


class MockAIProvider(AIProvider):
    def respond(self, message: str, language: str, context: list[dict[str, str]]) -> AIResponse:
        text = message.lower()
        if any(word in text for word in ("human", "staff", "person", "operator")):
            return AIResponse(answer="I will connect you with a staff member.", intent="human_assistance", confidence=0.98, action="human_handoff", needs_human=True, language=language)
        if any(word in text for word in ("appointment", "meeting", "schedule")):
            return AIResponse(answer="I can help arrange an appointment. Please provide your preferred department and time.", intent="appointment", confidence=0.94, action="book_appointment", language=language)
        if any(word in text for word in ("fee", "payment", "tuition")):
            return AIResponse(answer="I can help with fee information or create a support ticket for a payment issue.", intent="fee_information", confidence=0.89, language=language)
        if any(word in text for word in ("where", "location", "department", "office")):
            return AIResponse(answer="Please tell me which department or office you are looking for.", intent="location", confidence=0.86, action="get_department", language=language)
        return AIResponse(answer="I can help with admissions, fees, departments, appointments, and staff assistance.", intent="general_information", confidence=0.72, language=language)
