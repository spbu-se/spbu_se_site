# Architecture

Module map, data flow, design decisions, and conventions for the SE Site.

Covers: module responsibilities, execution flow, template structure, design rationale. Does not cover: endpoint schemas — see `doc/API_REFERENCE.md`, data models — see `doc/SCHEMA.md`.

## Module Map

### Application Core

| Module | Responsibility |
|---|---|
| `flask_se.py` | App factory, route registration, scheduler init, Flask-Admin init |
| `flask_se_config.py` | App configuration, secret management, DB path, ranking algorithm |
| `wsgi.py` | WSGI entry point (uWSGI) |
| `app.ini` | uWSGI process/thread configuration |

### View Modules

| Module | Responsibility |
|---|---|
| `flask_se_auth.py` | Authentication (email/password, VK OAuth, Google OAuth) |
| `flask_se_bachelor.py` | Bachelor program info pages + score data |
| `flask_se_diplomas.py` | Diploma themes CRUD |
| `flask_se_internships.py` | Internships CRUD |
| `flask_se_news.py` | News post system (submit, vote, delete, rank) |
| `flask_se_practice.py` | Practice module (student side): topics, reports, goals, defense |
| `flask_se_practice_admin.py` | Practice module (admin): manage theses, archive, export |
| `flask_se_practice_staff.py` | Practice module (staff/supervisor): notifications, reports |
| `flask_se_practice_table.py` | Excel table generation (pandas + openpyxl) |
| `flask_se_practice_yandex_disk.py` | Yandex Disk OAuth + file upload |
| `flask_se_review.py` | Thesis review workflow (peer review) |
| `flask_se_scholarships.py` | 13 static scholarship info pages |
| `flask_se_summer_schools.py` | Summer school pages (2021, 2022, 2024, 2026) |
| `flask_se_theses.py` | Thesis archive: search, upload, manage |
| `flask_se_admin.py` | Flask-Admin model views (CRUD for DB tables) |

### Supporting Modules

| Module | Responsibility |
|---|---|
| `se_models.py` | All SQLAlchemy models + `init_db()` seed data |
| `se_forms.py` | WTForms form definitions |
| `se_review_forms.py` | Review evaluation form (detailed rubric) |
| `se_sendmail.py` | Email notification service via SPbU SMTP |
| `extract_text.py` | Re-extract text content from thesis PDFs |

### Configuration Modules

| Module | Responsibility |
|---|---|
| `flask_se_practice_config.py` | Practice file paths, Yandex OAuth credentials, upload config |

## Data Flow

```
Request -> nginx (reverse proxy) -> uWSGI -> Flask app
                                              -> Route matched
                                              -> View function
                                                   -> Query DB (SQLAlchemy)
                                                   -> Render Jinja2 template
                                                   -> Return HTML response
```

### Scheduled Jobs (APScheduler)

Three background jobs run within the Flask context:

1. **RecalculatePostRank** — every hour: recalculate news ranking based on votes and views
1. **SendMailNotification** — every 10 seconds: process the email notification queue
1. **SendDiplomaThemesOnReviewNotification** — every 24 hours: notify about unmoderated themes

### Authentication Flow

- Email/password: pbkdf2:sha256 hashing, Flask-Login session management
- VK OAuth: redirect -> callback -> user lookup/create -> login
- Google OAuth: redirect -> callback -> user lookup/create -> login

### Static Site Generation

Frozen-Flask can build the entire site to a static directory:
`python flask_se.py build` outputs to `../docs/` for static hosting.

## Template Structure

Templates use a **Quick Website** bootstrap-based theme with four base layouts:

| Base Template | Description |
|---|---|
| `base_dark.html` | Dark theme, standard footer |
| `base_dark_footer_white.html` | Dark theme, white footer |
| `base_light.html` | Light theme, standard footer |
| `base_light_footer_white.html` | Light theme, white footer |

View-specific templates live in subdirectories: `auth/`, `news/`, `practice/student/`, `practice/staff/`, `practice/admin/`, `diplomas/`, `internships/`, `thesis_review/`, `scholarships/`, `admin/`, `notification/`.

Practice templates use `templates.py` enum files for path references rather than hardcoded strings.

## Design Decisions

### [2026-07-03] Dual Dep Management: uv (dev) + pip (prod)

Development uses `uv` for speed and lockfile consistency (`uv.lock`). Production
(Docker, CI on `current`) uses `pip install -r requirements.txt` — no `uv`
dependency.

`requirements.txt` is generated from `uv.lock` via:

```bash
uv export --no-dev --no-hashes > requirements.txt
```

**Why keep pip in prod**:

- Docker image stays smaller (no uv binary, no Rust toolchain)
- CI on `current` matches prod exactly (pip, Python 3.9)
- No runtime coupling to uv — prod can be deployed anywhere pip works
- uv is a dev tool only, like ruff or pre-commit

**Process implications**:

- Before every `staging → current` merge, `requirements.txt` must be regenerated
- Staging CI validates `requirements.txt` is fresh (fails if stale)
- New dep workflow: `uv add <pkg>` → commit → staging CI auto-verifies refresh

### [2026-06-27] No Flask Blueprints

Routes are registered via `app.add_url_rule()` in `flask_se.py` rather than Flask Blueprints. This keeps all routes visible in one file at the cost of module isolation. Each view function is imported from a separate module.

**Why not Blueprints**: The project predates widespread Blueprint adoption. Migration would add complexity without immediate benefit. If the project grows significantly, Blueprints would be the recommended refactor.

### [2026-06-27] Flat File Upload Structure

Uploaded files (PDFs, presentations, reviews) are stored in `static/` subdirectories organized by lifecycle stage:

- `static/thesis/texts/` — Published thesis PDFs
- `static/thesis/slides/` — Published presentations
- `static/thesis/reviews/` — Published reviews
- `static/practice/texts/` — Active practice works
- `static/tmp/texts/` — Temp uploads awaiting approval
- `static/onreview/reviews/` — Thesis-on-review files

**Why not object storage**: SQLite + local filesystem is simpler for a department-scale site. No cloud dependencies needed.

### [2026-06-29] Three-Tier Practice System

The practice module has three access tiers:

- **Student** (`/practice`): submit topics, weekly reports, upload materials, set goals/tasks
- **Staff/Supervisor** (`/practice_staff`): monitor advisees, comment on reports, notifications
- **Admin/Curator** (`/practice_admin`): full control, bulk operations, archive to main repository

**Why three tiers**: Mirrors the actual academic workflow. Students own their work, supervisors guide, curators administer.

### [2026-06-29] Single-File Models

All SQLAlchemy models live in `se_models.py` (not split by domain). The `init_db()` function creates seed data inline.

**Why single file**: Keeps the schema visible in one place. Database migrations (Alembic/Flask-Migrate) handle schema evolution; models are read-only references to the current schema.

## Conventions

### Coding

- Flask app pattern: factory function `create_app()` in `flask_se.py`
- Route registration: `app.add_url_rule()` with explicit endpoint names
- Template rendering: `render_template()` with context dicts
- Form handling: WTForms with `validate_on_submit()` pattern
- **SPDX headers**: every `.py` file starts with `# SPDX-License-Identifier: MIT`

### Database

- SQLite backend (`se.db`)
- SQLAlchemy ORM with declarative base
- Alembic migrations in `migrations/versions/`
- Seed data in `init_db()` called via `python flask_se.py init`

### File Uploads

- PDF-only for thesis documents
- File URIs stored in database, file bodies on filesystem
- Paths resolved relative to `src/static/`
