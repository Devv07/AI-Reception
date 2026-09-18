from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models import Department, Ticket, User, Visitor
from app.schemas import TicketCreate, TicketResponse, TicketUpdate
from app.security import get_current_user, require_roles
from app.services.actions.tickets import validate_ticket_values

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.get("", response_model=list[TicketResponse])
def list_tickets(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> list[Ticket]:
    return list(db.scalars(select(Ticket).where(Ticket.organization_id == current_user.organization_id).order_by(Ticket.created_at.desc())).all())


@router.post("", response_model=TicketResponse, status_code=201)
def create_ticket(payload: TicketCreate, db: Session = Depends(get_db)) -> Ticket:
    validate_ticket_values(payload.priority, payload.status)
    department = db.get(Department, payload.department_id)
    visitor = db.get(Visitor, payload.visitor_id)
    if department is None or visitor is None or department.organization_id != payload.organization_id or visitor.organization_id != payload.organization_id:
        raise HTTPException(status_code=404, detail="Department or visitor not found")
    ticket = Ticket(**payload.model_dump())
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(ticket_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Ticket:
    ticket = db.get(Ticket, ticket_id)
    if ticket is None or ticket.organization_id != current_user.organization_id:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@router.patch("/{ticket_id}", response_model=TicketResponse)
def update_ticket(ticket_id: UUID, payload: TicketUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_roles("admin", "staff"))) -> Ticket:
    ticket = db.get(Ticket, ticket_id)
    if ticket is None or ticket.organization_id != current_user.organization_id:
        raise HTTPException(status_code=404, detail="Ticket not found")
    values = payload.model_dump(exclude_unset=True)
    validate_ticket_values(values.get("priority", ticket.priority), values.get("status", ticket.status))
    for key, value in values.items():
        setattr(ticket, key, value)
    db.commit()
    db.refresh(ticket)
    return ticket
