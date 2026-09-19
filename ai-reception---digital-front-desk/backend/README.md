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

## Member 1 RAG

The Member 1 provider uses the canonical corpus in `backend/knowledge`, the shared Chroma collection `org_knowledge`, and organization-scoped metadata. Install the optional AI/RAG dependencies from `requirements.txt`, configure `AI_PROVIDER=member1` and `AI_API_KEY`, then index the corpus for an organization:

```powershell
python scripts/ingest_knowledge.py <organization-id>
```

Questions without a sufficiently relevant indexed result return an English human-assistance fallback instead of an invented answer. Source metadata is returned in the normalized AI response.

## Frontend connection

The main reception workflow uses the frontend API client and the intended base URL is `http://localhost:8000/api/v1`. WebSocket event delivery, visitor listing, analytics, and knowledge upload/search endpoints are not present in this branch.

See [BACKEND_ARCHITECTURE.md](../../docs/BACKEND_ARCHITECTURE.md), [API_CONTRACT.md](../../docs/API_CONTRACT.md), and [DATABASE.md](../../docs/DATABASE.md).
