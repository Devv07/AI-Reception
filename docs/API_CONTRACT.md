# API Contract

Base URL: `http://localhost:8000/api/v1`

## Endpoints

- `GET /health`
- `POST /auth/login`
- `GET /auth/me`
- `GET /organizations/{id}`
- `GET /departments`
- `POST /departments`
- `GET /departments/{id}`
- `POST /conversations`
- `GET /conversations`
- `GET /conversations/{id}`
- `POST /conversations/{id}/messages`
- `GET /conversations/{id}/messages`
- `GET|POST /appointments`
- `GET|PATCH /appointments/{id}`
- `GET|POST /tickets`
- `GET|PATCH /tickets/{id}`

Staff dashboard list/detail/update endpoints require `Authorization: Bearer <token>`. Visitor conversation creation and conversation-specific messaging remain kiosk-friendly.

## AI response

```json
{
  "answer": "...",
  "intent": "admission_information",
  "confidence": 0.94,
  "action": null,
  "needs_human": false,
  "language": "ne",
  "sources": []
}
```

Supported intents are general information, admission, fee, scholarship, department, office hours, contact, appointment, complaint, human assistance, location, and unknown. Supported actions are `answer_question`, `book_appointment`, `create_ticket`, `human_handoff`, and `get_department`.

There is no WebSocket endpoint in the current checkout. Dashboard event delivery must be added when the frontend live integration is restored.
