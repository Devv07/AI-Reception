from __future__ import annotations

import math
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


import numpy as np

from phone.audio.codec import PhoneAudioCodec


def create_test_audio(
    duration_seconds: float = 1.0,
    sample_rate: int = 8000,
) -> np.ndarray:
    """
    Generate a 440 Hz test tone as PCM16 audio.
    """

    sample_count = int(
        duration_seconds * sample_rate
    )

    time_axis = (
        np.arange(sample_count)
        / sample_rate
    )

    frequency = 440.0

    amplitude = 0.35

    audio = (
        amplitude
        * np.sin(
            2.0
            * math.pi
            * frequency
            * time_axis
        )
    )

    return (
        audio * 32767
    ).astype(np.int16)


def main() -> None:

    print()
    print("=" * 60)
    print("PHASE 10.4 - PHONE AUDIO CODEC TEST")
    print("=" * 60)
    print()

    codec = PhoneAudioCodec()

    print(
        "[SETUP] Phone sample rate: "
        f"{codec.phone_sample_rate} Hz"
    )

    print(
        "[SETUP] Whisper sample rate: "
        f"{codec.whisper_sample_rate} Hz"
    )

    original_audio = create_test_audio(
        duration_seconds=1.0,
        sample_rate=8000,
    )

    assert original_audio.dtype == np.int16
    assert original_audio.size == 8000

    print(
        "[TEST 1] Test PCM16 audio generation: PASS"
    )
    print(
        f"          Samples: {original_audio.size}"
    )

    original_pcm = codec.numpy_to_pcm16(
        original_audio
    )

    assert isinstance(
        original_pcm,
        bytes,
    )

    assert len(original_pcm) == 16000

    print(
        "[TEST 2] PCM16 byte conversion: PASS"
    )
    print(
        f"          PCM bytes: {len(original_pcm)}"
    )

    mulaw_audio = audioop.lin2ulaw(
        original_pcm,
        2,
    )

    assert isinstance(
        mulaw_audio,
        bytes,
    )

    assert len(mulaw_audio) == 8000

    print(
        "[TEST 3] PCM16 → μ-law conversion: PASS"
    )
    print(
        f"          μ-law bytes: {len(mulaw_audio)}"
    )

    decoded_pcm = codec.mulaw_to_pcm16(
        mulaw_audio
    )

    assert isinstance(
        decoded_pcm,
        bytes,
    )

    assert len(decoded_pcm) == 16000

    print(
        "[TEST 4] μ-law → PCM16 conversion: PASS"
    )

    decoded_numpy = codec.pcm16_to_numpy(
        decoded_pcm
    )

    assert decoded_numpy.dtype == np.int16
    assert decoded_numpy.size == 8000

    print(
        "[TEST 5] PCM16 NumPy conversion: PASS"
    )
    print(
        f"          Samples: {decoded_numpy.size}"
    )

    whisper_audio = codec.resample_to_whisper(
        decoded_numpy
    )

    assert whisper_audio.dtype == np.int16
    assert whisper_audio.size == 16000

    print(
        "[TEST 6] 8 kHz → 16 kHz resampling: PASS"
    )
    print(
        f"          Samples: {whisper_audio.size}"
    )

    complete_audio = (
        codec.mulaw_to_whisper_pcm(
            mulaw_audio
        )
    )

    assert complete_audio.dtype == np.int16
    assert complete_audio.size == 16000

    print(
        "[TEST 7] Complete μ-law → Whisper conversion: PASS"
    )

    duration = codec.get_duration_seconds(
        complete_audio
    )

    assert 0.99 <= duration <= 1.01

    print(
        "[TEST 8] Audio duration calculation: PASS"
    )
    print(
        f"          Duration: {duration:.4f} seconds"
    )

    info = codec.get_audio_info(
        complete_audio
    )

    assert info["sample_rate"] == 16000
    assert info["channels"] == 1
    assert info["sample_width_bytes"] == 2
    assert info["sample_count"] == 16000
    assert info["dtype"] == "int16"

    print(
        "[TEST 9] Audio information: PASS"
    )

    print()
    print("FINAL AUDIO INFO")
    print("-" * 60)
    print(info)

    print()
    print("=" * 60)
    print("ALL PHASE 10.4 TESTS PASSED")
    print("=" * 60)
    print()


if __name__ == "__main__":
    import audioop

    main()