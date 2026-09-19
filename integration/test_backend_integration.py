from __future__ import annotations

from integration.backend_client import BackendIntegrationClient
from integration.event import IntegrationEvent
from integration.event_publisher import EventPublisher


class FakeBackendClient:
    """
    Fake backend used for Phase 12 testing.

    No real HTTP request is made.
    """

    def __init__(self) -> None:
        self.received_events = []

    def send_event(
        self,
        event: IntegrationEvent,
    ) -> dict:

        self.received_events.append(
            event.to_dict()
        )

        return {
            "success": True,
            "status_code": 200,
            "response": {
                "message": "event accepted"
            },
            "event_id": event.event_id,
        }


def run_test() -> None:

    print()
    print("=" * 70)
    print("PHASE 12 - SHARED BACKEND INTEGRATION TEST")
    print("=" * 70)

    # --------------------------------------------------
    # 1. Test event creation
    # --------------------------------------------------

    event = IntegrationEvent(
        event_type="call_started",
        source="phone",
        call_sid="CA_PHASE12_TEST",
        conversation_id="phone-phase12-test",
        channel="phone",
        data={
            "caller_number": "+9779800000000",
            "called_number": "+17372508034",
        },
    )

    payload = event.to_dict()

    assert payload["event_type"] == "call_started"
    assert payload["source"] == "phone"
    assert payload["call_sid"] == "CA_PHASE12_TEST"
    assert (
        payload["conversation_id"]
        == "phone-phase12-test"
    )

    print("[TEST] Event creation: PASS")

    # --------------------------------------------------
    # 2. Test backend client
    # --------------------------------------------------

    fake_backend = FakeBackendClient()

    publisher = EventPublisher(
        backend_client=fake_backend,
        send_to_backend=True,
    )

    result = publisher.publish(event)

    assert result["success"] is True
    assert result["backend_sent"] is True

    assert len(
        fake_backend.received_events
    ) == 1

    print("[TEST] Backend client: PASS")

    # --------------------------------------------------
    # 3. Test phone event helper
    # --------------------------------------------------

    result = publisher.publish_call_event(
        event_type="speech_received",
        call_sid="CA_PHASE12_TEST",
        conversation_id="phone-phase12-test",
        data={
            "transcript": "Hello, I need information.",
        },
    )

    assert result["success"] is True

    print("[TEST] Phone event publisher: PASS")

    # --------------------------------------------------
    # 4. Test another phone event
    # --------------------------------------------------

    result = publisher.publish_call_event(
        event_type="ai_response_generated",
        call_sid="CA_PHASE12_TEST",
        conversation_id="phone-phase12-test",
        data={
            "response_text": (
                "Hello. How may I help you?"
            ),
        },
    )

    assert result["success"] is True

    print("[TEST] AI response event: PASS")

    # --------------------------------------------------
    # 5. Test visitor event
    # --------------------------------------------------

    result = publisher.publish_visitor_event(
        event_type="visitor_detected",
        visitor_id="visitor-001",
        data={
            "channel": "physical",
        },
    )

    assert result["success"] is True

    print("[TEST] Visitor event publisher: PASS")

    # --------------------------------------------------
    # 6. Event history
    # --------------------------------------------------

    events = publisher.get_events()

    assert len(events) == 4

    print("[TEST] Event history: PASS")

    # --------------------------------------------------
    # 7. Isolation check
    # --------------------------------------------------

    phone_events = [
        item
        for item in events
        if item["source"] == "phone"
    ]

    visitor_events = [
        item
        for item in events
        if item["source"] == "vision"
    ]

    assert len(phone_events) == 3
    assert len(visitor_events) == 1

    for item in phone_events:
        assert (
            item["conversation_id"]
            == "phone-phase12-test"
        )

    assert (
        visitor_events[0]["visitor_id"]
        == "visitor-001"
    )

    print("[TEST] Source isolation: PASS")

    print()
    print("=" * 70)
    print("PHASE 12.1 EVENT SYSTEM COMPLETE")
    print("=" * 70)
    print()


if __name__ == "__main__":
    run_test()