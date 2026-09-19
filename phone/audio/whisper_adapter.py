from __future__ import annotations

import wave
from pathlib import Path

import numpy as np

from phone.audio.codec import PhoneAudioCodec
from voice.stt.whisper_stt import WhisperSTT


class PhoneWhisperAdapter:
    """
    Adapter between the phone audio codec and the existing
    WhisperSTT implementation.

    Phone audio:
        8 kHz μ-law

    Whisper audio:
        16 kHz mono PCM16 WAV
    """

    def __init__(
        self,
        stt: WhisperSTT | None = None,
        codec: PhoneAudioCodec | None = None,
        recordings_dir: str | Path = "phone/recordings",
    ):
        self.stt = stt or WhisperSTT()
        self.codec = codec or PhoneAudioCodec()

        self.recordings_dir = Path(recordings_dir)

        if not self.recordings_dir.is_absolute():
            self.recordings_dir = (
                Path(__file__).resolve().parent.parent.parent
                / self.recordings_dir
            )

        self.recordings_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    def pcm16_to_wav(
        self,
        pcm_audio: np.ndarray,
        output_file: str | Path,
    ) -> Path:
        """
        Save 16 kHz mono PCM16 NumPy audio as a WAV file.
        """

        if not isinstance(pcm_audio, np.ndarray):
            raise TypeError(
                "pcm_audio must be a NumPy array"
            )

        pcm_audio = np.asarray(
            pcm_audio,
            dtype=np.int16,
        )

        output_path = Path(output_file)

        if not output_path.is_absolute():
            output_path = (
                self.recordings_dir
                / output_path
            )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with wave.open(
            str(output_path),
            "wb",
        ) as wav_file:

            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(
                self.codec.whisper_sample_rate
            )

            wav_file.writeframes(
                pcm_audio.astype(
                    "<i2",
                    copy=False,
                ).tobytes()
            )

        return output_path

    def transcribe_mulaw(
        self,
        mulaw_audio: bytes,
        output_file: str = "phone_stt_test.wav",
        language: str | None = None,
    ) -> str:
        """
        Convert Twilio μ-law audio into Whisper-ready WAV
        and transcribe it using the existing WhisperSTT.
        """

        if not isinstance(
            mulaw_audio,
            bytes,
        ):
            raise TypeError(
                "mulaw_audio must be bytes"
            )

        if not mulaw_audio:
            raise ValueError(
                "mulaw_audio cannot be empty"
            )

        whisper_audio = (
            self.codec.mulaw_to_whisper_pcm(
                mulaw_audio
            )
        )

        if whisper_audio.size == 0:
            raise ValueError(
                "Decoded audio is empty"
            )

        wav_path = self.pcm16_to_wav(
            whisper_audio,
            output_file,
        )

        print(
            f"[PHONE STT] WAV created: {wav_path}"
        )

        print(
            "[PHONE STT] Sending audio to "
            "Groq Whisper..."
        )

        if language:
            text = self.stt.transcribe(
                audio_file=str(wav_path),
                language=language,
            )
        else:
            text = self.stt.transcribe(
                audio_file=str(wav_path),
            )

        print(
            f"[PHONE STT] Transcription: {text}"
        )

        return text