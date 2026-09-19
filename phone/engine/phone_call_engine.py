from __future__ import annotations

import os
import wave
from pathlib import Path
from typing import Any

from phone.audio.ai_adapter import PhoneAIAdapter
from phone.audio.codec import PhoneAudioCodec
from phone.audio.tts_adapter import PhoneTTSAdapter
from phone.audio.whisper_adapter import PhoneWhisperAdapter
from phone.session.call_session import CallSession
from phone.telephony.handoff import handoff_manager


class PhoneCallEngine:
    """
    Complete processing engine for one phone call.

    Pipeline:

        μ-law audio
            ↓
        Whisper STT
            ↓
        Shared AI Brain
            ↓
        Handoff OR TTS
            ↓
        Twilio media response

    Phase 12.3:
    Important processing events are also recorded in CallSession.
    CallSession forwards selected events to the shared backend.
    """

    def __init__(
        self,
        codec: PhoneAudioCodec | None = None,
        whisper: PhoneWhisperAdapter | None = None,
        ai: PhoneAIAdapter | None = None,
        tts: PhoneTTSAdapter | None = None,
    ) -> None:

        self.codec = codec or PhoneAudioCodec()
        self.whisper = whisper or PhoneWhisperAdapter()
        self.ai = ai or PhoneAIAdapter()
        self.tts = tts or PhoneTTSAdapter()

    def process_caller_audio(
        self,
        session: CallSession,
        mulaw_audio: bytes,
        language: str | None = None,
        wav_output_file: str = "phone_caller_input.wav",
        tts_output_file: str = "phone_ai_response.wav",
    ) -> dict[str, Any]:

        if session is None:
            raise ValueError("session is required")

        if not session.active:
            raise RuntimeError(
                f"Call session is closed: "
                f"{session.call_sid}"
            )

        if not mulaw_audio:
            raise ValueError(
                "mulaw_audio is required"
            )

        session.touch()

        # --------------------------------------------------
        # 1. Caller audio received
        # --------------------------------------------------

        session.add_event(
            "caller_audio_received",
            {
                "audio_bytes": len(mulaw_audio),
            },
        )

        # --------------------------------------------------
        # 2. Whisper STT
        # --------------------------------------------------

        transcript = self.whisper.transcribe_mulaw(
            mulaw_audio=mulaw_audio,
            language=language,
            wav_output_file=wav_output_file,
        )

        transcript = (
            transcript.strip()
            if transcript
            else ""
        )

        if not transcript:
            session.add_event(
                "speech_received",
                {
                    "transcript": "",
                    "empty": True,
                },
            )

            return {
                "success": False,
                "call_sid": session.call_sid,
                "conversation_id": (
                    session.conversation_id
                ),
                "transcript": "",
                "response_text": "",
                "reason": "empty_transcript",
            }

        # --------------------------------------------------
        # 3. Publish actual speech event
        # --------------------------------------------------

        session.add_event(
            "speech_received",
            {
                "transcript": transcript,
            },
        )

        print()
        print("=" * 70)
        print("[PHONE] SPEECH RECEIVED")
        print(f"Call SID: {session.call_sid}")
        print(
            f"Conversation: "
            f"{session.conversation_id}"
        )
        print(f"Transcript: {transcript}")
        print("=" * 70)

        # --------------------------------------------------
        # 4. Shared AI Brain
        # --------------------------------------------------

        ai_result = self.ai.process_message_details(
            transcript=transcript,
            conversation_id=session.conversation_id,
        )

        response_text = (
            ai_result.get("response_text")
            or ""
        )

        handoff_required = bool(
            ai_result.get(
                "handoff_required",
                False,
            )
        )

        handoff_department = (
            ai_result.get(
                "handoff_department"
            )
        )

        # --------------------------------------------------
        # 5. Publish actual AI response event
        # --------------------------------------------------

        session.add_event(
            "ai_response_generated",
            {
                "response_text": response_text,
                "handoff_required": (
                    handoff_required
                ),
                "handoff_department": (
                    handoff_department
                ),
            },
        )

        print()
        print("=" * 70)
        print("[PHONE] AI RESPONSE GENERATED")
        print(f"Call SID: {session.call_sid}")
        print(
            f"Response: {response_text}"
        )
        print(
            f"Handoff required: "
            f"{handoff_required}"
        )

        if handoff_department:
            print(
                f"Department: "
                f"{handoff_department}"
            )

        print("=" * 70)

        # --------------------------------------------------
        # 6. Human handoff
        # --------------------------------------------------

        if handoff_required:

            session.add_event(
                "call_handoff",
                {
                    "department": (
                        handoff_department
                    ),
                    "reason": (
                        "AI requested human "
                        "assistance."
                    ),
                    "response_text": (
                        response_text
                    ),
                },
            )

            # Real Twilio handoff happens here.
            #
            # During Trial mode Twilio may reject
            # <Dial><Number>. The handoff manager
            # handles the Twilio API interaction.

            handoff_result = (
                handoff_manager.transfer_call(
                    session.call_sid
                )
            )

            session.add_event(
                "handoff_transfer_result",
                {
                    "success": handoff_result.get(
                        "success",
                        False,
                    ),
                    "target_number": (
                        handoff_result.get(
                            "target_number"
                        )
                    ),
                    "status": (
                        handoff_result.get(
                            "status"
                        )
                    ),
                },
            )

            return {
                "success": bool(
                    handoff_result.get(
                        "success",
                        False,
                    )
                ),
                "call_sid": session.call_sid,
                "conversation_id": (
                    session.conversation_id
                ),
                "transcript": transcript,
                "response_text": response_text,
                "handoff_required": True,
                "handoff_department": (
                    handoff_department
                ),
                "handoff": handoff_result,
            }

        # --------------------------------------------------
        # 7. Normal TTS response
        # --------------------------------------------------

        if not response_text:

            session.add_event(
                "tts_skipped",
                {
                    "reason": (
                        "empty_ai_response"
                    ),
                },
            )

            return {
                "success": False,
                "call_sid": session.call_sid,
                "conversation_id": (
                    session.conversation_id
                ),
                "transcript": transcript,
                "response_text": "",
                "reason": "empty_ai_response",
            }

        tts_result = self.tts.synthesize(
            text=response_text,
            output_file=tts_output_file,
        )

        # --------------------------------------------------
        # 8. Build Twilio media response
        # --------------------------------------------------

        mulaw_response = (
            tts_result["mulaw_audio"]
        )

        twilio_media_message = (
            self.tts.build_twilio_media_message(
                session.stream_sid,
                mulaw_response,
            )
        )

        session.add_event(
            "tts_generated",
            {
                "audio_bytes": len(
                    mulaw_response
                ),
                "stream_sid": (
                    session.stream_sid
                ),
            },
        )

        session.add_event(
            "twilio_media_response_ready",
            {
                "audio_bytes": len(
                    mulaw_response
                ),
                "stream_sid": (
                    session.stream_sid
                ),
            },
        )

        session.touch()

        return {
            "success": True,
            "call_sid": session.call_sid,
            "conversation_id": (
                session.conversation_id
            ),
            "transcript": transcript,
            "response_text": response_text,
            "handoff_required": False,
            "handoff_department": None,
            "mulaw_audio": mulaw_response,
            "twilio_media_message": (
                twilio_media_message
            ),
            "tts": tts_result,
        }

    def process_existing_wav(
        self,
        session: CallSession,
        wav_file: str | Path,
        language: str | None = None,
        caller_wav_output_file: str = (
            "phone_caller_input.wav"
        ),
        tts_output_file: str = (
            "phone_ai_response.wav"
        ),
    ) -> dict[str, Any]:
        """
        Process an existing WAV file as simulated
        caller audio.

        Used for local testing without a real phone call.
        """

        if session is None:
            raise ValueError(
                "session is required"
            )

        wav_path = Path(wav_file)

        if not wav_path.exists():
            raise FileNotFoundError(
                f"WAV file not found: {wav_path}"
            )

        with wave.open(
            str(wav_path),
            "rb",
        ) as wav:

            sample_width = wav.getsampwidth()
            channels = wav.getnchannels()
            sample_rate = wav.getframerate()
            frames = wav.readframes(
                wav.getnframes()
            )

        if sample_width != 2:
            raise ValueError(
                "Input WAV must be PCM16."
            )

        pcm16_audio = frames

        if channels > 1:
            pcm16_audio = (
                self.codec.stereo_to_mono(
                    pcm16_audio,
                    channels,
                )
            )

        if sample_rate != 8000:

            pcm16_audio = (
                self.codec.resample_pcm16(
                    pcm16_audio,
                    sample_rate,
                    8000,
                )
            )

        mulaw_audio = (
            self.codec.pcm16_to_mulaw(
                pcm16_audio
            )
        )

        return self.process_caller_audio(
            session=session,
            mulaw_audio=mulaw_audio,
            language=language,
            wav_output_file=(
                caller_wav_output_file
            ),
            tts_output_file=tts_output_file,
        )