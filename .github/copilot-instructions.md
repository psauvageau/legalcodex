# Copilot Instructions for legalcodex

## Big picture
- Python CLI application to talk to LLMs via a pluggable engine abstraction.
- Entry point `legalcodex/__main__.py` wires global flags (`--config`, `--verbose`, `--test`, `--log-window`) and subcommands.
- Current subcommands are `chat` (`legalcodex/_cli/cmd_chat.py`) and `test` (`legalcodex/_cli/cmd_test.py`).
- Data flow: CLI args ➜ `Config.load(...)` ➜ `EngineCommand` builds selected engine via `legalcodex.ai._engine_selector.ENGINES` ➜ command builds `Context` ➜ `Engine.run_messages(context)` ➜ provider API call.
- Why this shape: command code remains small/testable, and AI providers remain swappable behind the `Engine` interface.

## Architecture essentials

### Command-Line-Interface (CLI)
- All command-line interface implementation lives under `legalcodex/_cli/`.
- Commands: subclass `CliCmd` with `title`, implement `run(self, args)` and optional `add_arguments`. Register by adding the class to `COMMANDS` in `__main__.py`.

### LLM Interaction
- All code that interacts with LLMs live under `legalcodex/ai/`.
- All code that interacts with LLMs must go through the `Engine` abstraction (`legalcodex/ai/engine.py`).

- Engine: `legalcodex/ai/engine.py` defines the abstract `Engine` base class (`run_messages(context)`), and concrete engines live under `legalcodex/ai/engines/`.
- Engine selection: `legalcodex/ai/_engine_selector.py` maps engine names to concrete classes (currently `openai` and `mock`).
- Chat state: conversation behavior lives under `legalcodex/ai/chat/` (`chat_behaviour.py`, `chat_context.py`, `chat_summarizer.py`).
- Context/message types: `legalcodex/ai/context.py` and `legalcodex/ai/message.py`.

### General Use

- Config: `legalcodex/_config.py` reads `config.json` (`api_keys`, optional `model`, default from `legalcodex/ai/engines/_models.py`). Use `Config.load(path)`; do not access env directly in command logic.
- Exceptions: all exceptions raised in command logic should be wrapped in `LCException` (or a subclass) with a user-friendly message. Log the original exception at DEBUG level for troubleshooting. LCException should provide an actionable message to the end-user without exposing internal details or stack traces.

## API-agnostic architecture requirements
- All LegalCodex application logic must remain AI API agnostic.
- Application logic must not rely on provider-specific features from the OpenAI API (or any single provider API).
- All interactions with an LLM must go through the `Engine` abstract base class in `legalcodex/ai/engine.py`.
- `legalcodex/ai/engines/openai_engine.py` is a concrete implementation of `Engine`.
- This abstraction must be preserved so another LLM API can be adopted later with minimal changes to command and business logic.

## Project Layout

- `legalcodex/' contains the python source-code, organized into:
  - `__main__.py`: CLI entry point, command registry, logging setup.
  - `_cli/`: CLI command implementations (`cmd_chat.py`, `cmd_test.py`, `engine_cmd.py`).
  - `_config.py`: config dataclass and JSON loader.
  - `ai/`: provider-agnostic AI domain:
    - `engine.py`: abstract engine contract.
    - `_engine_selector.py`: engine registry.
    - `context.py`, `message.py`: context/message primitives.
    - `chat/`: chat behavior and context management.
    - `engines/`: concrete engines (`openai_engine.py`, `mock_engine.py`, `_models.py`).
  - `exceptions.py`: app exceptions (`LCException`, provider/domain-specific subclasses).

- `tests/` contains automated test files.
- `config.json` is the expected config file for API keys and settings; it is gitignored.
- `pytest.ini` and `mypy.ini` configure testing and type checking.
- `planning/` contains design docs and milestone notes in markdown files.
- `.work` contains irrelevant files that should be ignored by copilot.



## Developer workflows
- Install/editable: pip install -e .
- Run help: python -m legalcodex --help
- Example run: python -m legalcodex test "Summarize this NDA in 3 bullets."
- Example run (chat): python -m legalcodex chat
- Example run (chat without loading prior history): python -m legalcodex chat --no-load
- Debug logging: add `-v` to enable DEBUG; noisy libs are silenced in `init_log`.
- Tests: run `pytest` (current suite includes chat behavior/context tests).
- Type checking: run `mypy --strict legalcodex`.

## Conventions and patterns
- Message roles are constrained in `legalcodex/ai/message.py`; contexts passed to engines are `Context` collections of `Message`.
- Model selection is resolved by `Engine` using explicit CLI `--model` override first, then `Config.model`, then engine default.
- Engine selection is done through `--engine` and `ENGINES` mapping.
- `cmd_test` requires positional `prompt`; `cmd_chat` maintains chat history and supports commands (`help`, `history`, `reset`, `exit`/`quit`).
- Avoid logging secrets; API keys are read from `config.json` under `api_keys`.

### Logging
- all files should have a module-level logger (`_logger = logging.getLogger(__name__)`) and use it for all logging.
- all message to the console should be sent to the file's "_logger". print() should not be generally used.
- the DEBUG level should be informative for developers but not overwhelming;
- The INFO level should be relevant to the end-user

### Error handling
Generally, standard exceptions and third-party exceptions (e.g. from OpenAI) should not be allowed to reach the end-user. Instead, catch and re-raise as `LCException` (or a subclass such as `QuotaExceeded`) with a user-friendly message. Log the original exception at DEBUG level for troubleshooting.

## Integration points
- External API: openai Chat Completions via `OpenAI().chat.completions.create(model, messages=...)`.
- Token usage accounting exists in `OpenAIEngine` via `TokenCounter`.
- Swap engine: create a new subclass of `Engine` implementing `run_messages(context)->str`, then register it in `legalcodex/ai/_engine_selector.py`.

## File map (start here)
- legalcodex/__main__.py — CLI bootstrap, logging, command registry
- legalcodex/_cli/cli_cmd.py — command base contract
- legalcodex/_cli/engine_cmd.py — common engine init and shared args (`--engine`, `--model`)
- legalcodex/_cli/cmd_chat.py — interactive chat command
- legalcodex/_cli/cmd_test.py — one-shot prompt command
- legalcodex/_config.py — config dataclass and JSON loader
- legalcodex/ai/engine.py — engine abstraction
- legalcodex/ai/_engine_selector.py — engine registry
- legalcodex/ai/engines/openai_engine.py — OpenAI adapter
- legalcodex/ai/chat/chat_context.py — persisted chat context logic
- pytest.ini, mypy.ini — test/typing config (see notes above)

## Quick examples
- New command skeleton: create `legalcodex/_cli/cmd_myfeature.py` with a `title` and `run`; add to `COMMANDS`.
- New engine skeleton: implement `Engine.run_messages` in `legalcodex/ai/engines/` and add to `ENGINES` in `legalcodex/ai/_engine_selector.py`.
- Adjust chat defaults: update `DEFAULT_SYSTEM_PROMPT` / `DEFAULT_MAX_TURN` in `legalcodex/_cli/cmd_chat.py`.

## Copilot skills

- Skill file: `.github/skills/run_tests.md`
- Purpose: run automated tests by invoking `pytest` on the shell and capture output.
- Captured output log: `.github/skills/last_test_output.txt`
- Skill file: `.github/skills/create_cli_command.md`
- Purpose: scaffold a new CLI command (`cmd_<name>.py`) that inherits from `CliCmd` with an empty `run()` method, then register it in `legalcodex/__main__.py`.
