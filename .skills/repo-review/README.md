______________________________________________________________________

## name: repo-review description: Evaluate repository against docs/REPO_REVIEW.md checklist. Load when user says "review repo", "audit repo", "run repo review".

# repo-review

<!-- encoding: utf-8 -->

Evaluates the repository against the comprehensive checklist in `docs/REPO_REVIEW.md` and creates backlog items for gaps found.

## Usage policy

- **Only run on explicit user request** ("review repo", "audit")
- **Or after merge to current/main** to generate backlog when tasks are needed
- **Priority: low** — always skip if higher-priority work is available

## Workflow

1. Read `docs/REPO_REVIEW.md` — load all 10 phases and scoring criteria
1. For each phase, inspect the repository against every checkbox
1. For each unchecked/missing item, add a backlog entry to `TODO.md` under `## Repo Review Backlog`
1. Do NOT commit a score or report file — only update `TODO.md` with actionable items
1. Present a summary: phases checked, gaps found, backlog items created

## Phase-to-agent mapping

| Phase | How agent checks |
|-------|-----------------|
| 1 — Legal & Community | File existence checks: `LICENSE`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `.github/ISSUE_TEMPLATE/`, `SECURITY.md` |
| 2 — Architecture | Inspect `.gitignore`, `.dockerignore`, repo structure (`src/` vs `tests/`), lockfiles |
| 3 — Code quality | Check linter config (`pyproject.toml`, `.editorconfig`), grep for magic numbers, dead code patterns |
| 4 — Testing | Inspect `pytest` config, coverage settings, check for mocking patterns, parametrized tests |
| 5 — Security | Check `SECURITY.md`, pre-commit hooks, input validation patterns, `git log --oneline` for secret leaks |
| 6 — CI | Inspect `.github/workflows/*.yml`: matrix builds, caching, lint gates, artifact retention |
| 7 — CD | Inspect deploy workflows: versioning, changelog, zero-downtime patterns, smoke tests |
| 8 — Community | Check for `CODEOWNERS`, devcontainer config, stale-bot config, issue labels |
| 9 — Observability | Grep for `print` vs logging, `/healthz` endpoints, timeout patterns in network calls |
| 10 — Performance | Manual assessment — flag as "requires human review" |

## Scoring note

Per `docs/REPO_REVIEW.md` §Evaluation Workflow: calculate scores by phase, but do NOT commit the score. Use findings only to drive backlog creation.
