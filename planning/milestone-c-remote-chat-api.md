# Milestone C Plan — Remote ChatBehaviour REST API

## Objective
Expose `ChatBehaviour` through a REST API so a remote client can:
- Create a chat session with explicit model and runtime parameters.
- Send user prompts to that session.
- Receive assistant output as a stream of string chunks.

## Scope
In scope:
- HTTP API design and endpoint contracts.
- Session lifecycle management.
- Prompt submission API.
- Streaming response transport for incremental text.
- Error model and status codes.

Out of scope (for this milestone):
- Authentication/authorization strategy beyond placeholder hooks.
- Multi-tenant billing and quotas.
- Frontend/UI implementation.
- Distributed scaling and cross-process session replication.

## Proposed API Shape
Base path: `/api/v1`


### 0) Status
`GET /api/v1/status`

Confirm that the server is running and responsive.
(for development and testing purpose only)


Response (`200 OK`):
```json
{
  "version": "1.0.0",
  "cwd": "/users/legalcodex",
  "platform": "linux",
  "uptime": "2:00:00",
}
```

### 1) Create Session
`POST /api/v1/sessions`

Creates a server-side `ChatBehaviour` session and returns a `session_id`.

Request body:
```json
{
  "engine": "openai",
  "model": "gpt-4.1-mini",
  "parameters": {
    "temperature": 0.2,
    "max_turns": 50,
    "system_prompt": "You are a legal assistant."
  }
}
```

Response (`201 Created`):
```json
{
  "session_id": "sess_01JZ...",
  "engine": "openai",
  "model": "gpt-4.1-mini",
  "parameters": {
    "temperature": 0.2,
    "max_turns": 50,
    "system_prompt": "You are a legal assistant."
  },
  "created_at": "2026-02-20T12:00:00Z"
}
```

Notes:
- `model` is optional; if omitted, resolve with existing precedence (CLI/config default behavior equivalent).
- `parameters` should map only to supported `ChatBehaviour`/engine options.

### 2) Send Prompt + Stream Answer
`POST /api/v1/sessions/{session_id}/messages:stream`

Accepts a user prompt, appends it to session context, and streams assistant output as strings.

Request body:
```json
{
  "prompt": "Summarize the indemnity clause in 3 bullets."
}
```

Response (`200 OK`) transport options:

Option A (preferred): **Server-Sent Events (SSE)**
- `Content-Type: text/event-stream`
- Stream payload as repeated `data:` lines where each event is a JSON string chunk envelope:
```text
event: chunk
data: {"text":"The clause shifts liability"}

event: chunk
data: {"text":" for third-party claims"}

event: done
data: {"finish_reason":"stop"}
```

Option B: **NDJSON over chunked transfer**
- `Content-Type: application/x-ndjson`
- Each line is JSON with a string chunk:
```json
{"type":"chunk","text":"The clause shifts liability"}
{"type":"chunk","text":" for third-party claims"}
{"type":"done","finish_reason":"stop"}
```

Streaming contract:
- Chunks are incremental strings in order.
- Client concatenates `text` fields to reconstruct full answer.
- Terminal frame (`done`) is always emitted unless connection is aborted.

### 3) Optional Session Endpoints (recommended)
To support basic lifecycle and observability:
- `GET /api/v1/sessions/{session_id}` (metadata only)
- `DELETE /api/v1/sessions/{session_id}` (explicit cleanup)

## Data Contracts
### Session object
- `session_id: str`
- `engine: str`
- `model: str`
- `parameters: object`
- `created_at: datetime`
- `last_activity_at: datetime`

### Stream frame object
- `type: "chunk" | "done" | "error"`
- `text: str` (present for `chunk`)
- `finish_reason: str` (present for `done`)
- `error: { code: str, message: str }` (present for `error`)

## Error Handling
Return user-friendly errors aligned with existing `LCException` behavior.

Recommended HTTP statuses:
- `400 Bad Request` — invalid payload/parameters.
- `404 Not Found` — unknown `session_id`.
- `409 Conflict` — session state conflict (e.g., concurrent stream if disallowed).
- `429 Too Many Requests` — quota/rate limit.
- `500 Internal Server Error` — unexpected failure.
- `503 Service Unavailable` — upstream provider unavailable.

Error response shape:
```json
{
  "error": {
    "code": "invalid_request",
    "message": "Parameter 'prompt' must be a non-empty string."
  }
}
```

## Architecture Integration
- Keep all model/provider calls behind `Engine`.
- API layer converts HTTP payloads into domain types (`Context`, `Message`) and delegates to `ChatBehaviour`.
- No provider-specific logic in route handlers.
- Streaming adapter should consume engine/chat stream abstraction and emit API frames.

## Session Management Strategy
- Use in-memory session store for Milestone C (`session_id -> ChatBehaviour instance + metadata`).
- Add idle timeout cleanup (e.g., 30 minutes) to prevent stale sessions.
- Plan future abstraction (`SessionStore` interface) for Redis/database-backed scaling.

