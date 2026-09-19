from __future__ import annotations

from threading import RLock
from typing import Any

from phone.session.call_session import CallSession


class CallManager:
    """
    Thread-safe manager for multiple simultaneous phone calls.

    Every CallSession is completely independent.

    Example:

        CA001 -> conversation phone-aaa
        CA002 -> conversation phone-bbb
        CA003 -> conversation phone-ccc
    """

    def __init__(self) -> None:
        self._calls: dict[str, CallSession] = {}
        self._lock = RLock()

    def create_call(
        self,
        call_sid: str,
        caller_number: str = "",
        called_number: str = "",
    ) -> CallSession:
        if not call_sid:
            raise ValueError("call_sid is required")

        with self._lock:
            existing = self._calls.get(call_sid)

            if existing is not None:
                return existing

            session = CallSession(
                call_sid=call_sid,
                caller_number=caller_number,
                called_number=called_number,
            )

            session.add_event(
                "call_created",
                {
                    "caller_number": caller_number,
                    "called_number": called_number,
                },
            )

            self._calls[call_sid] = session

            print(
                f"[PHONE] Call session created: "
                f"{call_sid} "
                f"conversation={session.conversation_id}"
            )

            return session

    def get_call(self, call_sid: str) -> CallSession | None:
        if not call_sid:
            return None

        with self._lock:
            return self._calls.get(call_sid)

    def require_call(self, call_sid: str) -> CallSession:
        session = self.get_call(call_sid)

        if session is None:
            raise KeyError(f"Call session not found: {call_sid}")

        return session

    def close_call(
        self,
        call_sid: str,
        reason: str = "completed",
    ) -> CallSession:
        with self._lock:
            session = self.require_call(call_sid)
            session.close(reason)
            return session

    def remove_call(self, call_sid: str) -> CallSession | None:
        with self._lock:
            return self._calls.pop(call_sid, None)

    def active_calls(self) -> list[CallSession]:
        with self._lock:
            return [
                session
                for session in self._calls.values()
                if session.active
            ]

    def all_calls(self) -> list[CallSession]:
        with self._lock:
            return list(self._calls.values())

    def count_active(self) -> int:
        with self._lock:
            return sum(
                1
                for session in self._calls.values()
                if session.active
            )

    def count_total(self) -> int:
        with self._lock:
            return len(self._calls)

    def status(self) -> dict[str, Any]:
        with self._lock:
            calls = list(self._calls.values())

            return {
                "total_calls": len(calls),
                "active_calls": sum(
                    1 for session in calls if session.active
                ),
                "closed_calls": sum(
                    1 for session in calls if not session.active
                ),
                "calls": [
                    session.get_status()
                    for session in calls
                ],
            }

    def clear_closed(self) -> int:
        """
        Remove closed calls from memory.

        Returns the number of removed sessions.
        """

        with self._lock:
            closed_ids = [
                call_sid
                for call_sid, session in self._calls.items()
                if not session.active
            ]

            for call_sid in closed_ids:
                del self._calls[call_sid]

            return len(closed_ids)