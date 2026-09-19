from __future__ import annotations

import base64
import json
import sys
import time
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from fastapi import FastAPI
from fastapi.testclient import TestClient

from phone.session.manager import call_manager
from phone.telephony.media import (
    decode_media_payload,
    router as media_router,
)
from phone.telephony.webhook import (
    router as webhook_router,
)


app = FastAPI()

app.include_router(webhook_router)
app.include_router(media_router)


def wait_for_stream_detach(
    session,
    timeout: float = 1.0,
) -> bool:
    """
    Wait briefly for the WebSocket stop event to finish
    updating the CallSession.
    """

    deadline = time.time() + timeout

    while time.time() < deadline:

        if session.stream_sid is None:
            return True

        time.sleep(0.01)

    return session.stream_sid is None


def main() -> None:

    print()
    print("=" * 60)
    print("PHASE 10.3 - PHONE MEDIA WEBSOCKET TEST")
    print("=" * 60)
    print()

    call_manager._sessions.clear()

    test_call_sid = "TEST-CALL-200"
    test_stream_sid = "TEST-STREAM-200"

    session = call_manager.create_call(
        call_sid=test_call_sid,
        caller_number="+9779800000000",
        called_number="+9779811111111",
    )

    print("[SETUP] Test call session created.")

    client = TestClient(app)

    with client.websocket_connect(
        "/phone/media"
    ) as websocket:

        connected_message = {
            "event": "connected",
            "protocol": "Call",
            "version": "1.0",
        }

        websocket.send_text(
            json.dumps(connected_message)
        )

        print("[TEST 1] Connected event: PASS")

        start_message = {
            "event": "start",
            "sequenceNumber": "1",
            "start": {
                "accountSid": "AC-TEST",
                "streamSid": test_stream_sid,
                "callSid": test_call_sid,
                "tracks": ["inbound"],
                "mediaFormat": {
                    "encoding": "audio/x-mulaw",
                    "sampleRate": 8000,
                    "channels": 1,
                },
                "customParameters": {},
            },
            "streamSid": test_stream_sid,
        }

        websocket.send_text(
            json.dumps(start_message)
        )

        attached = False

        for _ in range(100):

            if session.stream_sid == test_stream_sid:
                attached = True
                break

            time.sleep(0.01)

        assert attached is True

        print(
            "[TEST 2] Start event and stream attachment: PASS"
        )

        raw_audio = bytes(
            [
                0xFF,
                0xFE,
                0xFD,
                0xFC,
                0xFB,
                0xFA,
                0xF9,
                0xF8,
            ]
        )

        encoded_audio = base64.b64encode(
            raw_audio
        ).decode("ascii")

        media_message = {
            "event": "media",
            "sequenceNumber": "2",
            "media": {
                "track": "inbound",
                "chunk": "1",
                "timestamp": "20",
                "payload": encoded_audio,
            },
            "streamSid": test_stream_sid,
        }

        websocket.send_text(
            json.dumps(media_message)
        )

        decoded_audio = decode_media_payload(
            encoded_audio
        )

        assert decoded_audio == raw_audio

        print(
            "[TEST 3] Media payload decoding: PASS"
        )
        print(
            f"          Audio bytes: "
            f"{len(decoded_audio)}"
        )

        stop_message = {
            "event": "stop",
            "sequenceNumber": "3",
            "stop": {
                "accountSid": "AC-TEST",
                "callSid": test_call_sid,
            },
            "streamSid": test_stream_sid,
        }

        websocket.send_text(
            json.dumps(stop_message)
        )

        detached = wait_for_stream_detach(
            session,
            timeout=1.0,
        )

        assert detached is True

        print(
            "[TEST 4] Stop event and stream cleanup: PASS"
        )

    event_types = [
        event["type"]
        for event in session.events
    ]

    assert "call_created" in event_types
    assert "stream_attached" in event_types
    assert "media_stream_started" in event_types
    assert "stream_detached" in event_types
    assert "media_stream_stopped" in event_types

    print(
        "[TEST 5] Session event tracking: PASS"
    )

    media_format = session.metadata.get(
        "media_format"
    )

    assert media_format is not None
    assert media_format["encoding"] == "audio/x-mulaw"
    assert media_format["sampleRate"] == 8000
    assert media_format["channels"] == 1

    print(
        "[TEST 6] Phone audio format metadata: PASS"
    )

    print()
    print("CALL SESSION STATUS")
    print("-" * 60)
    print(session.get_status())

    print()
    print("=" * 60)
    print("ALL PHASE 10.3 TESTS PASSED")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()