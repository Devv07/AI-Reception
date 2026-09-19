from __future__ import annotations

import asyncio
import time
from typing import Any

from phone.engine.concurrent_engine import PhoneConcurrentEngine
from phone.session.call_session import CallSession


class FakePhoneEngine:
    """
    Fake engine used only for concurrency testing.

    It simulates processing without calling:
    - Groq
    - Whisper
    - TTS
    - Twilio

    This makes the test fast and free.
    """

    async def process_caller_audio(
        self,
        session: CallSession,
        mulaw_audio: bytes,
        language: str | None = None,
        wav_output_file: str = "phone_caller_input.wav",
        tts_output_file: str = "phone_ai_response.wav",
    ) -> dict[str, Any]:

        await asyncio.sleep(0.5)

        return {
            "success": True,
            "call_sid": session.call_sid,
            "conversation_id": session.conversation_id,
            "audio_bytes": len(mulaw_audio),
        }


async def run_test() -> None:

    print()
    print("=" * 70)
    print("PHASE 11.2 - CONCURRENT PHONE ENGINE TEST")
    print("=" * 70)

    fake_engine = FakePhoneEngine()

    concurrent_engine = PhoneConcurrentEngine(
        engine=fake_engine
    )

    sessions = [
        CallSession(
            call_sid=f"CA_ENGINE_TEST_{index:03d}",
            caller_number=f"+9779804720{index:03d}",
            called_number="+17372508034",
        )
        for index in range(1, 4)
    ]

    print("[TEST] Created 3 independent call sessions.")

    for session in sessions:
        print(
            f"[TEST] {session.call_sid}"
            f" -> {session.conversation_id}"
        )

    fake_audio = b"\x00" * 1600

    start_time = time.perf_counter()

    results = await asyncio.gather(
        concurrent_engine.process_call(
            session=sessions[0],
            mulaw_audio=fake_audio,
        ),
        concurrent_engine.process_call(
            session=sessions[1],
            mulaw_audio=fake_audio,
        ),
        concurrent_engine.process_call(
            session=sessions[2],
            mulaw_audio=fake_audio,
        ),
    )

    elapsed = time.perf_counter() - start_time

    print()
    print("[TEST] Results:")

    for result in results:
        print(
            f"  {result['call_sid']}"
            f" -> {result['conversation_id']}"
        )

    print()
    print(f"[TEST] Total processing time: {elapsed:.2f}s")

    # If the three calls were processed sequentially,
    # the fake 0.5s delay would take about 1.5 seconds.
    #
    # Concurrent processing should be close to 0.5 seconds.
    assert elapsed < 1.0, (
        "Calls were not processed concurrently."
    )

    # Verify every result belongs to the correct session.
    for session, result in zip(sessions, results):

        assert result["call_sid"] == session.call_sid

        assert (
            result["conversation_id"]
            == session.conversation_id
        )

    # Verify conversations are unique.
    conversation_ids = {
        session.conversation_id
        for session in sessions
    }

    assert len(conversation_ids) == 3

    # Verify events remain isolated.
    for session in sessions:

        events = session.get_events()

        assert events

        for event in events:
            assert (
                event["call_sid"]
                == session.call_sid
            )

            assert (
                event["conversation_id"]
                == session.conversation_id
            )

    print()
    print("[TEST] Concurrent processing: PASS")
    print("[TEST] Call isolation:        PASS")
    print("[TEST] Conversation isolation: PASS")
    print("[TEST] Event isolation:        PASS")

    print()
    print("=" * 70)
    print("PHASE 11.2 COMPLETE")
    print("=" * 70)
    print()


if __name__ == "__main__":
    asyncio.run(run_test())