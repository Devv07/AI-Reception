from __future__ import annotations

from integration.event_publisher import event_publisher
from phone.session.call_session import CallSession


def run_test() -> None:

    print()
    print("=" * 70)
    print("PHASE 12.2 - PHONE EVENT INTEGRATION TEST")
    print("=" * 70)

    # --------------------------------------------------
    # Disable real backend delivery for this test.
    #
    # We only verify that phone events reach the
    # shared EventPublisher correctly.
    # --------------------------------------------------

    original_send_to_backend = (
        event_publisher.send_to_backend
    )

    event_publisher.send_to_backend = False

    try:

        event_publisher.clear_events()

        # --------------------------------------------------
        # Create isolated call
        # --------------------------------------------------

        session = CallSession(
            call_sid="CA_PHASE12_2_TEST",
            caller_number="+9779804720452",
            called_number="+17372508034",
        )

        print(
            "[TEST] Created call:"
            f" {session.call_sid}"
        )

        print(
            "[TEST] Conversation:"
            f" {session.conversation_id}"
        )

        # --------------------------------------------------
        # Incoming call
        # --------------------------------------------------

        session.add_event(
            "incoming_call",
            {
                "caller_number": (
                    session.caller_number
                ),
                "called_number": (
                    session.called_number
                ),
            },
        )

        # --------------------------------------------------
        # Speech received
        # --------------------------------------------------

        session.add_event(
            "speech_received",
            {
                "transcript": (
                    "Hello, I need information "
                    "about admissions."
                ),
            },
        )

        # --------------------------------------------------
        # AI response
        # --------------------------------------------------

        session.add_event(
            "ai_response_generated",
            {
                "response_text": (
                    "Hello. I can help you "
                    "with admissions information."
                ),
            },
        )

        # --------------------------------------------------
        # Handoff
        # --------------------------------------------------

        session.add_event(
            "call_handoff",
            {
                "department": "admissions",
                "reason": (
                    "Caller requested "
                    "human assistance."
                ),
            },
        )

        # --------------------------------------------------
        # Close call
        # --------------------------------------------------

        session.close(
            reason="test_completed"
        )

        # --------------------------------------------------
        # Validate local session history
        # --------------------------------------------------

        session_events = session.get_events()

        assert len(session_events) == 5

        print(
            "[TEST] Session event history: PASS"
        )

        # --------------------------------------------------
        # Validate integration publisher
        # --------------------------------------------------

        published_events = (
            event_publisher.get_events()
        )

        assert len(published_events) == 5

        print(
            "[TEST] Event publisher received "
            "all phone events: PASS"
        )

        # --------------------------------------------------
        # Validate event types
        # --------------------------------------------------

        event_types = [
            event["event_type"]
            for event in published_events
        ]

        expected_types = [
            "incoming_call",
            "speech_received",
            "ai_response_generated",
            "call_handoff",
            "call_closed",
        ]

        assert event_types == expected_types

        print(
            "[TEST] Event types: PASS"
        )

        # --------------------------------------------------
        # Validate call isolation
        # --------------------------------------------------

        for event in published_events:

            assert (
                event["call_sid"]
                == session.call_sid
            )

            assert (
                event["conversation_id"]
                == session.conversation_id
            )

            assert (
                event["channel"]
                == "phone"
            )

            assert (
                event["source"]
                == "phone"
            )

        print(
            "[TEST] Call identity isolation: PASS"
        )

        # --------------------------------------------------
        # Validate important event data
        # --------------------------------------------------

        speech_event = next(
            event
            for event in published_events
            if event["event_type"]
            == "speech_received"
        )

        assert (
            "transcript"
            in speech_event["data"]
        )

        ai_event = next(
            event
            for event in published_events
            if event["event_type"]
            == "ai_response_generated"
        )

        assert (
            "response_text"
            in ai_event["data"]
        )

        handoff_event = next(
            event
            for event in published_events
            if event["event_type"]
            == "call_handoff"
        )

        assert (
            handoff_event["data"]["department"]
            == "admissions"
        )

        print(
            "[TEST] Event data integrity: PASS"
        )

        # --------------------------------------------------
        # Verify close state
        # --------------------------------------------------

        assert session.active is False

        print(
            "[TEST] Call close state: PASS"
        )

        print()
        print("=" * 70)
        print("PHASE 12.2 COMPLETE")
        print("=" * 70)
        print()

    finally:

        event_publisher.clear_events()

        event_publisher.send_to_backend = (
            original_send_to_backend
        )


if __name__ == "__main__":
    run_test()