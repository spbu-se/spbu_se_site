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

## Setup

```bash
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

The site runs at `http://127.0.0.1:5000`.

## Configuration

Create these files in `src/configs/` (never committed):

| File | Purpose |
|------|---------|
| `flask_se_secret.conf` | Session signing secret key |
| `flask_se_mail.conf` | SMTP settings for email notifications |
| `flask_se_practice_yandex_secret.conf` | Yandex OAuth for practice file storage |
| `flask_se_vk_secret.conf` | VK OAuth client secret |
| `flask_se_thesis.conf` | Thesis upload API key (`SECRET_KEY_THESIS`) |

## Commands

| Command | Description |
|---------|-------------|
| `uv run python src/flask_se.py` | Run development server |
| `uv run python src/flask_se.py init` | Initialize database |
| `uv run python src/wsgi.py` | Run via WSGI (production) |
| `uv run pytest` | Run tests |
| `uv run ruff check src/` | Lint |
| `uv run ruff format src/` | Format |
| `uv run mdformat .` | Format markdown |

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

## Project structure

```
se-site/
├── src/                    # Application code (27 .py files)
│   ├── flask_se.py         # Main app, routes
│   ├── flask_se_admin.py   # Admin panel views
│   ├── flask_se_auth.py    # Authentication (email, VK, Google)
│   ├── flask_se_config.py  # App configuration
│   ├── flask_se_diplomas.py# Diploma themes
│   ├── flask_se_news.py    # News posts
│   ├── flask_se_practice.py# Student practice workflows
│   ├── flask_se_review.py  # Thesis review system
│   ├── flask_se_theses.py  # Thesis search and management
│   ├── se_models.py        # SQLAlchemy models
│   └── templates/          # Jinja2 templates (107 files)
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
| [docs/CODE_ISSUES.md](docs/CODE_ISSUES.md) | Known production bug inventory |
| [docs/DESIGN_DECISIONS.md](docs/DESIGN_DECISIONS.md) | Technology and framework decisions |
| [docs/DEVELOPMENT_PROCESS.md](docs/DEVELOPMENT_PROCESS.md) | Development workflow, conventions, testing |
| [docs/DOCS.md](docs/DOCS.md) | Documentation management conventions |
| [docs/GIT_FLOW.md](docs/GIT_FLOW.md) | Branching, merge strategy, commit discipline |
| [docs/QUALITY_MANAGEMENT.md](docs/QUALITY_MANAGEMENT.md) | Quality philosophy and policy |
| [docs/REPO_REVIEW.md](docs/REPO_REVIEW.md) | Repository audit checklist |
| [docs/REQUIREMENTS.md](docs/REQUIREMENTS.md) | Feature specifications and user roles |
| [docs/RETROSPECTIVES.md](docs/RETROSPECTIVES.md) | Process gap history |
| [docs/REVERSE_ENGINEERING.md](docs/REVERSE_ENGINEERING.md) | Extracting knowledge from legacy code |
| [docs/SCHEMA.md](docs/SCHEMA.md) | Database schema |
| [docs/TESTING.md](docs/TESTING.md) | Testing strategy and targets |
| [docs/TOOLING.md](docs/TOOLING.md) | Cross-platform tooling knowledge |

## Contributing

See [docs/GIT_FLOW.md](docs/GIT_FLOW.md) for branching model and commit conventions.
See [docs/DEVELOPMENT_PROCESS.md](docs/DEVELOPMENT_PROCESS.md) for full development workflow.

All contributions are welcome. Please ensure tests pass and code is formatted before committing.

## License

Apache 2.0 — see [LICENSE](LICENSE).
