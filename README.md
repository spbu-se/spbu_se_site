# SE Site — SPbSU System Programming Department

<!-- encoding: utf-8 -->

[![CI](https://github.com/spbu-se/spbu_se_site/actions/workflows/ci.yml/badge.svg)](https://github.com/spbu-se/spbu_se_site/actions)
[![Python](https://img.shields.io/badge/python-3.13-blue)](.python-version)
[![License](https://img.shields.io/badge/license-Apache%202.0-green)](LICENSE)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

Сайт кафедры системного программирования Математико-механического факультета СПбГУ.

Веб-сайт для публикации информации о кафедре: новости, дипломные темы, практики, отзывы, информация для абитуриентов и студентов.

## Prerequisites

- Python 3.9+ (production via pip), 3.13 (development via uv)
- SQLite (zero-config)
- uv (for development)
- git-lfs (materializes LFS-tracked binaries, see Setup below)

## Setup

```bash
# Once per machine: configure Git LFS (smudge/filter drivers)
git lfs install

git clone <repo-url>
cd spbu_se_site

# Production
pip install -r requirements.txt
python src/flask_se.py init
python src/flask_se.py

# Development
uv sync
uv run python src/flask_se.py init
uv run python src/flask_se.py
```

LFS-tracked files (`src/static/thesis/**`, `src/static/files/**`) materialize
automatically on clone/checkout via the `git lfs install` filter. If you
cloned before enabling LFS, run `git lfs pull` once to fetch them.

The site runs at `http://127.0.0.1:5000`.

## Configuration

Create these files in `src/configs/` (never committed; `*.conf.example` templates are committed):

| File | Purpose |
|------|---------|
| `flask_se_secret.conf` | Session signing secret key |
| `flask_se_mail.conf` | SMTP settings for email notifications |
| `flask_se_practice_yandex_secret.conf` | Yandex OAuth for practice file storage |
| `flask_se_vk_secret.conf` | VK OAuth client secret |
| `flask_se_thesis.conf` | Thesis upload API key (`SECRET_KEY_THESIS`) |

## Local prod-like run

`init_db` seeds deterministic role accounts (`src/se_seed_data.py`) so every
permission surface is reachable by logging in as one of them — password `1`:

`user@se.dev` (role 0), `thesis@se.dev` (role 2), `review@se.dev` (role 3),
`staff@se.dev` (staff), `admin@se.dev` (role 5). Surface map + flows:
`docs/ROLE_FEATURE_MATRIX.md`.

Optional dev-only env toggles (never set in prod): `SE_MAIL_DEV_DIR=.tmp/mail`
captures mail as `.eml` files instead of SMTP (recovery-link flows work
locally), `SE_SECRET_KEY=<value>` pins the session key across restarts,
`SE_DISABLE_RATE_LIMITS=1` lifts login/register throttling.

## Commands

| Command | Description |
|---------|-------------|
| `uv run python src/flask_se.py` | Run development server |
| `uv run python src/flask_se.py init` | Initialize database |
| `uv run python src/wsgi.py` | Run via WSGI (production) |
| `uv run pytest` | Run tests |
| `uv run ruff check src/ tests/` | Lint |
| `uv run ruff format src/ tests/` | Format |
| `uv run mdformat docs/ AGENTS.md CLAUDE.md README.md TODO.md .skills/ .opencode/commands/ .claude/ .agents/` | Format markdown (explicit paths — never `mdformat .`) |

## Deployment

The project includes Docker configuration:

- `Dockerfile` — uWSGI-based Flask container
- `docker-compose.yml` — Flask + nginx

Production uses `current` branch with uWSGI behind nginx.

### Docker quickstart

```bash
docker compose up --build
```

The entrypoint (`docker/entrypoint.sh`) initializes the SQLite database
automatically on first boot, so no manual `cp`/`init` step is needed.

## Релизы

Релизы помечаются тегами вида `vYYYY.MM.DD` (например, `v2025.09.09`). Публикация релиза:

1. Тег `vYYYY.MM.DD` (GPG-подписанный) пушится в канонический репозиторий.
1. CI (`deploy_to_production.yml`) автоматически разворачивает сайт в production
   и создаёт **черновик** релиза с заметками, сгенерированными по PR с момента
   предыдущего релиза.
1. Сопровождающий проверяет и публикует черновик вручную — автопубликации нет.

Ссылка на все релизы: https://github.com/spbu-se/spbu_se_site/releases

## Project structure

```
se-site/
├── src/                    # Application code (30 .py files)
│   ├── flask_se.py         # Application factory + route orchestration
│   ├── flask_se_scheduler.py  # APScheduler jobs
│   ├── flask_se_static.py  # Public static pages + legacy redirects
│   ├── sitemap.py          # Sitemap index + per-year theses sub-sitemaps
│   ├── flask_se_admin.py   # Admin panel views (custom CRUD)
│   ├── flask_se_auth.py    # Authentication (email, VK, Google)
│   ├── flask_se_config.py  # App configuration
│   ├── flask_se_diplomas.py# Diploma themes
│   ├── flask_se_news.py    # News posts
│   ├── flask_se_practice.py# Student practice workflows
│   ├── flask_se_review.py  # Thesis review system
│   ├── flask_se_theses.py  # Thesis search and management
│   ├── se_models.py        # SQLAlchemy models
│   └── templates/          # Jinja2 templates (114 files)
├── tests/                  # Comprehensive test suite
├── docs/                    # Process and architecture documentation
├── .github/workflows/      # CI/CD pipelines
└── docker-compose.yml      # Production deployment
```

## Documentation

| File | Purpose |
|------|---------|
| [docs/AI_AGENTS.md](docs/AI_AGENTS.md) | AI tooling config, output format conventions |
| [docs/AI_AGENT_EXPERIENCE.md](docs/AI_AGENT_EXPERIENCE.md) | Agent-collected debugging trails and dead ends |
| [docs/API_REFERENCE.md](docs/API_REFERENCE.md) | API endpoint reference |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Module design and data flow |
| [docs/BUSINESS_FEATURES.md](docs/BUSINESS_FEATURES.md) | User-facing workflow map and business value |
| [docs/CODE_ISSUES.md](docs/CODE_ISSUES.md) | Known production bug inventory |
| [docs/DESIGN_DECISIONS.md](docs/DESIGN_DECISIONS.md) | Technology and framework decisions |
| [docs/DEVELOPMENT_PROCESS.md](docs/DEVELOPMENT_PROCESS.md) | Development workflow, conventions, testing |
| [docs/DOCS.md](docs/DOCS.md) | Documentation management conventions |
| [docs/GIT_FLOW.md](docs/GIT_FLOW.md) | Branching, merge strategy, commit discipline |
| [docs/QUALITY_MANAGEMENT.md](docs/QUALITY_MANAGEMENT.md) | Quality philosophy and policy |
| [docs/REPO_REVIEW.md](docs/REPO_REVIEW.md) | Repository audit checklist |
| [docs/RELEASE_CHECKLIST.md](docs/RELEASE_CHECKLIST.md) | Pre-release verification guardrail |
| [docs/REQUIREMENTS.md](docs/REQUIREMENTS.md) | Feature specifications and user roles |
| [docs/RETROSPECTIVES.md](docs/RETROSPECTIVES.md) | Process gap history |
| [docs/REVERSE_ENGINEERING.md](docs/REVERSE_ENGINEERING.md) | Extracting knowledge from legacy code |
| [docs/SCHEMA.md](docs/SCHEMA.md) | Database schema |
| [docs/SEO_A11Y_ROADMAP.md](docs/SEO_A11Y_ROADMAP.md) | SEO/crawler/agent decisions and backlog |
| [docs/TESTING.md](docs/TESTING.md) | Testing strategy and targets |
| [docs/TOOLING.md](docs/TOOLING.md) | Cross-platform tooling knowledge |

## Contributing

See [docs/GIT_FLOW.md](docs/GIT_FLOW.md) for branching model and commit conventions.
See [docs/DEVELOPMENT_PROCESS.md](docs/DEVELOPMENT_PROCESS.md) for full development workflow.

All contributions are welcome. Please ensure tests pass and code is formatted before committing.

## License

Apache 2.0 — see [LICENSE](LICENSE).
