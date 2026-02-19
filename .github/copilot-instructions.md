# Copilot Instructions for legalcodex

## Big picture
- Python CLI to talk to LLMs via a pluggable engine. Entry point `legalcodex/__main__.py` wires global flags (`--config`, `--verbose`, `--test`) and subcommands. Single subcommand today: `test` in `legalcodex/_cli/cmd_test.py`.
- Data flow: CLI args ➜ load `Config` from `config.json` ➜ construct `OpenAIEngine` ➜ `Engine.run(prompt)` ➜ build OpenAI messages ➜ `chat.completions.create` ➜ print first choice content.
- Why this shape: commands stay small/testable; engine can be swapped by subclassing `Engine`.

## Architecture essentials
- Commands: subclass `CliCmd` with `title`, implement `run(self, args)` and optional `add_arguments`. Register by adding the class to `COMMANDS` in `__main__.py`.
- Engine: `legalcodex/engine.py` defines `Engine` and `OpenAIEngine`. Messages are built in `build_messages(prompt)` using roles Literal[`system`, `user`, `assistant`, `tool`]. The default `SYSTEM_PROMPT` is intentionally sarcastic.
- Config: `legalcodex/_config.py` reads `config.json` (`api_keys.openai`, optional `model`, default `gpt-4.1-mini`). Use `Config.load(path)`; do not access env directly here.

## API-agnostic architecture requirements
- All LegalCodex application logic must remain AI API agnostic.
- Application logic must not rely on provider-specific features from the OpenAI API (or any single provider API).
- All interactions with an LLM must go through the `Engine` abstract base class in `legalcodex/engine.py`.
- `legalcodex/engines/openai_engine.py` provides a concrete implementation of `Engine`.
- This abstraction must be preserved so another LLM API can be adopted later with minimal changes to command and business logic.

## Project Layout

- `legalcodex/' contains the python source-code, organized into:
  - `__main__.py`: CLI entry point, command registry, logging setup.
  - `_cli/`: directory for CLI command implementations.
  - `engine.py`: engine abstraction and OpenAI integration.
  - `_config.py`: config dataclass and JSON loader.

- `tests/` contains automated test files.
- `config.json` is the expected config file for API keys and settings; it is gitignored.
- `pytest.ini` and `mypy.ini` configure testing and type checking.
- `planning` contrains design docs and notes in markdown files, intended to be used by the copilot agent.
- `.work` contains irrelevant files that should be ignored by copilot.



## Developer workflows
- Install/editable: pip install -e .
- Run help: python -m legalcodex --help
- Example run: python -m legalcodex test "Summarize this NDA in 3 bullets."
- Debug logging: add `-v` to enable DEBUG; noisy libs are silenced in `init_log`.
- Tests: pytest with coverage is configured in `pytest.ini`; current suite is minimal (`tests/test_placeholder.py`).
- Type checking: run mypy legalcodex/ (note: `mypy.ini`'s files target appears stale; prefer explicit path).

## Conventions and patterns
- Message roles are constrained by `Role = Literal["system","user","assistant","tool"]`; build messages via `_message(role, content)`.
- Model selection comes exclusively from `Config.model`; there is no CLI override yet.
- The `test` command requires a positional `prompt`; it loads config and prints the first completion.
- Avoid logging secrets; `Config.load` expects keys under `api_keys.openai` in `config.json`.

### Logging
- all files should have a module-level logger (`_logger = logging.getLogger(__name__)`) and use it for all logging.
- all message to the console should be sent to the file's "_logger". print() should not be generally used.
- the DEBUG level should be informative for developers but not overwhelming;
- The INFO level should be relevant to the end-user

### Error handling
Generally, standard exceptions and third-party exceptions (e.g. from OpenAI) should not be allowed to reach the end-user. Instead, they should be caught and re-raised as `LegalCodexError` with a user-friendly message. The original exception should be logged at the DEBUG level for troubleshooting.

## Integration points
- External API: openai Chat Completions via `OpenAI().chat.completions.create(model, messages=...)`.
- Swap engine: create a new subclass of `Engine` with a `run(prompt)->str` and use it in commands instead of `OpenAIEngine`.

## File map (start here)
- legalcodex/__main__.py — CLI bootstrap, logging, command registry
- legalcodex/_cli/cli_cmd.py — command base contract
- legalcodex/_cli/cmd_test.py — reference command using `OpenAIEngine`
- legalcodex/engine.py — engine abstraction, message building, OpenAI call
- legalcodex/_config.py — config dataclass and JSON loader
- pytest.ini, mypy.ini — test/typing config (see notes above)

## Quick examples
- New command skeleton: create `legalcodex/_cli/cmd_myfeature.py` with a `title` and `run`; add to `COMMANDS`.
- Adjust system tone: edit `SYSTEM_PROMPT` in `engine.py` (impacts all calls).

## Copilot skills

- Skill file: `.github/skills/run_tests.md`
- Purpose: run automated tests by invoking `pytest` on the shell and capture output.
- Captured output log: `.github/skills/last_test_output.txt`
- Skill file: `.github/skills/create_cli_command.md`
- Purpose: scaffold a new CLI command (`cmd_<name>.py`) that inherits from `CliCmd` with an empty `run()` method, then register it in `legalcodex/__main__.py`.
