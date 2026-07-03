# TODO

Planned features, improvements, and postponed ideas for the SE Site.

## Done

- **CI workflow** — `ci.yml` (current, pip) + `ci-staging.yml` (staging, uv)
- **Pre-commit hooks verified** — ruff, mdformat, dprint, commitlint all pass; code fixed for zero lint issues
- **uv migration** — `pyproject.toml`, `.python-version`, `uv.lock`, `requirements.txt` generated via `uv export`

## Backlog

- **Create CHANGELOG.md** — start with an empty file, add release workflow docs

### Linters & Formatters (add incrementally)

1. **Add djlint** — Jinja2 template linting for 107 templates
   - Add to pre-commit config + dev group in pyproject.toml
   - Configure `.djlintrc` or pyproject.toml section
   - Run and fix all template issues
2. **Add Bandit** — Python security linter
   - Add to pre-commit config + dev group
   - Configure with `skips` for known false positives
   - Run and fix issues
3. **Add check-json + basic file hygiene hooks**
   - Built-in pre-commit hooks: `check-json`, `end-of-file-fixer`, `trailing-whitespace-fixer`
   - Add to `.pre-commit-config.yaml`
   - Run and fix issues
4. **Add codespell** — typo detection
   - Add to pre-commit config + dev group
   - Configure skip patterns for Russian text / URLs
   - Run and fix issues

## Postponed (icebox)

- **Upgrade to Python 3.12+** — evaluate feasibility of upgrading from 3.9
- **Add mypy type checking** — adopt strict typing across the codebase
- **Add code coverage tracking** — introduce pytest-cov with coverage targets
- **Docker optimization** — multi-stage build, smaller base image
- **Windows path support** — verify file path handling on Windows
- **Static site generator** — explore Frozen-Flask alternatives
