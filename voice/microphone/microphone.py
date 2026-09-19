import wave
from pathlib import Path
from typing import Optional

import numpy as np
import sounddevice as sd


class Microphone:
    """
    Handles microphone audio capture for the AI Reception system.

    Audio format:
        - Mono
        - 16-bit PCM
        - Configurable sample rate
    """

    def __init__(
        self,
        sample_rate: int = 16000,
        channels: int = 1,
        dtype: str = "int16",
        device: Optional[int] = None,
    ):
        self.sample_rate = sample_rate
        self.channels = channels
        self.dtype = dtype
        self.device = device

        self.last_audio = None

    def get_default_device(self):
        """
        Return the currently configured/default
        input device.
        """

        try:
            device_info = sd.query_devices(
                self.device,
                "input",
            )

            return device_info

        except Exception as error:
            raise RuntimeError(
                f"Unable to access microphone: {error}"
            ) from error

    def print_device_info(self) -> None:
        """
        Print information about the microphone device.
        """

        device_info = self.get_default_device()

        print("Microphone device:")
        print(
            f"  Name: "
            f"{device_info['name']}"
        )

        print(
            f"  Sample rate: "
            f"{device_info['default_samplerate']}"
        )

        print(
            f"  Input channels: "
            f"{device_info['max_input_channels']}"
        )

    def record(
        self,
        duration: float = 5.0,
    ) -> np.ndarray:
        """
        Record microphone audio for a fixed duration.

        Args:
            duration:
                Recording duration in seconds.

        Returns:
            NumPy array containing the recorded
            16-bit PCM audio.
        """

        if duration <= 0:
            raise ValueError(
                "Recording duration must be greater than 0."
            )

        print()
        print(
            f"Recording for {duration:.1f} seconds..."
        )
        print("Speak into the microphone.")

        try:

            recording = sd.rec(
                int(
                    duration
                    * self.sample_rate
                ),
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=self.dtype,
                device=self.device,
            )

            sd.wait()

        except Exception as error:

            raise RuntimeError(
                f"Microphone recording failed: {error}"
            ) from error

        # Make sure the returned array is int16.
        recording = np.asarray(
            recording,
            dtype=np.int16,
        )

        self.last_audio = recording

        print("Recording completed.")

        return recording

    def get_audio_level(
        self,
        audio: Optional[np.ndarray] = None,
    ) -> float:
        """
        Calculate the normalized RMS audio level.

        Returns:
            Value between approximately 0.0 and 1.0.
        """

        if audio is None:
            audio = self.last_audio

        if audio is None:
            return 0.0

        audio_float = (
            audio.astype(np.float32)
            / 32768.0
        )

        rms = np.sqrt(
            np.mean(
                np.square(audio_float)
            )
        )

        return float(rms)

    def save_wav(
        self,
        audio: np.ndarray,
        file_path: str,
    ) -> Path:
        """
        Save recorded audio as a WAV file.

        Args:
            audio:
                NumPy audio array.

            file_path:
                Destination WAV path.

        Returns:
            Path of the saved WAV file.
        """

        output_path = Path(file_path)

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        # Convert stereo/multi-channel audio
        # to bytes correctly.
        audio = np.asarray(
            audio,
            dtype=np.int16,
        )

        audio_bytes = audio.tobytes()

        try:

            with wave.open(
                str(output_path),
                "wb",
            ) as wav_file:

                wav_file.setnchannels(
                    self.channels
                )

                wav_file.setsampwidth(
                    2
                )

                wav_file.setframerate(
                    self.sample_rate
                )

                wav_file.writeframes(
                    audio_bytes
                )

        except Exception as error:

            raise RuntimeError(
                f"Unable to save WAV file: {error}"
            ) from error

        print(
            f"Audio saved to: "
            f"{output_path}"
        )

        return output_path

    def record_and_save(
        self,
        duration: float,
        file_path: str,
    ) -> Path:
        """
        Record audio and immediately save it as WAV.
        """

        audio = self.record(
            duration=duration
        )

        return self.save_wav(
            audio,
            file_path,
        )

    def list_input_devices(self) -> None:
        """
        Display available audio input devices.
        """

        print()
        print("=" * 60)
        print("AVAILABLE AUDIO INPUT DEVICES")
        print("=" * 60)

        devices = sd.query_devices()

        found_input_device = False

        for index, device in enumerate(devices):

            if device["max_input_channels"] <= 0:
                continue

            found_input_device = True

            print(
                f"[{index}] "
                f"{device['name']}"
            )

            print(
                f"    Input channels: "
                f"{device['max_input_channels']}"
            )

            print(
                f"    Default sample rate: "
                f"{device['default_samplerate']}"
            )

        if not found_input_device:

            print(
                "No microphone input devices found."
            )

        print("=" * 60)

    def test_microphone(self) -> bool:
        """
        Perform a short microphone test.

        Returns:
            True if audio appears to have been captured.
        """

        audio = self.record(
            duration=3.0
        )

        level = self.get_audio_level(
            audio
        )

        print(
            f"Audio RMS level: {level:.6f}"
        )

        if level <= 0.0001:

            print(
                "WARNING: Very little or no "
                "microphone audio was detected."
            )

            return False

        print(
            "Microphone audio detected successfully."
        )

        return True