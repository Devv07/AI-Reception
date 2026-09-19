from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, object]:
    return {
        "success": True,
        "data": {"status": "ok", "service": "ai-reception-backend"},
    }
