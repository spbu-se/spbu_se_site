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

## 2. Coverage Targets

| Scope | Target | Note |
|-------|--------|------|
| Production modules | 90% line coverage | Measured on `src/` excluding one-shot scripts |
| New modules | 50% line coverage | Before first commit to staging |
| Excluded | `thesesImport.py`, `migrations/` | One-shot importers — not exercised in normal operation |

Coverage is checked at staging→current gate. Steps below 90% block the merge.

## 3. Test Execution Strategy

Run the full suite before every push. Parallel-safe at any worker count — per-fixture Whoosh directories eliminate the filesystem race that previously limited workers.

Pre-push mandatory: tests pass, lint clean, format clean.

### 3a. Diagnostic discipline — save time, not screen space

| Rule | Why |
|------|-----|
| **Always `--tb=long`** during development. Only `-q` for final green check. | Full traceback on first run eliminates re-run to get failure details. |
| **Batch before re-run**: Found one failure? Grep for siblings and fix all before re-running. | Each re-run costs the full suite time. One pass fixes everything. |
| **Baseline first**: Unexpected errors? Stash changes, run same command. If errors persist → pre-existing. 5-min timebox. | Saves 10-30 min of false-diagnosis per session. |
| **`-n 1` for debug, `-n auto` for green**: Start with 1 worker to avoid parallel noise. Switch to `-n auto` for the final green check. | Fewer intermittent failures during development. |
| **Start simplest, escalate only when proven insufficient**: Choose the simplest isolation approach first. Test it. Only add complexity if the simple approach fails. | Prevents over-engineering (e.g., RamStorage → per-worker tempdir → per-fixture tempdir when per-fixture was correct from the start). |
| **Sentinel over offset**: Never hardcode line numbers or byte-count offsets to locate code in tests. Formatters shift line counts silently. Use sentinel pattern matching: `next(i for i, l in enumerate(lines) if l.startswith("target"))`. | `lines[589:]` broke when ruff format shifted the file. Sentinels survive formatting changes. |

Reference: `docs/DEVELOPMENT_PROCESS.md` §Project Doctrine Layer 3 — "Save attempts, not screen space."

### 3b. Known pre-existing failures

| Test | Error | Reason | Fixed? |
|------|-------|--------|--------|
| `test_reviewed_with_file` | `TemplateNotFound: notification/thesis_on_review_success.html` | Template file missing from `src/templates/notification/` | No — pre-existing, unrelated to code changes |
| `test_full_review_lifecycle` | `TemplateNotFound: notification/thesis_on_review_success.html` | Same missing template | No — pre-existing |

## 4. xfail Policy

Every xfailed test must have a documented reason linked to a `TODO.md` or `CODE_ISSUES.md` blocker entry. xfails are re-reviewed every 3 months or after refactoring the affected module — whichever comes first.

### Current xfails — permanent

| Test | Reason | Tracking |
|------|--------|----------|
| Google OAuth callback (1) | Requires OAuth session state not present in test | TODO.md Blocked |
| os.rename + Whoosh (3) | `patch("os.rename")` blocks Whoosh filesystem `create_index()` | TODO.md tech debt |
| thesesImport runpy (1) | `runpy.run_module` re-imports without patch | TODO.md tech debt |
| practice delete nonexistent (1) | Real bug: `AttributeError` on nonexistent report_id | TODO.md bug |

### Current xfails — intermittent CI

| Test | Reason | Tracking |
|------|--------|----------|
| theses xdist race (1) | Intermittent — user creation not visible to parallel worker | TODO.md tech debt |
| theses post_with_source_uri (1) | Intermittent CI failure: `assert 500 == 0` | TODO.md tech debt |
| theses post_with_presentation (1) | Intermittent CI failure: `assert 500 == 0` | TODO.md tech debt |
| theses bad authors (1) | Intermittent CI failure: `assert 500 == 0` | TODO.md tech debt |
| theses bad type (1) | Intermittent CI failure: `assert 500 == 0` | TODO.md tech debt |
| theses bad annotation (1) | Intermittent CI failure: `assert 500 == 0` | TODO.md tech debt |

**Previously fixed this session**: PyMuPDF dummy PDF (5), Google OAuth login redirect (1), practice_admin file I/O races (3), practice_staff auth race (1), theses xdist race (1 — `test_post_bad_type_id`), thesesImport module state (22). Total: 33 xfails removed.

### 4a. Intermittent CI failures — xfail strategy

Tests that pass locally but fail intermittently on CI:

- Use `strict=False` — a passing run does not count as failure.
- Reason format: `"Intermittent CI failure: <brief symptom description>"`
- Track in `TODO.md` tech debt with note linking to the test.
- Reviewed every 3 months per the general xfail policy. If a test fails on >50% of CI runs across 2 consecutive review cycles, escalate from xfail to fix.

Do NOT use `strict=False` for failures that reproduce locally — those are real bugs and must follow the zero-bug policy.

## 5. Xpassed Tests

0 xpassed tests remaining. All previously xpassed tests were investigated and fixed in session 6.

## 6. Long-Term Testing Gaps

Architectural issues that limit test coverage and require production code changes to resolve:

- **thesesImport module-level side effects**: `db.init_app(app)` at import time forces import-time monkeypatching in conftest, which breaks xdist isolation. Module-level `download` flag and direct `sys.exit()` calls also leak state between tests. Fix: refactor into a callable function with dependency injection. **Status**: mitigated — `try/except RuntimeError` guard in source + per-fixture Whoosh dirs, 22 stale xfails removed.
- **Whoosh index threading**: Whoosh indexes are not thread-safe, limiting xdist to 2 workers. Tests that create new DB rows and immediately query Whoosh are inherently racy. **Status**: resolved — per-fixture WHOOSHEE_DIR tempdirs eliminate the filesystem race. `-n auto` safe.
- **OAuth external dependencies**: Full-flow VK and Google OAuth tests require external config files and network access. CI tests use mock stubs — real OAuth flow is only tested manually.
- **Practice file upload branches**: Cyclomatic complexity in practice route handlers leaves ~30 untested code branches in file upload logic. Adding tests requires multipart fixture infrastructure.
- **Notification templates missing** (2): `notification/thesis_on_review_success.html` does not exist. `test_reviewed_with_file` and `test_full_review_lifecycle` fail with `TemplateNotFound`. Pre-existing, unrelated to code changes.

## 7. Deliberate Exclusions

What we explicitly do not test and why:

| Area | Why Not Tested | Validated By |
|------|----------------|--------------|
| Static site generation (Frozen-Flask) output | Build success is sufficient — output correctness is structural | Manual build check |
| Email delivery | SMTP is production-only, mocked in all tests | Production monitoring |
| Password security (scrypt) | Python 3.13 OpenSSL build lacks scrypt — mocked in all tests | Prod environment has different OpenSSL |
| UI/visual rendering | No browser testing framework configured | Manual review per release |
