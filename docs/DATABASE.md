# Database

PostgreSQL is the production database. Configure `DATABASE_URL` in `backend/.env` and run migrations from `backend/`:

```powershell
alembic upgrade head
```

Tables: `organizations`, `departments`, `users`, `visitors`, `conversations`, `messages`, `appointments`, `tickets`, and `documents`.

All primary keys use UUIDs. Organization-owned records carry `organization_id`; staff queries filter by the current user's organization. Appointment slots have an index over department, date, and time, and the service rejects duplicate pending/confirmed bookings.

Tests use an in-memory SQLite override so CI and local verification do not require PostgreSQL. This fallback is for tests only; production should use PostgreSQL.

Demo data is loaded after migrations:

```powershell
python scripts/seed_demo.py
```
