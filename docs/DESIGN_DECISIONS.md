# Design Decisions

<!-- encoding: utf-8 -->

Technology and implementation choices made during development. Each entry documents context, decision, rationale, and alternatives considered.

Covers: technology stack choices, framework-specific decisions, implementation patterns. Does not cover: language/framework-independent architecture — see `docs/ARCHITECTURE.md`, testing strategy — see `docs/TESTING.md`.

## Technology Stack

| Layer | Technology | Decision date | Rationale |
|-------|-----------|---------------|-----------|
| Framework | Flask 3.x | 2026-06-27 | Minimal, well-documented, sufficient for department-scale site |
| ORM | SQLAlchemy 2.x | 2026-06-27 | Mature, feature-rich, Flask community standard |
| Database | SQLite | 2026-06-27 | No server process, zero config, sufficient for concurrent usage |
| Full-text search | SQLite FTS5 | 2026-07-12 | Zero-dependency, atomic (inside SQLite), trigger-friendly, no filesystem races |
| Templates | Jinja2 | 2026-06-27 | Flask default, well-known |
| Admin panel | Custom CRUD (flask_se_crud.py) | 2026-07-12 | Flask-Admin 2.2.0 unmaintained since 2022; custom gives full control with \<200 LOC base class |
| Auth | Flask-Login + custom (email, VK, Google) | 2026-06-27 | Standard Flask auth stack |
| Scheduler | APScheduler (BackgroundScheduler) | 2026-07-12 | Standalone BackgroundScheduler replaces Flask-APScheduler (unmaintained since 2020) |
| Forms | WTForms | 2026-06-27 | Flask community standard, CSRF protection built-in |
| Migrations | Flask-Migrate (Alembic) | 2026-06-27 | Schema evolution tracking |
| Static assets | Quick Website theme (Bootstrap 4) | 2026-06-27 | Pre-existing design, responsive |

## [2026-07-03] Dual Dep Management: uv (dev) + pip (prod)

**Context**: Development needs fast dependency resolution and lockfile consistency. Production (Docker, CI on `current`) needs minimal image size.

**Decision**: Use `uv` for development and `pip` for production installs. `requirements.txt` is generated from `uv.lock` via `uv export --no-dev --no-hashes > requirements.txt`.

**Rationale**:

- Docker image stays smaller (no uv binary, no Rust toolchain)
- CI on `current` matches prod exactly (pip, Python 3.13)
- No runtime coupling to uv — prod can be deployed anywhere pip works
- uv is a dev tool only, like ruff or pre-commit

**Consequences**:

- Before every `staging → current` merge, `requirements.txt` must be regenerated
- Staging CI validates `requirements.txt` is fresh (fails if stale)
- New dep workflow: `uv add <pkg>` → commit → staging CI auto-verifies refresh

## [2026-06-27] No Flask Blueprints

**Context**: Routes are registered in a single module. The project predates widespread Blueprint adoption.

**Decision**: Use `app.add_url_rule()` in `flask_se.py` rather than Flask Blueprints.

**Rationale**: Keeps all routes visible in one file at the cost of module isolation. Each view function is imported from a separate module.

**Alternatives considered**: Flask Blueprints — would add complexity without immediate benefit. If the project grows significantly, Blueprints would be the recommended refactor.

## [2026-06-27] Flat File Upload Structure

**Context**: Uploaded files (PDFs, presentations, reviews) need organized storage.

**Decision**: Store in `static/` subdirectories organized by lifecycle stage:

- `static/thesis/texts/` — Published thesis PDFs
- `static/thesis/slides/` — Published presentations
- `static/thesis/reviews/` — Published reviews
- `static/practice/texts/` — Active practice works
- `static/tmp/texts/` — Temp uploads awaiting approval
- `static/onreview/reviews/` — Thesis-on-review files

**Rationale**: SQLite + local filesystem is simpler for a department-scale site. No cloud dependencies needed.

**Alternatives considered**: Object storage (S3, MinIO) — overkill for the scale.

## [2026-06-29] Three-Tier Practice System

**Context**: The practice module serves three distinct user roles with different responsibilities.

**Decision**: Three access tiers:

- **Student** (`/practice`): submit topics, weekly reports, upload materials, set goals/tasks
- **Staff/Supervisor** (`/practice_staff`): monitor advisees, comment on reports, notifications
- **Admin/Curator** (`/practice_admin`): full control, bulk operations, archive to main repository

**Rationale**: Mirrors the actual academic workflow. Students own their work, supervisors guide, curators administer.

## [2026-07-07] Factory Pattern for Parametrized Views

**Context**: Summer school pages are nearly identical across years (2021, 2022, 2024, 2026).

**Decision**: Use `create_summer_school_view(year)` that generates distinct view functions at registration time. Each function is renamed via `__name__` assignment so Flask's URL routing distinguishes them.

**Rationale**: Avoids duplicating 4 nearly identical view functions. The `schools` dict provides metadata per year; the view factory queries `SummerSchool.query.filter_by(year=year)`.

## [2026-07-07] Notification Enum for Template Paths

**Context**: Templates across multiple subdirectories (`notification/`, `practice/student/`, `practice/staff/`, `practice/admin/`) need consistent path references.

