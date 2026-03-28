# Release Notes


# 0.0.4

## Overview

Adds a production-ready chat frontend workflow with session persistence, accessibility/responsive improvements, and aligned backend/API updates.

## Details

- Added frontend chat API and logging modules, integrated into the authenticated app flow for session lifecycle operations.
- Added chat UI support for listing/creating/opening sessions, sending/rendering messages, and persisting the active session ID in `localStorage`.
- Improved UI responsiveness and accessibility, including sidebar behavior, keyboard navigation, and sticky chat header layout.
- Improved backend chat session/context handling in HTTP routes and chat session manager/context components for clearer state and error paths.
- Updated CLI remote chat integration and API documentation/OpenAPI artifacts to reflect the expanded chat surface.

## Breaking Changes

- None.


# 0.0.3

## Overview

Adds a full HTTP chat API with session lifecycle support, a remote CLI for driving it, and refreshed auth/documentation coverage.

## Details

- Introduced JWT-backed auth service and `require_user` dependency to guard API routes with role-aware token verification.
- Added chat HTTP endpoints for listing sessions, opening/creating sessions, sending messages, fetching context, resetting, and closing sessions (with chat context persisted on close).
- Shipped `chat-remote` CLI command that logs in via the HTTP API, reuses or creates chat sessions, sends messages, and supports history/reset/exit controls.
- Refactored chat session model/manager to persist engine/context metadata to disk and stream assistant replies, with a dedicated system prompt module and stronger singleton handling.
- Expanded API references (Markdown and OpenAPI) plus new chat/auth HTTP tests to cover the updated surface.

## Breaking Changes

- None.


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





