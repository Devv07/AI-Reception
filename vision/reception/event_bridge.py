from __future__ import annotations

from typing import Any

from integration.event_publisher import event_publisher


class VisionEventBridge:
    """
    Converts physical reception / vision events into shared
    backend integration events.

    The vision system remains independent from:
    - FastAPI
    - PostgreSQL
    - AI/RAG
    - Twilio

    Backend failures must never stop camera processing.
    """

    PUBLISHED_EVENTS = {
        "visitor_detected",
        "visitor_arrived",
        "visitor_left",
        "reception_started",
        "reception_ended",
    }

    @classmethod
    def publish(
        cls,
        event_type: str,
        visitor_id: str,
        data: dict[str, Any] | None = None,
    ) -> None:

        if event_type not in cls.PUBLISHED_EVENTS:
            return

        if not visitor_id:
            raise ValueError(
                "visitor_id is required"
            )

        try:

            result = (
                event_publisher.publish_visitor_event(
                    event_type=event_type,
                    visitor_id=visitor_id,
                    data=data or {},
                )
            )

            if not result.get("success"):

                print(
                    "[VISION EVENT BRIDGE] "
                    f"Backend delivery failed for "
                    f"{event_type}: "
                    f"{result.get('error', 'Unknown error')}"
                )

        except Exception as exc:

            print(
                "[VISION EVENT BRIDGE] "
                f"Event publishing error for "
                f"{event_type}: {exc}"
            )