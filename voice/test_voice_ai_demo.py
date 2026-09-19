import sys
from pathlib import Path


# ---------------------------------------------------------
# PROJECT ROOT
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from voice.microphone.microphone import Microphone
from voice.stt.whisper_stt import WhisperSTT


# ---------------------------------------------------------
# DEMO AI BRAIN
# ---------------------------------------------------------

class DemoAIBrain:
    """
    Temporary AI Brain used only for Phase 6 demonstration.

    This will later be replaced by the real shared AI Brain
    from app/ai/brain.py.
    """

    def process(self, user_text: str) -> str:

        user_text = user_text.strip()

        if not user_text:
            return "I didn't hear anything. Could you please repeat that?"

        text = user_text.lower()

        if "hello" in text or "hi" in text:
            return (
                "Hello! Welcome to our reception. "
                "How can I help you today?"
            )

        if "company" in text:
            return (
                "I'd be happy to provide information "
                "about our company."
            )

        if "help" in text:
            return (
                "Of course. Please tell me what you "
                "would like help with."
            )

        return (
            f"I received your request: '{user_text}'. "
            "The real AI Brain will handle this conversation "
            "in the next integration phase."
        )


# ---------------------------------------------------------
# MAIN DEMO
# ---------------------------------------------------------

def main():

    print("=" * 60)
    print("AI RECEPTION - VOICE AI DEMO")
    print("Phase 6 Temporary Integration")
    print("=" * 60)

    # -----------------------------------------------------
    # Initialize STT
    # -----------------------------------------------------

    print("\n[1] Initializing Groq Whisper...")

    try:
        stt = WhisperSTT()
        print(f"Model: {stt.model}")
        print("STT ready.")

    except Exception as error:
        print("STT initialization failed.")
        print(error)
        return

    # -----------------------------------------------------
    # Initialize microphone
    # -----------------------------------------------------

    print("\n[2] Initializing microphone...")

    microphone = Microphone(
        sample_rate=16000,
        channels=1,
        dtype="int16",
    )

    print("Microphone ready.")

    # -----------------------------------------------------
    # Initialize demo AI brain
    # -----------------------------------------------------

    print("\n[3] Initializing demo AI Brain...")

    brain = DemoAIBrain()

    print("Demo AI Brain ready.")

    # -----------------------------------------------------
    # Record
    # -----------------------------------------------------

    print("\n[4] Recording visitor speech")

    try:
        audio = microphone.record(
            duration=5.0
        )

    except Exception as error:
        print("Microphone recording failed.")
        print(error)
        return

    # -----------------------------------------------------
    # Save audio
    # -----------------------------------------------------

    recording_dir = (
        PROJECT_ROOT
        / "voice"
        / "recordings"
    )

    recording_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    audio_file = (
        recording_dir
        / "phase6_demo.wav"
    )

    try:
        microphone.save_wav(
            audio,
            str(audio_file),
        )

    except Exception as error:
        print("Unable to save audio.")
        print(error)
        return

    # -----------------------------------------------------
    # Speech to text
    # -----------------------------------------------------

    print("\n[5] Converting speech to text")

    try:
        user_text = stt.transcribe(
            str(audio_file)
        )

    except Exception as error:
        print("Whisper transcription failed.")
        print(error)
        return

    print()
    print("Visitor:")
    print(user_text)

    # -----------------------------------------------------
    # AI Brain
    # -----------------------------------------------------

    print("\n[6] Sending text to Demo AI Brain")

    response = brain.process(
        user_text
    )

    print()
    print("Receptionist:")
    print(response)

    # -----------------------------------------------------
    # Final result
    # -----------------------------------------------------

    print()
    print("=" * 60)
    print("VOICE AI DEMO COMPLETED")
    print("=" * 60)

    print()
    print("Pipeline:")
    print("Microphone")
    print("   ↓")
    print("WAV")
    print("   ↓")
    print("Groq Whisper")
    print("   ↓")
    print("Visitor Text")
    print("   ↓")
    print("Demo AI Brain")
    print("   ↓")
    print("Receptionist Response")
    print("=" * 60)


if __name__ == "__main__":
    main()