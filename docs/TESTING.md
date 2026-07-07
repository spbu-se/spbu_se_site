# Testing

<!-- encoding: utf-8 -->

Testing strategy, coverage targets, xfail policy, and known gaps for the SE Site project.

Covers: testing discipline, execution strategy, xfail policy, long-term gaps, deliberate exclusions. Does not cover: fixture implementation patterns — see `docs/TOOLING.md`, test-writing methodology — see `.skills/test-writer/`, reusable fixture templates — see `.skills/flask-test-patterns/`, individual bug details — see `docs/CODE_ISSUES.md`.

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

Run the full suite before every push. Stable parallel count is 2 workers — above that causes Whoosh index races.

Pre-push mandatory: tests pass, lint clean, format clean.

## 4. xfail Policy

Every xfailed test must have a documented reason linked to a `TODO.md` or `CODE_ISSUES.md` blocker entry. xfails are re-reviewed every 3 months or after refactoring the affected module — whichever comes first.

### Current xfails

| Test | Reason | Tracking |
|------|--------|----------|
| Whoosh-related tests (3) | `EmptyIndexError` in xdist — Whoosh index not thread-safe | TODO.md Blocked |
| Google OAuth full flow (2) | Requires `client_google.json` config file not in CI | TODO.md Blocked |
| thesesImport module state tests (23) | Module-level `db.init_app(app)` + mutable flags break isolation | Unfixable without production refactor |

## 5. Long-Term Testing Gaps

Architectural issues that limit test coverage and require production code changes to resolve:

- **thesesImport module-level side effects**: `db.init_app(app)` at import time forces import-time monkeypatching in conftest, which breaks xdist isolation. Module-level `download` flag and direct `sys.exit()` calls also leak state between tests. Fix: refactor into a callable function with dependency injection.
- **Whoosh index threading**: Whoosh indexes are not thread-safe, limiting xdist to 2 workers. Tests that create new DB rows and immediately query Whoosh are inherently racy.
- **OAuth external dependencies**: Full-flow VK and Google OAuth tests require external config files and network access. CI tests use mock stubs — real OAuth flow is only tested manually.
- **Practice file upload branches**: Cyclomatic complexity in practice route handlers leaves ~30 untested code branches in file upload logic. Adding tests requires multipart fixture infrastructure.

## 6. Deliberate Exclusions

What we explicitly do not test and why:

| Area | Why Not Tested | Validated By |
|------|----------------|--------------|
| Static site generation (Frozen-Flask) output | Build success is sufficient — output correctness is structural | Manual build check |
| Email delivery | SMTP is production-only, mocked in all tests | Production monitoring |
| Password security (scrypt) | Python 3.13 OpenSSL build lacks scrypt — mocked in all tests | Prod environment has different OpenSSL |
| UI/visual rendering | No browser testing framework configured | Manual review per release |
