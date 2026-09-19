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
    def get_last_event(self) -> dict[str, Any] | None: ...
    def get_state_name(self) -> str: ...
    def get_active_visitor_count(self) -> int: ...
    def get_primary_visitor_id(self) -> int | None: ...


@dataclass(frozen=True)
class PresenceSnapshot:
    available: bool
    present: bool
    state: str
    primary_visitor_id: int | None
    event: str | None = None
    error: str | None = None


class VisitorPresenceAdapter:
    """Expose Member 2 vision as presence events for the reception state machine."""

    def __init__(self, camera: CameraLike, tracker: TrackerLike, controller: ReceptionControllerLike):
        self.camera = camera
        self.tracker = tracker
        self.controller = controller
        self._started = False
        self._last_present = False

    @classmethod
    def from_member2(cls, camera_index: int = 0, model_path: str = "yolo11n.pt") -> "VisitorPresenceAdapter":
        try:
            from vision.camera.camera import Camera
            from vision.reception.reception_controller import ReceptionController
            from vision.tracking.visitor_tracker import VisitorTracker
        except ImportError as error:
            raise RuntimeError("Member 2 vision modules are not installed") from error

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
            except Exception as error:
                return PresenceSnapshot(False, self._last_present, "idle", None, error="camera_unavailable")

        try:
            if not self.camera.is_opened():
                return PresenceSnapshot(False, self._last_present, "idle", None, error="camera_unavailable")
            frame = self.camera.read()
            if frame is None:
                return self._snapshot(error="frame_unavailable")
            visitors = self.tracker.track(frame)
            visitor_ids = [int(visitor["visitor_id"]) for visitor in visitors if "visitor_id" in visitor]
            was_present = self._last_present
            self.controller.update_visitors(visitor_ids)
            event = self.controller.get_last_event()
            self._last_present = self.controller.get_active_visitor_count() > 0
            event_type = event.get("type") if event else (
                "visitor_detected" if self._last_present and not was_present else None
            )
            return self._snapshot(event=event_type)
        except Exception:
            return self._snapshot(error="vision_error")

    def close(self) -> None:
        try:
            self.camera.release()
        finally:
            self._started = False

    def _snapshot(self, event: str | None = None, error: str | None = None) -> PresenceSnapshot:
        return PresenceSnapshot(
            available=error is None,
            present=self._last_present,
            state=self.controller.get_state_name(),
            primary_visitor_id=self.controller.get_primary_visitor_id(),
            event=event,
            error=error,
        )