## Implementation Steps
1. Add API module scaffold (router, schemas, error mapper).
2. Implement in-memory session registry and ID generation.
3. Implement `POST /sessions` with validation + model/parameter resolution.
4. Implement `POST /sessions/{id}/messages:stream` with chunk streaming.
5. Map domain exceptions to HTTP error responses.
6. Add lifecycle endpoints (`GET`, `DELETE`) if adopted.
7. Add integration tests for session creation, streaming order, and error cases.
8. Document API usage examples in `README.md`.

## Acceptance Criteria
- Client can create a session with chosen model and parameters.
- Client can send a prompt referencing that session.
- Client receives streamed string chunks in-order and a final completion frame.
- Errors are user-friendly and do not expose internal stack traces.
- API layer remains engine-agnostic and `ChatBehaviour`-centric.

## Risks & Mitigations
- **Risk:** Client disconnect during stream.
  - **Mitigation:** Handle cancellation cleanly and persist consistent chat state.

- **Risk:** Session memory growth.
  - **Mitigation:** Enforce idle TTL and max sessions.

- **Risk:** Provider latency or intermittent failures.
  - **Mitigation:** Timeout policies, retries where safe, and structured error frames.

## Definition of Done
- REST API contracts implemented and documented.
- Session creation and prompt streaming work with `ChatBehaviour`.
- Streaming verified with integration tests.
- Error handling matches project exception conventions.

---

## Milestone C: Remote Chat API (ChatBehaviour)

### Goal
Expose `ChatBehaviour` through a REST API so a remote client can:
1. Create a chat session with model + runtime parameters.
2. Send user prompts.
3. Receive assistant output as a stream of strings.

---

## Authentication and Security (Added)

### Requirement
The API must require user login with `username/password` and store an access key in a browser cookie securely.

### Security Model (Established Practices)
- Use **server-side session auth** with an opaque access key (not raw credentials).
- Passwords are never stored in plaintext:
  - Hash with **Argon2id** (preferred) or bcrypt with strong cost.
  - Per-user unique salt (handled by the algorithm).
- On successful login, server sets an **HttpOnly secure cookie**:
  - `Set-Cookie: lc_access=<opaque_session_key>; HttpOnly; Secure; SameSite=Lax; Path=/api/v1; Max-Age=900`
- Rotate session/access key at login and refresh.
- Expire idle/old sessions and support explicit logout.
- Rate-limit login attempts and apply temporary lockout on repeated failures.
- Use generic login error messages (do not reveal whether username exists).
- All endpoints served over HTTPS only.
- Protect state-changing endpoints against CSRF (SameSite + CSRF token/header for unsafe methods).

---

## API Endpoints

### 1) Login
`POST /api/v1/auth/login`

**Request**
```json
{
  "username": "alice",
  "password": "********"
}
```

**Response**
- `204 No Content` (or `200`) with `Set-Cookie: lc_access=...`
- Optional body may include basic profile/session metadata (no secrets)

**Errors**
- `401 Unauthorized` invalid credentials
- `429 Too Many Requests` throttled
- `423 Locked` temporary account lockout (optional)

### 2) Logout
`POST /api/v1/auth/logout`

**Behavior**
- Invalidates server session
- Clears cookie (`Max-Age=0`)

### 3) Create Chat Session (Authenticated)
`POST /api/v1/sessions`

**Auth**
- Requires valid `lc_access` cookie

**Request**
```json
{
  "model": "gpt-4.1-mini",
  "engine": "openai",
  "temperature": 0.2,
  "max_turns": 20,
  "system_prompt": "You are a legal assistant."
}
```

**Response**
```json
{
  "session_id": "sess_123",
  "created_at": "2026-02-20T12:34:56Z"
}
```

### 4) Send Prompt + Stream Response (Authenticated)
`POST /api/v1/sessions/{session_id}/messages:stream`

**Auth**
- Requires valid `lc_access` cookie

**Request**
```json
{
  "prompt": "Summarize clause 7 in plain language."
}
```

**Streaming Response**
- Preferred: `text/event-stream` (SSE), event data is string chunks
- Alternative: `application/x-ndjson` with one JSON line per chunk

SSE example:
```
event: chunk
data: "Clause 7 limits liability..."

event: chunk
data: " It excludes indirect damages..."

event: done
data: ""
```

---

## Error Contract

For non-stream endpoints:
```json
{
  "error": {
    "code": "unauthorized",
    "message": "Authentication required."
  }
}
```

Common codes:
- `unauthorized` (401)
- `forbidden` (403)
- `not_found` (404)
- `validation_error` (400)
- `rate_limited` (429)
- `internal_error` (500)

---

## Architecture Constraints (Unchanged)

- Keep application logic API-agnostic.
- Route all LLM calls through `Engine` abstraction.
- Do not bind business logic to OpenAI-specific features.
- Chat behavior remains in `legalcodex/ai/chat/`.

---

## Acceptance Criteria (Updated)

- User can login via username/password.
- Browser receives/stores access key in secure cookie (`HttpOnly`, `Secure`, `SameSite`).
- Unauthenticated calls to session/message endpoints return 401.
- Authenticated user can create session and stream string output from ChatBehaviour.
- Logout invalidates session and cookie.
- Login endpoint enforces rate limits and safe error behavior.
- Tests cover auth success/failure, cookie flags, protected routes, and streaming with auth.