**Decision**: Use `templates.py` enum classes (`NotificationTemplates`, `PracticeStudentTemplates`, etc.) to reference template paths instead of hardcoded strings.

**Rationale**: Prevents typos in template names, enables IDE autocompletion, centralizes path changes.

## [2026-06-29] Single-File Models

**Context**: All SQLAlchemy models could be split by domain (practice, theses, auth, etc.).

**Decision**: Keep all models in `se_models.py`.

**Rationale**: Keeps the schema visible in one place. Database migrations (Alembic/Flask-Migrate) handle schema evolution; models are read-only references to the current schema.

## [2026-07-05] Basedpyright Per-Module Opt-Out Strategy

**Context**: Codebase has ~193 untyped functions out of ~202. Basedpyright with `typeCheckingMode = "all"` catches real bugs but produces many framework-level false positives.

**Decision**: Check all modules with basedpyright. Use `# pyright: ignore[code]` comments for framework-level patterns at the point of use rather than global overrides.

**Pattern suppress list**:

- `reportCallIssue` — for dynamic constructor kwargs (SQLAlchemy models)
- `reportAttributeAccessIssue` — for SQLAlchemy dynamic attributes/backrefs
- `reportOptionalMemberAccess` — for access after `.first()` without None check
- `reportAssignmentType` — for framework-level type mismatches (Flask-Admin config)

**Rationale**: The per-module opt-out allows progressive typing: files that are simple (config, forms) get full strict checking; complex files (views, models) get gradual coverage.

## [2026-07-05] Test-First, No Production Code Before 90% Coverage

**Context**: Safe refactoring requires tested behavior as ground truth. Production code had ~31% coverage at project start.

**Decision**: Freeze production code until test coverage reaches 90%.

**Exceptions**: Trivial one-line fixes (e.g., adding `.get("field", "")` default) that unblock tests can be applied during the coverage phase if they directly enable testing.

## [2026-07-12] Defensive Form Field Access

**Context**: Several production bugs traced to `request.form.get("field_name").strip()` raising `AttributeError` when the field is absent from the form data.

**Decision**: Always use `request.form.get("field_name", "", type=str).strip()` for form fields that may be absent.

**Known occurrences**: `flask_se_auth.py:197` (register_basic), `flask_se_auth.py:239-242` (user_profile), `flask_se_review.py` (submit_thesis_on_review). All fixed.

**Rationale**: `request.form.get()` returns `None` for absent fields. The `""` default converts `None` to a safe empty string before `.strip()` is called. The `type=str` parameter ensures consistent typing.

## [2026-07-12] Flask 2.3 → 3.1 Migration

**Context**: Flask 2.3.x reaches end-of-life. Flask 3.x drops `app.run()`, removes deprecated `Markup` re-export, and requires Werkzeug 3.x.

**Decision**: Upgrade Flask from 2.3.3 to 3.1.3. Remove incompatible extensions: Flask-Markdown (replaced with custom `@app.template_filter("markdown")` using stdlib `markdown`), Flask-SimpleMDE (replaced with vendored JS), Flask-BasicAuth (unused). Replace `app.run()` with `werkzeug.serving.run_simple()`.

**Rationale**: Flask 3.x is the current supported series. The removed extensions were all unmaintained. The custom markdown filter is \<10 LOC and supports the same `tables` extension.

**Alternatives considered**: Pinning Flask 2.3.x — would accumulate security debt. Forking the extensions — unmaintainable.

## [2026-07-12] SQLite FTS5 instead of Whoosh

**Context**: Whoosh was a pure-Python full-text search library wrapped by Flask-Whooshee. Whoosh has filesystem race conditions (`EmptyIndexError`), slow rebuilds (~37s), and no updates since 2016. Flask-Whooshee is similarly unmaintained.

**Decision**: Replace Whoosh/Flask-Whooshee with SQLite FTS5 virtual table (`thesis_fts`) with auto-sync triggers on INSERT/UPDATE/DELETE of the `thesis` table. Add `thesis_fts_search()` helper in `se_models.py`.

**Rationale**: SQLite FTS5 is zero-dependency (built into SQLite), atomic (index is inside the DB), trigger-friendly, and has no filesystem races. Index rebuild is instant via `INSERT INTO thesis_fts(thesis_fts) VALUES('rebuild')`. The three-tier priority sorting (metadata match > text-only match) is preserved in Python.

**Alternatives considered**: Elasticsearch — overkill for department-scale site. PostgreSQL full-text search — would require changing the database.

## [2026-07-12] Custom Admin CRUD instead of Flask-Admin

**Context**: Flask-Admin 2.2.0 (latest) is unmaintained since 2022. Three admin view test failures were xfailed due to Jinja2/Werkzeug incompatibility. No Flask-Admin 3.x release.

**Decision**: Build custom `CrudView` base class in `flask_se_crud.py` (\<200 LOC) with 8 admin view subclasses. All 77 admin routes preserved at same URLs with same behavior.

**Rationale**: Custom CRUD gives full control over template rendering, form handling, and access control. Eliminates an unmaintained security-critical dependency. The `CrudView` base class supports column lists, labels, choices, form overrides, form widgets, export, pagination, and role-based access.

**Alternatives considered**: Flask-Appbuilder — powerful but overkill, adds its own security model and template system.
