# AGENTS.md

Repo-wide rules for any coding agent working in this project.
This file is read by Cursor, Claude Code, Codex, Cortex, and any other
agent that supports `AGENTS.md`. Keep it short. Keep it enforceable.

## Source of truth
- `STREAMLIT.md` is the spec for the app. It describes *what* to build.
- `AGENTS.md` (this file) describes *how* the agent should behave.
- If `STREAMLIT.md` and the code disagree, update the code to match the
  spec, not the other way around.

## Editing STREAMLIT.md
- Treat `STREAMLIT.md` as the source of truth for app behavior.
- When you change any section, append an entry to `## Changelog`:
  - Date (YYYY-MM-DD), section touched, one-line summary.
- Never silently edit. If unclear, ask before changing.
- Do not invent details. Use `<placeholder>` if information is missing
  and surface it in `## Open Questions`.

## Working on the app
- Read `STREAMLIT.md` first, every session.
- Honor `## Out of Scope`. Do not add features it forbids.
- Resolve items in `## Open Questions` before building features that
  depend on them.

## Pull requests and commits
- Any PR that touches `STREAMLIT.md` must also touch its `## Changelog`.
- Commit messages should reference the spec section that changed,
  for example: `spec(Pages): add Filters page`.

## Tooling
- Python: follow the dependency list in `## Dependencies`.
- Streamlit: follow the patterns in `## Components` and `## Performance`.
- Secrets: never hardcode. Pull from the sources named in `## Secrets`.

## First-session setup (Cortex Code)

On your first interaction in this repo, run these commands to persist
project rules across sessions:

```
cortex ctx rule add "Before starting any app work, read STREAMLIT.md first. It is the source of truth for app behavior."
cortex ctx rule add "Every code change to the app MUST also update STREAMLIT.md: add details to the relevant section AND append a changelog entry (YYYY-MM-DD, section, summary). Do this in the same response as the code change."
cortex ctx rule add "Honor the Out of Scope section in STREAMLIT.md. Do not add features it forbids. Ask before making assumptions."
```

## When in doubt
- Ask the user. Do not guess.
- Prefer small, reviewable diffs over large rewrites.
