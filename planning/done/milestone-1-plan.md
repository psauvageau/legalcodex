# Milestone 1 Development Plan — Interactive Chat Command + Conversation State

## Objective
Deliver a first working conversational CLI experience by adding a `chat` command with multi-turn memory and basic session controls.

## Scope
In scope:
- New `chat` CLI command in `legalcodex/_cli/`
- Interactive REPL-style loop
- Conversation history persisted in-memory for the current session
- Basic user commands: `exit`, `reset`, `help`
- Integration with existing `Config` and `OpenAIEngine`

Out of scope (for this milestone):
- Document ingestion/indexing/retrieval
- Citations and grounding logic
- Persistent conversation storage across runs

## Deliverables
1. `legalcodex/_cli/cmd_chat.py` with `CommandChat(CliCmd)`
2. `legalcodex/__main__.py` updated to register `chat`
3. Conversation state model (lightweight, in-memory)
4. Help text and command usage examples in README
5. Unit tests for chat control flow and state reset behavior

## Functional Requirements
- Starting command: `python -m legalcodex chat`
- Prompt loop:
  - User enters prompt text
  - Assistant response is printed
  - History is appended for both user and assistant turns
- Reserved commands:
  - `exit`/`quit`: end session gracefully
  - `reset`: clear conversation history and confirm reset
  - `help`: print available commands and usage hints
- Empty input should be ignored with a small hint
- On API/runtime error: show concise error and continue loop

## Technical Design (M1)

### 1) Command layer
- Create `CommandChat` inheriting `CliCmd`
- Optional args:
  - `--system` custom system prompt override
  - `--max-turns` optional safety cap

### 2) Conversation state
- Represent state as `List[Message]` with roles aligned to engine roles
- Initialize with system message (default from engine or CLI override)
- For each turn:
  1. append user message
  2. call engine
  3. append assistant message

### 3) Engine interaction
- Reuse `OpenAIEngine` and current config loading path
- Add/extend engine call to accept history (if needed)
- Keep backward compatibility with existing `test` command

### 4) UX and resilience
- Prefixes:
  - `You>` for user input
  - `AI >` for output
- Catch `KeyboardInterrupt` and exit cleanly
- Catch API exceptions and keep session alive

## Implementation Tasks
1. Scaffold `cmd_chat.py` using command pattern
2. Register `CommandChat` in `__main__.py`
3. Implement chat REPL loop and reserved command handling
4. Add state container and history append/reset logic
5. Add/adjust engine method for multi-message conversation
6. Add tests:
   - command exits on `exit`
   - `reset` clears state
   - empty input does not call engine
   - conversation grows across turns
7. Update README usage docs

## Acceptance Criteria
- `python -m legalcodex chat` launches interactive session
- At least 2 conversational turns succeed in one session
- `reset` clears prior context and next answer behaves as fresh context
- `exit`/`quit` ends process with exit code 0
- Existing `test` command still works unchanged
- Tests pass for new chat behavior

## Risks & Mitigations
- **Risk:** Engine currently expects a single prompt only
  **Mitigation:** Add a non-breaking `run_messages(messages)` path while preserving `run(prompt)`.

- **Risk:** API errors break UX flow
  **Mitigation:** Wrap calls with retry-friendly error handling and continue loop.

- **Risk:** Token growth in long sessions
  **Mitigation:** Add optional `--max-turns` trimming for M1.

## Estimated Effort
- Command + loop: 0.5 day
- State + engine integration: 0.5–1 day
- Tests + docs: 0.5 day
- Total: ~2 days

## Definition of Done
- Code merged for `chat` command and registration
- Tests added and passing
- README updated with `chat` examples
- Manual smoke test completed on Windows PowerShell
