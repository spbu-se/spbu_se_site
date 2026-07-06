# TODO

<!-- encoding: utf-8 -->

## Batch run 2026-07-06 — session 2

- Fixed CI red: mdformat + pre-commit hook paths synced to CI (.skills/ .claude/ .agents/)
- Documented 6 undocumented knowledge gaps from prior session
- Added stale auto-branch sweep rule to unattended-mode skill
- Modeled practice_preparation() (28 tests, all POST branches)
- Modeled post_theses() (6 new tests, supervisor/staff/optional files)
- Modeled init_db() edge cases (9 new tests: idempotency, exact counts)
- 43 new tests, 1065 total, 0 failures
- CI Basic checks green on auto-branch

## Batch run 2026-07-06 — completed

- Modeled 4 previously untested modules (se_forms, se_review_forms, bachelor, thesesImport)
- 163 new tests, 1030 total, 0 failures
- CI green on staging-auto-\*
- Pre-flight checklist added to AGENTS.md
- Staging green rule §4.4 added to GIT_FLOW.md
- .tmp/ added to .gitignore for temporary files

## Planned

| Priority | Task | Effort | Depends on |
|----------|------|--------|------------|
| **P0** | Fix `None.strip()` crashes in `flask_se_auth.py:197,239-242`, `flask_se_review.py` | S | none |
| **P0** | Fix `read_table()` FileNotFoundError in `flask_se_practice_table.py` | S | none |
| **P0** | Test optimization — reduce SLOC, deduplicate parametrized lists, consolidate test files | M | Now |
| **P1** | Push coverage 59% → 90% (~200 tests across practice/review/theses) | XL | After test optimization |
| **P2** | Fix custom `__init__` kwargs in `se_models.py` (CurrentThesis, ThesisTask, ThesisReport) | S | After coverage |
| **P3** | Mypy strict for `src/` (~20 files, per-module overrides) | L | After code fixes |
| **P3** | Fix `AdminModelView(db.session)` → `db` deprecation | S | After coverage |
| **P3** | Fix `Users.query.get()` → `db.session.get()` deprecation | S | After coverage |
| **P4** | Test optimization (reduce SLOC, deduplicate parametrized lists) | M | After mypy |
| **P5** | Python 3.12+, Docker, static site, open source docs | M-S | Icebox |

## Blocked (with evidence)

| Task | Attempts | Result | What's needed |
|------|----------|--------|---------------|
| Practice deeper upload branches | 6 tests | ~30 branches remain | ~50 multipart fixture tests |
| Review full workflow | 14 tests (ThesisOnReview) | Multi-request state untestable | ~30 sequenced request tests |
| Practice admin file upload (xdist race) | 6 tests xfailed | File I/O race in xdist parallel workers — concurrent file creation corrupts test state | Isolate practice admin tests from xdist or use lock-based file fixtures |
| Thesis admin approval (Whoosh+xdist) | 3 tests, 2 xfailed | Whoosh `EmptyIndexError` | Whoosh index sync with per-test DB |
| Google OAuth full flow | 2 tests pass with patch | Needs `client_google.json` file | Config stub or file-level mock |

## Module Coverage

| Module | Coverage | Status |
|--------|----------|--------|
| `se_forms.py`, `se_review_forms.py`, `flask_se_bachelor.py` | 100% | Done (new) |
| `flask_se_config.py`, `scholarships.py`, `summer_schools.py` | 97-100% | Done |
| `se_models.py`, `se_sendmail.py` | 75-92% | Mostly done |
| `flask_se_news.py`, `auth.py`, `admin.py`, `diplomas.py`, `internships.py`, `practice_yandex_disk.py` | 45-60% | Partial |
| `flask_se_review.py`, `theses.py`, `practice_table.py`, `practice.py`, `practice_staff.py`, `practice_admin.py`, `flask_se.py` | 35-50% | Partial |
| `thesesImport.py` | ~2% (28 tests, 23 xfail—module interaction) | Modeled, needs isolation |
| **TOTAL** | **38%** (full suite adds test-only modules) | |

## Known bugs found in batch run

| Bug | Module | Impact |
|-----|--------|--------|
| `base_url + None` crashes when table has no `<a>` links | `thesesImport.py` (get_2019_371 etc.) | Scrape crashes on empty cells |
| `supervisor.split()[-3]` IndexError on short names | `thesesImport.py` (get_2022_271) | Scrape crashes on 1-2 word names |
| Wrong column index: checks cols[4] but uses cols[5] | `thesesImport.py` (get_2022_09_03_04) | Wrong file URL extracted |
| Hardcoded `2019` in filename despite being `2022` | `thesesImport.py` (get_2022_09_03_04) | Wrong year in download filename |
| `db.init_app(app)` at module level — blocks import after conftest | `thesesImport.py` | Requires import-time patching |
