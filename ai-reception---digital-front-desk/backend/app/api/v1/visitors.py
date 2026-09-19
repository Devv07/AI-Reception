from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.database.session import get_db
from app.models import Conversation, User, Visitor
from app.schemas import VisitorDashboardResponse
from app.security import get_current_user

router = APIRouter(prefix="/visitors", tags=["visitors"])


@router.get("", response_model=list[VisitorDashboardResponse])
def list_visitors(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[VisitorDashboardResponse]:
    visitors = db.scalars(
        select(Visitor)
        .options(
            selectinload(Visitor.conversations).selectinload(Conversation.messages),
            selectinload(Visitor.appointments),
            selectinload(Visitor.tickets),
        )
        .where(Visitor.organization_id == current_user.organization_id)
        .order_by(Visitor.last_seen.desc())
    ).all()
    result = []
    for visitor in visitors:
        conversation = max(visitor.conversations, key=lambda item: item.started_at, default=None)
        appointment = max(visitor.appointments, key=lambda item: item.created_at, default=None)
        ticket = max(visitor.tickets, key=lambda item: item.created_at, default=None)
        latest_message = conversation.messages[-1] if conversation and conversation.messages else None
        purpose = appointment.purpose if appointment else ticket.description if ticket else latest_message.content if latest_message else "General reception inquiry"
        department = str(appointment.department_id if appointment else ticket.department_id if ticket else conversation.assigned_department if conversation and conversation.assigned_department else "Unassigned")
        status = "Needs staff" if conversation and conversation.status == "human_requested" else "Active" if conversation and conversation.status == "active" else "Completed"
        channel = "Phone Call" if conversation and conversation.channel == "phone" else "Reception Kiosk"
        result.append(VisitorDashboardResponse(
            id=visitor.id,
            code=f"VIS-{str(visitor.id)[:8].upper()}",
            name=visitor.name or "Anonymous visitor",
            first_seen=visitor.first_seen,
            last_interaction=visitor.last_seen,
            purpose=purpose,
            department=department,
            status=status,
            channel=channel,
            duration="Recorded session",
        ))
    return result