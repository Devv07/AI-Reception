from __future__ import annotations

import asyncio
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from phone.audio.ai_adapter import PhoneAIAdapter
from phone.session.manager import call_manager


async def main() -> None:
    print()
    print("=" * 60)
    print("PHASE 10.6 - PHONE AI BRAIN TEST")
    print("=" * 60)
    print()

    print("[SETUP] Creating test phone call session...")

    call_sid = "CA_PHASE10_6_TEST"

    existing = call_manager.get_call(call_sid)
    if existing is not None:
        call_manager.remove_call(call_sid)

    session = call_manager.create_call(
        call_sid=call_sid,
        caller_number="+9779800000000",
        called_number="+9770100000000",
    )

    assert session.active
    assert session.conversation_id

    print("[TEST 1] Phone CallSession creation: PASS")
    print(f"          Call SID: {session.call_sid}")
    print(f"          Conversation ID: {session.conversation_id}")

    ai = PhoneAIAdapter()

    print("[TEST 2] Phone AI adapter initialization: PASS")

    caller_message = (
        "Hello, I need information about the college."
    )

    print()
    print("[TEST 3] Sending caller message to shared AI Brain...")
    print(f"          Message: {caller_message}")

    response = await ai.process_message(
        message=caller_message,
        conversation_id=session.conversation_id,
        caller_number=session.caller_number,
        call_sid=session.call_sid,
    )

    assert isinstance(response, str)
    assert response.strip()

    print()
    print("[TEST 3] Shared AI Brain response: PASS")
    print(f"          AI: {response}")

    session.add_event(
        "caller_message",
        {"text": caller_message},
    )

    session.add_event(
        "ai_response",
        {"text": response},
    )

    print()
    print("[TEST 4] Conversation event tracking: PASS")

    status = session.get_status()

    assert status["conversation_id"] == session.conversation_id
    assert status["event_count"] >= 3

    print("[TEST 5] Conversation ID preservation: PASS")
    print(f"          Conversation ID: {status['conversation_id']}")

    print()
    print("SESSION STATUS")
    print("-" * 60)

    for key, value in status.items():
        print(f"{key}: {value}")

    print()
    print("=" * 60)
    print("ALL PHASE 10.6 TESTS PASSED")
    print("=" * 60)
    print()


if __name__ == "__main__":
    asyncio.run(main())