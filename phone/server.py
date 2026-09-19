from __future__ import annotations

from fastapi import FastAPI

from phone.telephony.webhook import router as webhook_router
from phone.telephony.media import router as media_router


app = FastAPI(
    title="AI Reception Phone Engine",
    version="1.0.0",
)


@app.get("/")
async def root():
    return {
        "service": "AI Reception Phone Engine",
        "status": "running",
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "phone-engine",
    }


app.include_router(webhook_router)
app.include_router(media_router)