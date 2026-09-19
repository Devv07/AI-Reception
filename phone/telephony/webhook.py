from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import Response

from phone.session.manager import call_manager


router = APIRouter(prefix="/phone", tags=["Phone"])


@router.post("/incoming")
async def incoming_call(request: Request):
    form = await request.form()

    call_sid = str(form.get("CallSid", ""))
    caller_number = str(form.get("From", ""))
    called_number = str(form.get("To", ""))

    print()
    print("=" * 70)
    print("[PHONE INCOMING]")
    print(f"Call SID:       {call_sid}")
    print(f"Caller:         {caller_number}")
    print(f"Twilio Number:  {called_number}")
    print("=" * 70)

    if not call_sid:
        return Response(
            content="Missing CallSid",
            status_code=400,
            media_type="text/plain",
        )

    # Create or reuse the call session.
    session = call_manager.get_call(call_sid)

    if session is None:
        session = call_manager.create_call(
            call_sid=call_sid,
            caller_number=caller_number,
            called_number=called_number,
        )

    session.add_event(
        "incoming_call",
        {
            "caller_number": caller_number,
            "called_number": called_number,
        },
    )

    # ---------------------------------------------------------
    # TRIAL-SAFE TEST RESPONSE
    # ---------------------------------------------------------
    #
    # Twilio Trial blocks <Stream>, so we intentionally use
    # <Say> here to prove that:
    #
    # Phone -> Twilio -> our webhook -> TwiML -> phone
    #
    # Once this works, we can move to the AI voice flow.
    #
    twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say>
        Hello. You have successfully reached the AI Reception system.
        Your call is connected to our application.
    </Say>
</Response>
"""

    session.add_event(
        "trial_safe_response",
        {
            "mode": "say_test",
        },
    )

    print("[PHONE INCOMING] Returning trial-safe <Say> response.")
    print()

    return Response(
        content=twiml,
        media_type="application/xml",
    )