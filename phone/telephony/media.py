from __future__ import annotations

import asyncio
import audioop
import base64
import json
import time
from typing import Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from phone.engine.phone_call_engine import PhoneCallEngine
from phone.session.manager import call_manager


router = APIRouter(
    prefix="/phone",
    tags=["Phone"],
)


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

PACKET_DURATION_MS = 20

# Twilio μ-law @ 8 kHz:
# 8000 samples/sec × 0.020 sec = 160 samples
BYTES_PER_PACKET = 160

# End utterance after approximately 0.8 seconds of silence.
SILENCE_PACKETS_TO_END = 40

# Require approximately 60 ms of speech before starting.
MIN_SPEECH_PACKETS = 3

# Ignore extremely quiet background noise.
RMS_SPEECH_THRESHOLD = 500


# One engine can be shared because CallSession keeps
# conversation state isolated.
phone_engine = PhoneCallEngine()


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

def decode_media_payload(payload: str) -> bytes:
    return base64.b64decode(payload)


def get_audio_rms(mulaw_audio: bytes) -> int:
    """
    Calculate RMS after converting μ-law to PCM16.
    """
    if not mulaw_audio:
        return 0

    pcm16 = audioop.ulaw2lin(
        mulaw_audio,
        2,
    )

    return audioop.rms(
        pcm16,
        2,
    )


async def send_twilio_audio(
    websocket: WebSocket,
    stream_sid: str,
    mulaw_audio: bytes,
):
    """
    Send μ-law audio back to Twilio.

    Twilio accepts:
        audio/x-mulaw
        8000 Hz
        mono
        base64 payload
    """

    if not stream_sid:
        raise ValueError(
            "stream_sid cannot be empty"
        )

    if not mulaw_audio:
        return

    total_bytes = len(mulaw_audio)

    print()
    print(
        "[PHONE WS] Sending AI audio to caller."
    )

    print(
        f"[PHONE WS] Total μ-law bytes: "
        f"{total_bytes}"
    )

    # Send in 20 ms chunks.
    for start in range(
        0,
        total_bytes,
        BYTES_PER_PACKET,
    ):
        chunk = mulaw_audio[
            start:start + BYTES_PER_PACKET
        ]

        payload = base64.b64encode(
            chunk
        ).decode("ascii")

        message = {
            "event": "media",
            "streamSid": stream_sid,
            "media": {
                "payload": payload,
            },
        }

        await websocket.send_text(
            json.dumps(message)
        )

        # Yield to the event loop so the
        # WebSocket remains responsive.
        await asyncio.sleep(
            PACKET_DURATION_MS / 1000
        )

    # Tell Twilio that this response has
    # finished playing.
    mark_message = {
        "event": "mark",
        "streamSid": stream_sid,
        "mark": {
            "name": "ai_response_complete",
        },
    }

    await websocket.send_text(
        json.dumps(mark_message)
    )

    print(
        "[PHONE WS] AI audio sent successfully."
    )


# ---------------------------------------------------------
# Twilio events
# ---------------------------------------------------------

async def handle_connected(
    websocket: WebSocket,
    message: dict,
):
    print()
    print(
        "[PHONE WS] Twilio WebSocket connected."
    )

    print(
        f"[PHONE WS] Protocol: "
        f"{message.get('protocol')}"
    )

    print(
        f"[PHONE WS] Version: "
        f"{message.get('version')}"
    )


async def handle_start(
    websocket: WebSocket,
    message: dict,
) -> Optional[str]:

    start = message.get(
        "start",
        {},
    )

    stream_sid = (
        start.get("streamSid")
        or message.get("streamSid")
    )

    call_sid = start.get(
        "callSid"
    )

    print()
    print(
        "[PHONE WS] Twilio Media Stream started."
    )

    print(
        f"[PHONE WS] Call SID: "
        f"{call_sid}"
    )

    print(
        f"[PHONE WS] Stream SID: "
        f"{stream_sid}"
    )

    if not call_sid:
        print(
            "[PHONE WS] ERROR: Missing CallSid."
        )
        return stream_sid

    session = call_manager.get_call(
        call_sid
    )

    if session is None:
        print(
            "[PHONE WS] Call session was not "
            "created by webhook."
        )

        session = call_manager.create_call(
            call_sid=call_sid
        )

    if stream_sid:
        session.attach_stream(
            stream_sid
        )

    media_format = start.get(
        "mediaFormat",
        {},
    )

    session.metadata[
        "media_format"
    ] = media_format

    session.add_event(
        "media_stream_started",
        {
            "stream_sid": stream_sid,
            "media_format": media_format,
        },
    )

    print(
        "[PHONE WS] Media format:"
    )

    print(
        f"  encoding: "
        f"{media_format.get('encoding')}"
    )

    print(
        f"  sample rate: "
        f"{media_format.get('sampleRate')}"
    )

    print(
        f"  channels: "
        f"{media_format.get('channels')}"
    )

    return stream_sid


