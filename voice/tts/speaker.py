import pyttsx3
from typing import Optional


class Speaker:
    """
    Local Text-to-Speech speaker for the AI Reception system.

    Uses the operating system's installed speech engine.
    """

    def __init__(
        self,
        rate: int = 165,
        volume: float = 1.0,
        voice: Optional[str] = None,
    ):
        self.rate = rate
        self.volume = volume
        self.voice = voice

        try:
            self.engine = pyttsx3.init()
        except Exception as error:
            raise RuntimeError(
                f"Unable to initialize TTS engine: {error}"
            ) from error

        self._configure()

    def _configure(self) -> None:
        """
        Configure speech rate, volume, and optional voice.
        """

        self.engine.setProperty(
            "rate",
            self.rate,
        )

        self.engine.setProperty(
            "volume",
            self.volume,
        )

        if self.voice:
            self.engine.setProperty(
                "voice",
                self.voice,
            )

    def get_voices(self):
        """
        Return all voices available on the system.
        """

        try:
            return self.engine.getProperty("voices")
        except Exception as error:
            raise RuntimeError(
                f"Unable to retrieve TTS voices: {error}"
            ) from error

    def list_voices(self) -> None:
        """
        Print all installed system voices.
        """

        voices = self.get_voices()

        print()
        print("=" * 60)
        print("AVAILABLE TTS VOICES")
        print("=" * 60)

        if not voices:
            print("No TTS voices found.")
            print("=" * 60)
            return

        for index, voice in enumerate(voices):
            print(f"[{index}]")
            print(f"  Name: {voice.name}")
            print(f"  ID: {voice.id}")

            if hasattr(voice, "languages"):
                print(f"  Languages: {voice.languages}")

            print()

        print("=" * 60)

    def set_voice(self, voice_id: str) -> None:
        """
        Change the active TTS voice.
        """

        if not voice_id:
            raise ValueError(
                "Voice ID cannot be empty."
            )

        self.voice = voice_id

        self.engine.setProperty(
            "voice",
            voice_id,
        )

    def set_rate(self, rate: int) -> None:
        """
        Change speech rate.
        """

        if rate <= 0:
            raise ValueError(
                "Speech rate must be greater than zero."
            )

        self.rate = rate

        self.engine.setProperty(
            "rate",
            rate,
        )

    def set_volume(self, volume: float) -> None:
        """
        Change speech volume.

        Range:
            0.0 - 1.0
        """

        if not 0.0 <= volume <= 1.0:
            raise ValueError(
                "Volume must be between 0.0 and 1.0."
            )

        self.volume = volume

        self.engine.setProperty(
            "volume",
            volume,
        )

    def speak(self, text: str) -> None:
        """
        Speak the supplied text through the speaker.
        """

        if text is None:
            raise ValueError(
                "Text cannot be None."
            )

        text = str(text).strip()

        if not text:
            raise ValueError(
                "Text cannot be empty."
            )

        print()
        print("Receptionist:")
        print(text)

        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as error:
            raise RuntimeError(
                f"TTS speech failed: {error}"
            ) from error

    def stop(self) -> None:
        """
        Stop current speech.
        """

        try:
            self.engine.stop()
        except Exception as error:
            raise RuntimeError(
                f"Unable to stop TTS engine: {error}"
            ) from error

    def test_speech(self) -> bool:
        """
        Test the speaker with a reception greeting.
        """

        test_text = (
            "Hello. Welcome to our reception. "
            "How can I help you today?"
        )

        try:
            self.speak(test_text)
            return True
        except Exception as error:
            print()
            print("TTS test failed.")
            print(error)
            return False