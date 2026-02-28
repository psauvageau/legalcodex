# Release Notes


# 0.0.2

## Overview

Adds HTTP server mode with cookie-based auth endpoints and a minimal login frontend, plus a CLI entrypoint to run the server.

## Details

- Introduced FastAPI app with static asset serving and new endpoints: `/api/v1/status` for health, `/api/v1/auth/login|logout|session` for cookie-backed authentication, and `/` serving the bundled frontend. Frontend path can be overridden via `LC_FRONTEND_PATH`.
- Added `serve` CLI command to run the HTTP server (host/port/reload/workers) using uvicorn, with centralized logging setup and optional GUI log window.
- Shipped a Vue-based login page (`index.html`, `js/auth-app.js`, `styles.css`) that handles session check, login, and logout states.
- Added simple in-memory user access layer (`sauvp`/`hello`, `dan`/`ninja`) to validate credentials for the auth routes.
- Added HTTP API tests covering auth/session flow, cookies, and static asset serving.

## Breaking Changes

- None.

# 0.0.1

## Overview

Initial release of `legalcodex` with CLI-first architecture, streaming LLM support, and session management.

## Details

- Added streaming-first engine architecture with an OpenAI implementation that streams tokens, counts usage, and wraps quota errors gracefully.
- Introduced chat session management (system prompt, history trim + summarization, save/load to chat_context.json) and enriched CLI chat commands (history, reset, help, exit, `--system`, `--max-turns`, `--no-load`).
- Centralized engine bootstrapping via shared CLI base, enabling engine/model selection for chat, serve, and test commands.
- Added mock engine plus unit tests covering chat context trimming/serialization and chat behaviour flows.
- Expanded repo tooling and docs (.coveragerc, mypy target update, .gitignore tweak, Copilot prompts/skills, planning docs).

## Breaking Changes
- Legacy engine entry point was replaced by the new `legalcodex.ai` module layout; update imports to `legalcodex.ai.engine.Engine` and related helpers.





