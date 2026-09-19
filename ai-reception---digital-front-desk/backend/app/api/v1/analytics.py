from collections import Counter
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.database.session import get_db
from app.models import Conversation, User, Visitor
from app.schemas import AnalyticsResponse
from app.security import get_current_user

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("", response_model=AnalyticsResponse)
def analytics(
    timeframe: str = Query("today"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AnalyticsResponse:
    if timeframe not in {"today", "week", "month"}:
        raise HTTPException(status_code=422, detail="Invalid analytics timeframe")
    days = {"today": 1, "week": 7, "month": 30}[timeframe]
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    conversations = list(db.scalars(
        select(Conversation)
        .options(selectinload(Conversation.messages))
        .where(Conversation.organization_id == current_user.organization_id)
    ).all())
    conversations = [item for item in conversations if _as_utc(item.started_at) >= cutoff]
    visitors = list(db.scalars(select(Visitor).where(Visitor.organization_id == current_user.organization_id)).all())
    visitors = [item for item in visitors if _as_utc(item.first_seen) >= cutoff]

    visitor_hours = Counter(item.first_seen.strftime("%H:00") for item in visitors)
    intents = Counter(message.intent for item in conversations for message in item.messages if message.intent)
    channels = Counter("Reception Kiosk" if item.channel == "web" else item.channel.title() for item in conversations)
    handoffs = sum(item.status == "human_requested" for item in conversations)
    resolved = max(len(conversations) - handoffs, 0)

    return AnalyticsResponse(
        visitors_by_hour=[{"hour": hour, "count": count} for hour, count in sorted(visitor_hours.items())],
        top_intents=[{"intent": intent, "count": count} for intent, count in intents.most_common()],
        department_demand=[],
        channel_usage=[{"name": name, "value": count} for name, count in channels.items()],
        outcomes=[
            {"outcome": "Resolved by AI directly", "percentage": round(resolved / len(conversations) * 100) if conversations else 0},
            {"outcome": "Transferred to Staff", "percentage": round(handoffs / len(conversations) * 100) if conversations else 0},
        ],
    )


def _as_utc(value: datetime) -> datetime:
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)