# Skill: Create a New CLI Command

Use this skill to scaffold a new command in `legalcodex/_cli/` and register it in the CLI entrypoint.

## Goal

- Create a new command file in `legalcodex/_cli/`.
- Make the command inherit from `CliCmd`.
- Implement `run()` method.
- Register the command in `legalcodex/__main__.py` so it is available from the CLI.

## Steps

1. Create a file named `legalcodex/_cli/cmd_<name>.py`.
2. Add a command class named `Command<Name>(CliCmd)`.
3. Set `title` to the CLI command name.
4. Implement:

```python
from __future__ import annotations

import argparse
from .cli_cmd import CliCmd


class CommandName(CliCmd):
    title: str = "name"

    def add_arguments(self, parser:argparse.ArgumentParser)->None:
        """
        Add command specific arguments to the parser
        Override this method to add command specific arguments
        """
        pass

    def run(self, args: argparse.Namespace) -> None:
        pass
```

5. Update `legalcodex/__main__.py`:
   - Add `from ._cli import cmd_<name>`
   - Add `cmd_<name>.Command<Name>,` to the `COMMANDS` list

## Verification

- `python -m legalcodex --help` shows the new command.
- `python -m legalcodex <name> --help` resolves successfully.

## Notes

- Keep the command minimal; add arguments later via `add_arguments()`.
- Follow existing style in `cmd_test.py` and `cli_cmd.py`.
