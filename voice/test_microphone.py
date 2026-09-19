import sys
from pathlib import Path


# ---------------------------------------------------------
# Add project root to Python path
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from voice.microphone.microphone import Microphone


OUTPUT_FILE = (
    PROJECT_ROOT
    / "voice"
    / "recordings"
    / "phase4_test.wav"
)


def main():

    print("=" * 60)
    print("AI RECEPTION - PHASE 4")
    print("Microphone Input Test")
    print("=" * 60)

    microphone = Microphone(
        sample_rate=16000,
        channels=1,
        dtype="int16",
    )

    # ---------------------------------------------------------
    # TEST 1
    # Display microphone devices
    # ---------------------------------------------------------

    print("\n[TEST 1] Checking microphone devices")

    microphone.list_input_devices()

    # ---------------------------------------------------------
    # TEST 2
    # Display selected microphone
    # ---------------------------------------------------------

    print("\n[TEST 2] Checking selected microphone")

    try:

        microphone.print_device_info()

        print("PASS")

    except Exception as error:

        print("FAILED")
        print()
        print(error)

        return

    # ---------------------------------------------------------
    # TEST 3
    # Record audio
    # ---------------------------------------------------------

    print("\n[TEST 3] Recording microphone audio")

    print(
        "You will have 5 seconds to speak."
    )

    try:

        audio = microphone.record(
            duration=5.0
        )

        print("PASS")

    except Exception as error:

        print("FAILED")
        print()
        print(error)

        return

    # ---------------------------------------------------------
    # TEST 4
    # Check captured audio
    # ---------------------------------------------------------

    print("\n[TEST 4] Checking captured audio")

    print(
        f"Audio samples: "
        f"{len(audio)}"
    )

    print(
        f"Audio shape: "
        f"{audio.shape}"
    )

    print(
        f"Audio data type: "
        f"{audio.dtype}"
    )

    expected_samples = (
        5 * microphone.sample_rate
    )

    if len(audio) != expected_samples:

        print(
            "WARNING: Unexpected number "
            "of audio samples."
        )

    else:

        print("Sample count is correct.")

    print("PASS")

    # ---------------------------------------------------------
    # TEST 5
    # Calculate audio level
    # ---------------------------------------------------------

    print("\n[TEST 5] Checking audio level")

    audio_level = microphone.get_audio_level(
        audio
    )

    print(
        f"RMS audio level: "
        f"{audio_level:.6f}"
    )

    if audio_level <= 0.0001:

        print(
            "WARNING: Microphone captured "
            "almost no sound."
        )

        print(
            "Check your microphone or "
            "Windows microphone permissions."
        )

    else:

        print(
            "Microphone audio detected."
        )

    print("PASS")

    # ---------------------------------------------------------
    # TEST 6
    # Save WAV file
    # ---------------------------------------------------------

    print("\n[TEST 6] Saving WAV file")

    try:

        saved_file = microphone.save_wav(
            audio,
            str(OUTPUT_FILE),
        )

        if not saved_file.exists():

            print(
                "FAILED: WAV file was not created."
            )

            return

        file_size = (
            saved_file.stat().st_size
        )

        print(
            f"File size: "
            f"{file_size} bytes"
        )

        print("PASS")

    except Exception as error:

        print("FAILED")
        print()
        print(error)

        return

    # ---------------------------------------------------------
    # Final result
    # ---------------------------------------------------------

    print()
    print("=" * 60)
    print("PHASE 4 MICROPHONE TEST COMPLETED")
    print("=" * 60)

    print(
        f"WAV file: {saved_file}"
    )

    print(
        f"Audio level: "
        f"{audio_level:.6f}"
    )

    print()
    print(
        "Microphone capture is ready "
        "for Phase 5 - Groq Whisper STT."
    )

    print("=" * 60)


if __name__ == "__main__":
    main()