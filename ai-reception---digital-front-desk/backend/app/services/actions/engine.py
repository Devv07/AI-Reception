from uuid import UUID

from sqlalchemy.orm import Session

from app.models import Conversation
from app.schemas import AIResponse
from app.services.actions.handoff import request_handoff


class ActionEngine:
    def execute(self, db: Session, conversation: Conversation, response: AIResponse, organization_id: UUID) -> None:
        if response.action not in {None, "answer_question", "book_appointment", "create_ticket", "human_handoff", "get_department"}:
            raise ValueError("Unsupported AI action")
        if response.action == "human_handoff" or response.needs_human:
            request_handoff(db, conversation)
        elif response.action in {"answer_question", "book_appointment", "create_ticket", "get_department"}:
            return
