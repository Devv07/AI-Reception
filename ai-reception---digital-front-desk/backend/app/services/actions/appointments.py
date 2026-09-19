from datetime import date, time
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Appointment, Conversation, Department, Visitor
from app.schemas import AppointmentCreate

VALID_APPOINTMENT_STATUSES = {"pending", "confirmed", "cancelled", "completed"}


def create_appointment(db: Session, payload: AppointmentCreate) -> Appointment:
    if payload.status not in VALID_APPOINTMENT_STATUSES:
        raise HTTPException(status_code=422, detail="Invalid appointment status")

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

    ensure_slot_available(db, payload.department_id, payload.appointment_date, payload.appointment_time)
    appointment = Appointment(**payload.model_dump())
    db.add(appointment)
    db.flush()
    return appointment


def ensure_slot_available(db: Session, department_id: UUID, appointment_date: date, appointment_time: time, exclude_id: UUID | None = None) -> None:
    query = select(Appointment).where(
        Appointment.department_id == department_id,
        Appointment.appointment_date == appointment_date,
        Appointment.appointment_time == appointment_time,
        Appointment.status.in_(["pending", "confirmed"]),
    )
    if exclude_id:
        query = query.where(Appointment.id != exclude_id)
    if db.scalar(query):
        raise HTTPException(status_code=409, detail="Appointment slot is already booked")
