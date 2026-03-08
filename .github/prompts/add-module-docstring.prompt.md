# Add Module Docstring Prompt

You are a careful maintenance agent for the LegalCodex Python codebase.

## Task
Add or improve the top-level module docstring in the target Python file.

## Audience
- Experienced software developers familiar with the LegalCodex project.
- They are not familiar with FastAPI or SQL database concepts.

## Inputs
- Target file: $TARGET_FILE
- Optional intent/context from user: $INTENT

## Required Docstring Content
Write a concise module docstring that explains:
1. The high-level purpose of the module.
2. The module's role in the overall LegalCodex architecture.
3. What responsibilities belong in this module vs what is delegated elsewhere.
4. Key integration points (for example route modules, service layer, DB models, mappers), with plain-language explanations of FastAPI/SQL terms when used.

## Writing Constraints
- Keep it concise: typically 4-10 lines.
- Use plain language first; avoid framework jargon where possible.
- If FastAPI terms are needed, explain them briefly in context.
- If SQL/ORM terms are needed, explain them briefly in context.
- Do not change runtime logic.
- Only edit the module docstring unless the user explicitly asks for more.
- Preserve existing style and tone in the file.

## Quality Bar
- Accurate to the actual code in the file.
- Helpful for onboarding someone to this module quickly.
- No vague statements; include concrete purpose and boundaries.

## Output Format
1) Summary
- One short sentence describing what docstring was added/updated.

2) Edit Applied
- File updated
- Final docstring text

3) Notes
- Mention any uncertainty if the file's responsibilities are ambiguous.

## How to Use in Copilot Chat
1. Attach this prompt file.
2. Provide:
   - $TARGET_FILE
   - $INTENT (optional)
3. Ask: Add or update the module docstring using this prompt.
