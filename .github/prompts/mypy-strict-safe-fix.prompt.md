
# LegalCodex Mypy Strict Safe-Fix Prompt

You are a careful maintenance agent for the LegalCodex Python codebase.

## Task
1. Run: `mypy --strict legalcodex`
2. Capture the full mypy output.
3. Fix only issues that are safe and do **not** change code logic.
4. Re-run `mypy --strict legalcodex`.
5. Report any remaining errors that cannot be fixed safely.

## Safety Constraints (must follow)
- Do not change business logic, control flow, or public behavior.
- Allowed fixes:
  - type annotations
  - narrowing/typing helpers (`cast`, `TypedDict`, `Protocol`, type aliases)
  - safe refactors for typing clarity only
  - import cleanup needed for typing
  - replacing obviously incorrect type hints with correct ones
- Not allowed without explicit user approval:
  - algorithm changes
  - changing return semantics
  - altering exception handling behavior
  - modifying CLI UX/outputs beyond typing-only necessity
- Keep edits minimal and localized.
- Preserve architecture constraints (engine-agnostic app logic).

## Process
1. Execute `mypy --strict legalcodex` and store the output as **Initial Report**.
2. Group errors by file and root cause.
3. Apply the smallest safe typing-only fixes.
4. Execute `mypy --strict legalcodex` again and store as **Final Report**.
5. Produce a user summary with:
   - what was fixed safely
   - what remains and why it was unsafe to auto-fix

## Output Format (use exactly these sections)
1) Initial Report
- Command run
- Raw mypy output (or concise excerpt if very long, but include totals)

2) Safe Fixes Applied
- File changed
- Error category
- Why fix is logic-preserving

3) Remaining Errors (Unsafe/Needs Decision)
- File + error
- Why not safely auto-fixable
- Suggested manual options (2-3 if applicable)

4) Final Report
- Command run
- Final mypy summary (errors remaining / resolved)

5) Next Decisions Needed
- Explicit questions for user approval where logic change may be required

## How to Use in Copilot Chat
1. Attach this prompt file.
2. Ask: "Run the mypy strict safe-fix prompt."
3. Review the "Remaining Errors" section and approve/reject any non-safe changes.

