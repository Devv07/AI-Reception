import time

from vision.presence_adapter import VisitorPresenceAdapter
from vision.reception.reception_controller import ReceptionController


class FakeCamera:
    def __init__(self, frames=None, error=None):
        self.frames = list(frames or [])
        self.error = error
        self.started = False

    def start(self):
        if self.error:
            raise RuntimeError(self.error)
        self.started = True

    def is_opened(self):
        return self.started

    def read(self):
        return self.frames.pop(0) if self.frames else object()

    def release(self):
        self.started = False


class FakeTracker:
    def __init__(self, detections):
        self.detections = list(detections)

    def track(self, frame):
        return self.detections.pop(0) if self.detections else []


def test_camera_unavailable_does_not_create_departure():
    adapter = VisitorPresenceAdapter(FakeCamera(error="camera unavailable"), FakeTracker([]), ReceptionController())
    snapshot = adapter.poll()
    assert snapshot.available is False
    assert snapshot.error == "camera_unavailable"
    assert snapshot.present is False


def test_one_person_enters_visitor_detected_state():
    adapter = VisitorPresenceAdapter(FakeCamera(), FakeTracker([[{"visitor_id": 7}]]), ReceptionController())
    snapshot = adapter.poll()
    assert snapshot.available is True
    assert snapshot.present is True
    assert snapshot.primary_visitor_id == 7
    assert snapshot.state == "visitor_detected"
    assert snapshot.event == "visitor_detected"


def test_person_leaving_emits_visitor_left():
    controller = ReceptionController(visitor_timeout=0.01)
    adapter = VisitorPresenceAdapter(FakeCamera(), FakeTracker([[{"visitor_id": 7}], []]), controller)
    adapter.poll()
    time.sleep(0.02)
    snapshot = adapter.poll()
    assert snapshot.present is False
    assert snapshot.event == "visitor_left"


def test_repeated_detection_is_deduplicated():
    controller = ReceptionController(visitor_timeout=1.0)
    adapter = VisitorPresenceAdapter(FakeCamera(), FakeTracker([[{"visitor_id": 7}], [{"visitor_id": 7}]]), controller)
    first = adapter.poll()
    second = adapter.poll()
    assert first.event == "visitor_detected"
    assert second.event is None
    assert controller.get_active_visitor_count() == 1