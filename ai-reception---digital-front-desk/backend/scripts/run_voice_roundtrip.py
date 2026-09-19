import argparse

from app.services.voice.roundtrip import CentralConversationVoiceAdapter


def main() -> None:
    parser = argparse.ArgumentParser(description="Run one Member 2 voice turn through the central API.")
    parser.add_argument("organization_id")
    parser.add_argument("--duration", type=float, default=5.0)
    parser.add_argument("--api-base-url", default="http://127.0.0.1:8000/api/v1")
    parser.add_argument("--audio-path")
    args = parser.parse_args()
    adapter = CentralConversationVoiceAdapter.from_member2(args.organization_id, args.api_base_url)
    turn = adapter.run_once(args.duration, args.audio_path)
    print({"conversation_id": turn.conversation_id, "transcript": turn.transcript, "answer": turn.answer, "intent": turn.intent})


if __name__ == "__main__":
    main()