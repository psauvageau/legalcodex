# Copilot instructions for legalcodex

## Big picture
- `legalcodex` is a Python CLI-first app with an HTTP server mode.
- CLI entrypoint: `legalcodex/__main__.py` registers `chat`, `serve`, and `test` commands.
- Core architecture is provider-agnostic: CLI/business logic talks to `Engine` (`legalcodex/ai/engine.py`), not directly to OpenAI.
- Current engines are registered in `legalcodex/ai/_engine_selector.py` (`openai`, `mock`).

## Primary data flows
- CLI flow: argparse args → `Config.load(...)` (`legalcodex/_config.py`) → `EngineCommand` creates engine → command builds `Context` / `ChatContext` → `engine.run_messages_stream(...)`.
- Chat flow (`legalcodex/_cli/cmd_chat.py`): loads/saves `chat_context.json`, supports commands (`help`, `history`, `reset`, `exit`/`quit`), and streams tokens to terminal.
- HTTP flow (`legalcodex/http_server/app.py`): `GET /` serves `frontend/index.html`, static assets are mounted from `frontend/`, API routes are under `/api/v1`.

## What to touch for common changes
- Add a CLI command: create `legalcodex/_cli/cmd_<name>.py` subclassing `CliCmd`, then register it in `COMMANDS` in `legalcodex/__main__.py`.
- Add an LLM provider: implement `Engine` in `legalcodex/ai/engines/` and register it in `ENGINES`.
- Extend HTTP API: add route modules under `legalcodex/http_server/routes/` and include them in `app.py` with `/api/v1` prefix.
- Update frontend landing page: edit files in `frontend/` (currently `index.html`, `styles.css`).

## Project-specific conventions (observed)
- Most modules use a module logger (`_logger = logging.getLogger(__name__)`).
- User-facing failures are wrapped as `LCException` (or subclasses like `QuotaExceeded`) with internal exception details logged.
- Config is loaded from `config.json` when present; fallback is env var `LC_API_KEY` (`legalcodex/_config.py`).
- `ChatContext` keeps a system prompt + rolling history; when history exceeds `max_messages`, old messages are summarized via `summarize_overflow(...)`.

## Developer workflows
- Install editable package: `pip install -e .`
- CLI help: `python -m legalcodex --help`
- Run one-shot prompt: `python -m legalcodex test "Summarize this NDA in 3 bullets."`
- Run interactive chat: `python -m legalcodex chat` (or `--no-load` to skip prior history)
- Run server: `python -m legalcodex serve --host 127.0.0.1 --port 8000 --reload`
- Tests: `pytest` (configured by `pytest.ini`, tests under `tests/`)
- Type-checking: `mypy` (configured by `mypy.ini`)

## Integration points
- OpenAI streaming call is in `legalcodex/ai/engines/openai_engine.py` via `OpenAI().chat.completions.create(..., stream=True)`.
- HTTP auth routes (`legalcodex/http_server/routes/auth.py`) currently use a demo credential check and cookie `lc_access` scoped to `/api/v1`.
- HTTP route behavior is validated in `tests/http_api/test_auth_routes.py` (includes frontend `/` and `/styles.css` serving checks).
