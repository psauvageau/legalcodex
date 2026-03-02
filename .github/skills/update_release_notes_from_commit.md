````markdown
# Skill: Update Release Notes from a Commit

Use this skill to compare the current codebase against a user-supplied git commit and update `release-notes.md` with the functional changes introduced.

## Goal

- Diff the workspace against a given commit.
- Identify user-facing functionality that was added or changed.
- Append a release note entry following the established format in `release-notes.md`.

## Steps

1. Collect inputs from the user:
   - The commit hash (or ref) to compare against (e.g., `main` or a specific SHA).
   - The target version tag/title for the new release notes section.
   - Whether there are known breaking changes to call out.
2. Inspect changes relative to the commit: `git diff <commit>..HEAD` (include renamed files and stats if helpful) and note functional additions/changes.
3. Draft the new release notes section at the top of `release-notes.md`, matching the existing pattern:
   - `# <version>`
   - `## Overview` — 1-2 sentences summarizing the functional impact.
   - `## Details` — bullet list of notable functional changes (features or behavior changes). Avoid low-level refactors unless user-facing.
   - `## Breaking Changes` — list them; if none, state `- None.`
4. Keep existing sections intact and ordered newest-to-oldest.
5. Save changes (use `apply_patch` for single-file edits).

## Verification

- Confirm the new section matches the established headings and bullet style in `release-notes.md`.
- Ensure the described items align with the actual diff and focus on functionality introduced or changed.
````