import sounddevice as sd
from scipy.io.wavfile import write


def record_audio(
    filename="voice/audio/recording.wav",
    duration=5,
    sample_rate=16000
):
    print(f"🎤 Recording for {duration} seconds...")

    audio = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype="int16"
    )

    sd.wait()

    write(filename, sample_rate, audio)

    print(f"✅ Audio saved: {filename}")

    return filename