import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.database.session import get_db
from app.models import Conversation, Message, User, Visitor
from app.schemas import ConversationCreate, ConversationCreated, ConversationResponse, MessageCreate, MessageResponse
from app.services.actions.engine import ActionEngine
from app.services.ai.orchestrator import AIOrchestrator
from app.security import get_optional_current_user, get_current_user

router = APIRouter(prefix="/conversations", tags=["conversations"])
VALID_CHANNELS = {"web", "voice", "phone"}
logger = logging.getLogger(__name__)


def _conversation_query(conversation_id: UUID):
    return select(Conversation).options(selectinload(Conversation.messages)).where(Conversation.id == conversation_id)


@router.post("", response_model=ConversationCreated, status_code=201)
def create_conversation(payload: ConversationCreate, db: Session = Depends(get_db)) -> ConversationCreated:
    if payload.channel not in VALID_CHANNELS:
        raise HTTPException(status_code=422, detail="Unsupported channel")
    visitor = None
    if payload.email:
        visitor = db.scalar(select(Visitor).where(Visitor.organization_id == payload.organization_id, Visitor.email == payload.email))
    if visitor is None and payload.phone:
        visitor = db.scalar(select(Visitor).where(Visitor.organization_id == payload.organization_id, Visitor.phone == payload.phone))
    if visitor is None:
        visitor = Visitor(**payload.model_dump(exclude={"channel"}))
        db.add(visitor)
        db.flush()
    else:
        visitor.last_seen = db.execute(select(Visitor.last_seen).where(Visitor.id == visitor.id)).scalar_one_or_none() or visitor.last_seen
        visitor.name = payload.name or visitor.name
        visitor.preferred_language = payload.preferred_language
    conversation = Conversation(organization_id=payload.organization_id, visitor_id=visitor.id, channel=payload.channel, status="active")
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return ConversationCreated(conversation_id=conversation.id, visitor_id=visitor.id, status=conversation.status, channel=conversation.channel)


@router.get("/{conversation_id}", response_model=ConversationResponse)
def get_conversation(conversation_id: UUID, db: Session = Depends(get_db), current_user: User | None = Depends(get_optional_current_user)) -> Conversation:
    conversation = db.scalar(_conversation_query(conversation_id))
    if conversation is None or (current_user is not None and conversation.organization_id != current_user.organization_id):
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


@router.get("", response_model=list[ConversationResponse])
def list_conversations(organization_id: UUID | None = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> list[Conversation]:
    if organization_id is not None and organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Organization access denied")
    return list(db.scalars(select(Conversation).options(selectinload(Conversation.messages)).where(Conversation.organization_id == current_user.organization_id).order_by(Conversation.started_at.desc())).all())


@router.post("/{conversation_id}/messages")
def create_message(conversation_id: UUID, payload: MessageCreate, db: Session = Depends(get_db), current_user: User | None = Depends(get_optional_current_user)) -> dict[str, object]:
    conversation = db.scalar(_conversation_query(conversation_id))
    if conversation is None or (current_user is not None and conversation.organization_id != current_user.organization_id):
        raise HTTPException(status_code=404, detail="Conversation not found")
    visitor_message = Message(conversation_id=conversation.id, role="user", content=payload.content, language=payload.language)
    db.add(visitor_message)
    db.flush()
    context = [{"role": message.role, "content": message.content} for message in conversation.messages]
    try:
        ai_response = AIOrchestrator().respond(payload.content, payload.language, context)
        ActionEngine().execute(db, conversation, ai_response, conversation.organization_id)
    except Exception:
        logger.exception("AI orchestration failed")
        db.rollback()
        conversation = db.scalar(_conversation_query(conversation_id))
        if conversation is None:
            raise HTTPException(status_code=404, detail="Conversation not found")
        visitor_message = Message(conversation_id=conversation.id, role="user", content=payload.content, language=payload.language)
        db.add(visitor_message)
        ai_response = {
            "answer": "I'm having trouble accessing the assistant right now. Would you like me to connect you with a staff member?",
            "intent": "unknown",
            "confidence": 0.0,
            "action": "human_handoff",
            "needs_human": True,
            "language": payload.language,
            "sources": [],
        }
        from app.schemas import AIResponse
        ai_response = AIResponse.model_validate(ai_response)
        ActionEngine().execute(db, conversation, ai_response, conversation.organization_id)
    assistant_message = Message(conversation_id=conversation.id, role="assistant", content=ai_response.answer, language=ai_response.language, intent=ai_response.intent, confidence=ai_response.confidence)
    db.add(assistant_message)
    db.commit()
    db.refresh(assistant_message)
    return {"message": MessageResponse.model_validate(assistant_message), "ai_response": ai_response}


@router.get("/{conversation_id}/messages", response_model=list[MessageResponse])
def list_messages(conversation_id: UUID, db: Session = Depends(get_db), current_user: User | None = Depends(get_optional_current_user)) -> list[Message]:
    conversation = db.get(Conversation, conversation_id)
    if conversation is None or (current_user is not None and conversation.organization_id != current_user.organization_id):
        raise HTTPException(status_code=404, detail="Conversation not found")
    return list(db.scalars(select(Message).where(Message.conversation_id == conversation_id).order_by(Message.created_at)).all())
