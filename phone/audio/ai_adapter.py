from __future__ import annotations

from typing import Any

from services.ai.pipeline import chat


class PhoneAIAdapter:

    ORG_ID = "texas-college"

    ORG_NAME = (
        "Texas College of Management and IT"
    )

    CHANNEL = "phone"

    def __init__(self):
        self._chat = chat

    async def process_message(
        self,
        message: str,
        conversation_id: str,
        caller_number: str = "",
        call_sid: str = "",
    ) -> str:

        result = await self.process_message_details(
            message=message,
            conversation_id=conversation_id,
            caller_number=caller_number,
            call_sid=call_sid,
        )

        return result["response_text"]

    async def process_message_details(
        self,
        message: str,
        conversation_id: str,
        caller_number: str = "",
        call_sid: str = "",
    ) -> dict[str, Any]:

        message = message.strip()

        if not message:
            return {
                "response_text": "",
                "handoff_required": False,
                "handoff_department": "",
                "raw_response": None,
            }

        if not conversation_id:
            raise ValueError(
                "conversation_id is required "
                "for phone AI processing"
            )

        print()
        print("=" * 60)
        print("[PHONE AI]")
        print(f"Caller: {caller_number}")
        print(f"Call SID: {call_sid}")
        print(f"Conversation: {conversation_id}")
        print(f"Message: {message}")
        print("=" * 60)

        try:

            response = await self._chat(
                query=message,
                org_id=self.ORG_ID,
                conversation_id=conversation_id,
                channel=self.CHANNEL,
                org_name=self.ORG_NAME,
            )

        except Exception as exc:

            print(
                "[PHONE AI] Shared AI Brain error."
            )

            print(
                f"[PHONE AI] Error: {exc}"
            )

            raise

        response_text = self._extract_response_text(
            response
        )

        handoff_required = (
            self._extract_handoff_required(
                response
            )
        )

        handoff_department = (
            self._extract_handoff_department(
                response
            )
        )

        print(
            f"[PHONE AI] Response: {response_text}"
        )

        print(
            f"[PHONE AI] Handoff required: "
            f"{handoff_required}"
        )

        if handoff_department:

            print(
                f"[PHONE AI] Handoff department: "
                f"{handoff_department}"
            )

        return {
            "response_text": response_text,
            "handoff_required": handoff_required,
            "handoff_department": handoff_department,
            "raw_response": response,
        }

    @staticmethod
    def _extract_response_text(
        response: Any,
    ) -> str:

        if response is None:
            return ""

        if isinstance(response, str):
            return response.strip()

        if isinstance(response, dict):

            response_text = response.get(
                "response"
            )

            if isinstance(response_text, str):
                return response_text.strip()

            for key in (
                "answer",
                "text",
                "message",
                "content",
            ):

                value = response.get(key)

                if isinstance(value, str):
                    return value.strip()

            return str(response).strip()

        for attribute in (
            "response",
            "answer",
            "text",
            "message",
            "content",
        ):

            value = getattr(
                response,
                attribute,
                None,
            )

            if isinstance(value, str):
                return value.strip()

        return str(response).strip()

    @staticmethod
    def _extract_handoff_required(
        response: Any,
    ) -> bool:

        if not isinstance(response, dict):
            return False

        value = response.get(
            "handoff_required"
        )

        if isinstance(value, bool):
            return value

        if isinstance(value, str):

            return value.strip().lower() in {
                "true",
                "yes",
                "1",
                "required",
            }

        if isinstance(value, int):

            return value == 1

        return False

    @staticmethod
    def _extract_handoff_department(
        response: Any,
    ) -> str:

        if not isinstance(response, dict):
            return ""

        value = response.get(
            "handoff_department"
        )

        if isinstance(value, str):
            return value.strip()

        return ""


__all__ = [
    "PhoneAIAdapter",
]