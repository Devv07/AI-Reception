from __future__ import annotations

import audioop
import base64
import wave
from pathlib import Path
from typing import Any

import numpy as np
import pyttsx3
from scipy.signal import resample_poly


class PhoneTTSAdapter:
    """
    Phone-specific TTS pipeline.

    Converts text into:
        pyttsx3 WAV
        -> mono PCM16
        -> 8 kHz PCM16
        -> G.711 μ-law
        -> Base64

    The final Base64 payload can be placed directly
    inside a Twilio Media Stream message.
    """

    PHONE_SAMPLE_RATE = 8000
    PHONE_CHANNELS = 1
    PHONE_SAMPLE_WIDTH = 2

    def __init__(
        self,
        rate: int = 165,
        volume: float = 1.0,
        preferred_voice: str = "zira",
        output_dir: str | Path = "phone/recordings",
    ):
        self.rate = rate
        self.volume = volume
        self.preferred_voice = preferred_voice.lower()

        self.output_dir = Path(output_dir)

        if not self.output_dir.is_absolute():
            self.output_dir = (
                Path(__file__).resolve().parent.parent.parent
                / self.output_dir
            )

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    def _create_engine(self):
        engine = pyttsx3.init()

        engine.setProperty("rate", self.rate)
        engine.setProperty("volume", self.volume)

        voices = engine.getProperty("voices")

        selected_voice = None

        for voice in voices:
            voice_name = str(
                getattr(voice, "name", "")
            ).lower()

            voice_id = str(
                getattr(voice, "id", "")
            ).lower()

            if self.preferred_voice in voice_name:
                selected_voice = voice
                break

            if self.preferred_voice in voice_id:
                selected_voice = voice
                break

        if selected_voice is not None:
            engine.setProperty(
                "voice",
                selected_voice.id,
            )

            print(
                f"[PHONE TTS] Voice: "
                f"{getattr(selected_voice, 'name', selected_voice.id)}"
            )
        else:
            print(
                "[PHONE TTS] Preferred voice not found. "
                "Using system default voice."
            )

        return engine

    def synthesize_to_wav(
        self,
        text: str,
        output_file: str = "phone_tts.wav",
    ) -> Path:
        text = text.strip()

        if not text:
            raise ValueError(
                "text cannot be empty"
            )

        output_path = Path(output_file)

        if not output_path.is_absolute():
            output_path = self.output_dir / output_path

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        print()
        print("[PHONE TTS] Generating speech...")
        print(f"[PHONE TTS] Text: {text}")

        engine = self._create_engine()

        try:
            engine.save_to_file(
                text,
                str(output_path),
            )

            engine.runAndWait()

        finally:
            try:
                engine.stop()
            except Exception:
                pass

        if not output_path.exists():
            raise RuntimeError(
                f"TTS WAV file was not created: {output_path}"
            )

        if output_path.stat().st_size == 0:
            raise RuntimeError(
                f"TTS WAV file is empty: {output_path}"
            )

        print(
            f"[PHONE TTS] WAV created: {output_path}"
        )

        return output_path

    @staticmethod
    def _read_wav(
        wav_path: str | Path,
    ) -> tuple[bytes, int, int, int]:
        wav_path = Path(wav_path)

        with wave.open(str(wav_path), "rb") as wav_file:
            channels = wav_file.getnchannels()
            sample_width = wav_file.getsampwidth()
            sample_rate = wav_file.getframerate()
            pcm_data = wav_file.readframes(
                wav_file.getnframes()
            )

        return (
            pcm_data,
            sample_rate,
            channels,
            sample_width,
        )

    @staticmethod
    def _convert_to_mono_pcm16(
        pcm_data: bytes,
        channels: int,
        sample_width: int,
    ) -> bytes:
        if not pcm_data:
            raise ValueError(
                "PCM audio is empty"
            )

        if sample_width != 2:
            pcm_data = audioop.lin2lin(
                pcm_data,
                sample_width,
                2,
            )

        if channels == 1:
            return pcm_data

        if channels == 2:
            return audioop.tomono(
                pcm_data,
                2,
                0.5,
                0.5,
            )

        raise ValueError(
            f"Unsupported channel count: {channels}"
        )

    @staticmethod
    def _resample_to_8khz(
        pcm_data: bytes,
        input_sample_rate: int,
    ) -> bytes:
        if input_sample_rate == 8000:
            return pcm_data

        samples = np.frombuffer(
            pcm_data,
            dtype="<i2",
        )

        if samples.size == 0:
            raise ValueError(
                "PCM audio contains no samples"
            )

        gcd = np.gcd(
            input_sample_rate,
            8000,
        )

        up = 8000 // gcd
        down = input_sample_rate // gcd

        resampled = resample_poly(
            samples.astype(np.float32),
            up,
            down,
        )

        resampled = np.clip(
            resampled,
            -32768,
            32767,
        ).astype("<i2")

        return resampled.tobytes()

    @staticmethod
    def pcm16_to_mulaw(
        pcm_data: bytes,
    ) -> bytes:
        if not pcm_data:
            raise ValueError(
                "PCM audio cannot be empty"
            )

        return audioop.lin2ulaw(
            pcm_data,
            2,
        )

    @staticmethod
    def mulaw_to_base64(
        mulaw_data: bytes,
    ) -> str:
        if not mulaw_data:
            raise ValueError(
                "μ-law audio cannot be empty"
            )

        return base64.b64encode(
            mulaw_data
        ).decode("ascii")

    def wav_to_mulaw(
        self,
        wav_path: str | Path,
    ) -> bytes:
        (
            pcm_data,
            sample_rate,
            channels,
            sample_width,
        ) = self._read_wav(wav_path)

        print()
        print("[PHONE TTS] Source WAV:")
        print(f"  Sample rate: {sample_rate}")
        print(f"  Channels: {channels}")
        print(f"  Sample width: {sample_width} bytes")

        pcm_data = self._convert_to_mono_pcm16(
            pcm_data,
            channels,
            sample_width,
        )

        pcm_data = self._resample_to_8khz(
            pcm_data,
            sample_rate,
        )

        mulaw_data = self.pcm16_to_mulaw(
            pcm_data
        )

        print(
            "[PHONE TTS] Converted to "
            "8 kHz mono μ-law."
        )

        print(
            f"[PHONE TTS] μ-law bytes: "
            f"{len(mulaw_data)}"
        )

        return mulaw_data

    def synthesize(
        self,
        text: str,
        output_file: str = "phone_tts.wav",
    ) -> bytes:
        wav_path = self.synthesize_to_wav(
            text=text,
            output_file=output_file,
        )

        return self.wav_to_mulaw(
            wav_path
        )

    def synthesize_base64(
        self,
        text: str,
        output_file: str = "phone_tts.wav",
    ) -> str:
        mulaw_data = self.synthesize(
            text=text,
            output_file=output_file,
        )

        payload = self.mulaw_to_base64(
            mulaw_data
        )

        print(
            f"[PHONE TTS] Base64 payload length: "
            f"{len(payload)}"
        )

        return payload

    def create_twilio_media_message(
        self,
        stream_sid: str,
        text: str,
        output_file: str = "phone_tts.wav",
    ) -> dict[str, Any]:
        if not stream_sid:
            raise ValueError(
                "stream_sid cannot be empty"
            )

        payload = self.synthesize_base64(
            text=text,
            output_file=output_file,
        )

        return {
            "event": "media",
            "streamSid": stream_sid,
            "media": {
                "payload": payload,
            },
        }

    @staticmethod
    def get_audio_duration(
        mulaw_data: bytes,
    ) -> float:
        if not mulaw_data:
            return 0.0

        # G.711 μ-law is 1 byte per sample at 8 kHz.
        return len(mulaw_data) / 8000.0