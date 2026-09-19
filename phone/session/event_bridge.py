from __future__ import annotations

from typing import Any

from integration.event_publisher import event_publisher


class PhoneEventBridge:
    """
    Converts internal CallSession events into shared backend events.

    Backend failures must never terminate an active phone call.
    """

    PUBLISHED_EVENTS = {
        "call_created",
        "incoming_call",
        "stream_attached",
        "stream_detached",

        # Phone processing
        "caller_audio_received",
        "speech_received",
        "ai_response_generated",
        "tts_generated",
        "twilio_media_response_ready",

        # Handoff
        "call_handoff",
        "handoff_transfer_result",

        # Call lifecycle
        "call_closed",
    }

    @classmethod
    def publish(
        cls,
        event_type: str,
        call_sid: str,
        conversation_id: str,
        data: dict[str, Any] | None = None,
    ) -> None:

        if event_type not in cls.PUBLISHED_EVENTS:
            return

        try:
            result = event_publisher.publish_call_event(
                event_type=event_type,
                call_sid=call_sid,
                conversation_id=conversation_id,
                data=data or {},
            )

            if not result.get("success"):
                print(
                    "[PHONE EVENT BRIDGE] "
                    f"Backend delivery failed for "
                    f"{event_type}: "
                    f"{result.get('error', 'Unknown error')}"
                )

        except Exception as exc:
            print(
                "[PHONE EVENT BRIDGE] "
                f"Event publishing error for "
                f"{event_type}: {exc}"
            )