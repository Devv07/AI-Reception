import re
from datetime import date, time
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Conversation, Department
from app.schemas import AIResponse, AppointmentCreate, TicketCreate
from app.services.actions.appointments import create_appointment
from app.services.actions.departments import find_department
from app.services.actions.handoff import request_handoff
from app.services.actions.tickets import create_ticket

DATE_PATTERN = re.compile(r"\b(20\d{2}-\d{2}-\d{2})\b")
TIME_PATTERN = re.compile(r"(?:at|@)\s*(\d{1,2})(?::(\d{2}))?\s*(am|pm)?\b", re.IGNORECASE)


def _find_department_for_text(db: Session, organization_id: UUID, text: str) -> Department | None:
    departments = list(db.scalars(select(Department).where(
        Department.organization_id == organization_id,
        Department.active.is_(True),
    ).order_by(Department.name)).all())
    lowered = text.lower()
    return next((department for department in departments if department.name.lower() in lowered), None) or (
        departments[0] if len(departments) == 1 else None
    )


def _parse_booking_request(text: str) -> tuple[date | None, time | None, str | None]:
    date_match = DATE_PATTERN.search(text)
    time_match = TIME_PATTERN.search(text)
    purpose_match = re.search(r"\bfor\s+(.+)$", text, re.IGNORECASE)
    appointment_date = date.fromisoformat(date_match.group(1)) if date_match else None
    appointment_time = None
    if time_match:
        hour = int(time_match.group(1))
        minute = int(time_match.group(2) or 0)
        meridiem = (time_match.group(3) or "").lower()
        if meridiem == "pm" and hour < 12:
            hour += 12
        if meridiem == "am" and hour == 12:
            hour = 0
        appointment_time = time(hour=hour, minute=minute)
    purpose = purpose_match.group(1).strip() if purpose_match else None
    return appointment_date, appointment_time, purpose


class ActionEngine:
    def execute(
        self,
        db: Session,
        conversation: Conversation,
        response: AIResponse,
        organization_id: UUID,
        request_text: str = "",
    ) -> AIResponse:
        if conversation.organization_id != organization_id:
            raise ValueError("Conversation organization mismatch")
        if response.action not in {None, "answer_question", "book_appointment", "create_ticket", "human_handoff", "get_department"}:
            raise ValueError("Unsupported AI action")
        if response.action == "human_handoff" or response.needs_human:
            request_handoff(db, conversation)
        elif response.action == "book_appointment":
            appointment_date, appointment_time, purpose = _parse_booking_request(request_text)
            department = _find_department_for_text(db, organization_id, request_text)
            if not appointment_date or not appointment_time or not purpose or not department:
                response.answer = "I can book the appointment. Please provide the department, date (YYYY-MM-DD), time, and purpose."
                return response
            appointment = create_appointment(db, AppointmentCreate(
                organization_id=organization_id,
                conversation_id=conversation.id,
                visitor_id=conversation.visitor_id,
                department_id=department.id,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                purpose=purpose,
            ))
            response.answer = (
                f"Your appointment request with {department.name} is confirmed for "
                f"{appointment.appointment_date.isoformat()} at {appointment.appointment_time.strftime('%H:%M')}."
            )
        elif response.action == "create_ticket":
            department = _find_department_for_text(db, organization_id, request_text)
            if department is None:
                response.answer = "Please provide the department for your complaint so I can create the ticket."
                return response
            ticket = create_ticket(db, TicketCreate(
                organization_id=organization_id,
                conversation_id=conversation.id,
                visitor_id=conversation.visitor_id,
                department_id=department.id,
                category="complaint",
                title="Reception complaint",
                description=request_text.strip() or "Complaint submitted through reception.",
            ))
            response.answer = f"Your complaint has been recorded as ticket {ticket.id}. The {department.name} team will review it."
        elif response.action == "get_department":
            department = find_department(db, organization_id, request_text)
            if department is None:
                department = _find_department_for_text(db, organization_id, request_text)
            if department is None:
                response.answer = "Please tell me the department or office you are looking for."
                return response
            location = department.location or "the main reception desk"
            response.answer = f"{department.name} is located at {location}."
        return response
