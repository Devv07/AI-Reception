import pytest

from app.services.voice.roundtrip import CentralConversationVoiceAdapter, VoicePipelineError


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


class FakeClientResponse:
    def __init__(self, response):
        self.response = response

    def raise_for_status(self):
        if self.response.status_code >= 400:
            raise RuntimeError(self.response.text)

    def json(self):
        return self.response.json()


class FakeClientBridge:
    def __init__(self, client):
        self.client = client

    def post(self, url, json):
        path = url[url.index('/api/v1'):]
        return FakeClientResponse(self.client.post(path, json=json))


class FakeHttpClient:
    def __init__(self):
        self.calls = []

    def post(self, url, json):
        self.calls.append((url, json))
        if url.endswith('/conversations'):
            return FakeResponse({"conversation_id": "voice-conversation-1"})
        return FakeResponse({
            "ai_response": {
                "answer": "For BIT admission, please review the verified requirements with our admissions team.",
                "intent": "admission_information",
                "confidence": 0.94,
                "action": None,
                "needs_human": False,
                "language": "en",
                "sources": [{"source": "texas_college_programs_fees.md"}],
            }
        })


class FakeRecorder:
    def record_and_save(self, duration, file_path):
        return file_path


class FakeSTT:
    def transcribe(self, audio_file, language=None):
        assert language == "en"
        return "What are the BIT admission requirements?"


class FakeTTS:
    def __init__(self):
        self.spoken = []

    def speak(self, text):
        self.spoken.append(text)


def test_voice_roundtrip_uses_central_conversation_api_and_english_tts():
    client = FakeHttpClient()
    tts = FakeTTS()
    adapter = CentralConversationVoiceAdapter(
        recorder=FakeRecorder(),
        stt=FakeSTT(),
        tts=tts,
        organization_id="org-123",
        client=client,
    )

    turn = adapter.run_once(duration=0.1, audio_path="voice.wav")

    assert turn.conversation_id == "voice-conversation-1"
    assert turn.transcript == "What are the BIT admission requirements?"
    assert turn.intent == "admission_information"
    assert turn.answer.startswith("For BIT admission")
    assert tts.spoken == [turn.answer]
    assert client.calls == [
        (
            "http://127.0.0.1:8000/api/v1/conversations",
            {"organization_id": "org-123", "channel": "voice", "preferred_language": "en"},
        ),
        (
            "http://127.0.0.1:8000/api/v1/conversations/voice-conversation-1/messages",
            {"content": "What are the BIT admission requirements?", "language": "en"},
        ),
    ]


def test_voice_roundtrip_reuses_conversation_for_follow_up():
    client = FakeHttpClient()
    adapter = CentralConversationVoiceAdapter(
        recorder=FakeRecorder(), stt=FakeSTT(), tts=FakeTTS(), organization_id="org-123", client=client
    )

    adapter.run_once(audio_path="first.wav")
    adapter.run_once(audio_path="second.wav")

    assert [url for url, _ in client.calls].count("http://127.0.0.1:8000/api/v1/conversations") == 1
    assert len(client.calls) == 3


def test_microphone_failure_is_reported_without_calling_ai():
    class BrokenRecorder:
        def record_and_save(self, duration, file_path):
            raise OSError("device unavailable")

    client = FakeHttpClient()
    adapter = CentralConversationVoiceAdapter(
        recorder=BrokenRecorder(), stt=FakeSTT(), tts=FakeTTS(), organization_id="org-123", client=client
    )

    with pytest.raises(VoicePipelineError, match="microphone"):
        adapter.run_once(audio_path="voice.wav")
    assert client.calls == []


def test_non_english_api_response_is_rejected_before_tts():
    class NonEnglishClient(FakeHttpClient):
        def post(self, url, json):
            response = super().post(url, json)
            if url.endswith('/messages'):
                response.payload["ai_response"]["language"] = "ne"
            return response

    tts = FakeTTS()
    adapter = CentralConversationVoiceAdapter(
        recorder=FakeRecorder(), stt=FakeSTT(), tts=tts, organization_id="org-123", client=NonEnglishClient()
    )

    with pytest.raises(VoicePipelineError, match="central conversation API"):
        adapter.run_once(audio_path="voice.wav")
    assert tts.spoken == []


def test_voice_roundtrip_persists_through_fastapi(client, seed_data):
    tts = FakeTTS()
    adapter = CentralConversationVoiceAdapter(
        recorder=FakeRecorder(),
        stt=FakeSTT(),
        tts=tts,
        organization_id=str(seed_data["organization"].id),
        client=FakeClientBridge(client),
    )

    turn = adapter.run_once(audio_path="voice.wav")

    conversation = client.get(f"/api/v1/conversations/{turn.conversation_id}")
    assert conversation.status_code == 200
    assert conversation.json()["channel"] == "voice"
    assert len(conversation.json()["messages"]) == 2
    assert tts.spoken == [turn.answer]
