# Testing

<!-- encoding: utf-8 -->

Testing strategy, coverage targets, xfail policy, and known gaps for the SE Site project. Part of quality management — see `docs/QUALITY_MANAGEMENT.md` for philosophy and policy.

Covers: testing discipline, execution strategy, xfail policy, long-term gaps, deliberate exclusions. Does not cover: fixture implementation patterns — see `docs/TOOLING.md`, test-writing methodology and reusable fixture templates — see `docs/AI_AGENTS.md` §Skills, individual bug details — see `docs/CODE_ISSUES.md`, quality philosophy — see `docs/QUALITY_MANAGEMENT.md`.

## 1. Testing Discipline

### TDD-First

Write tests from specs before implementation. Tests drive the code, not the other way around.

### Zero Bugs Policy

Any bug found during development blocks all feature work until fixed. A bug is any behavior that deviates from documented specs.

### Edge Case Audit

Every test batch must consider and test:

- Empty/null inputs
- Boundary values (0, max length, edge years)
- Corrupt or malformed data
- Failure modes (DB down, file missing, permission denied)

Where edge cases emerge during testing, improve process documentation: what was missed and how to catch it next time.

### Shared fixtures live in conftest

When several test modules need the same setup (a role, a theme row, an entity), define the fixture **once** in `tests/conftest.py` and request it per module. Duplicating a fixture across files trips the CI pylint-similarities check (R0801; run `uv run pylint --disable=all --enable=similarities src/ tests/`) — hit 2026-09-06 with three copies of `make_theme` in the #70 test files (#280).

## 2. Coverage Targets

| Scope | Target | Note |
|-------|--------|------|
| Production modules | 90% line coverage | Measured on `src/` excluding one-shot scripts |
| New modules | 50% line coverage | Before first commit to staging |
| Excluded | `wsgi.py`, `extract_text.py` | One-shot importers/entrypoints — not exercised in normal operation |

Coverage is checked at staging→current gate. Steps below 90% block the merge.

## 3. Test Execution Strategy

Run the full suite before every push. Parallel-safe at any worker count — the FTS5 index lives inside the session-seeded SQLite DB template, so per-test copies are race-free.

Pre-push mandatory: tests pass, lint clean, format clean.

### 3a. Diagnostic discipline — save time, not screen space

| Rule | Why |
|------|-----|
| **Never `-q`; always `--tb=long`** | `-q` hides exactly the failure context a run exists to surface. Full traceback on first run eliminates re-run to get failure details. |
| **Every run writes a log; never truncate output** | Capture every pytest/tool run to `.tmp/<run>.log` (`2>&1 | tee .tmp/<run>.log`). `Select-Object -Last/-First`, `head`/`tail`, or `| Select-String "FAIL"` filter out failure context and counts — search the captured file with `rg`/grep instead. |
| **Batch before re-run**: Found one failure? Grep for siblings and fix all before re-running. | Each re-run costs the full suite time. One pass fixes everything. |
| **Baseline first**: Unexpected errors? Stash changes, run same command. If errors persist → pre-existing. 5-min timebox. | Saves 10-30 min of false-diagnosis per session. |
| **`-n 1` for debug, `-n auto` for green**: Start with 1 worker to avoid parallel noise. Switch to `-n auto` for the final green check. | Fewer intermittent failures during development. |
| **Start simplest, escalate only when proven insufficient**: Choose the simplest isolation approach first. Test it. Only add complexity if the simple approach fails. | Prevents over-engineering (e.g., RamStorage → per-worker tempdir → per-fixture tempdir when per-fixture was correct from the start). |
| **Sentinel over offset**: Never hardcode line numbers or byte-count offsets to locate code in tests. Formatters shift line counts silently. Use sentinel pattern matching: `next(i for i, l in enumerate(lines) if l.startswith("target"))`. | `lines[589:]` broke when ruff format shifted the file. Sentinels survive formatting changes. |

Reference: `docs/DEVELOPMENT_PROCESS.md` §Project Doctrine Layer 3 — "Save attempts, not screen space."

### 3b. CI-cost review — reason before you buy CI time

CI time is a shared, queue-blocking budget. A change that materially increases
it must carry its reasoning and a "good enough" compromise before merge.
Trigger (any):

- a new always-on CI job, or
- roughly doubling a job's median runtime, or
- adding ≳2 min to a job's median runtime.

When triggered: state the added cost, the coverage gained, and the cheapest
compromise that keeps the signal (budget cap on cases, path filter so
irrelevant PRs skip the job, cache of heavy setup like Playwright browsers,
reduced scope with full coverage local-only). Worked example — the `e2e`
browser suite: 3 journeys, path-filtered job, Playwright browser cache.

### 3c. e2e live-browser suite (top-level `e2e/`)

