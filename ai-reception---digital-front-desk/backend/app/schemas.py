from datetime import date, datetime, time
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class APIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(APIModel):
    id: UUID
    organization_id: UUID
    name: str
    email: EmailStr
    role: str
    department_id: UUID | None
    active: bool


class OrganizationResponse(APIModel):
    id: UUID
    name: str
    slug: str
    description: str | None
    phone: str | None
    email: str | None
    address: str | None
    timezone: str


class DepartmentCreate(BaseModel):
    organization_id: UUID
    name: str = Field(min_length=1, max_length=200)
    description: str | None = None
    contact: str | None = None
    location: str | None = None
    active: bool = True


class DepartmentResponse(APIModel):
    id: UUID
    organization_id: UUID
    name: str
    description: str | None
    contact: str | None
    location: str | None
    active: bool


class VisitorDashboardResponse(BaseModel):
    id: UUID
    code: str
    name: str
    first_seen: datetime
    last_interaction: datetime
    purpose: str
    department: str
    status: Literal["Active", "Completed", "Needs staff"]
    channel: Literal["Reception Kiosk", "Phone Call"]
    duration: str


class AnalyticsResponse(BaseModel):
    visitors_by_hour: list[dict[str, int | str]]
    top_intents: list[dict[str, int | str]]
    department_demand: list[dict[str, int | str]]
    channel_usage: list[dict[str, int | str]]
    outcomes: list[dict[str, int | str]]


class VisitorCreate(BaseModel):
    organization_id: UUID
    name: str | None = None
    phone: str | None = None
    email: EmailStr | None = None
    preferred_language: str = "en"


class ConversationCreate(VisitorCreate):
    channel: str = "web"


class ConversationCreated(BaseModel):
    conversation_id: UUID
    visitor_id: UUID
    status: str
    channel: str


class MessageCreate(BaseModel):
    content: str = Field(min_length=1, max_length=10000)
    language: str = "en"


class AIResponse(BaseModel):
    answer: str
    intent: Literal[
        "general_information",
        "admission_information",
        "fee_information",
        "scholarship_information",
        "department_information",
        "office_hours",
        "contact_information",
        "appointment",
        "complaint",
        "human_assistance",
        "unknown",
    ]
    confidence: float = Field(ge=0, le=1)
    action: Literal["answer_question", "book_appointment", "create_ticket", "human_handoff", "get_department"] | None = None
    needs_human: bool = False
    language: Literal["en"] = "en"
    sources: list[dict[str, str]] = Field(default_factory=list)


class MessageResponse(APIModel):
    id: UUID
    conversation_id: UUID
    role: str
    content: str
    language: str
    intent: str | None
    confidence: float | None
    created_at: datetime


class ConversationResponse(APIModel):
    id: UUID
    organization_id: UUID
    visitor_id: UUID
    channel: str
    status: str
    started_at: datetime
    ended_at: datetime | None
    assigned_department: UUID | None
    messages: list[MessageResponse] = []


class AppointmentCreate(BaseModel):
    organization_id: UUID
    conversation_id: UUID | None = None
    visitor_id: UUID
    department_id: UUID
    requested_staff: str | None = None
    appointment_date: date
    appointment_time: time
    purpose: str = Field(min_length=1)
    status: str = "pending"


class AppointmentUpdate(BaseModel):
    status: str | None = None
    appointment_date: date | None = None
    appointment_time: time | None = None
    purpose: str | None = None


class AppointmentResponse(APIModel):
    id: UUID
    organization_id: UUID
    conversation_id: UUID | None
    visitor_id: UUID
    department_id: UUID
    requested_staff: str | None
    appointment_date: date
    appointment_time: time
    purpose: str
    status: str
    created_at: datetime


class TicketCreate(BaseModel):
    organization_id: UUID
    conversation_id: UUID | None = None
    visitor_id: UUID
    department_id: UUID
    category: str | None = None
    title: str = Field(min_length=1, max_length=240)
    description: str = Field(min_length=1)
    priority: str = "medium"
    status: str = "open"


class TicketUpdate(BaseModel):
    priority: str | None = None
    status: str | None = None
    assigned_user: UUID | None = None


class TicketResponse(APIModel):
    id: UUID
    organization_id: UUID
    conversation_id: UUID | None
    visitor_id: UUID
    department_id: UUID
    category: str | None
    title: str
    description: str
    priority: str
    status: str
    assigned_user: UUID | None
    created_at: datetime
    updated_at: datetime
