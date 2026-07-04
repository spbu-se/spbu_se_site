# TODO

## Done This Session

- [x] P0: Fix pre-commit exclude patterns (vendor noise)
- [x] P0: Create OPEN_QUESTIONS.md
- [x] P1: Fix 7 test failures — all 56 passing
- [x] P1: Add pytest-cov with 10% threshold
- [x] P2: Add 19 view function tests (30% coverage)
- [x] P2: Add auth + view tests (97 total, CI green)
- [x] P3: Add djlint, bandit, codespell config + hooks
- [x] P4: Fix CI — BOM encoding, temp DB, engine dispose
- [x] **CI (staging) is green** — 97 tests pass (1/5 for retrospective)

## Still Pending

- **Edge case parametrized tests** — fuzz helpers with boundary inputs
- **se_sendmail tests** — notification queue, email formatting
- **Practice tests** — dashboard, new thesis, reports
- **Verify uv caching** in ci-staging.yml
- **Run retrospective after 5 green CI runs** (1/5 done)

## Backlog (next items, one by one)

- **Clean up stale CI workflows** — `linter.yml` (Black vs Ruff), `ci.yml` (duplicates staging), 3 of 9 are stale
- **Raise coverage threshold** — bump from 10% to 25-30% (actual is 30%)
- **Merge staging → current** — 30 commits ahead, CI green, merge and tag
- **Run djlint on 107 templates** — trigger the reformat commit
- **Fix Bandit findings** — `debug=True` on `app.run()`, `requests` without timeout

## Icebox

- Upgrade to Python 3.12+
- Add mypy type checking
- Docker optimization
- Windows path support
- Static site generator improvements
