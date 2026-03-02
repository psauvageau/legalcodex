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
- The `loading` and `unauthenticated` sections in index.html must remain unchanged; new markup is added only inside the `v-else` (authenticated) block.

## File Map
Files to create or modify (all under `frontend/`):

| File | Role |
|---|---|
| `index.html` | **Modify** — add chat HTML template inside the existing authenticated `v-else` section; add `<script>` import for `chat-api.js` |
| `styles.css` | **Modify** — append chat-specific rules; all new classes use the `chat-` prefix |
| `js/auth-app.js` | **Modify** — add chat-related `data`, `methods`, and `mounted` hooks to the existing `createApp` instance |
| `js/chat-api.js` | **Create** — standalone `async function` helpers for chat endpoints, following the same pattern as `apiLogin`/`apiLogout`/`apiCheckSession` in auth-app.js. Imported by auth-app.js via `import { ... } from "./chat-api.js"` |

No new HTML pages or Vue components; everything stays in a single `createApp` call.

## Vue Reactive State Shape
Extend the existing `data()` in auth-app.js with:

```js
// --- chat state (added alongside existing auth state) ---
sessions: [],               // Array<{ session_id: string, description: string|null }>
currentSessionId: null,      // string | null
messages: [],                // Array<{ role: 'user'|'assistant'|'system', content: string }>
draft: '',                   // textarea v-model
isSending: false,            // true while POST /messages is in-flight
chatError: '',               // inline error string; cleared on next action
sidebarOpen: true,           // toggle for responsive collapse
```

## HTML Skeleton (authenticated block)
Replace the current authenticated `v-else` card body with:

```html
<section v-else class="chat-shell">
  <!-- header -->
  <header class="chat-header">
    <button class="chat-sidebar-toggle" @click="sidebarOpen = !sidebarOpen">☰</button>
    <h1>LegalCodex</h1>
    <button @click="submitLogout" :disabled="isSubmitting">Sign out</button>
  </header>

  <div class="chat-body">
    <!-- side panel -->
    <aside v-show="sidebarOpen" class="chat-sidebar">
      <button @click="createSession">+ New session</button>
      <ul class="chat-session-list">
        <li v-for="s in sessions" :key="s.session_id"
            :class="{ active: s.session_id === currentSessionId }"
            @click="openSession(s.session_id)">
          {{ s.description || s.session_id }}
        </li>
      </ul>
      <!-- reset / close actions for current session -->
    </aside>

    <!-- main pane -->
    <div class="chat-main">
      <div class="chat-messages" ref="messagesContainer">
        <!-- empty state or message list -->
      </div>

      <!-- input bar (present from Task 1, disabled until Task 4 wires it) -->
      <div class="chat-input-bar">
        <textarea v-model="draft" :disabled="isSending" placeholder="Type a message…"
                  @keydown.enter.exact.prevent="sendMessage"
                  rows="1"></textarea>
        <button @click="sendMessage" :disabled="isSending || !draft.trim()">Send</button>
      </div>
      <p v-if="chatError" class="chat-error">{{ chatError }}</p>
    </div>
  </div>
</section>
```

## CSS Class Convention
- All new classes use the `chat-` prefix (e.g., `chat-shell`, `chat-sidebar`, `chat-messages`, `chat-input-bar`, `chat-error`).
- Append rules to `styles.css`; do not modify existing auth/card rules.

## Scroll-to-Bottom Strategy
- Use a Vue template ref (`ref="messagesContainer"`) on the `.chat-messages` div.
- Before appending a new assistant message, check: `el.scrollTop + el.clientHeight >= el.scrollHeight - 40`. If true (user is near bottom), call `el.scrollTop = el.scrollHeight` after the DOM updates via `this.$nextTick()`.
- A "jump to latest" button appears when the user has scrolled up.

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

## Implementation Tasks
To keep work incremental and testable, tackle these tasks in order:

1) **Scaffold chat shell**
	- In `index.html`: replace the authenticated `v-else` card body with the chat shell HTML skeleton above (header, sidebar, main pane, input bar — all static/disabled).
	- Create `js/chat-api.js` with empty placeholder exports for later tasks.
	- In `js/auth-app.js`: import `chat-api.js`; add the new chat state properties to `data()` (all at defaults). No new methods yet beyond existing auth code.
	- In `styles.css`: append `chat-*` rules for two-column layout, sidebar, main pane, input bar, and responsive collapse.
	- Do **not** modify the `loading` or `unauthenticated` sections.
	- Test: manual load → login → see layout frame with sidebar, empty main pane, and disabled input bar.

2) **Session list wiring**
	- In `js/chat-api.js`: implement `apiListSessions()` and `apiCreateSession(opts)`.
	- In `js/auth-app.js`: after `checkSession` resolves as authenticated, call `apiListSessions()` and store result in `sessions`; auto-select the first session and set `currentSessionId`.
	- Wire the "+ New session" button to call `apiCreateSession({})`; push the returned `SessionInfo` into `sessions` and select it.
	- Test: login → sessions load; create session adds to list; state persists during view lifecycle.

3) **Load session context**
	- In `js/chat-api.js`: implement `apiGetContext(sessionId)`.
	- In `js/auth-app.js`: add `openSession(sessionId)` method; calls `apiGetContext`, maps returned `history` array to `messages`, sets `currentSessionId`.
	- Render history as simple text rows (no markdown yet); auto-scroll to bottom on load.
	- Test: switch between sessions and verify distinct histories.

4) **Send message flow**
	- In `js/chat-api.js`: implement `apiSendMessage(sessionId, message)`.
	- In `js/auth-app.js`: add `sendMessage()` method; sets `isSending = true`, pushes user message into `messages`, calls `apiSendMessage`, pushes assistant response, sets `isSending = false`. On error, set `chatError` and re-enable input.
	- Input bar is already in DOM from Task 1; now enable its event bindings.
	- Apply scroll-to-bottom strategy on assistant message arrival.
	- Handle 400/404 with inline error state and re-enable input.
	- Test: send message returns assistant text; errors surface and recover.

5) **Reset/close actions**
	- In `js/chat-api.js`: implement `apiResetContext(sessionId)` and `apiCloseSession(sessionId)`.
	- In `js/auth-app.js`: add `resetSession()` (clears `messages`) and `closeSession()` (removes from `sessions`, selects next or creates new).
	- Add reset/close buttons in sidebar under session list, visible when a session is selected.
	- Test: reset clears history; close removes/archives and prevents further messages.

6) **Markdown + formatting polish**
	- Render assistant/user messages with markdown support and code block styling; add role labels and copy button for code blocks.
	- Add empty-state copy, message timestamps (client-side), and basic error toast.
	- Test: markdown renders; copy works; empty state shows when no messages.

7) **Responsive + accessibility pass**
	- Collapse side panel on small screens with toggle; ensure input bar stays above keyboard; add focus rings and ARIA labels.
	- Test: viewport resize; keyboard-only navigation through controls.

8) **State persistence**
	- Store last `session_id` in `localStorage` and restore on load.
	- Test: reload after login → resumes last session.

9) **Future streaming placeholder (optional)**
	- Add “responding…” placeholder with animated dots while awaiting response; structure code to later swap in streaming.
	- Test: visible during request; disappears on completion or error.