async def process_utterance(
    websocket: WebSocket,
    session,
    audio_buffer: bytes,
):
    """
    Process one detected caller utterance.
    """

    if not audio_buffer:
        return

    print()
    print(
        "=" * 60
    )
    print(
        "[PHONE WS] CALLER UTTERANCE DETECTED"
    )
    print(
        "=" * 60
    )

    print(
        f"[PHONE WS] Audio bytes: "
        f"{len(audio_buffer)}"
    )

    try:
        result = await phone_engine.process_caller_audio(
            session=session,
            mulaw_audio=audio_buffer,
            wav_output_file=(
                f"call_{session.call_sid}_input.wav"
            ),
            tts_output_file=(
                f"call_{session.call_sid}_response.wav"
            ),
        )

        transcript = result.get(
            "transcript",
            "",
        )

        response = result.get(
            "response",
            "",
        )

        response_audio = result.get(
            "mulaw_audio",
            b"",
        )

        if not transcript:
            print(
                "[PHONE WS] No transcript produced."
            )
            return

        if not response_audio:
            print(
                "[PHONE WS] No AI audio generated."
            )
            return

        print()
        print(
            "[PHONE WS] Caller:"
        )
        print(
            f"  {transcript}"
        )

        print()
        print(
            "[PHONE WS] AI:"
        )
        print(
            f"  {response}"
        )

        await send_twilio_audio(
            websocket=websocket,
            stream_sid=session.stream_sid,
            mulaw_audio=response_audio,
        )

        session.add_event(
            "ai_audio_sent",
            {
                "audio_bytes": len(
                    response_audio
                ),
            },
        )

        session.touch()

    except Exception as exc:
        print()
        print(
            "[PHONE WS] ERROR processing "
            "caller utterance."
        )

        print(
            f"[PHONE WS] {exc}"
        )

        session.add_event(
            "processing_error",
            {
                "error": str(exc),
            },
        )


async def handle_media(
    websocket: WebSocket,
    message: dict,
    session,
    audio_buffer: bytearray,
    speech_started: bool,
    speech_packets: int,
    silence_packets: int,
):
    """
    Process one Twilio inbound media packet.

    Returns updated state:
        audio_buffer
        speech_started
        speech_packets
        silence_packets
    """

    media = message.get(
        "media",
        {},
    )

    track = media.get(
        "track"
    )

    # Bidirectional Streams provide
    # inbound caller audio.
    if track and track != "inbound":
        return (
            audio_buffer,
            speech_started,
            speech_packets,
            silence_packets,
        )

    payload = media.get(
        "payload",
        "",
    )

    if not payload:
        return (
            audio_buffer,
            speech_started,
            speech_packets,
            silence_packets,
        )

    audio_bytes = decode_media_payload(
        payload
    )

    if not audio_bytes:
        return (
            audio_buffer,
            speech_started,
            speech_packets,
            silence_packets,
        )

    rms = get_audio_rms(
        audio_bytes
    )

    # -----------------------------------------------------
    # Speech starts
    # -----------------------------------------------------

    if rms >= RMS_SPEECH_THRESHOLD:

        if not speech_started:
            speech_packets += 1

            if speech_packets >= MIN_SPEECH_PACKETS:
                speech_started = True
                silence_packets = 0

                print()
                print(
                    "[PHONE VAD] Speech started."
                )

                print(
                    f"[PHONE VAD] RMS: {rms}"
                )

        else:
            silence_packets = 0

    # -----------------------------------------------------
    # Silence
    # -----------------------------------------------------

    else:

        if speech_started:
            silence_packets += 1

        else:
            speech_packets = 0

    # -----------------------------------------------------
    # Buffer caller audio once speech begins
    # -----------------------------------------------------

    if speech_started:
        audio_buffer.extend(
            audio_bytes
        )

    # -----------------------------------------------------
    # End of utterance
    # -----------------------------------------------------

    if (
        speech_started
        and silence_packets
        >= SILENCE_PACKETS_TO_END
    ):

        utterance = bytes(
            audio_buffer
        )

        print()
        print(
            "[PHONE VAD] Speech ended."
        )

        print(
            f"[PHONE VAD] Utterance bytes: "
            f"{len(utterance)}"
        )

        # Reset state BEFORE expensive AI work.
        audio_buffer.clear()

        speech_started = False
        speech_packets = 0
        silence_packets = 0

        await process_utterance(
            websocket=websocket,
            session=session,
            audio_buffer=utterance,
        )

    return (
        audio_buffer,
        speech_started,
        speech_packets,
        silence_packets,
    )


