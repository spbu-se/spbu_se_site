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

## Backlog (next items, one by one)

- **Clean up stale CI workflows** — `linter.yml` (Black vs Ruff), `ci.yml` (duplicates staging), 3 of 9 are stale
- **Merge staging → current** — 32 commits ahead, CI green, merge and tag

## Batch-ready

### P1: Fix password_recovery 500 on production

| Item | Detail |
|------|--------|
| **What** | `GET /password_recovery.html` returns 500 on both dev and production |
| **Root cause** | Route exists (`flask_se_auth.py:223`) but no template file `src/templates/password_recovery.html` |
| **Design** | Stub page extending `base_light.html` with message: "Функция восстановления пароля временно недоступна" |
| **Pattern** | Follow `src/templates/nooffer.html` — extends base_light, blocks: title, description, content |
| **Test** | `GET /password_recovery.html` → 200 (not 500) |

### P2: Clean stale CI workflows

| Item | Detail |
|------|--------|
| **What** | 8 workflows in `.github/workflows/`, ~3 are stale |
| **Stale candidates** | `linter.yml` (Black vs Ruff — replaced by ruff), `ci.yml` (duplicates ci-staging.yml for staging), `deploy_to_staging.yml` (if auto-deploy disabled), `gh-pages.yml` (if not used) |
| **Approach** | Check each workflow's trigger and content. Remove or disable stale ones. |
| **Verify** | `gh workflow list` shows only active workflows |

### P3: Edge case parametrized tests

| Item | Detail |
|------|--------|
| **What** | Fuzz helper functions with boundary inputs |
| **Functions** | `secure_filename`, `post_ranking_score`, `plural_hours`, `get_thesis_type_id_string`, `allowed_file` |
| **Pattern** | `@pytest.mark.parametrize` with edge cases (None, empty, huge values, Unicode edge cases) |
| **File** | Add to `tests/test_helpers.py` |

## Icebox

- Upgrade to Python 3.12+
- Add mypy type checking
- Docker optimization
- Windows path support
- Static site generator improvements
