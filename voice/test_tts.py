from voice.tts.groq_tts import text_to_speech


def main():
    print("\n=== AI Reception TTS Test ===\n")

    text = "Hello! Welcome to our organization. How can I help you today?"

    output_file = text_to_speech(
        text=text
    )

    print(f"\n🎵 Audio generated successfully:")
    print(output_file)


if __name__ == "__main__":
    main()