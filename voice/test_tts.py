import sys
from pathlib import Path


# ---------------------------------------------------------
# PROJECT ROOT
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from voice.tts.speaker import Speaker


def main():

    print("=" * 60)
    print("AI RECEPTION - PHASE 7")
    print("Female Text-to-Speech + Speaker")
    print("=" * 60)

    print("\n[TEST 1] Initializing TTS engine")

    try:
        speaker = Speaker(
            rate=165,
            volume=1.0,
        )

        print("TTS engine initialized successfully.")
        print("PASS")

    except Exception as error:
        print("FAILED")
        print()
        print(error)
        return

    print("\n[TEST 2] Checking installed voices")

    try:
        voices = speaker.get_voices()

        if not voices:
            print("FAILED: No TTS voices found.")
            return

        print(f"Found {len(voices)} installed voice(s).")
        print()

        female_voice_id = None

        for index, voice in enumerate(voices):

            print(
                f"  [{index}] "
                f"{voice.name}"
            )

            # Microsoft Zira is the female English voice
            if "zira" in voice.name.lower():
                female_voice_id = voice.id

        if female_voice_id is None:
            print()
            print("FAILED: Microsoft Zira voice was not found.")
            return

        print()
        print("Female voice selected:")
        print("Microsoft Zira Desktop - English (United States)")
        print("PASS")

    except Exception as error:
        print("FAILED")
        print()
        print(error)
        return

    print("\n[TEST 3] Selecting female voice")

    try:

        speaker.set_voice(female_voice_id)

        print("Microsoft Zira selected successfully.")
        print("PASS")

    except Exception as error:
        print("FAILED")
        print()
        print(error)
        return

    print("\n[TEST 4] Testing female receptionist")

    print()
    print("Your computer should now speak using the female voice:")
    print()
    print(
        "Hello. Welcome to our reception. "
        "How can I help you today?"
    )

    try:

        speaker.speak(
            "Hello. Welcome to our reception. "
            "How can I help you today?"
        )

        print()
        print("Female speaker test completed.")
        print("PASS")

    except Exception as error:
        print("FAILED")
        print()
        print(error)
        return

    print()
    print("=" * 60)
    print("PHASE 7 FEMALE VOICE TEST COMPLETED")
    print("=" * 60)
    print("Text → Microsoft Zira → Speaker")
    print("=" * 60)


if __name__ == "__main__":
    main()