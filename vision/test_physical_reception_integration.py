from __future__ import annotations

import time

from integration.event_publisher import event_publisher
from vision.reception.reception_controller import (
    ReceptionController,
    ReceptionState,
)


def main() -> None:

    print("=" * 70)
    print("PHASE 12.6 - PHYSICAL RECEPTION INTEGRATION TEST")
    print("=" * 70)

    # ---------------------------------------------------------
    # Local test only.
    # Do not send events to the real shared backend.
    # ---------------------------------------------------------

    event_publisher.send_to_backend = False
    event_publisher.clear_events()

    # Use short delays so the test completes quickly.
    reception = ReceptionController(
        greeting_delay=0.0,
        visitor_timeout=0.1,
    )

    # =========================================================
    # STEP 1 - Simulate VisitorTracker output
    # =========================================================

    # This represents:
    #
    # Camera -> YOLO -> ByteTrack
    #
    # where ByteTrack returned tracker ID 42.

    tracker_output = [
        {
            "visitor_id": 42,
        }
    ]

    visitor_ids = [
        visitor["visitor_id"]
        for visitor in tracker_output
    ]

    # This is the exact call made by physical_reception.py.
    reception.update_visitors(visitor_ids)

    events = event_publisher.get_events()

    assert len(events) == 3

    assert events[0]["event_type"] == "visitor_detected"
    assert events[1]["event_type"] == "visitor_arrived"
    assert events[2]["event_type"] == "reception_started"

    print("[TEST] Camera -> tracker -> controller: PASS")
    print("[TEST] Visitor detected event: PASS")
    print("[TEST] Visitor arrived event: PASS")
    print("[TEST] Reception started event: PASS")

    # =========================================================
    # STEP 2 - Verify physical channel
    # =========================================================

    for event in events:

        assert event["source"] == "vision"
        assert event["channel"] == "physical"
        assert event["visitor_id"] == "1"

    print("[TEST] Vision source identity: PASS")
    print("[TEST] Physical channel identity: PASS")

    # =========================================================
    # STEP 3 - Verify ByteTrack ID is not physical identity
    # =========================================================

    # Simulate the tracker changing its ID.
    #
    # Previous tracker ID:
    #     42
    #
    # New tracker ID:
    #     91
    #
    # The same physical visitor must remain visitor #1.

    tracker_output = [
        {
            "visitor_id": 91,
        }
    ]

    visitor_ids = [
        visitor["visitor_id"]
        for visitor in tracker_output
    ]

    reception.update_visitors(visitor_ids)

    events = event_publisher.get_events()

    assert len(events) == 3

    assert reception.get_primary_visitor() == 1
    assert reception.get_active_visitor_count() == 1

    print("[TEST] ByteTrack ID change handling: PASS")
    print("[TEST] Physical visitor identity persistence: PASS")

    # =========================================================
    # STEP 4 - Verify temporary detection loss
    # =========================================================

    reception.update_visitors([])

    # Only a temporary loss occurred.
    # Visitor must still be considered active.

    assert reception.get_primary_visitor() == 1
    assert reception.get_active_visitor_count() == 1

    events = event_publisher.get_events()

    assert len(events) == 3

    print("[TEST] Temporary detection loss handling: PASS")

    # =========================================================
    # STEP 5 - Verify real visitor departure
    # =========================================================

    time.sleep(0.15)

    reception.update_visitors([])

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

    assert (
        reception.state
        == ReceptionState.VISITOR_LEFT
    )

    print("[TEST] Visitor timeout detection: PASS")
    print("[TEST] Visitor left event: PASS")

    # =========================================================
    # STEP 6 - Verify new visitor arrival
    # =========================================================

    tracker_output = [
        {
            "visitor_id": 200,
        }
    ]

    visitor_ids = [
        visitor["visitor_id"]
        for visitor in tracker_output
    ]

    reception.update_visitors(visitor_ids)

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
        reception.get_primary_visitor()
        == 1
    )

    print("[TEST] New visitor detection: PASS")
    print("[TEST] New visitor lifecycle: PASS")

    # =========================================================
    # STEP 7 - Verify reception end
    # =========================================================

    reception.finish_interaction()

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

    print("[TEST] Reception ended event: PASS")
    print("[TEST] Controller cleanup: PASS")

    # =========================================================
    # STEP 8 - Print complete physical event flow
    # =========================================================

    print()
    print("[TEST] COMPLETE PHYSICAL EVENT FLOW:")

    for index, event in enumerate(
        events,
        start=1,
    ):

        print(
            f"  {index}. "
            f"{event['event_type']} "
            f"| source={event['source']} "
            f"| channel={event['channel']} "
            f"| visitor={event['visitor_id']}"
        )

    # =========================================================
    # FINAL
    # =========================================================

    print("=" * 70)
    print(
        "PHASE 12.6 PHYSICAL RECEPTION "
        "INTEGRATION COMPLETE"
    )
    print("=" * 70)


if __name__ == "__main__":
    main()