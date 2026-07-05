# TODO

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
| Thesis admin approval (Whoosh+xdist) | 3 tests, 2 xfailed | Whoosh `EmptyIndexError` | Whoosh index sync with per-test DB |
| Google OAuth full flow | 2 tests pass with patch | Needs `client_google.json` file | Config stub or file-level mock |

## Module Coverage

| Module | Coverage | Status |
|--------|----------|--------|
| `flask_se_config.py`, `bachelor.py`, `scholarships.py`, `summer_schools.py`, `se_forms.py` | 97-100% | Done |
| `se_models.py`, `se_sendmail.py` | 75-92% | Mostly done |
| `flask_se_news.py`, `auth.py`, `admin.py`, `diplomas.py`, `internships.py`, `practice_yandex_disk.py` | 45-60% | Partial |
| `flask_se_review.py`, `theses.py`, `practice_table.py`, `practice.py`, `practice_staff.py`, `practice_admin.py`, `flask_se.py` | 35-50% | Partial |
| **TOTAL** | **59%** | |
