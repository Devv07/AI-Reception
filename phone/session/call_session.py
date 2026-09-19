from __future__ import annotations

from datetime import datetime, timezone
from threading import RLock
from typing import Any
from uuid import uuid4

from phone.session.event_bridge import PhoneEventBridge


class CallSession:
    """
    Represents one isolated phone call.

    Every call gets:
    - its own Call SID
    - its own conversation ID
    - its own event history
    - its own stream SID
    - its own processing lock

    The processing lock prevents two audio chunks from the SAME
    call from being processed simultaneously.

    Different calls can still process concurrently.

    Phase 12.2:
    Selected phone lifecycle events are also forwarded to the
    shared backend through PhoneEventBridge.
    """

    def __init__(
        self,
        call_sid: str,
        caller_number: str = "",
        called_number: str = "",
    ) -> None:

        if not call_sid:
            raise ValueError("call_sid is required")

        self.call_sid = call_sid
        self.caller_number = caller_number
        self.called_number = called_number

        self.conversation_id = (
            f"phone-{uuid4().hex}"
        )

        self.created_at = self._now()
        self.updated_at = self.created_at
        self.closed_at: datetime | None = None

        self.active = True

        self.stream_sid: str | None = None

        self.metadata: dict[str, Any] = {}

        self.events: list[dict[str, Any]] = []

        self._lock = RLock()

        self.processing_lock = RLock()

    @staticmethod
    def _now() -> datetime:
        return datetime.now(timezone.utc)

    def touch(self) -> None:
        with self._lock:
            self.updated_at = self._now()

    def attach_stream(
        self,
        stream_sid: str,
    ) -> None:

        if not stream_sid:
            raise ValueError(
                "stream_sid is required"
            )

        with self._lock:

            self.stream_sid = stream_sid
            self.updated_at = self._now()

            self.add_event(
                "stream_attached",
                {
                    "stream_sid": stream_sid,
                },
            )

    def detach_stream(self) -> None:

        with self._lock:

            old_stream_sid = self.stream_sid

            self.stream_sid = None
            self.updated_at = self._now()

            self.add_event(
                "stream_detached",
                {
                    "stream_sid": old_stream_sid,
                },
            )

    def add_event(
        self,
        event_type: str,
        data: dict[str, Any] | None = None,
    ) -> None:

        if not event_type:
            raise ValueError(
                "event_type is required"
            )

        event_data = data or {}

        event = {
            "type": event_type,
            "timestamp": self._now().isoformat(),
            "call_sid": self.call_sid,
            "conversation_id": self.conversation_id,
            "data": event_data,
        }

        with self._lock:

            self.events.append(event)
            self.updated_at = self._now()

        # --------------------------------------------------
        # Phase 12.2
        # Send selected phone lifecycle events to the
        # shared backend.
        #
        # This is intentionally outside the session lock.
        # The backend must never hold the CallSession lock.
        # --------------------------------------------------

        PhoneEventBridge.publish(
            event_type=event_type,
            call_sid=self.call_sid,
            conversation_id=self.conversation_id,
            data={
                **event_data,
                "caller_number": self.caller_number,
                "called_number": self.called_number,
            },
        )

    def close(
        self,
        reason: str = "completed",
    ) -> None:

        with self._lock:

            if not self.active:
                return

            self.active = False
            self.closed_at = self._now()
            self.updated_at = self.closed_at

        self.add_event(
            "call_closed",
            {
                "reason": reason,
            },
        )

    def get_duration(self) -> float:

        with self._lock:

            end_time = (
                self.closed_at
                or self._now()
            )

            return (
                end_time - self.created_at
            ).total_seconds()

    def get_idle_duration(self) -> float:

        with self._lock:

            return (
                self._now() - self.updated_at
            ).total_seconds()

    def get_status(
        self,
    ) -> dict[str, Any]:

        with self._lock:

            return {
                "call_sid": self.call_sid,
                "caller_number": self.caller_number,
                "called_number": self.called_number,
                "conversation_id": self.conversation_id,
                "active": self.active,
                "stream_sid": self.stream_sid,
                "created_at": (
                    self.created_at.isoformat()
                ),
                "updated_at": (
                    self.updated_at.isoformat()
                ),
                "closed_at": (
                    self.closed_at.isoformat()
                    if self.closed_at
                    else None
                ),
                "duration_seconds": (
                    self.get_duration()
                ),
                "event_count": len(self.events),
            }

    def get_events(
        self,
    ) -> list[dict[str, Any]]:

        with self._lock:
            return list(self.events)

    def __repr__(self) -> str:

        return (
            f"CallSession("
            f"call_sid={self.call_sid!r}, "
            f"conversation_id="
            f"{self.conversation_id!r}, "
            f"active={self.active!r}"
            f")"
        )