# Front-End Authentication Plan (Vue-based, Common UX Pattern)

## Goal
Implement a standard web authentication UX for LegalCodex front-end pages served from `frontend/`, using a **Vue-based** front-end and the existing cookie-auth API:
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/logout`

## Current Backend Contract (as of now)
- `POST /api/v1/auth/login` expects JSON `{ username, password }`.
- On success, backend sets `HttpOnly` cookie `lc_access=GRANTED` scoped to `/api/v1`.
- `POST /api/v1/auth/logout` clears that cookie.
- No explicit session bootstrap endpoint yet (`GET /api/v1/auth/session` recommended).

## UX Pattern to Follow
1. App load shows a short loading state.
2. Front-end performs a silent session check.
3. If authenticated → show app shell.
4. If not authenticated → show login form.
5. Login submit shows disabled/loading button state.
6. Invalid credentials show inline error message.
7. Logout returns user to login screen.

## Front-End Technology Decision (Updated)
Use **Vue 3** as the UI layer.

### Why Vue for this project now
- Cleaner state-driven UI than manual DOM toggling.
- Good fit for a Python-first team and incremental complexity.
- Can start without bundler using Vue ESM from CDN, matching current static-file architecture.

### Runtime approach (MVP)
- `frontend/index.html` loads Vue from CDN (`type="module"`).
- `frontend/js/auth-app.js` creates and mounts Vue app.
- Keep API calls with `fetch(..., { credentials: 'include' })`.

## Required HTML Changes (`frontend/index.html`)
- Add root mount node: `<div id="app"></div>`.
- Include Vue + app module scripts at end of body.
- Keep HTML minimal; render login/loading/app-shell via Vue template.

## Required JavaScript to Generate (`frontend/js/auth-app.js`)
1. **Vue app state**
   - `viewState`: `loading | unauthenticated | authenticated`
   - `isSubmitting`, `errorMessage`, `form.username`, `form.password`

2. **Vue methods**
   - `checkSession()`
   - `submitLogin()`
   - `submitLogout()`
   - `clearError()`

3. **API functions (same file for MVP)**
   - `login(username, password)` → `POST /api/v1/auth/login`
   - `logout()` → `POST /api/v1/auth/logout`
   - `checkSession()`:
     - Preferred: `GET /api/v1/auth/session`
     - Temporary fallback: protected API probe, treat `401` as unauthenticated

4. **Bootstrap**
   - On mount: run `checkSession()`
   - Render correct Vue view section

## CSS Updates Needed (`frontend/styles.css`)
- Layout for centered login card
- Input/button spacing
- Disabled/loading button styles
- Inline error style
- Minimal app-shell spacing

## Recommended Backend Follow-up
Add `GET /api/v1/auth/session`:
- `200 { authenticated: true }` when cookie valid
- `401 { authenticated: false }` otherwise

This makes Vue bootstrap deterministic and avoids probing unrelated endpoints.

## Implementation Sequence
1. Update `frontend/index.html` to mount Vue app.
2. Extend `frontend/styles.css` for auth UI states.
3. Implement `frontend/js/auth-app.js` (Vue state + methods + API calls).
4. Add backend session endpoint (recommended).
5. Manual QA for login/logout/reload/error states.

## Acceptance Criteria
- Initial load shows loading then correct auth state.
- Invalid credentials show inline error and keep login visible.
- Valid credentials switch to app shell without page reload.
- Refresh preserves authenticated UX when cookie is valid.
- Logout reliably returns to unauthenticated view.

## Test Plan
### Manual
- Wrong credentials → error shown.
- Correct credentials → app shell visible.
- Refresh after login → remains authenticated.
- Logout → login shown again.

### Automated (later)
- Playwright smoke tests for login failure/success/logout.
- Keep FastAPI route unit tests for auth cookie and static serving behavior.
