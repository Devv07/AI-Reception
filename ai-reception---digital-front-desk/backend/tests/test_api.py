from datetime import date

import pytest
from pydantic import ValidationError

from tests.conftest import login
from app.schemas import AIResponse
from app.services.ai.orchestrator import AIOrchestrator


def test_login(client, seed_data):
    token = login(client, seed_data["admin"], "admin-pass")
    assert token


def test_health(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "ok"


def test_conversation_creation(client, seed_data):
    organization = seed_data["organization"]
    response = client.post("/api/v1/conversations", json={"organization_id": str(organization.id), "name": "New Visitor", "phone": "555-0100", "channel": "web"})
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "active"
    assert body["channel"] == "web"
    assert body["conversation_id"]
    assert body["visitor_id"]


def test_message_creation_and_conversation_retrieval(client, seed_data):
    organization = seed_data["organization"]
    created = client.post("/api/v1/conversations", json={"organization_id": str(organization.id), "email": "message@example.com", "channel": "web"}).json()
    message = client.post(f"/api/v1/conversations/{created['conversation_id']}/messages", json={"content": "I need an appointment", "language": "en"})
    assert message.status_code == 200
    assert message.json()["ai_response"]["intent"] == "appointment"
    conversation = client.get(f"/api/v1/conversations/{created['conversation_id']}")
    assert conversation.status_code == 200
    assert len(conversation.json()["messages"]) == 2
    messages = client.get(f"/api/v1/conversations/{created['conversation_id']}/messages")
    assert len(messages.json()) == 2


def test_appointment_creation_and_conflict(client, seed_data):
    organization, department, visitor = seed_data["organization"], seed_data["department"], seed_data["visitor"]
    payload = {"organization_id": str(organization.id), "visitor_id": str(visitor.id), "department_id": str(department.id), "appointment_date": str(date.today()), "appointment_time": "10:00:00", "purpose": "Admission consultation"}
    first = client.post("/api/v1/appointments", json=payload)
    assert first.status_code == 201
    conflict = client.post("/api/v1/appointments", json=payload)
    assert conflict.status_code == 409


def test_ticket_creation(client, seed_data):
    organization, department, visitor = seed_data["organization"], seed_data["department"], seed_data["visitor"]
    response = client.post("/api/v1/tickets", json={"organization_id": str(organization.id), "visitor_id": str(visitor.id), "department_id": str(department.id), "title": "Payment issue", "description": "Payment is not visible", "priority": "high"})
    assert response.status_code == 201
    assert response.json()["status"] == "open"
    assert response.json()["priority"] == "high"


def test_authorization(client, seed_data):
    organization = seed_data["organization"]
    department_payload = {"organization_id": str(organization.id), "name": "Accounts"}
    assert client.post("/api/v1/departments", json=department_payload).status_code == 401
    reception_token = login(client, seed_data["reception"], "reception-pass")
    assert client.post("/api/v1/departments", json=department_payload, headers={"Authorization": f"Bearer {reception_token}"}).status_code == 403
    admin_token = login(client, seed_data["admin"], "admin-pass")
    assert client.post("/api/v1/departments", json=department_payload, headers={"Authorization": f"Bearer {admin_token}"}).status_code == 201


def test_conversation_organization_isolation(client, seed_data):
    organization = seed_data["organization"]
    created = client.post("/api/v1/conversations", json={"organization_id": str(organization.id), "phone": "555-0199", "channel": "web"}).json()
    token = login(client, seed_data["other_admin"], "other-pass")
    headers = {"Authorization": f"Bearer {token}"}
    assert client.get(f"/api/v1/conversations/{created['conversation_id']}", headers=headers).status_code == 404
    assert client.get(f"/api/v1/conversations?organization_id={organization.id}", headers=headers).status_code == 403
    assert client.post(f"/api/v1/conversations/{created['conversation_id']}/messages", json={"content": "hello"}, headers=headers).status_code == 404


def test_ai_failure_returns_safe_handoff(client, seed_data, monkeypatch):
    from app.api.v1 import conversations

    organization = seed_data["organization"]
    created = client.post("/api/v1/conversations", json={"organization_id": str(organization.id), "phone": "555-0188", "channel": "web"}).json()

    def fail(*args, **kwargs):
        raise TimeoutError("provider timed out")

    monkeypatch.setattr(conversations.AIOrchestrator, "respond", fail)
    response = client.post(f"/api/v1/conversations/{created['conversation_id']}/messages", json={"content": "Can someone help?"})
    assert response.status_code == 200
    assert response.json()["ai_response"]["needs_human"] is True
    assert "trouble accessing" in response.json()["ai_response"]["answer"]
    assert client.get(f"/api/v1/conversations/{created['conversation_id']}").json()["status"] == "human_requested"


def test_ai_contract_rejects_invalid_action():
    with pytest.raises(ValidationError):
        AIResponse(answer="bad", intent="unknown", confidence=0.1, action="delete_database", language="en")


def test_low_confidence_ai_response_becomes_handoff():
    class LowConfidenceProvider:
        def respond(self, message, language, context):
            return {"answer": "unverified", "intent": "admission_information", "confidence": 0.2, "action": "book_appointment", "language": language, "sources": []}

    response = AIOrchestrator(LowConfidenceProvider()).respond("question", "en", [])
    assert response.intent == "unknown"
    assert response.action == "human_handoff"
    assert response.needs_human is True
    assert response.sources == []


def test_other_organization_cannot_read_appointments_or_tickets(client, seed_data):
    organization, department, visitor = seed_data["organization"], seed_data["department"], seed_data["visitor"]
    appointment = client.post("/api/v1/appointments", json={"organization_id": str(organization.id), "visitor_id": str(visitor.id), "department_id": str(department.id), "appointment_date": str(date.today()), "appointment_time": "13:00:00", "purpose": "Consultation"}).json()
    ticket = client.post("/api/v1/tickets", json={"organization_id": str(organization.id), "visitor_id": str(visitor.id), "department_id": str(department.id), "title": "Private issue", "description": "Private details"}).json()
    token = login(client, seed_data["other_admin"], "other-pass")
    headers = {"Authorization": f"Bearer {token}"}
    assert client.get(f"/api/v1/appointments/{appointment['id']}", headers=headers).status_code == 404
    assert client.get(f"/api/v1/tickets/{ticket['id']}", headers=headers).status_code == 404
    assert client.get("/api/v1/appointments", headers=headers).json() == []
    assert client.get("/api/v1/tickets", headers=headers).json() == []