Real-server browser journeys over the seeded deterministic environment
(`se_seed_data` accounts, password `1`; no test mocks — real werkzeug hashing,
CSRF, rate limiters). `e2e/conftest.py` builds a fresh seeded DB under `.tmp`
and serves the real `app` through werkzeug on an ephemeral port; Playwright
Chromium drives 2-3 canonical journeys (auth gate redirect, seed-admin login +
admin surface, self-registration). Excluded from the default suite
(`testpaths = ["tests"]`, `e2e` marker) — run explicitly:

```console
uv run pytest e2e -m e2e --no-cov -n 0
```

Runs on CI only in the path-filtered `e2e` job (`ci.yml`), never in the
`test`/serviceability jobs.

## 4. xfail Policy

Every xfailed test must have a documented reason linked to a `TODO.md` or `CODE_ISSUES.md` blocker entry. xfails are re-reviewed every 3 months or after refactoring the affected module — whichever comes first.

### Current xfails — permanent (strict=False)

| Test | Count | Reason | Tracking |
|------|-------|--------|----------|
| Google OAuth callback | 1 | Requires OAuth session state not present in test | TODO.md Blocked |

### Current xfails — intermittent CI (strict=False)

None — the `post_theses` cluster (shared `static/tmp` same-name upload race between xdist workers) is fixed via a per-worker isolated `THESIS_UPLOAD_ROOT` (2026-08-15).

### Current xfails — strict=True (must stay failing; xpass = suite error)

| Test | Count | Reason | Tracking |
|------|-------|--------|----------|
| admin staff create/edit views | 2 | `test_admin_create_views_load[staff]`, `test_admin_edit_views_load[staff]` | CODE_ISSUES.md — reason text still cites Flask-Admin (stale); verify after next admin refactor |

Reference run (2026-08-17, `pytest --tb=no -q -rxX`): **1351 passed, 4 skipped, 3 xfailed, 1 xpassed**. The intermittent-marker count drifts between runs (flaky XPASS whenever the path passes); re-verify drift is stability, not flakiness, before touching any marker.

Reference run (2026-08-19, `pytest --tb=no -q -rxX`): **1354 passed, 4 skipped, 3 xfailed, 1 xpassed** — dual-provider maps added 3 rendered-page tests.

Reference run (2026-08-20, `pytest --tb=no -q -rxX`): **1388 passed, 4 skipped, 3 xfailed, 1 xpassed** — compliance-followups added `TestUserExport` (3: zip contents, password_hash exclusion, owned posts) + `/profile/export.zip` login-required route (1).

Reference run (2026-08-20, `pytest --tb=no -q -rxX`): **1364 passed, 4 skipped, 3 xfailed, 1 xpassed** — GTM removal + dormant Metrica added 10 guardrail tests (`tests/test_analytics.py`).

