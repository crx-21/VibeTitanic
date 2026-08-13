# Code review — project rules

Project-specific configuration for the [code-review](../skills/code-review/SKILL.md) skill.
Only deviations from the skill's defaults are listed here. Everything else uses the
built-in behavior.

## Context Gathering

- **Source of truth**: PR title and PR body. No issue tracker / ticket integration is
  configured. Branch names use the `[Type] short description` convention (e.g.
  `[Feature] Add data loader with schema validation`), so the prefix + slug is also
  acceptable as a fallback when the body is empty.

## Build Verification

- **Command**: `pytest -v` (resolved by `pytest.ini` at the project root; runs from
  the repo root with `pythonpath = src`).
- **Python interpreter**: `C:\Users\CrX\AppData\Local\Python\bin\python.exe`
  (the project's actual installed interpreter; the default `python` on PATH
  currently hits the Microsoft Store shim, which doesn't work).

## Coding Conventions

- None beyond the skill defaults. No project-specific style/lint config exists.
- Python >= 3.10 (the project requires 3.10+).
- Prefer the existing `src/` package layout over loose scripts.

## Output Format

- Built-in format. No custom structure.

## Posting Mechanics

- **Stdout / chat only** for now — no open PR review flow is configured.
- When an open PR exists, post the summary as a top-level PR comment (no inline
  comments on specific lines until the team has decided on a comment style).

## Re-review Thread Handling

- Default: **Reply and resolve**. Resolve a thread only after the author pushes
  a fix that verifies the change.

## CI Integration

- **Skipped** for now. Add GitHub Actions integration in a follow-up PR once
  the team has decided on a model and a secret-management policy.
