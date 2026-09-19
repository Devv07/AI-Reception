from datetime import date

from tests.conftest import login


def test_visitors_and_analytics_are_database_backed_and_isolated(client, seed_data):
    organization = seed_data["organization"]
    department = seed_data["department"]
    visitor = seed_data["visitor"]
    conversation = client.post(
        "/api/v1/conversations",
        json={"organization_id": str(organization.id), "email": visitor.email, "channel": "web"},
    ).json()
    message = client.post(
        f"/api/v1/conversations/{conversation['conversation_id']}/messages",
        json={"content": "What are the BIT admission requirements?", "language": "en"},
    )
    assert message.status_code == 200
    token = login(client, seed_data["admin"], "admin-pass")
    headers = {"Authorization": f"Bearer {token}"}

    visitors = client.get("/api/v1/visitors", headers=headers)
    assert visitors.status_code == 200
    assert len(visitors.json()) == 1
    assert visitors.json()[0]["id"] == str(visitor.id)

    appointment = client.post(
        "/api/v1/appointments",
        json={
            "organization_id": str(organization.id),
            "conversation_id": conversation["conversation_id"],
            "visitor_id": str(visitor.id),
            "department_id": str(department.id),
            "appointment_date": str(date.today()),
            "appointment_time": "15:00:00",
            "purpose": "Admission consultation",
        },
    )
    assert appointment.status_code == 201

    analytics = client.get("/api/v1/analytics?timeframe=month", headers=headers)
    assert analytics.status_code == 200
    assert analytics.json()["top_intents"]
    assert analytics.json()["channel_usage"]

    other_token = login(client, seed_data["other_admin"], "other-pass")
    other_headers = {"Authorization": f"Bearer {other_token}"}
    assert client.get("/api/v1/visitors", headers=other_headers).json() == []
    assert client.get("/api/v1/analytics", headers=other_headers).json()["top_intents"] == []
