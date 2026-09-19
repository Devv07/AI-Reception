# Backend Architecture

The backend is a single FastAPI service using SQLAlchemy 2.x and PostgreSQL. Alembic owns schema changes; application startup never creates tables.

```text
Frontend /reception or dashboard
        |
        v
FastAPI API routers -> auth and organization checks -> services
                                      |                 |
                                      v                 v
                              Action Engine       AI Orchestrator
                                      |                 |
                                      v                 v
                               SQLAlchemy DB       Mock AI Provider
```

The current branch contains the REST backend, model layer, mock AI contract, action handlers, and frontend mock services. WebSockets, RAG retrieval, knowledge APIs, and a live frontend API adapter are not present in this checkout and remain integration work.

## Safety boundaries

- AI returns a validated proposal. It does not write to the database.
- The Action Engine validates supported actions and owns state changes.
- Authenticated reads and writes are scoped to the current user's `organization_id`.
- Visitor conversation access remains public by opaque conversation ID for kiosk use; a JWT on that request is checked against the conversation organization.
- Errors return JSON without stack traces. AI failures create a safe human-handoff response.
