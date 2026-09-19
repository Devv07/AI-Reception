from __future__ import annotations

import asyncio
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from phone.telephony.webhook import router, call_manager


app = FastAPI()

app.include_router(router)


async def run_test() -> None:

    print()
    print("=" * 60)
    print("PHASE 10.2 - INCOMING CALL WEBHOOK TEST")
    print("=" * 60)
    print()

    call_manager._sessions.clear()

    test_call_sid = "TEST-CALL-100"
    caller = "+9779800000000"
    receiver = "+9779811111111"

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:

        response = await client.post(
            "/phone/incoming",
            data={
                "CallSid": test_call_sid,
                "From": caller,
                "To": receiver,
            },
        )

    assert response.status_code == 200
    print("[TEST 1] Webhook HTTP response: PASS")

    assert response.headers["content-type"].startswith(
        "application/xml"
    )
    print("[TEST 2] TwiML content type: PASS")

    body = response.text

    assert "<Response>" in body
    assert "<Say>" in body
    assert "<Hangup/>" in body
    print("[TEST 3] TwiML structure: PASS")

    assert "Hello. You have reached the AI reception system." in body
    print("[TEST 4] Greeting response: PASS")

    session = call_manager.get_call(test_call_sid)

    assert session is not None
    print("[TEST 5] CallSession creation: PASS")

    assert session.call_sid == test_call_sid
    assert session.caller_number == caller
    assert session.called_number == receiver
    print("[TEST 6] Caller information: PASS")

    assert session.conversation_id.startswith("phone-")
    print("[TEST 7] Conversation ID: PASS")
    print(
        f"          Conversation: "
        f"{session.conversation_id}"
    )

    event_types = [
        event["type"]
        for event in session.events
    ]

    assert "call_created" in event_types
    assert "incoming_call" in event_types
    print("[TEST 8] Incoming call event: PASS")

    assert session.active is True
    print("[TEST 9] Call active state: PASS")

    print()
    print("CALL SESSION")
    print("-" * 60)
    print(session.get_status())

    print()
    print("=" * 60)
    print("ALL PHASE 10.2 TESTS PASSED")
    print("=" * 60)
    print()


if __name__ == "__main__":
    asyncio.run(run_test())