from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


class CameraLike(Protocol):
    def start(self) -> None: ...
    def read(self) -> Any: ...
    def is_opened(self) -> bool: ...
    def release(self) -> None: ...


class TrackerLike(Protocol):
    def track(self, frame: Any) -> list[dict[str, Any]]: ...


class ReceptionControllerLike(Protocol):
    def update_visitors(self, visitor_ids: list[int]) -> None: ...
    def get_last_event(self) -> str | None: ...
    def get_active_visitor_count(self) -> int: ...
    def get_primary_visitor(self) -> int | None: ...


@dataclass(frozen=True)
class PresenceSnapshot:
    available: bool
    present: bool
    state: str
    primary_visitor_id: int | None
    event: str | None = None
    error: str | None = None


class VisitorPresenceAdapter:
    """
    Adapter between Member 2's physical vision system and
    the shared reception presence interface.

    Important distinction:

    - ReceptionController uses logical visitor ID #1 for the
      physical receptionist lifecycle.
    - This adapter exposes the current ByteTrack visitor ID
      because the presence adapter represents raw vision
      presence information expected by the shared contract.

    The ReceptionController itself is not modified.
    """

    def __init__(
        self,
        camera: CameraLike,
        tracker: TrackerLike,
        controller: ReceptionControllerLike,
    ) -> None:
        self.camera = camera
        self.tracker = tracker
        self.controller = controller

        self._started = False
        self._last_present = False
        self._current_tracker_id: int | None = None

    @classmethod
    def from_member2(
        cls,
        camera_index: int = 0,
        model_path: str = "yolo11n.pt",
    ) -> "VisitorPresenceAdapter":
        try:
            from vision.camera.camera import Camera
            from vision.reception.reception_controller import (
                ReceptionController,
            )
            from vision.tracking.visitor_tracker import VisitorTracker
        except ImportError as error:
            raise RuntimeError(
                "Member 2 vision modules are not installed"
            ) from error

        return cls(
            Camera(camera_index=camera_index),
            VisitorTracker(model_path=model_path),
            ReceptionController(),
        )

    def poll(self) -> PresenceSnapshot:
        if not self._started:
            try:
                self.camera.start()
                self._started = True
            except Exception:
                return PresenceSnapshot(
                    available=False,
                    present=self._last_present,
                    state="idle",
                    primary_visitor_id=self._current_tracker_id,
                    error="camera_unavailable",
                )

        try:
            if not self.camera.is_opened():
                return PresenceSnapshot(
                    available=False,
                    present=self._last_present,
                    state="idle",
                    primary_visitor_id=self._current_tracker_id,
                    error="camera_unavailable",
                )

            frame = self.camera.read()

            if frame is None:
                return self._snapshot(
                    error="frame_unavailable"
                )

            visitors = self.tracker.track(frame)

            visitor_ids = [
                int(visitor["visitor_id"])
                for visitor in visitors
                if "visitor_id" in visitor
            ]

            tracker_id = (
                visitor_ids[0]
                if visitor_ids
                else None
            )

            was_present = self._last_present

            self.controller.update_visitors(visitor_ids)

            self._last_present = (
                self.controller.get_active_visitor_count() > 0
            )

            self._current_tracker_id = (
                tracker_id
                if self._last_present
                else None
            )

            controller_event = (
                self.controller.get_last_event()
            )

            event_type: str | None = None

            # A new physical presence is represented as
            # visitor_detected by the adapter, regardless of
            # whether the controller has already advanced to
            # GREETING because backend event publishing took time.
            if self._last_present and not was_present:
                event_type = "visitor_detected"

            elif controller_event == "visitor_left":
                event_type = "visitor_left"

            # Preserve the semantic state of the presence
            # transition. The controller can advance internally
            # during update_visitors() because integration event
            # publishing may take time.
            if event_type == "visitor_detected":
                return self._snapshot(
                    state_override="visitor_detected",
                    event=event_type,
                )

            return self._snapshot(
                event=event_type
            )

        except Exception:
            return self._snapshot(
                error="vision_error"
            )

    def close(self) -> None:
        try:
            self.camera.release()
        finally:
            self._started = False
            self._last_present = False
            self._current_tracker_id = None

    def _get_state_name(self) -> str:
        state = getattr(
            self.controller,
            "state",
            None,
        )

        if state is None:
            return "idle"

        value = getattr(
            state,
            "value",
            None,
        )

        if value is not None:
            return str(value)

        return str(state)

    def _snapshot(
        self,
        event: str | None = None,
        error: str | None = None,
        state_override: str | None = None,
    ) -> PresenceSnapshot:
        return PresenceSnapshot(
            available=error is None,
            present=self._last_present,
            state=(
                state_override
                if state_override is not None
                else self._get_state_name()
            ),
            primary_visitor_id=self._current_tracker_id,
            event=event,
            error=error,
        )