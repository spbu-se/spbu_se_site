# SE Site вЂ” SPbSU System Programming Department

<!-- encoding: utf-8 -->

[![CI (staging)](https://github.com/iakov/spbu_se_site/actions/workflows/ci-staging.yml/badge.svg)](https://github.com/iakov/spbu_se_site/actions)
[![Python](https://img.shields.io/badge/python-3.13-blue)](.python-version)
[![License](https://img.shields.io/badge/license-Apache%202.0-green)](LICENSE)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

РЎР°Р№С‚ РєР°С„РµРґСЂС‹ СЃРёСЃС‚РµРјРЅРѕРіРѕ РїСЂРѕРіСЂР°РјРјРёСЂРѕРІР°РЅРёСЏ РњР°С‚РµРјР°С‚РёРєРѕ-РјРµС…Р°РЅРёС‡РµСЃРєРѕРіРѕ С„Р°РєСѓР»СЊС‚РµС‚Р° РЎРџР±Р“РЈ.

Р’РµР±-СЃР°Р№С‚ РґР»СЏ РїСѓР±Р»РёРєР°С†РёРё РёРЅС„РѕСЂРјР°С†РёРё Рѕ РєР°С„РµРґСЂРµ: РЅРѕРІРѕСЃС‚Рё, РґРёРїР»РѕРјРЅС‹Рµ С‚РµРјС‹, РїСЂР°РєС‚РёРєРё, РѕС‚Р·С‹РІС‹, РёРЅС„РѕСЂРјР°С†РёСЏ РґР»СЏ Р°Р±РёС‚СѓСЂРёРµРЅС‚РѕРІ Рё СЃС‚СѓРґРµРЅС‚РѕРІ.

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

Create these files in the project root (never committed):

| File | Purpose |
|------|---------|
| `flask_se_secret.conf` | Secret key, database path, thesis API key |
| `flask_se_mail.conf` | SMTP settings for email notifications |
| `flask_se_practice_yandex_secret.conf` | Yandex OAuth for practice file storage |

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

- `Dockerfile` вЂ” uWSGI-based Flask container
- `docker-compose.yml` вЂ” Flask + nginx

Production uses `current` branch with uWSGI behind nginx.

## Project structure

```
se-site/
в”њв”Ђв”Ђ src/                    # Application code (60 files)
в”‚   в”њв”Ђв”Ђ flask_se.py         # Main app, routes
в”‚   в”њв”Ђв”Ђ flask_se_auth.py    # Authentication (email, VK, Google)
в”‚   в”њв”Ђв”Ђ flask_se_news.py    # News posts
в”‚   в”њв”Ђв”Ђ flask_se_theses.py  # Thesis search and management
в”‚   в”њв”Ђв”Ђ flask_se_diplomas.py# Diploma themes
в”‚   в”њв”Ђв”Ђ flask_se_practice.py# Student practice workflows
в”‚   в”њв”Ђв”Ђ flask_se_review.py  # Thesis review system
в”‚   в”њв”Ђв”Ђ se_models.py        # SQLAlchemy models
в”‚   в””в”Ђв”Ђ templates/          # Jinja2 templates (107 files)
в”њв”Ђв”Ђ tests/                  # Test suite (258+ tests, 47% coverage)
в”њв”Ђв”Ђ doc/                    # Process and architecture documentation
в”њв”Ђв”Ђ .github/workflows/      # CI/CD pipelines
в””в”Ђв”Ђ docker-compose.yml      # Production deployment
```

## Documentation

| File | Purpose |
|------|---------|
| [docs/DEVELOPMENT_PROCESS.md](docs/DEVELOPMENT_PROCESS.md) | Development workflow, conventions, testing |
| [docs/GIT_FLOW.md](docs/GIT_FLOW.md) | Branching, commits, staging workflow |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Module design and data flow |
| [docs/REVERSE_ENGINEERING.md](docs/REVERSE_ENGINEERING.md) | Extracting knowledge from legacy code |
| [docs/TOOLING.md](docs/TOOLING.md) | Cross-platform tooling knowledge |
| [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | Common errors and fixes |
| [docs/API_REFERENCE.md](docs/API_REFERENCE.md) | API endpoint reference |
| [docs/SCHEMA.md](docs/SCHEMA.md) | Database schema |
| [docs/REPO_REVIEW.md](docs/REPO_REVIEW.md) | Repository audit checklist |

## Contributing

See [docs/GIT_FLOW.md](docs/GIT_FLOW.md) for branching model and commit conventions.
See [docs/DEVELOPMENT_PROCESS.md](docs/DEVELOPMENT_PROCESS.md) for full development workflow.

All contributions are welcome. Please ensure tests pass and code is formatted before committing.

## License

Apache 2.0 вЂ” see [LICENSE](LICENSE).
