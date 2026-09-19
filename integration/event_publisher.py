from __future__ import annotations

import asyncio
import json
from typing import Any

from integration.backend_client import BackendIntegrationClient
from integration.event import IntegrationEvent


class EventPublisher:
    """
    Publishes AI Reception events.

    The publisher has two responsibilities:

    1. Keep a local event history for debugging.
    2. Send events to the shared backend when configured.

    A backend failure does NOT crash the reception system.
    """

    def __init__(
        self,
        backend_client: BackendIntegrationClient | None = None,
        send_to_backend: bool = True,
    ) -> None:

        self.backend_client = (
            backend_client
            or BackendIntegrationClient()
        )

        self.send_to_backend = send_to_backend

        self.events: list[IntegrationEvent] = []

    def publish(
        self,
        event: IntegrationEvent,
    ) -> dict[str, Any]:

        if not isinstance(event, IntegrationEvent):
            raise TypeError(
                "event must be an IntegrationEvent"
            )

        self.events.append(event)

        print()
        print("[INTEGRATION EVENT]")
        print(
            json.dumps(
                event.to_dict(),
                indent=2,
                ensure_ascii=False,
            )
        )

        if not self.send_to_backend:
            return {
                "success": True,
                "backend_sent": False,
                "event_id": event.event_id,
            }

        result = self.backend_client.send_event(event)

        if result.get("success"):
            print(
                "[INTEGRATION] Backend event sent successfully."
            )
        else:
            print(
                "[INTEGRATION] Backend event delivery failed:"
            )
            print(
                f"  {result.get('error', 'Unknown error')}"
            )

        return {
            **result,
            "backend_sent": True,
        }

    async def publish_async(
        self,
        event: IntegrationEvent,
    ) -> dict[str, Any]:

        return await asyncio.to_thread(
            self.publish,
            event,
        )

    def publish_call_event(
        self,
        event_type: str,
        call_sid: str,
        conversation_id: str,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:

        event = IntegrationEvent(
            event_type=event_type,
            source="phone",
            call_sid=call_sid,
            conversation_id=conversation_id,
            channel="phone",
            data=data or {},
        )

        return self.publish(event)

    async def publish_call_event_async(
        self,
        event_type: str,
        call_sid: str,
        conversation_id: str,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:

        event = IntegrationEvent(
            event_type=event_type,
            source="phone",
            call_sid=call_sid,
            conversation_id=conversation_id,
            channel="phone",
            data=data or {},
        )

        return await self.publish_async(event)

    def publish_visitor_event(
        self,
        event_type: str,
        visitor_id: str,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:

        event = IntegrationEvent(
            event_type=event_type,
            source="vision",
            visitor_id=visitor_id,
            channel="physical",
            data=data or {},
        )

        return self.publish(event)

    def get_events(self) -> list[dict[str, Any]]:
        return [
            event.to_dict()
            for event in self.events
        ]

    def clear_events(self) -> None:
        self.events.clear()


event_publisher = EventPublisher()