# Milestone E — Migrate User & Chat Storage to Postgres

> **Status:** Planned
> **Date:** 2026-03-07
> **Depends on:** Milestone D (PaaS Deployment on Render)

## Summary

Replace the in-memory user dict (`_MOCK_USER_DB`) and the filesystem-based chat session
persistence (`.chat_sessions/*.json`) with a Postgres database hosted on Render.

- **ORM:** SQLAlchemy 2.0 (sync) + Alembic for schema migrations
- **Driver:** psycopg2-binary (sync — no async route conversion needed)
- **Tests:** SQLite in-memory via SQLAlchemy's engine-agnostic layer
- **Password hashing:** stays as placeholder (separate task)

Existing code interacts with the DB through the same `UsersAccess` and
`ChatSessionManager` singletons — their public APIs remain identical, minimising
impact on the 7+ call sites.

---

## Database Tables

| Table | Columns | Source |
|---|---|---|
| `users` | `id` (serial PK), `username` (unique), `password_hash`, `security_groups` (JSON array) | `User` dataclass in `legalcodex/_user_access.py` |
| `chat_sessions` | `uid` (UUID PK), `username` (FK→users.username), `created_at`, `engine_name`, `engine_model`, `engine_params` (JSON nullable), `system_prompt`, `max_messages`, `trim_length`, `summary` | `ChatSession` + `ChatContext` |
| `chat_messages` | `id` (serial PK), `session_uid` (FK→chat_sessions.uid, ON DELETE CASCADE), `ordinal` (int), `role` (string), `content` (text) | `Message` entries in `ChatContext._history` |

> `ChatContext` is 1:1 with `ChatSession` — its scalar fields live directly on the
> session row to avoid an extra join. The repeating part (messages) gets its own table.

---

## Steps

### Step 0 — Render Postgres Setup (infrastructure)

1. In the **Render dashboard**, create a new **PostgreSQL** instance in the same region
   as the web service.
2. Copy the **Internal Database URL** (`postgres://user:pass@host:5432/dbname`).
3. Add environment variable `LC_DATABASE_URL` to the Render web service, set to that URL.

### Step 1 — Add dependencies

In `setup.cfg` → `install_requires`, add:

- `SQLAlchemy>=2.0`
- `psycopg2-binary`
- `alembic`

Run `pip install -e .` locally.

### Step 2 — Create the DB package (`legalcodex/db/`)

| File | Purpose |
|---|---|
| `legalcodex/db/__init__.py` | Package marker |
| `legalcodex/db/connection.py` | `create_engine` singleton, `SessionLocal` factory, `init_db()`, `get_session()` context manager. Reads `LC_DATABASE_URL`; falls back to local SQLite `legalcodex_dev.db`. |
| `legalcodex/db/models.py` | `Base = declarative_base()` + `UserModel`, `ChatSessionModel`, `ChatMessageModel` ORM classes |
| `legalcodex/db/mappers.py` | Domain ↔ ORM mapping helpers (`user_model_to_domain`, `session_model_to_domain`, etc.) |
| `legalcodex/db/seed.py` | One-time script to insert the 3 demo users. Runnable via `python -m legalcodex.db.seed`. |

### Step 3 — Initialise Alembic

1. `alembic init legalcodex/db/migrations`
2. Edit `legalcodex/db/migrations/env.py` to import `Base.metadata` and read
   `LC_DATABASE_URL`.
3. Set `script_location = legalcodex/db/migrations` in `alembic.ini`.
4. `alembic revision --autogenerate -m "initial schema"` → creates tables.
5. `alembic upgrade head` → applies.

> **What is Alembic?** It tracks DB schema changes as numbered Python scripts
> ("migrations"). When you change a model, run `alembic revision --autogenerate`
> to generate a script, then `alembic upgrade head` to apply it.

### Step 4 — Register `LC_DATABASE_URL` env var

In `legalcodex/_environ.py`, add:

LC_DATABASE_URL: Final[str] = "LC_DATABASE_URL"


### Step 5 — Hook DB lifecycle into FastAPI

In `legalcodex/http_server/app.py`, add a **lifespan** context manager:

- **Startup:** validate DB engine connection (fail fast on bad URL).
- **Shutdown:** call `engine.dispose()` to close the connection pool.

### Step 6 — Migrate `UsersAccess` to DB

