# Task 7 QA Checklist (Responsive + Accessibility)

Scope from plan:
- Collapse side panel on small screens with toggle.
- Ensure input bar stays above keyboard.
- Add focus rings and ARIA labels.
- Validate viewport resize and keyboard-only navigation.

## Test Environment
- App running locally (`python -m legalcodex serve --host 127.0.0.1 --port 8000 --reload`).
- Browser: Chrome or Edge (latest).
- Auth test account available.
- Start from logged-in state on chat UI.

## Pass/Fail Tracker
- [ ] Desktop viewport checks pass
- [ ] Mobile viewport checks pass
- [ ] Keyboard-only navigation checks pass
- [ ] ARIA labeling checks pass
- [ ] Focus-visible checks pass
- [ ] No regressions in core chat actions (create/open/send/reset/close)

## 1) Viewport Resize Checks

### 1.1 Desktop (>= 861px)
- [ ] Sidebar is visible by default.
- [ ] Backdrop is not visible.
- [ ] Session list and chat pane appear side-by-side.
- [ ] Header toggle is present and does not break layout.
- [ ] Composer remains visible at bottom of chat pane.

Expected result:
- Two-column layout is stable; no overlap/cutoff of content.

### 1.2 Mobile (<= 860px)
- [ ] Sidebar is hidden initially (or can be hidden) and chat pane remains usable.
- [ ] Tapping sidebar toggle opens sidebar as overlay drawer.
- [ ] Backdrop appears when drawer is open.
- [ ] Tapping backdrop closes drawer.
- [ ] Pressing `Escape` closes drawer.
- [ ] Selecting a session closes drawer automatically.

Expected result:
- Sidebar behaves like a mobile drawer with clear open/close states.

## 2) Input Bar Above Keyboard (Mobile)

Run on device emulation or real phone.
- [ ] Open drawer closed state and focus chat textarea.
- [ ] On-screen keyboard appears.
- [ ] Textarea and Send button remain visible/reachable.
- [ ] Type a multi-line message (`Shift+Enter` on hardware keyboard if available).
- [ ] Send message and verify composer remains visible after response.

Expected result:
- Composer is not obscured by the on-screen keyboard and remains actionable.

## 3) Keyboard-Only Navigation

Do not use mouse after initial page load.
- [ ] `Tab` reaches sidebar toggle, sign-out, session controls, textarea, and Send.
- [ ] `Enter` activates focused buttons (toggle, session open, create/reset/close, send).
- [ ] Session entries are focusable controls (not mouse-only rows).
- [ ] `Escape` closes mobile drawer when open.
- [ ] Focus order is logical and no keyboard trap occurs.

Expected result:
- Full chat control path is operable by keyboard only.

## 4) Focus Ring Visibility

- [ ] Visible focus ring appears on sidebar toggle.
- [ ] Visible focus ring appears on session buttons.
- [ ] Visible focus ring appears on textarea.
- [ ] Visible focus ring appears on Send/reset/close/sign-out buttons.

Expected result:
- Focus indicator is consistently visible on interactive chat controls.

## 5) ARIA Label Checks

Use browser devtools Accessibility pane.
- [ ] Sidebar toggle exposes accessible name and expanded state (`aria-expanded`).
- [ ] Sidebar toggle references controlled panel (`aria-controls`).
- [ ] Sidebar panel has descriptive label.
- [ ] Session list has an accessible label.
- [ ] Session buttons have accessible names.
- [ ] Textarea has accessible label.
- [ ] Send/reset/close/sign-out controls have accessible labels.

Expected result:
- Interactive controls have meaningful accessible names and required ARIA state.

## 6) Regression Sanity (Quick)

- [ ] Create session still works.
- [ ] Open/switch session still works.
- [ ] Send message still works.
- [ ] Reset session still works.
- [ ] Close session still works.
- [ ] Logout still works.

Expected result:
- Task 7 changes do not break existing chat/auth flows.

## Defect Log Template

- Area:
- Steps to reproduce:
- Actual result:
- Expected result:
- Viewport/device:
- Severity:
- Screenshot/video:
