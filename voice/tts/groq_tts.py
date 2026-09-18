import os

from dotenv import load_dotenv
from groq import Groq


load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY is not configured.")


client = Groq(api_key=api_key)


MODEL = "canopylabs/orpheus-v1-english"
DEFAULT_VOICE = "autumn"


def text_to_speech(
    text,
    output_file="voice/audio/response.wav",
    voice=DEFAULT_VOICE
):
    """
    Convert text to speech using Groq TTS.

    Args:
        text: Text to convert to speech.
        output_file: Path where the WAV file will be saved.
        voice: Groq Orpheus voice ID.

    Returns:
        Path to the generated audio file.
    """

    if not text or not text.strip():
        raise ValueError("Text cannot be empty.")

    text = text.strip()

    if len(text) > 200:
        raise ValueError(
            "Groq Orpheus TTS currently accepts a maximum of 200 characters."
        )

    response = client.audio.speech.create(
        model=MODEL,
        voice=voice,
        input=text,
        response_format="wav"
    )

    response.write_to_file(output_file)

    print(f"✅ Speech saved: {output_file}")

    return output_file