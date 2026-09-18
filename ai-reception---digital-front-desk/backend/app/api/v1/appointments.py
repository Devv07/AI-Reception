from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models import Appointment, Department, User, Visitor
from app.schemas import AppointmentCreate, AppointmentResponse, AppointmentUpdate
from app.security import get_current_user, require_roles
from app.services.actions.appointments import ensure_slot_available

router = APIRouter(prefix="/appointments", tags=["appointments"])
VALID_STATUSES = {"pending", "confirmed", "cancelled", "completed"}


def _check_status(status: str) -> None:
    if status not in VALID_STATUSES:
        raise HTTPException(status_code=422, detail="Invalid appointment status")


@router.get("", response_model=list[AppointmentResponse])
def list_appointments(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> list[Appointment]:
    return list(db.scalars(select(Appointment).where(Appointment.organization_id == current_user.organization_id).order_by(Appointment.appointment_date, Appointment.appointment_time)).all())


@router.post("", response_model=AppointmentResponse, status_code=201)
def create_appointment(payload: AppointmentCreate, db: Session = Depends(get_db)) -> Appointment:
    _check_status(payload.status)
    department = db.get(Department, payload.department_id)
    visitor = db.get(Visitor, payload.visitor_id)
    if department is None or visitor is None or department.organization_id != payload.organization_id or visitor.organization_id != payload.organization_id:
        raise HTTPException(status_code=404, detail="Department or visitor not found")
    ensure_slot_available(db, payload.department_id, payload.appointment_date, payload.appointment_time)
    appointment = Appointment(**payload.model_dump())
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment


@router.get("/{appointment_id}", response_model=AppointmentResponse)
def get_appointment(appointment_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Appointment:
    appointment = db.get(Appointment, appointment_id)
    if appointment is None or appointment.organization_id != current_user.organization_id:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointment


@router.patch("/{appointment_id}", response_model=AppointmentResponse)
def update_appointment(appointment_id: UUID, payload: AppointmentUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_roles("admin", "staff"))) -> Appointment:
    appointment = db.get(Appointment, appointment_id)
    if appointment is None or appointment.organization_id != current_user.organization_id:
        raise HTTPException(status_code=404, detail="Appointment not found")
    values = payload.model_dump(exclude_unset=True)
    if "status" in values:
        _check_status(values["status"])
    if "appointment_date" in values or "appointment_time" in values:
        ensure_slot_available(db, appointment.department_id, values.get("appointment_date", appointment.appointment_date), values.get("appointment_time", appointment.appointment_time), appointment.id)
    for key, value in values.items():
        setattr(appointment, key, value)
    db.commit()
    db.refresh(appointment)
    return appointment