Modify `legalcodex/_user_access.py`:

1. **Keep** `User` dataclass, `SGrp`, `PWHash` types unchanged (domain model).
2. **Remove** `_USERS`, `_MOCK_USER_DB`, hardcoded user list.
3. **Rewrite** `UsersAccess.find(username)` → DB query on `UserModel`, convert via
   mapper, raise `UserNotFound` if no row.
4. **Rewrite** `UsersAccess.authenticate(username, password)` → query by username,
   compare hash, return `User` or `None`.

**All 7 callers remain unchanged** — they use `.find()` / `.authenticate()` which
keep their signatures.

### Step 7 — Migrate `ChatSessionManager` to DB

Modify `legalcodex/ai/chat/chat_session_manager.py`:

1. **Keep** the in-memory `_sessions` dict as a **write-through cache** for active
   sessions (avoids a DB write per streamed message).
2. **`add_session()`** → insert `ChatSessionModel` + `ChatMessageModel` rows, then
   cache in memory.
3. **`get_session(id)`** → check memory first; on miss, query DB + join messages,
   reconstruct domain objects, cache.
4. **`close_session(id)`** → remove from memory, upsert session row + replace message
   rows in a single transaction.
5. **`get_sessions(user)`** → query DB for that user's sessions, merge with in-memory.
6. **Remove** `_save_session`, `_load_session`, `get_path`, `_session_filename` and all
   filesystem / `os` logic.

Also in `legalcodex/ai/chat/chat_session.py`:

- Remove the `save(filename)` file-based override.
- `Serializable[ChatSessionSchema]` can stay for API serialisation; `save`/`load`
  methods become unused.

### Step 8 — Update tests

1. **Shared fixture** (`tests/conftest.py` or per-file `setUp`):
   - Create SQLite in-memory engine (`sqlite:///:memory:`).
   - `Base.metadata.create_all(engine)` → tables.
   - Seed demo users.
   - Monkeypatch `legalcodex.db.connection.SessionLocal`.
   - `tearDown` drops tables.

2. **`tests/test_chat_session.py`** — seed test user in SQLite, remove mock-DB
   dependency.
3. **`tests/http_api/test_auth_routes.py`** — same SQLite fixture; login queries seeded
   DB.
4. **`tests/http_api/test_chat_routes.py`** — remove `.chat_sessions/*.json` cleanup;
   sessions live in SQLite.

### Step 9 — Data migration for existing JSON sessions (optional)

Write `legalcodex/db/migrate_json_sessions.py`:

- Scan `.chat_sessions/*.json`, deserialise each, insert into DB.
- Optional — existing chat history may not be worth preserving.

### Step 10 — Update deployment

1. Render web service has `LC_DATABASE_URL` pointed at internal Postgres URL.
2. **Pre-deploy command** (Render supports this): `alembic upgrade head`.
3. After first deploy: run seed script via Render shell or include as a data migration.

### Step 11 — CLI fallback (local dev)

`LC_DATABASE_URL` falls back to local SQLite `legalcodex_dev.db`. This means:

- `python -m legalcodex chat` works locally without Postgres.
- `cmd_chat.py`'s hardcoded `find("test")` keeps working if local DB is seeded.

---

## Verification

| Check | Command / action |
|---|---|
| Unit tests | `pytest` — all existing tests pass using SQLite in-memory |
| Local CLI smoke test | `python -m legalcodex chat` with local SQLite |
| Local server smoke test | `python -m legalcodex serve` → hit `/api/v1/auth/login` + `/api/v1/chat/sessions` |
| Type checking | `mypy` passes (SQLAlchemy 2.0 has type stubs) |
| Render deploy | Push → `alembic upgrade head` runs in pre-deploy → live endpoints work |

---

## Decisions

| Decision | Rationale |
|---|---|
| SQLAlchemy + Alembic over raw SQL | Schema migration tooling + DB-agnostic testing with SQLite |
| Sync driver (psycopg2) | Avoids converting routes to `async def`; migrate to async later |
| Password hashing stays placeholder | Limits scope; tackled separately |
| In-memory cache for active sessions | Avoids DB write per streamed message; matches current close-to-persist pattern |
| SQLite for tests | No Docker/Postgres in CI; SQLAlchemy abstracts the engine |
| `security_groups` as JSON array | Simpler than a join table; groups are small fixed strings, not entities |