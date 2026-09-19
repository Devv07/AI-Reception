from __future__ import annotations

import audioop
from typing import Optional

import numpy as np
from scipy.signal import resample_poly


class PhoneAudioCodec:
    """
    Converts Twilio phone audio into PCM audio suitable
    for the Whisper STT pipeline.

    Twilio format:
        Encoding: μ-law
        Sample rate: 8000 Hz
        Channels: 1

    Whisper input:
        PCM16
        Sample rate: 16000 Hz
        Channels: 1
    """

    PHONE_SAMPLE_RATE = 8000
    WHISPER_SAMPLE_RATE = 16000
    CHANNELS = 1

    def __init__(
        self,
        phone_sample_rate: int = PHONE_SAMPLE_RATE,
        whisper_sample_rate: int = WHISPER_SAMPLE_RATE,
    ):
        self.phone_sample_rate = phone_sample_rate
        self.whisper_sample_rate = whisper_sample_rate

        if self.phone_sample_rate <= 0:
            raise ValueError(
                "phone_sample_rate must be greater than 0"
            )

        if self.whisper_sample_rate <= 0:
            raise ValueError(
                "whisper_sample_rate must be greater than 0"
            )

    def mulaw_to_pcm16(
        self,
        mulaw_bytes: bytes,
    ) -> bytes:
        """
        Convert μ-law encoded audio to signed 16-bit PCM.

        Input:
            8-bit μ-law bytes

        Output:
            little-endian signed 16-bit PCM bytes
        """

        if not isinstance(mulaw_bytes, bytes):
            raise TypeError(
                "mulaw_bytes must be bytes"
            )

        if not mulaw_bytes:
            return b""

        pcm16_bytes = audioop.ulaw2lin(
            mulaw_bytes,
            2,
        )

        return pcm16_bytes

    def pcm16_to_numpy(
        self,
        pcm16_bytes: bytes,
    ) -> np.ndarray:
        """
        Convert PCM16 little-endian bytes into
        a NumPy int16 mono array.
        """

        if not isinstance(pcm16_bytes, bytes):
            raise TypeError(
                "pcm16_bytes must be bytes"
            )

        if not pcm16_bytes:
            return np.array(
                [],
                dtype=np.int16,
            )

        return np.frombuffer(
            pcm16_bytes,
            dtype="<i2",
        ).copy()

    def numpy_to_pcm16(
        self,
        audio: np.ndarray,
    ) -> bytes:
        """
        Convert a NumPy audio array into PCM16 bytes.
        """

        if not isinstance(audio, np.ndarray):
            raise TypeError(
                "audio must be a NumPy array"
            )

        if audio.size == 0:
            return b""

        audio = np.asarray(
            audio,
            dtype=np.int16,
        )

        return audio.astype(
            "<i2",
            copy=False,
        ).tobytes()

    def resample_to_whisper(
        self,
        pcm16_audio: np.ndarray,
    ) -> np.ndarray:
        """
        Resample PCM16 audio from the phone sample rate
        to the Whisper sample rate.

        Returns:
            NumPy int16 mono audio at 16 kHz.
        """

        if not isinstance(
            pcm16_audio,
            np.ndarray,
        ):
            raise TypeError(
                "pcm16_audio must be a NumPy array"
            )

        if pcm16_audio.size == 0:
            return np.array(
                [],
                dtype=np.int16,
            )

        if (
            self.phone_sample_rate
            == self.whisper_sample_rate
        ):
            return pcm16_audio.astype(
                np.int16,
                copy=True,
            )

        audio_float = (
            pcm16_audio.astype(
                np.float32
            )
            / 32768.0
        )

        resampled = resample_poly(
            audio_float,
            self.whisper_sample_rate,
            self.phone_sample_rate,
        )

        resampled = np.clip(
            resampled,
            -1.0,
            1.0,
        )

        return (
            resampled * 32767.0
        ).astype(np.int16)

    def mulaw_to_whisper_pcm(
        self,
        mulaw_bytes: bytes,
    ) -> np.ndarray:
        """
        Complete conversion:

            μ-law 8 kHz
                ↓
            PCM16 8 kHz
                ↓
            PCM16 16 kHz

        Returns:
            NumPy int16 mono audio at 16 kHz.
        """

        pcm16_bytes = self.mulaw_to_pcm16(
            mulaw_bytes
        )

        pcm16_audio = self.pcm16_to_numpy(
            pcm16_bytes
        )

        return self.resample_to_whisper(
            pcm16_audio
        )

    def get_duration_seconds(
        self,
        audio: np.ndarray,
        sample_rate: Optional[int] = None,
    ) -> float:
        """
        Calculate audio duration.
        """

        if sample_rate is None:
            sample_rate = self.whisper_sample_rate

        if sample_rate <= 0:
            raise ValueError(
                "sample_rate must be greater than 0"
            )

        if audio.size == 0:
            return 0.0

        return audio.size / sample_rate

    def get_audio_info(
        self,
        audio: np.ndarray,
        sample_rate: Optional[int] = None,
    ) -> dict:
        """
        Return useful information about an audio buffer.
        """

        if sample_rate is None:
            sample_rate = self.whisper_sample_rate

        return {
            "sample_rate": sample_rate,
            "channels": self.CHANNELS,
            "sample_width_bytes": 2,
            "sample_count": int(audio.size),
            "duration_seconds": round(
                self.get_duration_seconds(
                    audio,
                    sample_rate,
                ),
                4,
            ),
            "dtype": str(audio.dtype),
        }