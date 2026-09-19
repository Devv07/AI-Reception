from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from phone.audio.tts_adapter import PhoneTTSAdapter


def main() -> None:
    print()
    print("=" * 60)
    print("PHASE 10.7 - PHONE TTS TEST")
    print("=" * 60)
    print()

    tts = PhoneTTSAdapter(
        rate=165,
        volume=1.0,
        preferred_voice="zira",
    )

    print("[TEST 1] Phone TTS adapter initialization: PASS")

    text = (
        "Hello! Welcome to Texas College of Management and IT. "
        "How may I help you today?"
    )

    print()
    print("[TEST 2] Generating phone speech...")
    print(f"          Text: {text}")

    wav_path = tts.synthesize_to_wav(
        text=text,
        output_file="phase10_7_tts.wav",
    )

    assert wav_path.exists()
    assert wav_path.stat().st_size > 0

    print("[TEST 2] TTS WAV generation: PASS")
    print(f"          WAV: {wav_path}")

    print()
    print("[TEST 3] Converting WAV to 8 kHz μ-law...")

    mulaw_audio = tts.wav_to_mulaw(
        wav_path
    )

    assert isinstance(mulaw_audio, bytes)
    assert len(mulaw_audio) > 0

    print("[TEST 3] 8 kHz μ-law conversion: PASS")
    print(f"          μ-law bytes: {len(mulaw_audio)}")

    duration = tts.get_audio_duration(
        mulaw_audio
    )

    assert duration > 0

    print()
    print("[TEST 4] Phone audio duration: PASS")
    print(f"          Duration: {duration:.2f} seconds")

    print()
    print("[TEST 5] Converting μ-law to Base64...")

    payload = tts.mulaw_to_base64(
        mulaw_audio
    )

    assert isinstance(payload, str)
    assert payload

    print("[TEST 5] Base64 payload generation: PASS")
    print(f"          Base64 length: {len(payload)}")

    print()
    print("[TEST 6] Creating Twilio Media message...")

    twilio_message = tts.create_twilio_media_message(
        stream_sid="MZ_PHASE10_7_TEST",
        text=text,
        output_file="phase10_7_twilio.wav",
    )

    assert twilio_message["event"] == "media"
    assert (
        twilio_message["streamSid"]
        == "MZ_PHASE10_7_TEST"
    )
    assert "payload" in twilio_message["media"]
    assert twilio_message["media"]["payload"]

    print("[TEST 6] Twilio Media message: PASS")

    print()
    print("TWILIO MEDIA MESSAGE")
    print("-" * 60)
    print(f"event: {twilio_message['event']}")
    print(
        f"streamSid: "
        f"{twilio_message['streamSid']}"
    )
    print(
        "payload length: "
        f"{len(twilio_message['media']['payload'])}"
    )

    print()
    print("=" * 60)
    print("ALL PHASE 10.7 TESTS PASSED")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()