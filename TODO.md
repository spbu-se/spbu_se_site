# TODO

Planned features, improvements, and postponed ideas for the SE Site.

## Priority 0: Immediate Fixes

- [ ] **Fix pre-commit exclude patterns** — vendor noise from trailing-whitespace
- [ ] **Run pre-commit --all-files** — verify all hooks pass clean
- [ ] **Create OPEN_QUESTIONS.md** — store unresolved questions

## Priority 1: Fix Existing Tests

- [ ] **Fix 7 test failures** — /index.html 302, plural_hours(24), get_thesis_type_id_string(1), init_db staff lookup
- [ ] **Add pytest-cov** — dev dep + [tool.coverage] config in pyproject.toml
- [ ] **Set coverage target** — add to ci-staging.yml

## Priority 2: Expand Test Coverage

- [ ] **Auth tests** — login, logout, register form
- [ ] **News tests** — list, submit (form), vote endpoint
- [ ] **Theses tests** — search page, filter form, download
- [ ] **Internships tests** — index page, filter, detail view
- [ ] **Diploma themes tests** — browse, detail, add form
- [ ] **Practice (student) tests** — dashboard, new thesis, reports
- [ ] **Summer schools tests** — list page, individual pages
- [ ] **Error handler tests** — 404, bad IDs, missing params
- [ ] **se_sendmail tests** — notification queue, email formatting
- [ ] **Edge case parametrized tests** — fuzz helpers with boundary inputs

## Priority 3: Linters & Formatters

- [ ] **Add djlint** — Jinja2 template linting for 107 templates
- [ ] **Add Bandit** — Python security linter
- [ ] **Add codespell** — typo detection
- [ ] **Add check-json + file hygiene** — already partially done, verify

## Priority 4: CI & Infrastructure

- [ ] **Verify uv caching** — in ci-staging.yml works
- [ ] **Add pytest --cov** — to ci-staging.yml
- [ ] **Add pre-commit gate** — uv run pre-commit run --all-files to ci-staging.yml

## Priority 5: Process (minimal)

- [ ] **OPEN_QUESTIONS.md created**
- [ ] **Retrospective after 5 green CI runs** — run retrospective analysis skill

## Icebox

- Upgrade to Python 3.12+
- Add mypy type checking
- Docker optimization
- Windows path support
- Static site generator improvements
