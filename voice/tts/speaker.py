import pyttsx3


class Speaker:
    """
    Windows text-to-speech speaker.

    Uses Microsoft Zira as the preferred female voice.
    The pyttsx3 engine is created and used in the same thread.
    """

    def __init__(
        self,
        rate: int = 165,
        volume: float = 1.0,
        preferred_voice: str = "zira",
    ):
        self.rate = rate
        self.volume = volume
        self.preferred_voice = preferred_voice.lower()

        self.voice_id = None
        self.voice_name = "Unknown"

        # Only discover the voice here.
        # The actual TTS engine is created inside speak().
        self._find_preferred_voice()

    def _find_preferred_voice(self) -> None:
        engine = pyttsx3.init()

        try:
            voices = engine.getProperty("voices")

            print("[TTS] Available voices:")

            for voice in voices:
                name = getattr(voice, "name", "")
                print(f"  - {name}")

                if self.preferred_voice in name.lower():
                    self.voice_id = voice.id
                    self.voice_name = name
                    print(f"[TTS] Selected female voice: {name}")
                    return

            # Fallback female voices
            female_names = [
                "zira",
                "hazel",
                "susan",
                "samantha",
                "female",
            ]

            for voice in voices:
                name = getattr(voice, "name", "").lower()

                if any(item in name for item in female_names):
                    self.voice_id = voice.id
                    self.voice_name = voice.name
                    print(
                        f"[TTS] Selected fallback female voice: "
                        f"{voice.name}"
                    )
                    return

            # Last fallback
            if voices:
                self.voice_id = voices[0].id
                self.voice_name = voices[0].name

                print(
                    f"[TTS] Female voice not found. "
                    f"Using: {voices[0].name}"
                )

        finally:
            try:
                engine.stop()
            except Exception:
                pass

    def speak(self, text: str) -> None:
        """
        Speak text synchronously.

        The engine is created and destroyed inside this same call.
        This avoids Windows COM/thread issues with pyttsx3.
        """

        if not text or not text.strip():
            return

        print(f"Receptionist: {text}")

        engine = pyttsx3.init()

        try:
            engine.setProperty("rate", self.rate)
            engine.setProperty("volume", self.volume)

            if self.voice_id:
                engine.setProperty("voice", self.voice_id)

            engine.say(text)
            engine.runAndWait()

        finally:
            try:
                engine.stop()
            except Exception:
                pass

    def stop(self) -> None:
        """
        Compatibility method.
        """

        pass

    def get_voice(self) -> str:
        return self.voice_id or ""

    def get_voice_name(self) -> str:
        return self.voice_name