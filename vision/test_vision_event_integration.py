from __future__ import annotations

from integration.event_publisher import event_publisher
from vision.reception.event_bridge import VisionEventBridge


def run_test() -> None:

    print()
    print("=" * 70)
    print("PHASE 12.4 - VISION EVENT INTEGRATION TEST")
    print("=" * 70)

    # --------------------------------------------------
    # No real backend HTTP request.
    # --------------------------------------------------

    original_send_to_backend = (
        event_publisher.send_to_backend
    )

    event_publisher.send_to_backend = False

    try:

        event_publisher.clear_events()

        visitor_id = "visitor-001"

        # --------------------------------------------------
        # Visitor detected
        # --------------------------------------------------

        VisionEventBridge.publish(
            event_type="visitor_detected",
            visitor_id=visitor_id,
            data={
                "person_count": 1,
                "detection_source": "yolo11n",
            },
        )

        # --------------------------------------------------
        # Visitor arrived
        # --------------------------------------------------

        VisionEventBridge.publish(
            event_type="visitor_arrived",
            visitor_id=visitor_id,
            data={
                "person_count": 1,
            },
        )

        # --------------------------------------------------
        # Reception started
        # --------------------------------------------------

        VisionEventBridge.publish(
            event_type="reception_started",
            visitor_id=visitor_id,
            data={
                "mode": "physical_reception",
            },
        )

        # --------------------------------------------------
        # Reception ended
        # --------------------------------------------------

        VisionEventBridge.publish(
            event_type="reception_ended",
            visitor_id=visitor_id,
            data={
                "reason": "visitor_left",
            },
        )

        # --------------------------------------------------
        # Visitor left
        # --------------------------------------------------

        VisionEventBridge.publish(
            event_type="visitor_left",
            visitor_id=visitor_id,
            data={
                "person_count": 0,
            },
        )

        # --------------------------------------------------
        # Validate
        # --------------------------------------------------

        events = event_publisher.get_events()

        assert len(events) == 5

        print(
            "[TEST] Vision events published: PASS"
        )

        expected_types = [
            "visitor_detected",
            "visitor_arrived",
            "reception_started",
            "reception_ended",
            "visitor_left",
        ]

        actual_types = [
            event["event_type"]
            for event in events
        ]

        assert actual_types == expected_types

        print(
            "[TEST] Event types: PASS"
        )

        # --------------------------------------------------
        # Validate every event
        # --------------------------------------------------

        for event in events:

            assert (
                event["source"]
                == "vision"
            )

            assert (
                event["channel"]
                == "physical"
            )

            assert (
                event["visitor_id"]
                == visitor_id
            )

            assert (
                event["call_sid"]
                is None
            )

            assert (
                event["conversation_id"]
                is None
            )

        print(
            "[TEST] Visitor identity isolation: PASS"
        )

        # --------------------------------------------------
        # Validate event data
        # --------------------------------------------------

        detected_event = next(
            event
            for event in events
            if event["event_type"]
            == "visitor_detected"
        )

        assert (
            detected_event["data"]["person_count"]
            == 1
        )

        assert (
            detected_event["data"][
                "detection_source"
            ]
            == "yolo11n"
        )

        left_event = next(
            event
            for event in events
            if event["event_type"]
            == "visitor_left"
        )

        assert (
            left_event["data"]["person_count"]
            == 0
        )

        print(
            "[TEST] Event data integrity: PASS"
        )

        # --------------------------------------------------
        # Test second visitor isolation
        # --------------------------------------------------

        VisionEventBridge.publish(
            event_type="visitor_detected",
            visitor_id="visitor-002",
            data={
                "person_count": 1,
            },
        )

        events = event_publisher.get_events()

        assert len(events) == 6

        second_visitor_event = events[-1]

        assert (
            second_visitor_event["visitor_id"]
            == "visitor-002"
        )

        assert (
            second_visitor_event["visitor_id"]
            != visitor_id
        )

        print(
            "[TEST] Multiple visitor isolation: PASS"
        )

        print()
        print("=" * 70)
        print("PHASE 12.4 VISION INTEGRATION LAYER COMPLETE")
        print("=" * 70)
        print()

    finally:

        event_publisher.clear_events()

        event_publisher.send_to_backend = (
            original_send_to_backend
        )


if __name__ == "__main__":
    run_test()