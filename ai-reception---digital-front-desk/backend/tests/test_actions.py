from datetime import date

from app.schemas import AIResponse
from tests.conftest import login


def _conversation(client, organization):
    response = client.post(
        "/api/v1/conversations",
        json={"organization_id": str(organization.id), "name": "Action Visitor", "channel": "web"},
    )
    assert response.status_code == 201
    return response.json()["conversation_id"]


def _action_response(intent, action, answer="Action response"):
    return AIResponse(
        answer=answer,
        intent=intent,
        confidence=0.99,
        action=action,
        needs_human=action == "human_handoff",
        language="en",
    )


def test_appointment_action_persists_and_conflict_is_handled(client, seed_data, monkeypatch):
    from app.api.v1 import conversations

    monkeypatch.setattr(
        conversations.AIOrchestrator,
        "respond",
        lambda self, *args: _action_response("appointment", "book_appointment"),
    )
    conversation_id = _conversation(client, seed_data["organization"])
    request = {
        "content": "Book an appointment with Admissions on 2099-01-02 at 10:30 for BIT counseling",
        "language": "en",
    }
    first = client.post(f"/api/v1/conversations/{conversation_id}/messages", json=request)
    assert first.status_code == 200
    assert "2099-01-02" in first.json()["ai_response"]["answer"]

    token = login(client, seed_data["admin"], "admin-pass")
    appointments = client.get("/api/v1/appointments", headers={"Authorization": f"Bearer {token}"})
    assert appointments.status_code == 200
    assert len(appointments.json()) == 1

    second_conversation_id = _conversation(client, seed_data["organization"])
    conflict = client.post(f"/api/v1/conversations/{second_conversation_id}/messages", json=request)
    assert conflict.status_code == 200
    assert conflict.json()["ai_response"]["needs_human"] is True
    appointments = client.get("/api/v1/appointments", headers={"Authorization": f"Bearer {token}"})
    assert len(appointments.json()) == 1


def test_complaint_action_creates_linked_ticket(client, seed_data, monkeypatch):
    from app.api.v1 import conversations

    monkeypatch.setattr(
        conversations.AIOrchestrator,
        "respond",
        lambda self, *args: _action_response("complaint", "create_ticket"),
    )
    conversation_id = _conversation(client, seed_data["organization"])
    response = client.post(
        f"/api/v1/conversations/{conversation_id}/messages",
        json={"content": "Complaint for Admissions: my application status is incorrect.", "language": "en"},
    )
    assert response.status_code == 200

    token = login(client, seed_data["admin"], "admin-pass")
    tickets = client.get("/api/v1/tickets", headers={"Authorization": f"Bearer {token}"})
    assert tickets.status_code == 200
    assert len(tickets.json()) == 1
    ticket = tickets.json()[0]
    assert ticket["conversation_id"] == conversation_id
    assert "application status" in ticket["description"]


def test_human_assistance_updates_conversation_status(client, seed_data, monkeypatch):
    from app.api.v1 import conversations

    monkeypatch.setattr(
        conversations.AIOrchestrator,
        "respond",
        lambda self, *args: _action_response("human_assistance", "human_handoff"),
    )
    conversation_id = _conversation(client, seed_data["organization"])
    response = client.post(
        f"/api/v1/conversations/{conversation_id}/messages",
        json={"content": "Please connect me with a staff member.", "language": "en"},
    )
    assert response.status_code == 200
    conversation = client.get(f"/api/v1/conversations/{conversation_id}")
    assert conversation.json()["status"] == "human_requested"


def test_department_action_uses_organization_department(client, seed_data, monkeypatch):
    from app.api.v1 import conversations

    monkeypatch.setattr(
        conversations.AIOrchestrator,
        "respond",
        lambda self, *args: _action_response("department_information", "get_department"),
    )
    conversation_id = _conversation(client, seed_data["organization"])
    response = client.post(
        f"/api/v1/conversations/{conversation_id}/messages",
        json={"content": "Where is Admissions?", "language": "en"},
    )
    assert response.status_code == 200
    assert "Admissions" in response.json()["ai_response"]["answer"]


def test_action_cannot_cross_organization_boundary(client, seed_data, monkeypatch):
    from app.api.v1 import conversations

    monkeypatch.setattr(
        conversations.AIOrchestrator,
        "respond",
        lambda self, *args: _action_response("human_assistance", "human_handoff"),
    )
    conversation_id = _conversation(client, seed_data["organization"])
    token = login(client, seed_data["other_admin"], "other-pass")
    response = client.post(
        f"/api/v1/conversations/{conversation_id}/messages",
        headers={"Authorization": f"Bearer {token}"},
        json={"content": "Please help.", "language": "en"},
    )
    assert response.status_code == 404
