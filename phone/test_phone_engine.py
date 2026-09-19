from __future__ import annotations

import sys
import time
from pathlib import Path


# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from phone.session.call_manager import CallManager


def main() -> None:

    print()
    print("=" * 60)
    print("PHASE 10.1 - PHONE CALL ENGINE TEST")
    print("=" * 60)
    print()

    manager = CallManager()

    # ========================================================
    # TEST 1
    # ========================================================

    call = manager.create_call(
        call_sid="TEST-CALL-001",
        caller_number="+9779800000000",
        called_number="+9779811111111",
    )

    assert call.active is True

    print("[TEST 1] Call session creation: PASS")

    # ========================================================
    # TEST 2
    # ========================================================

    assert call.call_sid == "TEST-CALL-001"

    assert call.caller_number == "+9779800000000"

    assert call.called_number == "+9779811111111"

    print("[TEST 2] Call information: PASS")

    # ========================================================
    # TEST 3
    # ========================================================

    conversation_id = call.conversation_id

    assert conversation_id.startswith(
        "phone-"
    )

    print(
        "[TEST 3] Conversation ID generation: PASS"
    )

    print(
        f"          Conversation: {conversation_id}"
    )

    # ========================================================
    # TEST 4
    # ========================================================

    call.attach_stream(
        "TEST-STREAM-001"
    )

    assert (
        call.stream_sid
        == "TEST-STREAM-001"
    )

    print(
        "[TEST 4] Stream attachment: PASS"
    )

    # ========================================================
    # TEST 5
    # ========================================================

    call.add_event(
        "visitor_message",
        {
            "text": "Hello",
        },
    )

    assert len(call.events) >= 2

    print(
        "[TEST 5] Event tracking: PASS"
    )

    # ========================================================
    # TEST 6
    # ========================================================

    time.sleep(0.1)

    call.touch()

    assert call.get_duration() >= 0

    assert call.get_idle_duration() >= 0

    print(
        "[TEST 6] Activity tracking: PASS"
    )

    # ========================================================
    # TEST 7
    # ========================================================

    active_count = manager.get_active_call_count()

    assert active_count == 1

    print(
        "[TEST 7] Active call management: PASS"
    )

    # ========================================================
    # TEST 8
    # ========================================================

    manager.close_call(
        "TEST-CALL-001",
        reason="test_completed",
    )

    assert call.active is False

    assert manager.get_active_call_count() == 0

    print(
        "[TEST 8] Call closing: PASS"
    )

    # ========================================================
    # TEST 9
    # ========================================================

    second_call = manager.create_call(
        call_sid="TEST-CALL-002",
        caller_number="+9779822222222",
        called_number="+9779833333333",
    )

    assert (
        second_call.conversation_id
        != call.conversation_id
    )

    print(
        "[TEST 9] Conversation isolation: PASS"
    )

    # ========================================================
    # STATUS
    # ========================================================

    print()
    print("CALL MANAGER STATUS")
    print("-" * 60)

    status = manager.get_status()

    print(status)

    print()

    # ========================================================
    # FINAL
    # ========================================================

    print("=" * 60)
    print("ALL PHASE 10.1 TESTS PASSED")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()