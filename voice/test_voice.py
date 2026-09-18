from voice.audio.recorder import record_audio
from voice.stt.groq_stt import transcribe_audio


def main():
    print("\n=== AI Reception Voice Test ===\n")

    audio_file = record_audio(
        duration=5
    )

    print("\n🧠 Sending audio to Groq Whisper...")

    text = transcribe_audio(audio_file)

    print("\n========== RESULT ==========")
    print(text)
    print("============================")


if __name__ == "__main__":
    main()