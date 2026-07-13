# Architecture

<!-- encoding: utf-8 -->

Module map, data flow, and conventions for the SE Site.

Covers: module responsibilities, execution flow, template structure. Does not cover: technology choices — see `docs/DESIGN_DECISIONS.md`, endpoint schemas — see `docs/API_REFERENCE.md`, data models — see `docs/SCHEMA.md`.

## Module Map

### Application Core

| Module | Responsibility |
|---|---|
| `flask_se.py` | Module-level app (singleton `app = Flask(__name__)`), route registration, scheduler init, custom admin views init |
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
| `flask_se_admin.py` | Custom admin CRUD views (DB table management via `CrudView` base class) |

### Supporting Modules

| Module | Responsibility |
|---|---|---|
| `se_models.py` | All SQLAlchemy models + `init_db()` seed data |
| `se_forms.py` | WTForms form definitions |
| `se_review_forms.py` | Review evaluation form (detailed rubric) |
| `se_internship_forms.py` | Internship and diploma theme form definitions |
| `se_sendmail.py` | Email notification service via SPbU SMTP |
| `flask_se_crud.py` | Generic CRUD base class for admin views |
| `extract_text.py` | Re-extract text content from thesis PDFs |
| `thesesImport.py` | Import theses from external sources (web scraping, batch processing) |

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

### Scheduled Jobs (BackgroundScheduler)

Three background jobs run within the Flask context:

1. **RecalculatePostRank** — every hour: recalculate news ranking based on votes and views
1. **SendMailNotification** — every 10 seconds: process the email notification queue
1. **SendDiplomaThemesOnReviewNotification** — every 24 hours: notify about unmoderated themes

### Authentication Flow

- Email/password: pbkdf2:sha256 hashing, Flask-Login session management
- VK OAuth: redirect -> callback -> user lookup/create -> login
- Google OAuth: redirect -> callback -> user lookup/create -> login

### Static Site Generation

Frozen-Flask can build the entire site to a static directory. See `docs/DESIGN_DECISIONS.md` for technology choices.

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

## Conventions

### Coding

- **SPDX headers**: every `.py` file starts with `# SPDX-License-Identifier: Apache-2.0`

### Database

- SQLite backend (`se.db`)
- SQLAlchemy ORM with declarative base
- Alembic migrations in `migrations/versions/`
- Seed data in `init_db()` called via `python flask_se.py init`

### File Uploads

- PDF-only for thesis documents
- File URIs stored in database, file bodies on filesystem
- Paths resolved relative to `src/static/`
