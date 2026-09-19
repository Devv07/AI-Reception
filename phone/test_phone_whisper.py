from __future__ import annotations

import audioop
import math
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


import numpy as np

from phone.audio.codec import PhoneAudioCodec
from phone.audio.whisper_adapter import PhoneWhisperAdapter
from voice.stt.whisper_stt import WhisperSTT


def create_test_audio(
    duration_seconds: float = 2.0,
    sample_rate: int = 8000,
) -> np.ndarray:
    """
    Generate a speech-like test signal.

    This is only used to verify the complete audio pipeline.
    It is NOT expected to produce meaningful words from Whisper.
    """

    sample_count = int(
        duration_seconds * sample_rate
    )

    time_axis = (
        np.arange(sample_count)
        / sample_rate
    )

    frequency_1 = 220.0
    frequency_2 = 440.0

    signal = (
        0.25
        * np.sin(
            2.0
            * math.pi
            * frequency_1
            * time_axis
        )
        +
        0.10
        * np.sin(
            2.0
            * math.pi
            * frequency_2
            * time_axis
        )
    )

    return (
        np.clip(signal, -1.0, 1.0)
        * 32767
    ).astype(np.int16)


def main() -> None:

    print()
    print("=" * 60)
    print("PHASE 10.5 - PHONE WHISPER STT TEST")
    print("=" * 60)
    print()

    print("[SETUP] Creating codec...")

    codec = PhoneAudioCodec()

    print(
        "[TEST 1] Phone codec initialization: PASS"
    )

    print("[SETUP] Creating WhisperSTT...")

    stt = WhisperSTT()

    assert stt.is_configured()

    print(
        "[TEST 2] WhisperSTT configuration: PASS"
    )

    print("[SETUP] Generating test audio...")

    original_audio = create_test_audio(
        duration_seconds=2.0,
        sample_rate=8000,
    )

    assert original_audio.dtype == np.int16
    assert original_audio.size == 16000

    print(
        "[TEST 3] 8 kHz PCM test audio: PASS"
    )

    original_pcm = codec.numpy_to_pcm16(
        original_audio
    )

    mulaw_audio = audioop.lin2ulaw(
        original_pcm,
        2,
    )

    assert len(mulaw_audio) == 16000

    print(
        "[TEST 4] Simulated Twilio μ-law audio: PASS"
    )

    whisper_audio = (
        codec.mulaw_to_whisper_pcm(
            mulaw_audio
        )
    )

    assert whisper_audio.dtype == np.int16
    assert whisper_audio.size == 32000

    print(
        "[TEST 5] μ-law → 16 kHz PCM: PASS"
    )

    adapter = PhoneWhisperAdapter(
        stt=stt,
        codec=codec,
    )

    wav_path = adapter.pcm16_to_wav(
        whisper_audio,
        "phase10_5_test.wav",
    )

    assert wav_path.exists()
    assert wav_path.stat().st_size > 44

    print(
        "[TEST 6] Whisper-ready WAV creation: PASS"
    )

    print(
        f"          WAV: {wav_path}"
    )

    print()
    print("[TEST 7] Sending audio to Groq Whisper...")
    print()

    transcription = stt.transcribe(
        audio_file=str(wav_path),
    )

    assert isinstance(
        transcription,
        str,
    )

    print()
    print(
        "[TEST 7] Groq Whisper request: PASS"
    )

    print(
        f"          Transcription: {transcription!r}"
    )

    print()
    print("=" * 60)
    print("PHASE 10.5 PHONE WHISPER PIPELINE PASSED")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()