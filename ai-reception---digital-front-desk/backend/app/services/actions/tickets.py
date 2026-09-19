from fastapi import HTTPException

from app.models import Conversation, Department, Ticket, Visitor
from app.schemas import TicketCreate

VALID_PRIORITIES = {"low", "medium", "high"}
VALID_TICKET_STATUSES = {"open", "in_progress", "resolved", "closed"}


def validate_ticket_values(priority: str, status: str) -> None:
    if priority not in VALID_PRIORITIES:
        raise HTTPException(status_code=422, detail="Invalid ticket priority")
    if status not in VALID_TICKET_STATUSES:
        raise HTTPException(status_code=422, detail="Invalid ticket status")


def create_ticket(db, payload: TicketCreate) -> Ticket:
    validate_ticket_values(payload.priority, payload.status)
    department = db.get(Department, payload.department_id)
    visitor = db.get(Visitor, payload.visitor_id)
    conversation = db.get(Conversation, payload.conversation_id) if payload.conversation_id else None
    if (
        department is None
        or visitor is None
        or department.organization_id != payload.organization_id
        or visitor.organization_id != payload.organization_id
        or (conversation is not None and (
            conversation.organization_id != payload.organization_id
            or conversation.visitor_id != payload.visitor_id
        ))
    ):
        raise HTTPException(status_code=404, detail="Department, visitor, or conversation not found")

    ticket = Ticket(**payload.model_dump())
    db.add(ticket)
    db.flush()
    return ticket
