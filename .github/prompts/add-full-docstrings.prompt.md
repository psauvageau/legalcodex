# Add Full Docstrings Prompt

You are a careful maintenance agent for the LegalCodex Python codebase.

## Task
Add or improve docstrings for each class, method, and function in the target Python file.

## Audience
- Experienced software developers familiar with the LegalCodex project.
- They are not familiar with FastAPI or SQL database concepts.

## Inputs
- Target file: $TARGET_FILE
- Optional intent/context from user: $INTENT

## Required Docstring Coverage
Ensure all of the following are documented in the target file:
1. Module-level functions.
2. Classes.
3. Public methods.
4. Non-trivial private/internal methods that benefit maintainability.

## Required Docstring Content
For each documented object, write concise docstrings that explain:
1. High-level purpose and responsibility.
2. Where the object fits in the LegalCodex architecture.
3. Boundaries: what this object does vs what is delegated elsewhere.
4. Parameters/returns only when useful for understanding behavior.

## Writing Constraints
- Keep each docstring concise and practical.
- Prioritize plain language over framework jargon.
- If FastAPI terms are needed, explain them in one short phrase.
- If SQL/ORM terms are needed, explain them in one short phrase.
- Do not change runtime logic.
- Avoid rewriting unrelated code.
- Preserve existing style and tone in the file.
- Avoid repetitive boilerplate across docstrings.

## Quality Bar
- Accurate to the actual implementation.
- Focused on purpose and architectural role, not line-by-line mechanics.
- Useful for quick onboarding and maintenance.

## Output Format
1) Summary
- One short sentence describing the docstring pass.

2) Edit Applied
- File updated
- Coverage report (which classes/functions/methods received docstrings)

3) Notes
- Mention any ambiguity where intent could not be inferred confidently.

## How to Use in Copilot Chat
1. Attach this prompt file.
2. Provide:
   - $TARGET_FILE
   - $INTENT (optional)
3. Ask: Add or improve docstrings for all classes, methods, and functions in the target file using this prompt.
