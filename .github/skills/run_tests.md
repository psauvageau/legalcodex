# Skill: Run Automated Tests

Use this skill to run automated tests and capture the full output from the shell.

## Goal

- Execute the project test suite with `pytest`.
- Capture both stdout and stderr output.
- Return a compact summary plus the captured log.

## Command

Run from repository root.

### PowerShell (Windows)

```powershell
pytest 2>&1 | Tee-Object -FilePath .github/skills/last_test_output.txt
```

### POSIX shells (bash/zsh)

```bash
pytest 2>&1 | tee .github/skills/last_test_output.txt
```

## What to report

- Exit code.
- Pass/fail summary line from `pytest`.
- Path to captured output file:
  - `.github/skills/last_test_output.txt`

## Notes

- Do not alter test files while running this skill.
- If `pytest` is missing, report dependency/setup issue and stop.
