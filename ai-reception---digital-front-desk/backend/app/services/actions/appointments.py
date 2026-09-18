from datetime import date, time
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Appointment


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
