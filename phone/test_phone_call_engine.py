from __future__ import annotations

import asyncio
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from phone.engine.phone_call_engine import PhoneCallEngine
from phone.session.manager import call_manager


async def main() -> None:
    print()
    print("=" * 60)
    print("PHASE 10.8 - END-TO-END PHONE CALL TEST")
    print("=" * 60)
    print()

    # ------------------------------------------------------
    # TEST 1: Create phone session
    # ------------------------------------------------------

    call_sid = "CA_PHASE10_8_TEST"

    existing = call_manager.get_call(
        call_sid
    )

    if existing is not None:
        call_manager.remove_call(
            call_sid
        )

    session = call_manager.create_call(
        call_sid=call_sid,
        caller_number="+9779800000000",
        called_number="+9770100000000",
    )

    assert session.active
    assert session.conversation_id

    # Simulate Twilio Media Stream
    session.attach_stream(
        "MZ_LOCAL_PHASE10_8_TEST"
    )

    print(
        "[TEST 1] Phone call session: PASS"
    )

    print(
        f"          Call SID: "
        f"{session.call_sid}"
    )

    print(
        f"          Conversation ID: "
        f"{session.conversation_id}"
    )

    print(
        f"          Stream SID: "
        f"{session.stream_sid}"
    )

    # ------------------------------------------------------
    # TEST 2: Initialize engine
    # ------------------------------------------------------

    engine = PhoneCallEngine()

    print()
    print(
        "[TEST 2] Phone call engine initialization: PASS"
    )

    # ------------------------------------------------------
    # Find existing Phase 10.7 speech WAV
    # ------------------------------------------------------

    input_wav = (
        PROJECT_ROOT
        / "phone"
        / "recordings"
        / "phase10_7_tts.wav"
    )

    if not input_wav.exists():
        raise FileNotFoundError(
            "Phase 10.7 TTS file not found: "
            f"{input_wav}"
        )

    print()
    print(
        "[SETUP] Using speech WAV:"
    )
    print(
        f"        {input_wav}"
    )

    # ------------------------------------------------------
    # TEST 3: Complete phone pipeline
    # ------------------------------------------------------

    print()
    print(
        "[TEST 3] Running complete phone pipeline..."
    )

    result = await engine.process_existing_wav(
        session=session,
        wav_file=input_wav,
        wav_output_file=(
            "phase10_8_caller_input.wav"
        ),
        tts_output_file=(
            "phase10_8_ai_response.wav"
        ),
    )

    transcript = result["transcript"]
    response = result["response"]
    mulaw_audio = result["mulaw_audio"]
    base64_payload = result["base64_payload"]
    twilio_message = result["twilio_message"]

    assert transcript
    assert response
    assert mulaw_audio
    assert base64_payload
    assert twilio_message

    print()
    print(
        "[TEST 3] Complete phone pipeline: PASS"
    )

    print(
        f"          Transcript: {transcript}"
    )

    print(
        f"          AI response: {response}"
    )

    # ------------------------------------------------------
    # TEST 4: Verify Twilio message
    # ------------------------------------------------------

    assert (
        twilio_message["event"]
        == "media"
    )

    assert (
        twilio_message["streamSid"]
        == session.stream_sid
    )

    assert (
        twilio_message["media"]["payload"]
    )

    print()
    print(
        "[TEST 4] Twilio Media message: PASS"
    )

    print(
        f"          Event: "
        f"{twilio_message['event']}"
    )

    print(
        f"          Stream SID: "
        f"{twilio_message['streamSid']}"
    )

    print(
        f"          Payload length: "
        f"{len(twilio_message['media']['payload'])}"
    )

    # ------------------------------------------------------
    # TEST 5: Verify conversation events
    # ------------------------------------------------------

    status = session.get_status()

    assert (
        status["conversation_id"]
        == session.conversation_id
    )

    assert status["event_count"] >= 6

    print()
    print(
        "[TEST 5] Conversation event tracking: PASS"
    )

    print(
        f"          Event count: "
        f"{status['event_count']}"
    )

    # ------------------------------------------------------
    # TEST 6: Verify session remains active
    # ------------------------------------------------------

    assert session.active

    print()
    print(
        "[TEST 6] Call session remains active: PASS"
    )

    # ------------------------------------------------------
    # Final status
    # ------------------------------------------------------

    print()
    print("SESSION STATUS")
    print("-" * 60)

    for key, value in status.items():
        print(
            f"{key}: {value}"
        )

    print()
    print("RECORDED EVENTS")
    print("-" * 60)

    for event in session.events:
        print(
            f"{event['type']}: "
            f"{event['data']}"
        )

    print()
    print("=" * 60)
    print(
        "ALL PHASE 10.8 LOCAL TESTS PASSED"
    )
    print("=" * 60)
    print()


if __name__ == "__main__":
    asyncio.run(main())