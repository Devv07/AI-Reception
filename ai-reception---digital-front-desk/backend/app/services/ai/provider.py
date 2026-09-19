from abc import ABC, abstractmethod
import asyncio
import inspect
from typing import Any

from app.core.config import get_settings
from app.schemas import AIResponse


class AIProvider(ABC):
    @abstractmethod
    def respond(
        self,
        message: str,
        language: str,
        context: list[dict[str, str]],
    ) -> AIResponse:
        raise NotImplementedError


class MockAIProvider(AIProvider):
    def respond(
        self,
        message: str,
        language: str,
        context: list[dict[str, str]],
    ) -> AIResponse:
        text = message.lower().strip()

        # Human assistance
        if any(
            word in text
            for word in (
                "human",
                "staff",
                "person",
                "operator",
                "agent",
                "representative",
                "talk to someone",
                "speak with someone",
            )
        ):
            return AIResponse(
                answer="I will connect you with a staff member.",
                intent="human_assistance",
                confidence=0.98,
                action="human_handoff",
                needs_human=True,
                language="en",
            )

        # Appointments
        if any(
            word in text
            for word in (
                "appointment",
                "meeting",
                "schedule",
                "book an appointment",
                "make an appointment",
            )
        ):
            return AIResponse(
                answer="I can help arrange an appointment. Please provide your preferred department and time.",
                intent="appointment",
                confidence=0.94,
                action="book_appointment",
                language="en",
            )

        # Admissions
        if any(
            word in text
            for word in (
                "admission",
                "admissions",
                "apply",
                "application",
                "enroll",
                "enrollment",
                "eligibility",
                "requirement",
                "requirements",
                "entrance",
                "join bit",
                "bit admission",
            )
        ):
            return AIResponse(
                answer="I can help with admission requirements, eligibility, application procedures, and enrollment information.",
                intent="admission_information",
                confidence=0.95,
                language="en",
            )

        # Complaints take precedence over payment/fee keywords.
        if any(
            word in text
            for word in (
                "complaint",
                "complain",
                "issue",
                "problem",
                "unhappy",
                "dissatisfied",
            )
        ):
            return AIResponse(
                answer="I'm sorry you're experiencing an issue. I can help record your complaint and connect you with the appropriate department.",
                intent="complaint",
                confidence=0.91,
                action="create_ticket",
                language="en",
            )

        # Fees / payments
        if any(
            word in text
            for word in (
                "fee",
                "fees",
                "payment",
                "tuition",
                "cost",
                "price",
                "charges",
            )
        ):
            return AIResponse(
                answer="I can help with tuition fees, payment information, and payment-related support.",
                intent="fee_information",
                confidence=0.94,
                language="en",
            )

        # Scholarships
        if any(
            word in text
            for word in (
                "scholarship",
                "scholarships",
                "financial aid",
                "financial assistance",
                "grant",
            )
        ):
            return AIResponse(
                answer="I can help with scholarship and financial assistance information.",
                intent="scholarship_information",
                confidence=0.94,
                language="en",
            )

        # Departments
        if any(
            phrase in text
            for phrase in (
                "which departments",
                "what departments",
                "departments available",
                "departments do you have",
                "available departments",
                "academic departments",
            )
        ):
            return AIResponse(
                answer="I can provide information about the departments and offices available at the college.",
                intent="department_information",
                confidence=0.93,
                action="get_department",
                language="en",
            )

        # Office / department location
        if any(
            word in text
            for word in (
                "where is",
                "where can i find",
                "location",
                "located",
                "office location",
                "department location",
            )
        ):
            return AIResponse(
                answer="Please tell me which department or office location you are looking for.",
                intent="department_information",
                confidence=0.90,
                action="get_department",
                language="en",
            )

        # Office hours
        if any(
            phrase in text
            for phrase in (
                "office hours",
                "opening hours",
                "opening time",
                "closing time",
                "what time do you open",
                "what time does the college open",
                "what time do you close",
                "when are you open",
            )
        ):
            return AIResponse(
                answer="I can provide information about the college's office hours.",
                intent="office_hours",
                confidence=0.93,
                language="en",
            )

        # Contact information
        if any(
            phrase in text
            for phrase in (
                "contact",
                "phone number",
                "telephone number",
                "email address",
                "email",
                "how can i contact",
                "contact information",
            )
        ):
            return AIResponse(
                answer="I can provide the college's contact information.",
                intent="contact_information",
                confidence=0.92,
                language="en",
            )

        # General information
        return AIResponse(
            answer="I can help with admissions, fees, scholarships, departments, office hours, appointments, contact information, complaints, and staff assistance.",
            intent="general_information",
            confidence=0.72,
            language="en",
        )


class Member1AIProvider(AIProvider):
    """Adapt Member 1's intent, RAG, and LLM pipeline to the core contract."""

    def respond(
        self,
        message: str,
        language: str,
        context: list[dict[str, str]],
    ) -> AIResponse:
        from app.services.ai.member1.pipeline import respond

        result = _run_async(respond(message, context))
        return normalize_ai_response(result)


LEGACY_INTENT_MAP = {
    "greeting": "general_information",
    "faq": "general_information",
    "admission": "admission_information",
    "fees": "fee_information",
    "human_handoff": "human_assistance",
    "location": "department_information",
}

LEGACY_ACTION_MAP = {
    "answer": "answer_question",
    "department_redirect": "get_department",
}


def normalize_ai_response(value: AIResponse | dict[str, Any]) -> AIResponse:
    """Convert provider-specific output into the application's single contract."""
    data = value.model_dump() if isinstance(value, AIResponse) else dict(value)
    data["intent"] = LEGACY_INTENT_MAP.get(data.get("intent"), data.get("intent", "unknown"))
    data["action"] = LEGACY_ACTION_MAP.get(data.get("action"), data.get("action"))
    data["answer"] = data.get("answer", data.get("response", ""))
    data["needs_human"] = data.get("needs_human", data.get("handoff_required", False))
    data["language"] = "en"
    sources = data.get("sources", [])
    data["sources"] = [
        source if isinstance(source, dict) else {"source": str(source)}
        for source in sources
    ]
    return AIResponse.model_validate(data)


def create_provider() -> AIProvider:
    settings = get_settings()
    if settings.ai_provider.lower() in {"member1", "groq", "rag"}:
        return Member1AIProvider()
    return MockAIProvider()


def _run_async(value: Any) -> Any:
    if not inspect.isawaitable(value):
        return value
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(value)

    raise RuntimeError("The Member 1 provider cannot run inside an active event loop")