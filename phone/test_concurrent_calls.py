from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from time import sleep

from phone.session.call_manager import CallManager


def create_test_call(
    manager: CallManager,
    index: int,
):
    call_sid = f"CA_CONCURRENT_{index:03d}"

    session = manager.create_call(
        call_sid=call_sid,
        caller_number=f"+9779804720{index:03d}",
        called_number="+17372508034",
    )

    session.add_event(
        "test_processing_started",
        {
            "test_index": index,
        },
    )

    # Simulate a little processing time.
    sleep(0.2)

    session.add_event(
        "test_processing_finished",
        {
            "test_index": index,
        },
    )

    return session


def main() -> None:
    print()
    print("=" * 70)
    print("PHASE 11.1 - CONCURRENT CALL SESSION TEST")
    print("=" * 70)

    manager = CallManager()

    number_of_calls = 10

    print(f"[TEST] Creating {number_of_calls} simultaneous calls...")

    with ThreadPoolExecutor(
        max_workers=number_of_calls
    ) as executor:

        sessions = list(
            executor.map(
                lambda index: create_test_call(manager, index),
                range(1, number_of_calls + 1),
            )
        )

    print()
    print("[TEST] Checking session isolation...")

    assert len(sessions) == number_of_calls
    assert manager.count_total() == number_of_calls
    assert manager.count_active() == number_of_calls

    call_sids = {
        session.call_sid
        for session in sessions
    }

    conversation_ids = {
        session.conversation_id
        for session in sessions
    }

    # Every call SID must be unique.
    assert len(call_sids) == number_of_calls

    # Every conversation ID must be unique.
    assert len(conversation_ids) == number_of_calls

    # Verify each session contains only its own events.
    for session in sessions:
        events = session.get_events()

        assert events

        for event in events:
            assert event["call_sid"] == session.call_sid
            assert event["conversation_id"] == session.conversation_id

    print("[TEST] Unique Call SIDs:       PASS")
    print("[TEST] Unique conversation IDs: PASS")
    print("[TEST] Event isolation:         PASS")
    print("[TEST] Active session count:     PASS")

    print()
    print("[TEST] Closing all calls...")

    for session in sessions:
        manager.close_call(
            session.call_sid,
            reason="concurrent_test_complete",
        )

    assert manager.count_active() == 0
    assert manager.count_total() == number_of_calls

    print("[TEST] All calls closed:        PASS")

    print()
    print("=" * 70)
    print("PHASE 11.1 COMPLETE")
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()