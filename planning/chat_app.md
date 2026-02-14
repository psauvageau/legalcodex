# Chat Application Workflow (Coding-Ready Spec for LegalCodex)

## Purpose
Define an implementation-ready plan for Milestone 1 chat behavior in this repository, aligned with the current CLI architecture and engine abstraction.

## Current Baseline (As-Is)
- `legalcodex/_cli/cmd_chat.py` exists and runs a basic REPL with `exit`/`quit` only.
- `legalcodex/_cli/engine_cmd.py` initializes an engine from `--engine` and `Config.load()`.
- `legalcodex/engine.py` exposes only `Engine.run(prompt: str) -> str`.
- `legalcodex/engines/openai_engine.py` currently builds single-turn messages internally.
- Error contract already exists via `LCException` in `legalcodex/exceptions.py`.

## Milestone 1 Scope (Concrete)
In scope:
- Multi-turn chat in one process (`python -m legalcodex chat`).
- In-memory conversation history for the active session.
- Reserved commands: `help`, `reset`, `exit`, `quit`.
- Optional CLI args: `--system`, `--max-turns`.
- Friendly error handling in loop without terminating session.

Out of scope:
- Persistence across program runs.
- Retrieval/citations.
- Tool calling.

## CLI Contract
Command:
- `python -m legalcodex chat [--engine <name>] [--system <text>] [--max-turns <int>]`

Arguments:
- `--system`: optional system-prompt override for this session.
- `--max-turns`: optional cap for retained conversational turns (user+assistant pairs), minimum value `1`.

Behavioural rules:
- Prompt prefix: `You>`
- Output prefix: `AI >`
- Empty input (after `.strip()`): do not call engine; print short hint.
- `help`: print command help and continue.
- `reset`: clear history to system-only state; print confirmation and continue.
- `exit`/`quit`: exit loop normally with status code `0`.

## Data Model and State Rules
State container:
- `history: list[Message]` where `Message` is role/content based and engine-compatible.

Required roles:
- `system`, `user`, `assistant` (tool role not used in M1).

Initialization:
- `history = [system_message]`
- `system_message` comes from `--system` if provided, otherwise engine default.

Per-turn update order:
1. Append user message.
2. Invoke engine with full `history`.
3. Append assistant message.
4. Apply `max-turns` trimming if configured, while always preserving the first system message.

Trimming rule for `--max-turns`:
- Keep at most `max_turns * 2` non-system messages (latest pairs).
- Preserve system message at index `0`.

## Engine Interface Changes (Non-Breaking)
To preserve API-agnostic architecture and keep existing commands working:

1. In `legalcodex/engine.py`:
- Keep `run(prompt: str) -> str` unchanged.
- Add new abstract method:
   - `run_messages(messages: list[Message]) -> str`

2. In provider engines (starting with OpenAI):
- Implement `run_messages` as primary conversation path.
- Keep `run(prompt)` as wrapper that builds a 2-message input and delegates to `run_messages`.

3. In chat command:
- Call `engine.run_messages(history)` each turn.

This keeps `cmd_test.py` unchanged and backward compatible.

## Error Handling Contract
User-facing rule:
- No raw third-party exceptions should be shown directly.

Implementation rule:
- Catch provider/runtime exceptions in engine layer and raise `LCException` (or subclass) with concise message.
- In `CommandChat.run`, catch `LCException` per turn, display concise error, continue loop.
- Catch `KeyboardInterrupt` and exit cleanly with a short message.

Logging rule:
- Use module `_logger` (no `print` for operational logs).
- Debug logs may include control flow and turn counts, never secrets/API keys.

## File-Level Implementation Plan
1. `legalcodex/engine.py`
- Add shared `Role`/`Message` typing (or equivalent shared type alias).
- Add abstract `run_messages(messages)`.

2. `legalcodex/engines/openai_engine.py`
- Implement `run_messages`.
- Keep `run(prompt)` by delegating.
- Keep message conversion provider-specific inside this file.

3. `legalcodex/engines/mock_engine.py`
- Implement deterministic `run_messages` for tests.

4. `legalcodex/_cli/cmd_chat.py`
- Add args `--system`, `--max-turns`.
- Add helpers for command detection, reset, trim, and help text.
- Replace single-prompt calls with message-history calls.

5. `README.md`
- Add `chat` usage and control commands.

6. `tests/`
- Add chat behavior tests for control flow and state transitions.

## Test Cases (Minimum)
1. `exit` ends loop without engine call.
2. `reset` clears prior conversation and retains system prompt.
3. Empty input does not call engine.
4. Two normal prompts produce two engine calls and growth in history.
5. `--max-turns=1` keeps only latest pair plus system.
6. Engine error during turn shows message and loop continues.

## Suggested Test Approach
- Unit-test command loop with monkeypatched `input()` and captured stdout/stderr.
- Use `MockEngine` or a stub engine injected via `EngineCommand` path.
- Avoid network/API calls in tests.

## Runtime Pseudocode (M1)

```text
initialize engine
system_prompt = args.system or default_system_prompt
history = [system_message(system_prompt)]

print start banner
loop:
   read user input (You>)
   normalize with strip()

   if empty: print hint; continue
   if help: print command help; continue
   if reset: history = [system_message]; print confirmation; continue
   if exit/quit: break

   append user message to history
   try:
      reply = engine.run_messages(history)
   except LCException:
      print concise error
      remove last user message (optional policy) or leave for audit
      continue

   append assistant message
   trim history using max_turns if configured
   print AI response
```

## Definition of Done (Milestone 1)
- `python -m legalcodex chat` supports multi-turn chat in one session.
- Reserved commands `help`, `reset`, `exit`, `quit` work as specified.
- Existing `python -m legalcodex test <prompt>` remains unchanged.
- New tests for chat control flow pass.
- README includes `chat` command examples.