Reference run (2026-08-20, `pytest --tb=no -q -rxX`): **1363 passed, 4 skipped, 3 xfailed, 1 xpassed** — Frozen-Flask purged (removed `test_main_build_dispatch`, the freezer's only test).

Reference run (2026-08-20, `pytest --tb=no -q -rxX`): **1376 passed, 4 skipped, 3 xfailed, 1 xpassed** — consent gate shipped: `tests/test_consent.py` (10), `tests/test_analytics.py` +3 (no-consent/declined metrica cases); `test_maps_lazy` key-block assertion made multiline-tolerant.

Reference run (2026-08-20, `pytest --tb=no -q -rxX`): **1384 passed, 4 skipped, 3 xfailed, 1 xpassed** — security headers shipped: `tests/test_security_headers.py` (8) covering CSP allowlist, header presence on pages/assets/404, the `SE_COOKIE_SECURE` HSTS/upgrade gate, and omitted CORP.

Reference run (2026-08-21, `pytest --tb=no -q -rxX`): **1394 passed, 4 skipped, 3 xfailed, 1 xpassed** — account deletion shipped: `tests/test_auth_views.py::TestUserDelete` (6: login-required, POST-only, anonymization, content retention, logout, relogin-block).

Reference run (2026-08-21, `pytest --tb=no -q -rxX`): **1402 passed, 4 skipped, 3 xfailed, 1 xpassed** — Alembic removed, self-healing `ensure_schema()` shipped: `tests/test_migrations.py::TestSchemaDeltas` (8: fresh-DB init, backup+repair, server_default NOT NULL, synthesized constant defaults, exotic-nullable warning, fail-loud UNIQUE, idempotency, FTS5 index creation).

Reference run (2026-09-10, `uv run pytest --tb=long`): **1515 passed, 4 skipped, 1 xpassed** (1520 collected) — registration hardening (`#314`: strict name/e-mail validation + config-gated SmartCaptcha) and notification UX (`#315`: shared `_flash.html`, dismissible/auto-hide feedback).

## 5. Xpassed Tests

Tests that pass locally but have `xfail` markers (all `strict=False`, so xpass is non-fatal): intermittent CI failures that happen to pass on this machine. Tracked in the §4 "Current xfails — intermittent CI (strict=False)" table. Check xpass count by capturing the run to a log (`uv run pytest --tb=long 2>&1 | tee .tmp/xpass.log`) and searching the log for `xpassed`.

## 5b. Role-journey suite (`tests/test_role_journeys.py`)

Cross-cutting HTTP journeys over the seeded deterministic environment
(`src/se_seed_data.py`, accounts in `docs/ROLE_FEATURE_MATRIX.md`): real POST
login as every seeded account (password `1`), password recovery end-to-end via
the local `.eml` mail capture (`SE_MAIL_DEV_DIR`), and self-registration. They
complement the per-module deep suites by exercising the auth lifecycle against
the actual seed — run with the default suite, coverage-included. Password
*verification* against the real hash (the in-process `check_password_hash`
mock always returns true) lives in a subprocess test, and the live browser
suites (top-level `e2e/`) cover the unmocked path.

## 6. Long-Term Testing Gaps

Architectural issues that limit test coverage and require production code changes to resolve:

- **thesis import module-level side effects** — **resolved 2026-08-22**: the legacy `thesesImport.py` (import-time `db.init_app`, module-level `download` flag, direct `sys.exit()`) was replaced by `thesis_import.py`, which is import-safe (no side effects), validates records, and collects per-record errors instead of exiting. Covered by `tests/test_thesis_import.py`.
- **FTS5 index inside SQLite — no separate index management needed**
- **OAuth external dependencies**: Full-flow VK and Google OAuth tests require external config files and network access. CI tests use mock stubs — real OAuth flow is only tested manually.
- **Practice file upload branches**: Cyclomatic complexity in practice route handlers leaves ~30 untested code branches in file upload logic. Adding tests requires multipart fixture infrastructure.

## 7. Deliberate Exclusions

What we explicitly do not test and why:

| Area | Why Not Tested | Validated By |
|------|----------------|--------------|
| Static site generation (Frozen-Flask) output | Build success is sufficient — output correctness is structural | Manual build check |
| Email delivery | SMTP is production-only, mocked in all tests | Production monitoring |
| Password security (scrypt) | Python 3.13 OpenSSL build lacks scrypt — mocked in all tests | Prod environment has different OpenSSL |
| UI/visual rendering | No browser testing framework configured | Manual review per release |

## 8. Troubleshooting — Common Test Errors

### APScheduler: background jobs fire during tests

**When:** Running pytest — `SendMailNotification` fires every 10s against the test DB.
**Cause:** `BackgroundScheduler` started at import time. Background jobs see the test DB with no tables.
**Fix:** Since the application-factory refactor, `tests/conftest.py` sets `SE_START_SCHEDULER=0` before importing `flask_se`, so jobs are registered but never started. Do not remove that env var.

### init_db: crashes on second call

**When:** Calling `init_db()` twice in the same test.
**Cause:** `init_db()` runs `db.session.commit()` before `db.drop_all()`. If the session has expired objects from the first call, the flush crashes.
**Fix:** Call `db.session.remove()` before the second `init_db()` call.

### VK/Google OAuth: import crashes with missing deps

**When:** Importing `flask_se_auth` without all OAuth dependencies installed.
**Cause:** OAuth libraries are imported at module level. `vk_api` or `google_auth_oauthlib` failures propagate up.
**Fix:** Ensure all OAuth deps are in `pyproject.toml`. During testing, the monkeypatch in `conftest.py` must happen before any `from flask_se import` line.

### SQLite: "attempt to write a readonly database"

**When:** CI (Linux) test fixtures try to `CREATE TABLE`.
**Cause:** `tempfile.NamedTemporaryFile` keeps the fd open — SQLAlchemy engine can't write.
**Fix:** Use `tempfile.mkdtemp()` instead; let SQLAlchemy create the `.db` file.

### SQLite: "no such table: notification"

**When:** APScheduler fires `SendMailNotification` during tests.
**Cause:** Scheduler started during app init; runs on the test's temp DB which has no tables yet.
**Fix:** The factory's `SE_START_SCHEDULER=0` gate (set in `tests/conftest.py`) prevents this. Ensure conftest still sets it before importing `flask_se`.

### Password hashing: "unsupported hash type scrypt"

**When:** `check_password_hash` on Python 3.13.
**Cause:** OpenSSL build of Python 3.13 doesn't include scrypt support.
**Fix:** Skip password-verification tests, or use a different hash algorithm in dev config.
