from __future__ import annotations

from datetime import datetime, timezone

_conversations: dict[str, list[dict[str, str]]] = {}


async def get_memory(conversation_id: str) -> list[dict[str, str]]:
    return list(_conversations.get(conversation_id, []))


async def save_memory(conversation_id: str, user_msg: str, ai_msg: str) -> None:
    history = _conversations.setdefault(conversation_id, [])
    history.append({"user": user_msg, "assistant": ai_msg, "timestamp": datetime.now(timezone.utc).isoformat()})
    del history[:-10]


async def clear_memory(conversation_id: str) -> None:
    _conversations.pop(conversation_id, None)