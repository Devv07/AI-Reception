from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent.parent

load_dotenv(PROJECT_ROOT / ".env")


# ============================================================
# TWILIO
# ============================================================

TWILIO_ACCOUNT_SID = os.getenv(
    "TWILIO_ACCOUNT_SID",
    "",
)

TWILIO_AUTH_TOKEN = os.getenv(
    "TWILIO_AUTH_TOKEN",
    "",
)

TWILIO_PHONE_NUMBER = os.getenv(
    "TWILIO_PHONE_NUMBER",
    "",
)

REAL_RECEPTION_PHONE_NUMBER = os.getenv(
    "REAL_RECEPTION_PHONE_NUMBER",
    "",
)


# ============================================================
# PUBLIC PHONE SERVER
# ============================================================

PHONE_PUBLIC_BASE_URL = os.getenv(
    "PHONE_PUBLIC_BASE_URL",
    "",
)

PHONE_MEDIA_WS_URL = os.getenv(
    "PHONE_MEDIA_WS_URL",
    "",
)


# ============================================================
# PHONE AUDIO
# ============================================================

PHONE_SAMPLE_RATE = 8000

PHONE_CHANNELS = 1

PHONE_AUDIO_FORMAT = "mulaw"


# ============================================================
# CALL LIMITS
# ============================================================

CALL_TIMEOUT_SECONDS = 30

MAX_CALL_DURATION_SECONDS = 30 * 60


# ============================================================
# VALIDATION
# ============================================================

def validate_phone_config() -> None:

    missing = []

    if not TWILIO_ACCOUNT_SID:
        missing.append("TWILIO_ACCOUNT_SID")

    if not TWILIO_AUTH_TOKEN:
        missing.append("TWILIO_AUTH_TOKEN")

    if not TWILIO_PHONE_NUMBER:
        missing.append("TWILIO_PHONE_NUMBER")

    if not REAL_RECEPTION_PHONE_NUMBER:
        missing.append(
            "REAL_RECEPTION_PHONE_NUMBER"
        )

    if not PHONE_PUBLIC_BASE_URL:
        missing.append("PHONE_PUBLIC_BASE_URL")

    if not PHONE_MEDIA_WS_URL:
        missing.append("PHONE_MEDIA_WS_URL")

    if missing:
        raise RuntimeError(
            "Missing phone configuration: "
            + ", ".join(missing)
        )