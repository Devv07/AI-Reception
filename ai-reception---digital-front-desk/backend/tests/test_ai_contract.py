import pytest

from app.schemas import AIResponse
from app.services.ai.orchestrator import AIOrchestrator
from app.services.ai.provider import MockAIProvider


@pytest.fixture
def assistant():
    return AIOrchestrator(MockAIProvider())


def assert_contract(response: AIResponse, intent: str, action: str | None = None, needs_human: bool = False):
    assert response.intent == intent
    assert 0 <= response.confidence <= 1
    assert response.answer
    assert response.action == action
    assert response.needs_human is needs_human
    assert response.language == "en"
    assert isinstance(response.sources, list)


def test_bit_admission_question_uses_normalized_contract(assistant):
    response = assistant.respond("What are the BIT admission requirements?", "ne", [])
    assert_contract(response, "admission_information")


def test_tuition_fee_question_uses_normalized_contract(assistant):
    response = assistant.respond("How much is tuition?", "en", [])
    assert_contract(response, "fee_information")


def test_department_question_uses_normalized_contract(assistant):
    response = assistant.respond("Which departments are available?", "en", [])
    assert_contract(response, "department_information", "get_department")


def test_appointment_request_uses_normalized_contract(assistant):
    response = assistant.respond("I need to schedule an appointment.", "en", [])
    assert_contract(response, "appointment", "book_appointment")


def test_complaint_uses_normalized_contract(assistant):
    response = assistant.respond("I want to make a complaint about a problem.", "en", [])
    assert_contract(response, "complaint", "create_ticket")


def test_human_assistance_uses_normalized_contract(assistant):
    response = assistant.respond("Please let me speak with a human.", "en", [])
    assert_contract(response, "human_assistance", "human_handoff", True)


def test_general_and_unknown_questions_use_normalized_contract(assistant):
    general = assistant.respond("Tell me about the college.", "en", [])
    assert_contract(general, "general_information")

    class UnknownProvider:
        def respond(self, message, language, context):
            return {
                "answer": "Not verified.",
                "intent": "faq",
                "confidence": 0.2,
                "action": "answer",
                "language": "ne",
                "sources": ["unverified-source"],
            }

    unknown = AIOrchestrator(UnknownProvider()).respond("What is not verified?", "ne", [])
    assert_contract(unknown, "unknown", "human_handoff", True)
