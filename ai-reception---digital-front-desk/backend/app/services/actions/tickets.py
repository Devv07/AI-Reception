from fastapi import HTTPException

VALID_PRIORITIES = {"low", "medium", "high"}
VALID_TICKET_STATUSES = {"open", "in_progress", "resolved", "closed"}


def validate_ticket_values(priority: str, status: str) -> None:
    if priority not in VALID_PRIORITIES:
        raise HTTPException(status_code=422, detail="Invalid ticket priority")
    if status not in VALID_TICKET_STATUSES:
        raise HTTPException(status_code=422, detail="Invalid ticket status")
