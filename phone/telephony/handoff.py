from __future__ import annotations

from typing import Any

from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse

from phone.config import (
    REAL_RECEPTION_PHONE_NUMBER,
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
    TWILIO_PHONE_NUMBER,
)


class PhoneHandoffManager:
    """
    Transfers an active AI Reception call
    to the human receptionist.
    """

    def __init__(self) -> None:
        if not TWILIO_ACCOUNT_SID:
            raise RuntimeError("TWILIO_ACCOUNT_SID is not configured")

        if not TWILIO_AUTH_TOKEN:
            raise RuntimeError("TWILIO_AUTH_TOKEN is not configured")

        if not TWILIO_PHONE_NUMBER:
            raise RuntimeError("TWILIO_PHONE_NUMBER is not configured")

        if not REAL_RECEPTION_PHONE_NUMBER:
            raise RuntimeError("REAL_RECEPTION_PHONE_NUMBER is not configured")

        self.client = Client(
            TWILIO_ACCOUNT_SID,
            TWILIO_AUTH_TOKEN,
        )

    def build_transfer_twiml(self) -> str:
        response = VoiceResponse()

        response.say(
            "Please wait while I connect you with our receptionist."
        )

        dial = response.dial(
            timeout=30,
            caller_id=TWILIO_PHONE_NUMBER,
        )

        dial.number(REAL_RECEPTION_PHONE_NUMBER)

        return str(response)

    def transfer_call(self, call_sid: str) -> dict[str, Any]:
        if not call_sid:
            raise ValueError("call_sid is required")

        twiml = self.build_transfer_twiml()

        print()
        print("=" * 60)
        print("[PHONE HANDOFF]")
        print(f"Call SID: {call_sid}")
        print(f"Transferring to: {REAL_RECEPTION_PHONE_NUMBER}")
        print("=" * 60)

        call = self.client.calls(call_sid).update(
            twiml=twiml
        )

        print(
            f"[PHONE HANDOFF] Twilio accepted transfer: "
            f"{call.sid}"
        )

        return {
            "success": True,
            "call_sid": call.sid,
            "target_number": REAL_RECEPTION_PHONE_NUMBER,
            "status": getattr(call, "status", None),
            "twiml": twiml,
        }


handoff_manager = PhoneHandoffManager()