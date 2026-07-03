# TODO

## Done This Session

- [x] P0: Fix pre-commit exclude patterns (vendor noise)
- [x] P0: Create OPEN_QUESTIONS.md
- [x] P1: Fix 7 test failures — all 56 passing
- [x] P1: Add pytest-cov with 10% threshold
- [x] P2: Add 19 view function tests (30% coverage)
- [x] P3: Add djlint, bandit, codespell config + hooks
- [x] Push staging to trigger CI

## Priority 2: Expand Test Coverage (remaining)

- [ ] **Auth tests** — login/logout with valid credentials, register
- [ ] **News tests** — list, submit (form), vote endpoint
- [ ] **Theses tests** — filter form, download, temp workflow
- [ ] **Internships tests** — index page, filter, detail view
- [ ] **Diploma themes tests** — browse, detail, add form
- [ ] **Practice (student) tests** — dashboard, new thesis, reports
- [ ] **se_sendmail tests** — notification queue, email formatting
- [ ] **Edge case parametrized tests** — fuzz helpers with boundary inputs

## Priority 4: CI & Infrastructure

- [ ] **Verify uv caching** — in ci-staging.yml works
- [ ] **Verify CI is green** — check staging CI status

## Priority 5: Process

- [ ] **Run retrospective after 5 green CI runs**

## Icebox

- Run djlint reformat on 107 templates
- Fix Bandit findings (debug=True, request timeout)
- Upgrade to Python 3.12+
- Add mypy type checking
- Docker optimization
- Windows path support
- Static site generator improvements
