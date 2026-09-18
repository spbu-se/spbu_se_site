# Contributing to SE Site

<!-- encoding: utf-8 -->

Thank you for considering contributing to the SPbSU System Programming Department website.

## Quick start

```bash
git lfs install
git clone <repo-url>
cd spbu_se_site
uv sync
uv run python src/flask_se.py init
uv run python src/flask_se.py
```

The site runs at `http://127.0.0.1:5000`. `init_db` seeds deterministic role
accounts (password `1`) so every permission surface is reachable — see
`docs/ROLE_FEATURE_MATRIX.md`.

## Branching

See `docs/GIT_FLOW.md`. All work branches from `upstream/current`:

- `feat/<name>` for features
- `fix/<name>` for bug fixes
- `docs/<name>` for documentation
- `chore/<name>` for maintenance
- `test/<name>` for test-only work
- `refactor/<name>` for refactors
- `ci/<name>` for CI changes
- `hotfix/<name>` for production hotfixes

Never commit directly to `current`; changes land there only via squash-merged PRs.

## Commit discipline

Use semantic commit messages: `type: short description` (e.g., `feat: add login`,
`docs: update GIT_FLOW.md`). Add a scope when it helps: `fix(audit): ...`,
`test(e2e): ...`, `chore(deps): ...`. Group related changes into atomic commits.
Push a clean commit chain, not WIP history.

## Pull requests

Open a PR against `current`. Follow the existing PR body pattern:

```
## Summary

<one-paragraph description of what this PR does>

## Changes

- <bullet per logical change>

## Verification

- <pre-push gate green>
- <test results>
```

Include `Closes #<n>` / `References #<n>` per issue (one per line).

## Pre-commit / Pre-push

- `uv run pre-commit run --all-files --hook-stage pre-push` before every push
- Pre-push checks, in order: actionlint, `uv lock --check`, mdformat, ruff
  format + lint, pylint similarities, vulture dead-code, gitleaks config drift,
  asset-pipeline guard, basedpyright
- If a hook fails, fix the issue — never `--no-verify`

## Development process

Full workflow: `docs/DEVELOPMENT_PROCESS.md`.
AI tooling conventions: `docs/AI_AGENTS.md`.
