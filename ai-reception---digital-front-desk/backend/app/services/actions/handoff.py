from sqlalchemy.orm import Session

from app.models import Conversation


def request_handoff(db: Session, conversation: Conversation) -> Conversation:
    conversation.status = "human_requested"
    db.add(conversation)
    return conversation
