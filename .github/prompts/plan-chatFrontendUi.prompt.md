# Chat Frontend UI Plan

## Goals
- Deliver a ChatGPT-like web UI on top of existing auth shell.
- Support single-session chat plus session list/switching.
- Work with current non-streaming /api/v1/chat endpoints while paving a path for future token streaming.

## Assumptions
- Auth flow remains as in frontend/index.html and frontend/js/auth-app.js: user must be authenticated first (cookie-based).
- Use current chat routes in legalcodex/http_server/routes/chat.py (non-streaming responses): list sessions, create/open, send message (aggregated text), reset, close.
- No attachments/uploads in this iteration.
- Styling builds on existing light theme; no design system in place yet.

## Layout
- App shell: header with app name and user status (logout link).
- Side panel (left, collapsible on mobile): session list with create button; session settings (rename, close), model selector, system prompt selector.
- Main pane: scrollable message history, role-tagged (user vs assistant), code block styling, timestamps, copy action.
- Sticky bottom input bar: multiline textarea, Enter to send (Shift+Enter newline), send button, stop/abort button during in-flight request, character counter.
- Responsive: side panel collapses to overlay on small screens; sticky input stays above mobile keyboard; ensure adequate tap targets.

## Flows
- Load: on auth-ready, fetch session list; open last-used session if available else create a new one.
- Session create/open: POST create; clicking session opens via GET; update side panel state.
- Send message: append user message locally; POST to send; disable input while waiting; on response append assistant message; scroll to bottom.
- Simulated streaming (optional): while waiting, show animated placeholder and progressively append chunks if backend later streams; fall back to single final render with current API.
- Reset/close: expose actions in side panel; clear or archive conversation view accordingly.

## UX Details
- Empty state: friendly prompt to start chatting; show shortcut hint (Enter to send, Shift+Enter newline).
- Message bubbles: differentiate background; show role label; support markdown rendering and code blocks with monospace font and copy button.
- Errors: inline toast and message-level error row with retry; re-enable input on failure.
- Scroll behavior: auto-scroll on new assistant messages unless user has scrolled up; add jump-to-latest control.
- State persistence: keep current session_id in memory; optionally store last session_id in localStorage to restore on reload.

## API Usage (current)
- GET /api/v1/chat/sessions → render list.
- POST /api/v1/chat/sessions → create new session; switch view to it.
- GET /api/v1/chat/session/{session_id} → open existing.
- POST /api/v1/chat/session/{session_id}/message → send user prompt, receive full assistant reply text; update history.
- POST /api/v1/chat/session/{session_id}/reset → clear history.
- POST /api/v1/chat/session/{session_id}/close → mark closed; hide from active list (or show archived state).

## Accessibility
- Keyboard: focus starts on input; tab order covers send/stop and session controls; Enter vs Shift+Enter behavior is clear.
- ARIA: labels on textarea, buttons (send/stop), session list items; live region for assistant responses.
- Contrast: ensure readable backgrounds for bubbles and buttons per WCAG AA.

## Open Questions / Next Steps
- Confirm visual theme (colors, typography) and code block styling.
- Decide how to display model/system prompt selectors (per session? global?).
- Define maximum message length and truncation/expand pattern.
- Plan for future streaming transport (SSE/NDJSON) and how to progressively render tokens.
- Whether to support session rename/archiving and persistence of session list locally.
