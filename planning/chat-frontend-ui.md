# Chat Frontend UI Plan

## Goals
- Deliver a ChatGPT-like web UI on top of existing auth shell.
- Support single-session chat plus session list/switching.
- Work with current non-streaming /api/v1/chat endpoints while paving a path for future token streaming.
- Reuse the current Vue 3 (CDN) auth shell in frontend/index.html and extend it into a single-page chat experience without adding a build step.

## Assumptions
- Auth flow remains as in frontend/index.html and frontend/js/auth-app.js: cookie-based login/logout with viewState `loading | unauthenticated | authenticated` and credentials: 'include' on fetch.
- Keep the no-bundler setup (Vue from CDN, single HTML entry, shared styles.css). Add chat UI inside the authenticated view while preserving the existing login form and card layout. Visual style remains functional for now; richer CSS will be provided later.
- Use current chat routes in legalcodex/http_server/routes/chat.py (non-streaming responses): list sessions, create/open, send message (aggregated text), reset, close.
- No attachments/uploads in this iteration.
- Styling builds on existing light theme; no design system in place yet.

## Layout
- App shell: reuse current card-based shell; once authenticated, swap the card body to the chat UI (header with app name and logout button stays).
- Side panel (left, collapsible on mobile): session list with create button; session settings (rename, close). Model and system prompt are fixed to backend defaults for now (no user controls).
- Main pane: scrollable message history, role-tagged (user vs assistant), code block styling, timestamps, copy action.
- Sticky bottom input bar: multiline textarea, Enter to send (Shift+Enter newline), send button, stop/abort button during in-flight request, character counter.
- Responsive: side panel collapses to overlay on small screens; sticky input stays above mobile keyboard; ensure adequate tap targets.

## Flows
- Load: on mount, reuse existing checkSession logic; if authenticated, immediately fetch session list and hydrate chat state.
- Session create/open: POST create/open; clicking session loads its context via GET; update side panel state.
- Send message: append user message locally; POST to send; disable input while waiting; on response append assistant message; scroll to bottom.
- Simulated streaming (optional): while waiting, show animated placeholder and progressively append chunks if backend later streams; fall back to single final render with current API.
- Reset/close: expose actions in side panel; clear or archive conversation view accordingly; on close, drop from list or mark archived.
- Logout: call existing logout handler; clear chat state to avoid leaking prior session data; return to unauthenticated card.

## UX Details
- Empty state: friendly prompt to start chatting; show shortcut hint (Enter to send, Shift+Enter newline).
- Message bubbles: differentiate background; show role label; support markdown rendering and code blocks with monospace font and copy button.
- Errors: inline toast and message-level error row with retry; re-enable input on failure.
- Scroll behavior: auto-scroll on new assistant messages unless user has scrolled up; add jump-to-latest control.
- State persistence: keep current session_id in memory; optionally store last session_id in localStorage to restore on reload.

## API Usage (current)
- GET /api/v1/chat/sessions → render list.
- POST /api/v1/chat/sessions → create new session or reopen when session_id provided (201/200); switch view to it.
- GET /api/v1/chat/sessions/{session_id}/context → load context for the selected session.
- POST /api/v1/chat/sessions/{session_id}/messages → send user prompt, receive full assistant reply text; update history.
- POST /api/v1/chat/sessions/{session_id}/reset → clear history.
- POST /api/v1/chat/sessions/{session_id}/close → mark closed; hide from active list (or show archived state).
- All requests use credentials: 'include' to send lc_access cookie, matching auth-app.js behavior.

## Accessibility
- Keyboard: focus starts on input; tab order covers send/stop and session controls; Enter vs Shift+Enter behavior is clear.
- ARIA: labels on textarea, buttons (send/stop), session list items; live region for assistant responses.
- Contrast: ensure readable backgrounds for bubbles and buttons per WCAG AA.

## Open Questions / Next Steps
To keep work incremental and testable, tackle these tasks in order:

1) **Scaffold chat shell**
	- Extend authenticated view in frontend/index.html to render a chat layout placeholder (side panel + main pane) using existing Vue app and styles.css.
	- Add minimal CSS for two-column layout and responsive collapse (no chat logic yet).
	- Test: manual load → login → see layout frame.

2) **Session list wiring**
	- Implement fetch of GET /api/v1/chat/sessions after successful session check; store sessions and current session_id.
	- Render session list with create button; on create call POST /chat/sessions, update list/state; select first session by default.
	- Test: login → sessions load; create session adds to list; state persists during view lifecycle.

3) **Load session context**
	- On session select, call GET /chat/sessions/{id}/context; store system prompt, summary, history.
	- Render history as simple text rows (no markdown yet); auto-scroll to bottom on load.
	- Test: switch between sessions and verify distinct histories.

4) **Send message flow**
	- Input bar: multiline textarea with Enter-to-send, Shift+Enter newline; disable while sending.
	- POST /chat/sessions/{id}/messages; append user then assistant message; scroll to bottom.
	- Handle 400/404 with inline error state and re-enable input.
	- Test: send message returns assistant text; errors surface and recover.

5) **Reset/close actions**
	- Add reset (POST /chat/sessions/{id}/reset) to clear context; add close (POST /chat/sessions/{id}/close) to remove or archive session.
	- Update session list state accordingly.
	- Test: reset clears history; close removes/archives and prevents further messages.

6) **Markdown + formatting polish**
	- Render assistant/user messages with markdown support and code block styling; add role labels and copy button for code blocks.
	- Add empty-state copy, message timestamps (client-side), and basic error toast.
	- Test: markdown renders; copy works; empty state shows when no messages.

7) **Responsive + accessibility pass**
	- Collapse side panel on small screens with toggle; ensure input bar stays above keyboard; add focus rings and ARIA labels.
	- Test: viewport resize; keyboard-only navigation through controls.

8) **State persistence**
	- Optionally store last session_id in localStorage and restore on load.
	- Test: reload after login → resumes last session.

9) **Future streaming placeholder (optional)**
	- Add “responding…” placeholder with animated dots while awaiting response; structure code to later swap in streaming.
	- Test: visible during request; disappears on completion or error.
