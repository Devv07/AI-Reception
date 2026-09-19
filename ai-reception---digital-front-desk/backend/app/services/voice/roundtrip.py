from __future__ import annotations

import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

import httpx


class VoicePipelineError(RuntimeError):
    """A recoverable microphone, STT, API, or TTS failure."""

    def __init__(self, stage: str, message: str):
        super().__init__(f"Voice {stage} failed: {message}")
        self.stage = stage


class Recorder(Protocol):
    def record_and_save(self, duration: float, file_path: str) -> Path: ...


class SpeechToText(Protocol):
    def transcribe(self, audio_file: str, language: str | None = None) -> str: ...


class TextToSpeech(Protocol):
    def speak(self, text: str) -> None: ...


@dataclass(frozen=True)
class VoiceTurn:
    conversation_id: str
    transcript: str
    answer: str
    intent: str
    needs_human: bool
    sources: list[dict[str, str]]


class CentralConversationVoiceAdapter:
    """Connect Member 2 voice I/O to Member 3's central conversation API."""

    def __init__(
        self,
        recorder: Recorder,
        stt: SpeechToText,
        tts: TextToSpeech,
        organization_id: str,
        api_base_url: str = "http://127.0.0.1:8000/api/v1",
        client: Any | None = None,
    ):
        self.recorder = recorder
        self.stt = stt
        self.tts = tts
        self.organization_id = organization_id
        self.api_base_url = api_base_url.rstrip("/")
        self.client = client or httpx.Client(timeout=60.0)
        self.conversation_id: str | None = None

    @classmethod
    def from_member2(
        cls,
        organization_id: str,
        api_base_url: str = "http://127.0.0.1:8000/api/v1",
    ) -> "CentralConversationVoiceAdapter":
        try:
            from voice.microphone.microphone import Microphone
            from voice.stt.whisper_stt import WhisperSTT
            from voice.tts.speaker import Speaker
        except ImportError as error:
            raise VoicePipelineError(
                "initialization",
                "Member 2 voice modules are not installed in this checkout",
            ) from error

        try:
            return cls(
                recorder=Microphone(sample_rate=16000, channels=1, dtype="int16"),
                stt=WhisperSTT(language="en"),
                tts=Speaker(rate=165, volume=1.0),
                organization_id=organization_id,
                api_base_url=api_base_url,
            )
        except Exception as error:
            raise VoicePipelineError("initialization", str(error)) from error

    def run_once(self, duration: float = 5.0, audio_path: str | None = None) -> VoiceTurn:
        path = Path(audio_path) if audio_path else Path(tempfile.gettempdir()) / "ai-reception-voice.wav"
        try:
            recorded_path = self.recorder.record_and_save(duration, str(path))
        except Exception as error:
            raise VoicePipelineError("microphone", str(error)) from error

        try:
            transcript = self.stt.transcribe(str(recorded_path), language="en").strip()
            if not transcript:
                raise ValueError("Whisper returned empty text")
        except Exception as error:
            raise VoicePipelineError("speech recognition", str(error)) from error

        try:
            if self.conversation_id is None:
                created = self.client.post(
                    f"{self.api_base_url}/conversations",
                    json={"organization_id": self.organization_id, "channel": "voice", "preferred_language": "en"},
                )
                created.raise_for_status()
                self.conversation_id = created.json()["conversation_id"]

            response = self.client.post(
                f"{self.api_base_url}/conversations/{self.conversation_id}/messages",
                json={"content": transcript, "language": "en"},
            )
            response.raise_for_status()
            payload = response.json()
            ai_response = payload["ai_response"]
            if ai_response.get("language") != "en":
                raise ValueError("central API returned a non-English response")
            answer = str(ai_response["answer"]).strip()
        except Exception as error:
            raise VoicePipelineError("central conversation API", str(error)) from error

        try:
            self.tts.speak(answer)
        except Exception as error:
            raise VoicePipelineError("text to speech", str(error)) from error

        return VoiceTurn(
            conversation_id=self.conversation_id,
            transcript=transcript,
            answer=answer,
            intent=str(ai_response["intent"]),
            needs_human=bool(ai_response.get("needs_human", False)),
            sources=list(ai_response.get("sources", [])),
        )