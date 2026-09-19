from fastapi import APIRouter

from app.api.v1 import health
from app.api.v1 import analytics, auth, appointments, conversations, departments, organizations, tickets, visitors

router = APIRouter(prefix="/api/v1")
router.include_router(health.router)
router.include_router(auth.router)
router.include_router(organizations.router)
router.include_router(departments.router)
router.include_router(conversations.router)
router.include_router(appointments.router)
router.include_router(tickets.router)
router.include_router(visitors.router)
router.include_router(analytics.router)
