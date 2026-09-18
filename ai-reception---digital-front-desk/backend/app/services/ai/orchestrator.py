from app.schemas import AIResponse
from app.services.ai.provider import AIProvider, MockAIProvider


class AIOrchestrator:
    def __init__(self, provider: AIProvider | None = None):
        self.provider = provider or MockAIProvider()

    def respond(self, message: str, language: str, context: list[dict[str, str]]) -> AIResponse:
        response = AIResponse.model_validate(self.provider.respond(message, language, context))
        if response.intent == "unknown" or response.confidence < 0.6:
            return AIResponse(
                answer="I do not have enough verified information to answer that safely. Would you like me to connect you with a staff member?",
                intent="unknown",
                confidence=response.confidence,
                action="human_handoff",
                needs_human=True,
                language=language,
                sources=[],
            )
        return response
