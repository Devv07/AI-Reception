from __future__ import annotations

import time

from integration.event_publisher import event_publisher
from vision.reception.reception_controller import (
    ReceptionController,
)


def main() -> None:

    print("=" * 70)
    print("PHASE 12.5 - RECEPTION CONTROLLER EVENT TEST")
    print("=" * 70)

    # ---------------------------------------------------------
    # Disable real backend during local test.
    # ---------------------------------------------------------

    event_publisher.send_to_backend = False
    event_publisher.clear_events()

    controller = ReceptionController(
        greeting_delay=0.0,
        visitor_timeout=0.1,
    )

    # ---------------------------------------------------------
    # 1. Visitor detection
    # ---------------------------------------------------------

    controller.update_visitors([7])

    events = event_publisher.get_events()

    assert len(events) == 3, (
        f"Expected 3 events after arrival, "
        f"got {len(events)}"
    )

    assert events[0]["event_type"] == "visitor_detected"
    assert events[1]["event_type"] == "visitor_arrived"
    assert events[2]["event_type"] == "reception_started"

    print("[TEST] Visitor detection event: PASS")
    print("[TEST] Visitor arrival event: PASS")
    print("[TEST] Reception started event: PASS")

    # ---------------------------------------------------------
    # 2. Verify logical visitor identity
    # ---------------------------------------------------------

    for event in events:

        assert event["visitor_id"] == "1"
        assert event["channel"] == "physical"
        assert event["source"] == "vision"
        assert event["call_sid"] is None
        assert event["conversation_id"] is None

    print("[TEST] Visitor identity: PASS")
    print("[TEST] Physical channel identity: PASS")

    # ---------------------------------------------------------
    # 3. ByteTrack ID must not become visitor identity
    # ---------------------------------------------------------

    controller.update_visitors([99])

    events = event_publisher.get_events()

    # The physical visitor is still present.
    # Therefore no new arrival event should be generated.
    assert len(events) == 3

    assert (
        controller.get_primary_visitor()
        == 1
    )

    print("[TEST] ByteTrack ID isolation: PASS")

    # ---------------------------------------------------------
    # 4. Visitor leaves
    # ---------------------------------------------------------

    time.sleep(0.15)

    controller.update_visitors([])

    events = event_publisher.get_events()

    assert len(events) == 4

    assert (
        events[-1]["event_type"]
        == "visitor_left"
    )

    assert (
        events[-1]["visitor_id"]
        == "1"
    )

    assert (
        events[-1]["data"]["reason"]
        == "visitor_timeout"
    )

    print("[TEST] Visitor left event: PASS")

    # ---------------------------------------------------------
    # 5. New visitor after previous visitor left
    # ---------------------------------------------------------

    controller.update_visitors([123])

    events = event_publisher.get_events()

    assert len(events) == 7

    assert (
        events[-3]["event_type"]
        == "visitor_detected"
    )

    assert (
        events[-2]["event_type"]
        == "visitor_arrived"
    )

    assert (
        events[-1]["event_type"]
        == "reception_started"
    )

    assert (
        events[-3]["visitor_id"]
        == "1"
    )

    print("[TEST] New visitor lifecycle: PASS")
    print("[TEST] Logical visitor ID reset behavior: PASS")

    # ---------------------------------------------------------
    # 6. Finish interaction
    # ---------------------------------------------------------

    controller.finish_interaction()

    events = event_publisher.get_events()

    assert len(events) == 8

    assert (
        events[-1]["event_type"]
        == "reception_ended"
    )

    assert (
        events[-1]["visitor_id"]
        == "1"
    )

    assert (
        events[-1]["data"]["reason"]
        == "interaction_finished"
    )

    assert (
        controller.get_primary_visitor()
        is None
    )

    assert (
        controller.get_active_visitor_count()
        == 0
    )

    print("[TEST] Reception ended event: PASS")
    print("[TEST] Controller reset: PASS")

    # ---------------------------------------------------------
    # 7. Print event sequence
    # ---------------------------------------------------------

    print()
    print("[TEST] Published event sequence:")

    for index, event in enumerate(
        events,
        start=1,
    ):

        print(
            f"  {index}. "
            f"{event['event_type']} "
            f"(visitor={event['visitor_id']})"
        )

    print("=" * 70)
    print(
        "PHASE 12.5 RECEPTION CONTROLLER "
        "INTEGRATION COMPLETE"
    )
    print("=" * 70)


if __name__ == "__main__":
    main()