async def handle_stop(
    message: dict,
    session,
):
    print()
    print(
        "[PHONE WS] Twilio Media Stream stopped."
    )

    session.add_event(
        "media_stream_stopped",
        {
            "stream_sid": session.stream_sid,
        },
    )

    session.detach_stream()


# ---------------------------------------------------------
# Main WebSocket endpoint
# ---------------------------------------------------------

@router.websocket("/media")
async def media_stream(
    websocket: WebSocket,
):
    await websocket.accept()

    print()
    print("=" * 60)
    print(
        "[PHONE WS] NEW TWILIO MEDIA CONNECTION"
    )
    print("=" * 60)

    session = None

    audio_buffer = bytearray()

    speech_started = False
    speech_packets = 0
    silence_packets = 0

    connected_at = time.time()

    try:

        while True:

            raw_message = (
                await websocket.receive_text()
            )

            try:
                message = json.loads(
                    raw_message
                )

            except json.JSONDecodeError:
                print(
                    "[PHONE WS] Invalid JSON received."
                )
                continue

            event = message.get(
                "event"
            )

            # ---------------------------------------------
            # Connected
            # ---------------------------------------------

            if event == "connected":

                await handle_connected(
                    websocket,
                    message,
                )

            # ---------------------------------------------
            # Start
            # ---------------------------------------------

            elif event == "start":

                stream_sid = (
                    await handle_start(
                        websocket,
                        message,
                    )
                )

                call_sid = (
                    message
                    .get("start", {})
                    .get("callSid")
                )

                if call_sid:
                    session = (
                        call_manager.get_call(
                            call_sid
                        )
                    )

                if session is None:
                    print(
                        "[PHONE WS] WARNING: "
                        "No call session available."
                    )

            # ---------------------------------------------
            # Media
            # ---------------------------------------------

            elif event == "media":

                if session is None:

                    print(
                        "[PHONE WS] Media received "
                        "before session initialization."
                    )

                    continue

                (
                    audio_buffer,
                    speech_started,
                    speech_packets,
                    silence_packets,
                ) = await handle_media(
                    websocket=websocket,
                    message=message,
                    session=session,
                    audio_buffer=audio_buffer,
                    speech_started=speech_started,
                    speech_packets=speech_packets,
                    silence_packets=silence_packets,
                )

            # ---------------------------------------------
            # Stop
            # ---------------------------------------------

            elif event == "stop":

                if session is not None:

                    await handle_stop(
                        message,
                        session,
                    )

                break

            # ---------------------------------------------
            # DTMF
            # ---------------------------------------------

            elif event == "dtmf":

                if session is not None:

                    dtmf = message.get(
                        "dtmf",
                        {},
                    )

                    session.add_event(
                        "dtmf_received",
                        {
                            "digit": dtmf.get(
                                "digit"
                            ),
                        },
                    )

                    print(
                        "[PHONE WS] DTMF:"
                        f" {dtmf.get('digit')}"
                    )

            # ---------------------------------------------
            # Mark
            # ---------------------------------------------

            elif event == "mark":

                if session is not None:

                    mark = message.get(
                        "mark",
                        {},
                    )

                    session.add_event(
                        "mark_received",
                        {
                            "name": mark.get(
                                "name"
                            ),
                        },
                    )

                    print(
                        "[PHONE WS] Mark:"
                        f" {mark.get('name')}"
                    )

            else:

                print(
                    "[PHONE WS] Unknown event:"
                    f" {event}"
                )

    except WebSocketDisconnect:

        print()
        print(
            "[PHONE WS] Twilio WebSocket disconnected."
        )

    except Exception as exc:

        print()
        print(
            "[PHONE WS] WebSocket error:"
        )

        print(
            f"[PHONE WS] {exc}"
        )

        if session is not None:

            session.add_event(
                "websocket_error",
                {
                    "error": str(exc),
                },
            )

    finally:

        duration = (
            time.time()
            - connected_at
        )

        print()
        print(
            "[PHONE WS] Connection closed."
        )

        print(
            f"[PHONE WS] Duration: "
            f"{duration:.1f}s"
        )