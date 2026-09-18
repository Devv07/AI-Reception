# AI Reception Backend

Backend for the AI Front Desk project. The service uses FastAPI, Pydantic v2, SQLAlchemy 2.x, PostgreSQL, Alembic, JWT authentication, and a mock AI provider.

## Setup

From this directory:

```powershell
..\..\venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Set `DATABASE_URL` and `JWT_SECRET` in `.env`. PostgreSQL is the production database. Tests override the database with an in-memory SQLite database.

Never use the demo credentials or example secret outside a local demonstration.

## Run migrations and server

```powershell
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

Open `http://localhost:8000/docs` for the OpenAPI UI. Health is available at `GET /api/v1/health`.

## Demo data

After migrations, seed the TCMIT demonstration data:

```powershell
python scripts/seed_demo.py
```

The script is idempotent and prints credentials explicitly marked `DEMO ONLY`.

## Tests

```powershell
pytest
```

The mock AI provider is intentionally replaceable through `app.services.ai.provider.AIProvider`. It returns validated proposals only; database-changing actions are validated and executed by `app.services.actions.ActionEngine` and its handlers. AI failures return a safe human-handoff response.

## Frontend connection

The current frontend still uses its local mock services and has no Vite API proxy in this checkout. The intended base URL is `http://localhost:8000/api/v1`; connect the frontend service methods to these REST endpoints before the final live demo. WebSocket event delivery and knowledge/RAG endpoints are not present in this branch.

See [BACKEND_ARCHITECTURE.md](../../docs/BACKEND_ARCHITECTURE.md), [API_CONTRACT.md](../../docs/API_CONTRACT.md), and [DATABASE.md](../../docs/DATABASE.md).
