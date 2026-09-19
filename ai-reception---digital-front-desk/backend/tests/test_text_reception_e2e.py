from tests.conftest import login


def create_conversation(client, organization):
    response = client.post(
        "/api/v1/conversations",
        json={"organization_id": str(organization.id), "name": "Text Visitor", "channel": "web"},
    )
    assert response.status_code == 201
    return response.json()["conversation_id"]


def send_message(client, conversation_id, content):
    response = client.post(
        f"/api/v1/conversations/{conversation_id}/messages",
        json={"content": content, "language": "en"},
    )
    assert response.status_code == 200
    return response.json()


def test_admission_is_persisted(client, seed_data):
    conversation_id = create_conversation(client, seed_data["organization"])
    result = send_message(client, conversation_id, "What are the requirements for BIT admission?")
    assert result["ai_response"]["intent"] == "admission_information"
    assert result["ai_response"]["language"] == "en"
    assert result["ai_response"]["answer"]
    assert len(client.get(f"/api/v1/conversations/{conversation_id}/messages").json()) == 2


def test_fees_returns_useful_persisted_response(client, seed_data):
    conversation_id = create_conversation(client, seed_data["organization"])
    result = send_message(client, conversation_id, "How much is the tuition fee?")
    assert result["ai_response"]["intent"] == "fee_information"
    assert "tuition" in result["ai_response"]["answer"].lower()
    assert len(client.get(f"/api/v1/conversations/{conversation_id}/messages").json()) == 2


def test_departments_returns_department_information(client, seed_data):
    conversation_id = create_conversation(client, seed_data["organization"])
    result = send_message(client, conversation_id, "What departments are available?")
    assert result["ai_response"]["intent"] == "department_information"
    assert "Admissions" in result["ai_response"]["answer"]


def test_appointment_requests_details_then_persists_when_complete(client, seed_data):
    conversation_id = create_conversation(client, seed_data["organization"])
    missing = send_message(client, conversation_id, "I want to book an appointment.")
    assert missing["ai_response"]["intent"] == "appointment"
    assert "provide" in missing["ai_response"]["answer"].lower()

    complete = send_message(
        client,
        conversation_id,
        "Book an appointment with Admissions on 2099-05-06 at 11:00 for BIT counseling.",
    )
    assert complete["ai_response"]["intent"] == "appointment"
    assert "2099-05-06" in complete["ai_response"]["answer"]

    token = login(client, seed_data["admin"], "admin-pass")
    appointments = client.get("/api/v1/appointments", headers={"Authorization": f"Bearer {token}"})
    assert len(appointments.json()) == 1


def test_payment_complaint_creates_complaint_ticket(client, seed_data):
    conversation_id = create_conversation(client, seed_data["organization"])
    result = send_message(client, conversation_id, "I have a complaint about my payment.")
    assert result["ai_response"]["intent"] == "complaint"

    token = login(client, seed_data["admin"], "admin-pass")
    tickets = client.get("/api/v1/tickets", headers={"Authorization": f"Bearer {token}"})
    assert len(tickets.json()) == 1
    assert tickets.json()[0]["conversation_id"] == conversation_id
    assert "payment" in tickets.json()[0]["description"].lower()


def test_human_assistance_updates_conversation(client, seed_data):
    conversation_id = create_conversation(client, seed_data["organization"])
    result = send_message(client, conversation_id, "I want to talk to a human.")
    assert result["ai_response"]["intent"] == "human_assistance"
    assert client.get(f"/api/v1/conversations/{conversation_id}").json()["status"] == "human_requested"


def test_unknown_question_is_graceful_and_english(client, seed_data):
    conversation_id = create_conversation(client, seed_data["organization"])
    result = send_message(client, conversation_id, "What is the secret launch date for a product you do not have?")
    assert result["ai_response"]["language"] == "en"
    assert result["ai_response"]["answer"]


def test_organization_isolation_covers_conversation_appointment_and_ticket_reads(client, seed_data):
    organization = seed_data["organization"]
    conversation_id = create_conversation(client, organization)
    token = login(client, seed_data["other_admin"], "other-pass")
    headers = {"Authorization": f"Bearer {token}"}
    assert client.get(f"/api/v1/conversations/{conversation_id}", headers=headers).status_code == 404
    assert client.get("/api/v1/appointments", headers=headers).json() == []
    assert client.get("/api/v1/tickets", headers=headers).json() == []
