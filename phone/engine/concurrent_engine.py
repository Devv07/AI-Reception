from __future__ import annotations

import inspect
from typing import Any, Callable

from phone.engine.phone_call_engine import PhoneCallEngine
from phone.session.call_session import CallSession
from phone.session.manager import call_manager


class PhoneConcurrentEngine:
    """
    Concurrent processing layer for the phone engine.

    Different calls can be processed simultaneously.

    Example:

        Call A -> Session A -> Engine processing A
        Call B -> Session B -> Engine processing B
        Call C -> Session C -> Engine processing C

    Each CallSession owns its own processing lock, so operations
    belonging to different calls do not block each other.
    """

    def __init__(
        self,
        engine: PhoneCallEngine | None = None,
    ) -> None:
        self.engine = engine or PhoneCallEngine()

    async def process_call(
        self,
        session: CallSession,
        mulaw_audio: bytes,
        language: str | None = None,
        wav_output_file: str = "phone_caller_input.wav",
        tts_output_file: str = "phone_ai_response.wav",
    ) -> Any:
        """
        Process one caller's audio through the existing phone engine.

        The session-specific processing lock prevents two simultaneous
        operations for the SAME call.

        Different sessions have different locks, therefore different
        calls can run concurrently.
        """

        if session is None:
            raise ValueError("session is required")

        if not session.active:
            raise RuntimeError(
                f"Call session is closed: {session.call_sid}"
            )

        if not mulaw_audio:
            raise ValueError("mulaw_audio is required")

        session.touch()

        session.add_event(
            "concurrent_processing_started",
            {
                "audio_bytes": len(mulaw_audio),
            },
        )

        # Important:
        # This lock belongs ONLY to this CallSession.
        #
        # Session A lock != Session B lock.
        #
        # Therefore:
        # A + B can run simultaneously.
        #
        # But:
        # A + A cannot process two audio operations simultaneously.
        with session.processing_lock:

            if not session.active:
                raise RuntimeError(
                    f"Call session closed before processing: "
                    f"{session.call_sid}"
                )

            try:
                result = self.engine.process_caller_audio(
                    session=session,
                    mulaw_audio=mulaw_audio,
                    language=language,
                    wav_output_file=wav_output_file,
                    tts_output_file=tts_output_file,
                )

                # Support either an async or synchronous implementation
                # of PhoneCallEngine.
                if inspect.isawaitable(result):
                    result = await result

                session.add_event(
                    "concurrent_processing_finished",
                    {
                        "success": True,
                    },
                )

                session.touch()

                return result

            except Exception as exc:
                session.add_event(
                    "concurrent_processing_failed",
                    {
                        "error": str(exc),
                        "error_type": type(exc).__name__,
                    },
                )

                session.touch()

                raise

    async def process_call_by_sid(
        self,
        call_sid: str,
        mulaw_audio: bytes,
        language: str | None = None,
        wav_output_file: str = "phone_caller_input.wav",
        tts_output_file: str = "phone_ai_response.wav",
    ) -> Any:
        """
        Find an existing call session and process its audio.
        """

        session = call_manager.require_call(call_sid)

        return await self.process_call(
            session=session,
            mulaw_audio=mulaw_audio,
            language=language,
            wav_output_file=wav_output_file,
            tts_output_file=tts_output_file,
        )

    def get_active_call_count(self) -> int:
        """
        Return the number of currently active calls.
        """
        return call_manager.count_active()

    def get_call_status(self, call_sid: str) -> dict[str, Any]:
        """
        Return the current status of one call.
        """
        session = call_manager.require_call(call_sid)
        return session.get_status()