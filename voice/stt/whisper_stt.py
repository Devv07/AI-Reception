import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from groq import Groq


# ---------------------------------------------------------
# Load environment variables
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

ENV_FILE = PROJECT_ROOT / ".env"

load_dotenv(ENV_FILE)


class WhisperSTT:
    """
    Groq Whisper Speech-to-Text service.

    Converts recorded audio files into text.
    """

    DEFAULT_MODEL = "whisper-large-v3-turbo"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = DEFAULT_MODEL,
        language: Optional[str] = None,
    ):
        self.model = model
        self.language = language

        # -----------------------------------------------------
        # Get API key
        # -----------------------------------------------------

        self.api_key = (
            api_key
            or os.getenv("GROQ_API_KEY")
        )

        if not self.api_key:

            raise RuntimeError(
                "GROQ_API_KEY was not found.\n"
                f"Create a .env file at:\n"
                f"{ENV_FILE}\n"
                "and add:\n"
                "GROQ_API_KEY=your_api_key"
            )

        # -----------------------------------------------------
        # Initialize Groq client
        # -----------------------------------------------------

        self.client = Groq(
            api_key=self.api_key
        )

    def transcribe(
        self,
        audio_file: str,
        language: Optional[str] = None,
    ) -> str:
        """
        Transcribe an audio file using Groq Whisper.

        Args:
            audio_file:
                Path to WAV/audio file.

            language:
                Optional ISO-639-1 language code.
                Example: "en" for English.

        Returns:
            Transcribed text.
        """

        audio_path = Path(audio_file)

        # -----------------------------------------------------
        # Validate file
        # -----------------------------------------------------

        if not audio_path.exists():

            raise FileNotFoundError(
                f"Audio file not found: "
                f"{audio_path}"
            )

        if not audio_path.is_file():

            raise ValueError(
                f"Audio path is not a file: "
                f"{audio_path}"
            )

        # -----------------------------------------------------
        # Determine language
        # -----------------------------------------------------

        selected_language = (
            language
            if language is not None
            else self.language
        )

        print(
            f"Sending audio to Groq Whisper..."
        )

        print(
            f"Model: {self.model}"
        )

        print(
            f"Audio: {audio_path.name}"
        )

        try:

            with open(
                audio_path,
                "rb",
            ) as audio:

                request_data = {
                    "file": (
                        audio_path.name,
                        audio,
                    ),
                    "model": self.model,
                    "response_format": "json",
                    "temperature": 0.0,
                }

                # -------------------------------------------------
                # Add language only when explicitly provided.
                # -------------------------------------------------

                if selected_language:

                    request_data[
                        "language"
                    ] = selected_language

                transcription = (
                    self.client
                    .audio
                    .transcriptions
                    .create(
                        **request_data
                    )
                )

        except Exception as error:

            raise RuntimeError(
                "Groq Whisper transcription failed: "
                f"{error}"
            ) from error

        # -----------------------------------------------------
        # Extract text
        # -----------------------------------------------------

        text = getattr(
            transcription,
            "text",
            None,
        )

        if text is None:

            raise RuntimeError(
                "Groq returned a transcription "
                "without text."
            )

        text = text.strip()

        print(
            "Transcription completed."
        )

        return text

    def transcribe_wav(
        self,
        audio_file: str,
    ) -> str:
        """
        Convenience method for WAV files.
        """

        return self.transcribe(
            audio_file=audio_file
        )

    def is_configured(self) -> bool:
        """
        Check whether the Groq API key is configured.
        """

        return bool(self.api_key)