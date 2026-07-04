# TODO

## Done This Session

- [x] Retrospective: GPG dedup, session-start pre-commit, CI parity check, over-engineering guard
- [x] **djlint** — reformatted all 104 templates
- [x] **Bandit** — fixed 8 requests without timeout, suppressed debug=True (dev-only)
- [x] **Coverage threshold** — bumped from 25% to 30%
- [x] **Verify uv caching** in ci-staging.yml — properly configured, no change needed
- [x] **New tests** — 15 route tests for auth, news, theses, diplomas, internships (142 total)

## Still Pending

- **Edge case parametrized tests** — fuzz helpers with boundary inputs
- **se_sendmail tests** — notification queue, email formatting
- **Practice tests** — dashboard, new thesis, reports
- **Blocker: password_recovery.html template missing** — route exists but no template file — `TemplateNotFound`

## Backlog (next items, one by one)

- **Clean up stale CI workflows** — `linter.yml` (Black vs Ruff), `ci.yml` (duplicates staging), 3 of 9 are stale
- **Merge staging → current** — 32 commits ahead, CI green, merge and tag

## Icebox

- Upgrade to Python 3.12+
- Add mypy type checking
- Docker optimization
- Windows path support
- Static site generator improvements
