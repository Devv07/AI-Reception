from __future__ import annotations

from phone.engine.phone_call_engine import PhoneCallEngine
from phone.session.call_session import CallSession

from integration.event_publisher import event_publisher


class FakeWhisper:
    """
    Fake Whisper adapter.

    No Groq API call is made.
    """

    def transcribe_mulaw(
        self,
        mulaw_audio: bytes,
        language: str | None = None,
        wav_output_file: str = (
            "phone_caller_input.wav"
        ),
    ) -> str:

        return (
            "Hello, I want information "
            "about admissions."
        )


class FakeAI:
    """
    Fake AI adapter.

    No Groq/RAG call is made.
    """

    def process_message_details(
        self,
        transcript: str,
        conversation_id: str,
    ) -> dict:

        return {
            "response_text": (
                "Hello. I can help you "
                "with admissions information."
            ),
            "handoff_required": False,
            "handoff_department": None,
            "raw_response": {},
        }


class FakeTTS:
    """
    Fake TTS adapter.

    No Windows speaker or pyttsx3 call is made.
    """

    def synthesize(
        self,
        text: str,
        output_file: str = (
            "phone_ai_response.wav"
        ),
    ) -> dict:

        fake_mulaw = b"\x00" * 1600

        return {
            "mulaw_audio": fake_mulaw,
            "audio_bytes": len(fake_mulaw),
        }

    def build_twilio_media_message(
        self,
        stream_sid: str | None,
        mulaw_audio: bytes,
    ) -> dict:

        return {
            "event": "media",
            "stream_sid": stream_sid,
            "media": {
                "payload": "FAKE_BASE64_AUDIO"
            },
        }


def run_test() -> None:

    print()
    print("=" * 70)
    print("PHASE 12.3 - REAL PHONE EVENT FLOW TEST")
    print("=" * 70)

    # --------------------------------------------------
    # Disable actual backend HTTP delivery.
    # --------------------------------------------------

    original_send_to_backend = (
        event_publisher.send_to_backend
    )

    event_publisher.send_to_backend = False

    try:

        event_publisher.clear_events()

        # --------------------------------------------------
        # Create real CallSession
        # --------------------------------------------------

        session = CallSession(
            call_sid="CA_PHASE12_3_TEST",
            caller_number="+9779804720452",
            called_number="+17372508034",
        )

        print(
            "[TEST] Call session created."
        )

        # --------------------------------------------------
        # Create actual PhoneCallEngine with fake
        # external services.
        # --------------------------------------------------

        engine = PhoneCallEngine(
            whisper=FakeWhisper(),
            ai=FakeAI(),
            tts=FakeTTS(),
        )

        # --------------------------------------------------
        # Simulated caller μ-law audio
        # --------------------------------------------------

        fake_caller_audio = (
            b"\x00" * 1600
        )

        # --------------------------------------------------
        # Run actual engine pipeline
        # --------------------------------------------------

        result = (
            engine.process_caller_audio(
                session=session,
                mulaw_audio=fake_caller_audio,
            )
        )

        # --------------------------------------------------
        # Validate result
        # --------------------------------------------------

        assert result["success"] is True

        assert (
            result["call_sid"]
            == session.call_sid
        )

        assert (
            result["conversation_id"]
            == session.conversation_id
        )

        assert result["transcript"]

        assert result["response_text"]

        print(
            "[TEST] Phone engine pipeline: PASS"
        )

        # --------------------------------------------------
        # Get integration events
        # --------------------------------------------------

        events = (
            event_publisher.get_events()
        )

        print()
        print(
            f"[TEST] Published events: "
            f"{len(events)}"
        )

        for event in events:

            print(
                f"  - "
                f"{event['event_type']}"
            )

        # --------------------------------------------------
        # Required events
        # --------------------------------------------------

        event_types = [
            event["event_type"]
            for event in events
        ]

        assert (
            "speech_received"
            in event_types
        )

        assert (
            "ai_response_generated"
            in event_types
        )

        assert (
            "tts_generated"
            in event_types
        )

        assert (
            "twilio_media_response_ready"
            in event_types
        )

        print(
            "[TEST] Processing events: PASS"
        )

        # --------------------------------------------------
        # Verify speech data
        # --------------------------------------------------

        speech_event = next(
            event
            for event in events
            if event["event_type"]
            == "speech_received"
        )

        assert (
            speech_event["data"]["transcript"]
            == result["transcript"]
        )

        print(
            "[TEST] Speech event data: PASS"
        )

        # --------------------------------------------------
        # Verify AI data
        # --------------------------------------------------

        ai_event = next(
            event
            for event in events
            if event["event_type"]
            == "ai_response_generated"
        )

        assert (
            ai_event["data"]["response_text"]
            == result["response_text"]
        )

        print(
            "[TEST] AI event data: PASS"
        )

        # --------------------------------------------------
        # Verify identity isolation
        # --------------------------------------------------

        for event in events:

            assert (
                event["call_sid"]
                == session.call_sid
            )

            assert (
                event["conversation_id"]
                == session.conversation_id
            )

            assert (
                event["source"]
                == "phone"
            )

            assert (
                event["channel"]
                == "phone"
            )

        print(
            "[TEST] Event identity isolation: PASS"
        )

        # --------------------------------------------------
        # Verify local session history
        # --------------------------------------------------

        session_events = (
            session.get_events()
        )

        assert session_events

        print(
            "[TEST] Session event history: PASS"
        )

        print()
        print("=" * 70)
        print("PHASE 12.3 COMPLETE")
        print("=" * 70)
        print()

    finally:

        event_publisher.clear_events()

        event_publisher.send_to_backend = (
            original_send_to_backend
        )


if __name__ == "__main__":
    run_test()