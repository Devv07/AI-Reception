from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


@dataclass
class IntegrationEvent:
    """
    Standard event format shared by the AI Reception modules.

    This object is intentionally independent of:
    - FastAPI
    - PostgreSQL
    - Twilio
    - Groq
    - OpenCV
    """

    event_type: str
    source: str

    call_sid: str | None = None
    conversation_id: str | None = None

    visitor_id: str | None = None

    channel: str = "system"

    data: dict[str, Any] = field(default_factory=dict)

    event_id: str = field(
        default_factory=lambda: f"evt-{uuid4().hex}"
    )

    timestamp: str = field(
        default_factory=lambda: datetime.now(
            timezone.utc
        ).isoformat()
    )

    def __post_init__(self) -> None:
        if not self.event_type:
            raise ValueError("event_type is required")

        if not self.source:
            raise ValueError("source is required")

        if not self.channel:
            raise ValueError("channel is required")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def __repr__(self) -> str:
        return (
            f"IntegrationEvent("
            f"event_type={self.event_type!r}, "
            f"source={self.source!r}, "
            f"event_id={self.event_id!r}"
            f")"
        )