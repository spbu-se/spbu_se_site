# TODO

## Done This Session

- [x] **README rewrite** — badges, quick start, config table, doc links, project structure
- [x] **SPDX headers** — added `SPDX-License-Identifier: Apache-2.0` to all 60 `src/*.py` files
- [x] **readme-generator skill** — licensing rules, cross-platform Python probe, SPDX mapping
- [x] **REVERSE_ENGINEERING.md** — re-engineering cycle for legacy code extraction
- [x] **Process doc updates** — doc-to-code sync, artifact checklist, session start order, gate checks, mid-sprint violation, process docs during code work

## Running Plan

### P0: Speed up tests

Full test suite takes 2.8min. Target: \<1min.

### P1: 100% line coverage

Current: 50%. Target: 100%.

| Module | Est. coverage | Remaining |
|--------|--------------|-----------|
| auth | 30-40% | login flows, OAuth callbacks |
| news | 50% | submit, vote, delete |
| theses | 30% | download, CRUD |
| diplomas | 40% | CRUD, archive |
| internships | 40% | CRUD |
| practice | 10% | staff, admin, student flows |

### P2: Document API surface + requirements

Create `doc/API_SURFACE.md` and `doc/REQUIREMENTS.md`.

### P3: Fix existing staging-auto branches

Chain-merge all `staging-auto-*` branches to green CI, then merge to staging.

### P4: Add mypy type checking

Configure `strict = true` in pyproject.toml, exclude tests, add pre-commit hook, fix initial violations. Use `# type: ignore[code]` only when wire format differs.

### P6: Tooling quick wins

- **`uv lock --check` hook** — add to `.pre-commit-config.yaml` as `repo: local`, `language: system`, `entry: uv lock --check`, `pass_filenames: false`
- **`pytest-xdist`** — add to dev deps, update pytest command to `pytest -n auto` in `pyproject.toml` and `AGENTS.md`
- **`.editorconfig`** — add `[*.{yaml,yml}]`, `[*.json]`, `[*.toml]`, `[Makefile]` sections; set `trim_trailing_whitespace = false` for `[*.md]`

### P7: Ruff rules + test-writer skill

- **Enable `UP`, `SIM`, `RUF100`** ruff rules — add to `pyproject.toml [tool.ruff.lint] select`, fix any violations
- **Update `test-writer` skill** — add SE Site patterns: `seeded_client`, `logged_client`, `assert_ok`, SQLAlchemy `db.session`, `init_db()`, Flask test client conventions

## Icebox

- Upgrade to Python 3.12+
- Docker optimization
- Windows path support
- Static site generator improvements
