# TODO

Planned features, improvements, and postponed ideas for the SE Site.

## Done

- **CI workflow** — `ci.yml` (current, pip) + `ci-staging.yml` (staging, uv)
- **Pre-commit hooks verified** — ruff, mdformat, dprint, commitlint all pass; code fixed for zero lint issues
- **uv migration** — `pyproject.toml`, `.python-version`, `uv.lock`, `requirements.txt` generated via `uv export`

## Backlog

- **Create CHANGELOG.md** — start with an empty file, add release workflow docs

## Postponed (icebox)

- **Upgrade to Python 3.12+** — evaluate feasibility of upgrading from 3.9
- **Add mypy type checking** — adopt strict typing across the codebase
- **Add code coverage tracking** — introduce pytest-cov with coverage targets
- **Docker optimization** — multi-stage build, smaller base image
- **Windows path support** — verify file path handling on Windows
- **Static site generator** — explore Frozen-Flask alternatives
