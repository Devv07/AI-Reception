import sys
from pathlib import Path


# Project root:
# E:\Hackathon\AI-Reception
PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from voice.microphone.microphone import Microphone
from voice.stt.whisper_stt import WhisperSTT


RECORDING_DIR = PROJECT_ROOT / "voice" / "recordings"
AUDIO_FILE = RECORDING_DIR / "phase5_test.wav"


def main():

    print("=" * 60)
    print("AI RECEPTION - PHASE 5")
    print("Groq Whisper Speech-to-Text")
    print("=" * 60)

    # ---------------------------------------------------------
    # TEST 1: Groq configuration
    # ---------------------------------------------------------
    print("\n[TEST 1] Checking Groq configuration")

    try:
        stt = WhisperSTT()

        print("Groq API configuration found.")
        print(f"Whisper model: {stt.model}")
        print("PASS")

    except Exception as error:
        print("FAILED")
        print()
        print(error)
        return

    # ---------------------------------------------------------
    # TEST 2: Record speech
    # ---------------------------------------------------------
    print("\n[TEST 2] Recording speech")

    microphone = Microphone(
        sample_rate=16000,
        channels=1,
        dtype="int16",
    )

    try:
        RECORDING_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        print("You will have 5 seconds to speak.")
        print(
            "Example: Hello, I need information about "
            "your company."
        )

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
    # TEST 3: Check audio
    # ---------------------------------------------------------
    print("\n[TEST 3] Checking recorded audio")

    audio_level = microphone.get_audio_level(audio)

    print(f"RMS audio level: {audio_level:.6f}")

    if audio_level <= 0.0001:
        print("FAILED: Almost no audio detected.")
        print(
            "Check your microphone and "
            "Windows microphone permissions."
        )
        return

    print("Speech audio detected.")
    print("PASS")

    # ---------------------------------------------------------
    # TEST 4: Save WAV
    # ---------------------------------------------------------
    print("\n[TEST 4] Saving WAV file")

    try:
        saved_file = microphone.save_wav(
            audio,
            str(AUDIO_FILE),
        )

        print(f"Saved: {saved_file}")
        print("PASS")

    except Exception as error:
        print("FAILED")
        print()
        print(error)
        return

    # ---------------------------------------------------------
    # TEST 5: Groq Whisper transcription
    # ---------------------------------------------------------
    print("\n[TEST 5] Sending audio to Groq Whisper")

    try:
        text = stt.transcribe(
            audio_file=str(saved_file)
        )

    except Exception as error:
        print("FAILED")
        print()
        print(error)
        return

    # ---------------------------------------------------------
    # Result
    # ---------------------------------------------------------
    print()
    print("=" * 60)
    print("TRANSCRIPTION RESULT")
    print("=" * 60)
    print(text)
    print("=" * 60)

    if not text:
        print("WARNING: Whisper returned empty text.")
        print(
            "Try speaking more clearly or "
            "closer to the microphone."
        )
    else:
        print("Speech-to-text successful.")

    print()
    print("=" * 60)
    print("PHASE 5 TEST COMPLETED")
    print("=" * 60)
    print("Microphone → WAV → Groq Whisper → Text")
    print("=" * 60)


if __name__ == "__main__":
    main()