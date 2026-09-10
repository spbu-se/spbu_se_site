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
| Migrations | Self-healing `ensure_schema()` (models = source of truth; `db.create_all()` + PRAGMA-driven `ADD COLUMN`) | 2026-08-21 | Webhook deploys have no migration step; the Alembic tree is multi-headed and broken from scratch — see [2026-08-08] Lazy DDL guard and [2026-08-21] Self-healing boot-time schema |
| Static assets | Quick Website theme (Bootstrap 4) | 2026-06-27 | Pre-existing design, responsive |

## [2026-08-08] Date-based versioning + draft releases

**Context**: `docs/GIT_FLOW.md §7` and `docs/DEVELOPMENT_PROCESS.md §6` documented
SemVer ("determine SemVer bump from commit log"), but the actual release tags
were always zero-filled dates (`v2025.09.09`, `v2025.07.04`, …) — a silent
doc-drift. Releases were created manually on GitHub with one-line titles and no
structured notes, and the `deploy_to_production.yml` webhook fired on the tag
with no release artifacts or notes.

**Decision**:

- All releases use zero-filled date versions `vYYYY.MM.DD`. Tags are GPG-signed
  and pushed to the canonical repo only when a release is shipped — not on every
  merge to `current`.
- `deploy_to_production.yml` gains a `release` job: on a `v*.*.*` tag it runs
  the `release-notes` skill (via opencode, requires `OPENCODE_ZEN_API_KEY`) and
  creates a **DRAFT** GitHub release — never auto-published. The draft is
  reviewed and published manually by the maintainer.
- Release notes are two-part: Part 1 plain-English user summary, Part 2
  developer changelog (dependencies table, major changes, contributors, compare
  link). Encoded in `.skills/release-notes/`.

**Rationale**:

- Date versions are inherently ordered and unambiguous; no semantic bump to
  derive or mis-guess. Tag and release string stay identical (`v2026.08.08`).
- Draft semantics give a mandatory human review gate: notes are generated, but
  nothing ships unread. This mirrors the pattern proven in trik-lobe-server
  (LLM-generated notes + draft release + maintainer publish).
- The `release` job is guarded on the secret's presence so tag pushes keep
  deploying cleanly until `OPENCODE_ZEN_API_KEY` is configured (deliberate
  deviation from lobe-server's fail-loudly: here deploy and release are
  independent concerns).

**Consequences**:

- Release flow documented in `GIT_FLOW.md §7` and `DEVELOPMENT_PROCESS.md §6`;
  README gains a "Releases" section.
- Until the secret is added, draft notes are created manually following the
  skill (the agent acts as the notes generator).

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

## [2026-06-27] No Flask Blueprints (updated 2026-08-11)

**Context**: Routes were registered in a single module. The project predates widespread Blueprint adoption.

**Decision**: Use `app.add_url_rule()` via per-module `register_routes(app)` functions rather than Flask Blueprints.

**Rationale**: The original decision (single file, all routes visible) was revisited when the project grew to ~30 modules and 190+ routes. Blueprints would rename every endpoint (`bp.function` vs `function`), breaking ~30 templates and `_LEGACY_REDIRECTS`. Instead, each domain module owns a `register_routes(app)` helper called in order from `flask_se.py` — routes stay next to their views and endpoints stay byte-identical. `flask_se.py` remains the single orchestration point without holding every route line.

**Alternatives considered**: Flask Blueprints — would add complexity (endpoint renaming) without benefit here. Keeping all routes inline in `flask_se.py` — the complexity this refactor removed.

## [2026-08-11] Application factory

**Context**: `app` was a module-level `Flask(__name__)` with config, extensions, routes, and the scheduler all set up at import. This forced tests to monkeypatch `flask_se_config` globals *before* import (`tests/conftest.py`), a per-import `db.app = app; db.init_app(app)` idiom repeated in `extract_text.py`/`thesesImport.py`, and the APScheduler to start in every worker. *(Note 2026-08-22: `thesesImport.py` was removed and replaced by `thesis_import.py`, which never calls `db.init_app` at import — the per-import idiom now lives only in `extract_text.py`.)*

**Decision**: Introduce `create_app(config_overrides=None, start_scheduler=None)` in `flask_se.py`. The module-level `app = create_app()` singleton is preserved so `wsgi.py`, the import pipeline, and `from flask_se import app` in tests keep working unchanged. Config assignment moved into `_configure_app()`; extensions use `init_app()` (migrate, csrf); scheduler start is gated by the `SE_START_SCHEDULER` env var (production unset → runs; conftest sets `0` → never fires).

**Rationale**: `config_overrides` lets tests build a differently-configured instance without import-time monkeypatching; the env-gated scheduler fixes the "every worker fires N jobs" trigger at its root (the NotificationLog idempotency claim in `se_sendmail.py` remains as defense-in-depth); the import pipeline no longer side-starts background threads.

**Consequences**: `tests/conftest.py` sets `SE_START_SCHEDULER=0` before importing (replacing `scheduler.shutdown()`); `create_app` is the entry point for future multi-app or config-driven test setups. The `flask_se_config` global monkeypatch remains in conftest only because `init_db()` reads those globals directly (backup path), not because of app construction.

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

**Rationale**: Keeps the schema visible in one place. Database migrations (Alembic/Flask-Migrate) handle schema evolution; models are read-only references to the current schema. *(Superseded by [2026-08-21] — models are the schema source of truth and evolve via `ensure_schema()`; Alembic was removed.)*

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

## [2026-08-02] OAuth client secrets moved out of source into gitignored config files

**Context**: Issue #115 flagged a hardcoded VK client_secret in `flask_se_auth.py` (the VK OAuth URL). Ruff's `S105` rule flags hardcoded passwords/secrets, so keeping it in source would fail lint and, more importantly, leaks the secret in the repo.

**Decision**: Store OAuth client secrets in gitignored files under `src/configs/` (`flask_se_vk_secret.conf`), read at import in `flask_se_config.py` with an empty-string fallback (absent file → empty secret, VK login degrades gracefully). Client IDs stay in source (public, not secret). URL construction uses the config values.

**Rationale**: Matches the existing `MAIL_PASSWORD` and `YANDEX_SECRET` pattern. Empty fallback (not the secret) keeps the secret out of the repo and keeps `S105` clean. An empty secret means VK login fails until the operator provides the config — acceptable, consistent with how the other secrets degrade.

**Alternatives considered**: Keeping the secret in source with `# noqa: S105` — leaks the secret, defeats the purpose. Injecting via env vars — departs from the established config-file pattern.

## [2026-08-02] Ruff format/check covers `tests/` in CI and pre-push

**Context**: Pre-push and CI ruff checks gated only `src/`, so `tests/` accumulated formatting and lint drift (5 files, 35 errors: unused imports, duplicate `db` imports, unsorted import blocks, and a real N806/F811 shadowing bug in `test_se_models_deep.py`).

**Decision**: Extend `ruff format --check` and `ruff check` to `src/ tests/` in `ci.yml`, `ci-staging.yml`, and the pre-push hook. Run a one-time format sweep of `tests/` to bring it in line.

**Rationale**: Tests are code and deserve the same gate as production code. The drift was invisible precisely because the gate didn't cover `tests/`. Matches `pylint --enable=similarities` which already checks `src/ tests/`.

**Alternatives considered**: Keeping the gate src-only and relying on pre-commit for touched files — that is exactly how the drift accumulated (untouched files never get reformatted).

## [2026-08-02] Config secrets are file *contents*, never paths

**Context**: The 2026-08-02 security audit found `SECRET_KEY = <path to flask_se_secret.conf>` — i.e. Flask's session-signing key was a guessable filesystem path, never the file's contents. Anyone knowing the deploy path could forge session cookies (full account takeover). Same trap for `SECRET_KEY_THESIS = os.urandom(16).hex()` regenerated per import (inconsistent across the 4 uWSGI workers).

**Decision**: Add `flask_se_config.read_secret_from_file()`: reads a config file's trimmed contents, or returns `os.urandom(len).hex()` only when the file is absent (dev/fresh checkout). Used for `SECRET_KEY` (fallback_len=24) and `SECRET_KEY_THESIS` (fallback_len=16, new `flask_se_thesis.conf`). The thesis API key was also removed from the admin UI.

**Rationale**: Mirrors the existing `MAIL_PASSWORD` read pattern. A config file is stable across workers and restarts; the dev fallback is opaque random material, never a path.

**Alternatives considered**: Env-var injection — departs from the established config-file convention. Keeping the path-as-key — the vulnerability itself.

## [2026-08-02] Sanitize user HTML at the storage boundary (nh3)

**Context**: News posts were rendered through `textile.textile()` (sanitization off by default) then emitted with `{{ post.text|safe }}` — any registered user (open registration) could run stored XSS on the public news page. The `|markdown` filter had the same latent risk.

**Decision**: Sanitize rendered HTML with `nh3.clean()` before persisting it (news). `nh3` (Rust, ammonia port) is already a transitive dependency. The `|markdown` filter keeps Jinja's autoescape (returns a plain `str`) so it stays non-executable; do not wrap it in `Markup` without sanitizing first.

**Rationale**: Sanitize-then-store keeps the `|safe` render path but guarantees safe content; `nh3` is a hardened allowlist sanitizer with no Python-parse attack surface. It matches the "sanitize at the boundary" principle better than render-time sanitization, which would have to run on every view.

**Alternatives considered**: Render-time sanitization — runs repeatedly and still needs the filter change. Escaping instead of sanitizing — would show raw HTML tags to users.

## [2026-08-02] CSRFProtect global + POST-only mutations

**Context**: No CSRF protection existed; state-changing actions (news vote/delete, diploma delete/archive, review delete/claim, internship delete, temp-thesis approve/delete) ran on GET, enabling drive-by `<img>`/link attacks.

**Decision**: Enable Flask-WTF `CSRFProtect(app)` globally; add `{{ csrf_token() }}` to every POST form and the avatar fetch (JS reads a `<meta name="csrf-token">`); convert all GET mutations to POST (views read `request.form`/`request.values`); exempt `post_theses` (authenticated by `SECRET_KEY_THESIS`, called by an external script). Cookie hardened with `HttpOnly` + `SameSite=Lax` + `Secure` (env-gated).

**Rationale**: Global CSRFProtect is the standard defense; converting GET mutations to POST removes the entire class of CSRF-by-navigation attacks. Tests disable CSRF via `WTF_CSRF_ENABLED=False`.

**Alternatives considered**: Per-view manual tokens — error-prone across ~25 forms. Keeping GET mutations — leaves the drive-by hole open.

## [2026-08-02] OAuth state validation + gated insecure transport

**Context**: Google's callback had a dead `if not state: redirect(...)` (missing `return`) and no explicit state comparison; VK had no `state` param at all (OAuth login-CSRF/account confusion). `OAUTHLIB_INSECURE_TRANSPORT=1` was set unconditionally, allowing Google OAuth over HTTP in production.

**Decision**: Google compares `request.args["state"]` against the popped session value and redirects on mismatch. VK gets a real `/vk_login` that mints a state, stores it in session, and the callback validates it; the token exchange moved to a POST body (avoids secret-in-URL). `OAUTHLIB_INSECURE_TRANSPORT` is set only when `SE_DEV_OAUTH_INSECURE=1`.

**Rationale**: Standard OAuth state validation blocks login-CSRF; POST token exchange keeps `client_secret` out of logs/URLs; the insecure-transport flag should be dev-only.

**Alternatives considered**: Relying on the library's built-in state check — undocumented, converts misuse into 500s.

## [2026-08-02] In-memory rate limiter without new dependencies

**Context**: Login/register had no rate limiting and distinct error messages enabled account enumeration.

**Decision**: Add `flask_se_config.RateLimiter` — a small sliding-window in-memory limiter (login 10/5min per IP, register 5/h). Unify the login error message ("Пара логин и пароль указаны неверно") so it does not reveal whether an email exists. Minimum password length raised to 8.

**Rationale**: No new dependency; adequate defense-in-depth. Per-worker state is acceptable for a single-host site.

**Alternatives considered**: Flask-Limiter — new dependency, not worth it for this deployment.

## [2026-08-08] Mail jobs: SE_STAGING gate + DB idempotency

**Context**: Issue #76 — the daily "themes on review" digest arrived several times a day with drifting counts. Root cause: the APScheduler jobs run in **every** gunicorn/uwsgi worker (no app factory, scheduler starts at import in `flask_se.py`), so each worker fires the 24h job → N sends/day; and the count used `status==0` while the admin review page shows `status<2`. The developer's on-the-knee SMTP code was environment-unaware; his unmerged patch gated sends on an `SE_STAGING=1` env var.

**Decision**: Two complementary guards in `se_sendmail.py`: (1) `SE_STAGING` env gate — when set (staging systemd unit), `sendmail` is skipped but the notification queue is still consumed (drains instead of growing); (2) the 24h digest claims an atomic slot on a new `NotificationLog` table (unique `type`, `last_sent_at`) — the first worker to commit a fresh timestamp wins, concurrent workers skip. Count changed to `status < 2` to match the admin review view. The table is created lazily with `checkfirst=True` because the Alembic tree is multi-headed and deploys are webhook-driven (no `flask db upgrade` in the pipeline).

**Rationale**: Env gating matches the established `SE_*` pattern (no factory) and the developer's precedent; DB idempotency is robust to any worker count without systemd changes.

**Alternatives considered**: Gating scheduler start behind a second env var — requires a prod systemd tweak and still risks two units racing. Pure file lock — host-local, fragile across processes. Relying on `status==0` — the reported bug itself.

## [2026-08-08] Lazy DDL guard instead of Alembic migrations

**Context**: Two schema changes landed in one session — a new `NotificationLog` table and a `consultant` column on `thesis`. The Alembic tree in `src/migrations/` is multi-headed and deploys are webhook-driven (no `flask db upgrade` anywhere in the pipeline), so a conventional migration would not be applied on the servers.

**Decision**: Evolve the schema in code with a guarded, idempotent DDL helper per change: `NotificationLog.__table__.create(bind=db.engine, checkfirst=True)` (table) and `_ensure_thesis_consultant_column()` → `ALTER TABLE thesis ADD COLUMN consultant VARCHAR(2048)` when `inspect(db.engine).get_columns("thesis")` lacks it. Both swallow the concurrent-creation race (`OperationalError`/duplicate-column) so multiple workers on first request cannot double-apply. The helper runs at the top of the view(s) that need the column.

**Rationale**: Matches the deployment reality — webhook deploys rebuild/restart without a migration step, and the multi-head Alembic tree makes autogenerate unreliable. The guard is a one-time no-op after the first request, and tests get the schema free via `db.create_all()`.

**Alternatives considered**: Fixing the Alembic tree and running `flask db upgrade` on deploy — larger, riskier change touching deployment infrastructure. Adding columns via raw SQL in the old data-import path — fragmented, no single guard point.

## [2026-08-21] Self-healing boot-time schema (`ensure_schema`) instead of Alembic

**Context**: The 2026-08-08 lazy-DDL decision was being formalized into a boot-time auto-migrate step. The first attempt wired Alembic (`flask db upgrade` / `stamp`) into `docker/entrypoint.sh` — a regression against the documented decision: the Alembic tree in `src/migrations/` is multi-headed and **cannot build a fresh DB from scratch** (two roots `25130df4ed9f` + `c4e88555c985`, merge `33ca5df0bfc2`), deploys are webhook-driven (no migration step), and every historical migration is pure DDL (0 data operations). Review surfaced the existing decision and the requirement that the app be **self-healing with zero ops/admin intervention** (no `flask db current` pre-flight).

**Decision**: Remove Alembic (`flask-migrate` + `alembic` deps, `src/migrations/`) and replace it with a single idempotent `ensure_schema()` run at boot (`python flask_se.py migrate`, gated by `SE_AUTO_MIGRATE`, default on):

- **Fresh DB** (no `databases/se.db`) → `init_db()` (`db.create_all()` + seed) — the models are the schema source of truth.
- **Existing DB** → back up to `se_backup_<date>.db` (reuses `SQLITE_DATABASE_BACKUP_NAME`), then `ensure_schema()`: `db.create_all()` for missing tables + per-table `PRAGMA table_info` diff against the model, `ALTER TABLE ... ADD COLUMN` for every missing column.
- **Column-presence is the version marker** — no `alembic_version` table, no versioning needed now. Each delta self-verifies against the real DB state every boot.
- **Column-addability contract**: a missing column is auto-added when it is nullable OR has a `server_default`; otherwise a constant default is synthesized by type (`Boolean→0`, `Integer→0`, `Float/Numeric→0.0`, `String/Text→''`); exotic non-nullable types (e.g. DateTime) are added nullable with a logged warning. A missing column carrying UNIQUE/PK/FK cannot be added via SQLite `ADD COLUMN` → fail-loud with a precise message (the *developer* fixes the model; never an ops step).
- DDL runs inside `db.engine.begin()` (rollback on failure) and entrypoint `set -e` aborts boot loudly rather than serving a half-migrated schema.
- The scattered per-view guards (`_ensure_thesis_consultant_column` in `flask_se_theses.py`, `NotificationLog.__table__.create(checkfirst=True)` in `se_sendmail.py`) stay as their one-time first-request guards for hot paths; `ensure_schema()` is the systematic boot-time pass.

**Rationale**: Matches the deployment reality (webhook deploys rebuild/restart without a migration step) and the user's self-healing requirement (no ops intervention, no version-state drift). Target-schema repair from the models fixes any DB state regardless of history — including the legacy-unstamped case the Alembic path handled only by stamping with an assumption. All 29 historical migrations are pure DDL already reflected in the models, so schema-only repair is complete; no data backfills exist to lose.

**Consequences**: `Users.deleted` must carry `server_default=sa.false()` (it previously had only a Python-side default) so `ADD COLUMN ... NOT NULL` can backfill existing rows. Future columns: add to the model as nullable or with a `server_default` — no migration files.

**Alternatives considered**: Alembic auto-migrate at boot (built first) — regression; broken chain from scratch + assumption-based stamping. Squashing the Alembic tree to one baseline — keeps the machinery for no benefit (models already produce the fresh schema via `create_all`). A versioned ordered-deltas table — deferred; only needed for future non-additive changes (renames, drops, data backfills), same pattern, added when required.

## [2026-08-21] Soft-delete account tombstone (fired-employee model)

**Context**: Right-to-be-forgotten (152-ФЗ ст. 14 / GDPR Art. 17). Every owned-content table (`posts`, `theses`, `practice`, `post_votes`, `reviewer`, …) has a NOT NULL `user_id` FK with **no cascade**; a hard delete would break author attribution, `Staff` joins, and admin pages. Department decision (PRIVACY_COMPLIANCE.md §5 #6): "someone fired from the department — the domain account is deleted, but work results stay."

**Decision**: Soft-delete via `Users.deleted` + `/profile/delete` (POST, `@login_required`, CSRF-protected): flag the row, purge identifying login data (`email`, `password_hash`, `vk_id`/`fb_id`/`google_id`, `avatar_uri`, `how_to_contact`, `role`), keep `first_name`/`middle_name`/`last_name` so published-content attribution survives. `load_user()` returns `None` for deleted rows. Content rows are untouched.

**Rationale**: Content integrity — every owned-content table has a NOT NULL `user_id` FK with no cascade; the tombstone keeps FKs, attribution, and joins working while removing all login capability and identifying data.

**Alternatives considered**: Hard delete with FK null-out — breaks attribution and `Staff` joins; full cascade delete — violates the archival duty for educational records and the department's fired-employee model. Anonymized "Удалённый пользователь" placeholder names — rejected: published content keeps its attribution.

## [2026-08-10] Open Graph cards by design — block-based defaults + per-content overrides

**Context**: Every publicly shareable page (news items, internship details, diploma themes, scholarships, thesis archive) should render a proper preview card when pasted into social networks/messengers. Before this change `base_dark.html` hardcoded `og:title` to the site name and `og:image` to the 16×16 favicon, while `base_light.html` had **no** OG tags at all — so content pages shared as bare URLs with a generic title. One page even shipped a copy-pasted canonical pointing to `/diplomas/index.html`.

**Decision**: Make OG metadata block-driven in **both** base templates (`base_dark.html`, `base_light.html`): `og_title` defaults to the page's own `<title>` (`self.title()`), `og_image` defaults to a shared hero image (`main-back.jpg`), `og_type` defaults to `website`, plus mirrored `twitter:card` = `summary_large_image` tags. Content pages then override only what is content-specific: news items and diploma themes set title/description/type `article`; internship details also set title from `name_vacancy`, description from `description`/`requirements`, and a corrected canonical; news items additionally get a plain-text `og_description` excerpt (HTML stripped, truncated to 160 chars) computed in `get_post`. No per-content image generation — one good default image keeps previews consistent without an image pipeline.

**Rationale**: Block defaults make every page correct "by design" — any template that already defines `title`/`description` gets a sane card with zero further work, and future pages inherit it automatically. Per-content overrides stay minimal and live next to the content they describe. The excerpt helper avoids leaking raw textile/HTML markup into social previews.

**Alternatives considered**: Per-page hardcoded OG tags in every template — drifts, easy to forget. Server-generated per-content images (PDF first page, Pillow banner) — deferred, needs a font/caching pipeline for marginal preview gain. A separate meta framework — overkill for a hand-rolled template set.

## [2026-08-13] SEO/crawler/agent friendliness — SSR lists, sitemap index, pre-rendered og-images

**Context**: `docs/SEO_A11Y_ROADMAP.md` audit found: `/theses.html` (and diplomas themes, thesis-review list) render content only via JS `fetch`, so crawlers/agents read empty pages; `sitemap.py` fakes `lastmod` as today and excludes arg-bearing rules (so `thesis_card` is never indexed); `robots.txt` disallows only `/login.html`; OG blocks are missing on the two `*_footer_white.html` bases and `og:url` points at `request.url`; no JSON-LD, no `llms.txt`, no `humans.txt`.

**Decision**:

- **Server-render the JS-only lists** (D2): the `theses_search` route renders the initial list server-side into `#ThesisList` using the existing `_thesis_card.html` partial; `se_scripts.js` guards against double-fetch (skips the initial load when content is already present). Pagination links already hit `theses_search` server-side, so filtered/paginated pages become crawlable. Same treatment for diplomas themes and the thesis-review list. Progressive enhancement — no visible UX change.
- **Sitemap index with per-year theses sub-sitemaps** (D6): `sitemap.xml` serves static pages; `sitemap-theses-<year>.xml` generated per year from the theses archive (FTS-backed query), `lastmod` = per-thesis publish date. The theses archive is the site's most valuable crawlable content and was previously invisible to sitemaps because of the arg-bearing rule filter.
- **Pre-rendered og-images** (D7): committed 1200×630 images under `src/static/assets/img/og/`, one per section (theses, news, diplomas, internships, programs, contacts, summer school, faq, default), plus `apple-touch-icon`. Per-page `og_image` block overrides. **Guardrail: re-generate these images before pushing whenever the site design changes significantly** — stale previews degrade social/sharing quality silently.
- **Per-page real lastmod** (D8): static pages use a stable deploy-date constant; dynamic pages use real DB `updated`/`publish` timestamps. Replaces the "always today" `lastmod` crawlers distrust.
- `og:url` defaults to the page canonical (was `request.url`); `robots.txt` disallows `fetch_*`, `/admin/`, auth callbacks; add `humans.txt` and `llms.txt`.

**Rationale**: Server-rendering is the single largest agent/crawler/a11y win — content becomes readable without JS while keeping the existing interactive UX. Pre-rendered static images avoid a per-request image pipeline (matches the earlier "no per-content image generation" reasoning in the OG decision) while fixing preview consistency via a small curated asset set. Real `lastmod` and indexed theses pages are what make crawlers trust and discover the archive.

**Alternatives considered**: Per-content generated og-images (Pillow) — deferred, needs a font/caching pipeline for marginal gain. Parameterless sitemap only — loses the theses archive from sitemaps. JS-only lists unchanged — keeps crawlers blind to the archive. Per-page lastmod from git log at deploy — provably accurate but adds deploy-time coupling; DB timestamps are already available for dynamic content.

## [2026-08-10] Shareable thesis cards + search-result OG

**Context**: Issue #32 — the practice archive (`/theses.html`) let you share a link to a work's PDF or presentation, but not a "card" of the work itself (title + text + presentation together). Users wanted a shareable URL proving a specific work exists. Separately, a shared *search* URL (e.g. `/theses.html?search=android+performance`) rendered the generic archive preview, even though the page is a live search — so it couldn't be used to "prove a point" via preview text.

**Decision**: (1) A new route `thesis_card` at `/thesis_card?thesis_id=N` renders a standalone card page (extends `base_dark.html`) for a single non-temporary thesis with per-work OG fields: `og:title` = `{name_ru} [{publish_year}]`, `og:type` = `article`, canonical = the card URL, description = author/supervisor/course. The card markup is extracted into a shared `_thesis_card.html` partial used by both the AJAX list fragment (`fetch_theses.html`) and the card page; the card title links to the card page, and a "Скопировать ссылку" button copies the absolute card URL to the clipboard (delegated handler in `se_scripts.js`, so it works for AJAX-re-rendered lists). (2) `theses_search` reads the `search` query arg and, when present, overrides `og:title` to `Результаты поиска: "<query>"` (and `og:description` accordingly); without a query the static archive defaults remain.

**Rationale**: Reusing the card partial keeps the list and card markup from drifting. The `thesis_card` route filters `~Thesis.temporary` so only published works are shareable, mirroring `download_thesis` redirect behavior. Search-OG makes any shared `/theses.html?search=…` link preview meaningful and still works as a live search (the JS already restores the query into the search field from URL params).

**Alternatives considered**: Per-thesis image generation for the card (PDF first page) — deferred per the OG decision above. A path-based URL `/theses/<id>.html` — diverges from the existing query-param convention (`/thesis_download?thesis_id=`) and the sitemap already excludes arg-based rules.

## [2026-08-14] Deploy only on a published release

**Context**: `deploy_to_production.yml` fired the production webhook on every
`v*.*.*` tag push. `v2026.08.10` was tagged and deployed to production yet never
published as a release — production ran a version the public was never told
about, and the stale draft lingered on GitHub. Supersedes the deploy-on-tag
behavior described in [2026-08-08] "Date-based versioning + draft releases".

**Decision**: Deploy and release are fully decoupled:

- The `deploy` job in `deploy_to_production.yml` now runs on
  `release: types: [published]` (and `workflow_dispatch` for manual redeploys),
  not on tag push. It checks out `github.event.release.tag_name`, pins the tag
  and its commit SHA, and POSTs the webhook.
- The `release` job (draft creation) still runs on the `v*.*.*` tag push when
  `OPENCODE_ZEN_API_KEY` is set. Publishing the draft — never auto-published —
  is what triggers the deploy.

**Rationale**: A published release is always anchored to a tag, so the deploy job
can always be driven by `github.event.release.tag_name`. This closes the gap
where a tag push could ship code that was never released; a tag that is never
published never reaches production. Draft-on-tag keeps the mandatory human
review gate from [2026-08-08] intact.

**Consequences**: `GIT_FLOW.md §7`, `DEVELOPMENT_PROCESS.md §6`,
`RELEASE_CHECKLIST.md` (B2/B11) updated; the release-notes skill documents that
publishing triggers the deploy.

## [2026-08-15] Sanitize user HTML at render time (markdown + safe_html filters)

**Context**: the `markdown` template filter returned a plain `str`, so Jinja
autoescape re-escaped its HTML output and markdown fields (diploma themes,
practice reports/notifications, internship descriptions) displayed literal
tags (`<p>`, `<a href=...>`) as text. Marking output safe without sanitizing
would have created a stored-XSS hole — python-markdown 3.10.2 passes raw HTML
(`<script>`, `<iframe>`, `javascript:` hrefs) through unchanged and the source
is user-authored. `nh3` was already a dependency (write-time cleaning of news
posts, see [2026-08-02] "Sanitize user HTML at the storage boundary").

**Decision**: sanitize **at render time** in the template filters:

- `render_markdown` returns `Markup(nh3.clean(_markdown.markdown(text, extensions=["tables"])))`.
- New `safe_html` filter returns `Markup(nh3.clean(text))`; all raw `|safe`
  usages (news post body, summer-school constants) migrated to it.
- A template guardrail test fails any `|safe` not paired with `|safe_html`.

**Rationale**: a render-time choke point covers every current and future call
site and legacy rows retroactively, and cannot be bypassed by an unscanned
write path. It complements — does not replace — write-time cleaning (news
keeps `nh3.clean(textile(...))` on submit; the read path is defense-in-depth).

**Consequences**: XSS-vectors empirically verified removed (scripts, event
handlers, `javascript:`/`data:` schemes, `target`/`id`); `rel="noopener noreferrer"` added to links; inline `data:` images dropped (accepted, SVG-in-
data XSS). `nh3.clean` preserves the `tables` extension output. Regression +
guardrail tests in `tests/test_app.py` and `tests/test_diplomas_deep.py`
(PR #214).

## [2026-08-31] Google SSO removed from the UI — backend OAuth left live

**Context**: Google SSO was removed from the UI on 2026-07-01 (`bd46f667`
"Remove Google SSO button") — the `login.html` button was deleted, but the sweep
stopped there. `register_basic.html` kept offering "Google" with a button that
had pointed at `url_for('login_index')` (the login page) since the first commit
(`51217100`) — a day-one stub, never wired to `google_login`. The backend OAuth
was untouched: `/google_login` + `/google_callback` routes, `GOOGLE_CLIENT_ID`,
`client_google*.json`, the `google_id` column, and 5 deps (google-auth,
google-auth-oauthlib, cachecontrol, oauthlib, requests-oauthlib) remain live.
Reported 2026-08-31: clicking the Google button on the register page just
redirects to the login page.

**Decision**: remove the Google button from `register_basic.html`, keeping VK as
the only social option (mirrors `login.html`). Scope = UI only (user decision);
the backend OAuth routes are left as-is.

**Rationale**: the register-page button was dead UI (never pointed at Google);
keeping it misled visitors. The backend routes stay reachable by direct URL — a
documented state, not an accidental zombie.

**Consequences**: `DEVELOPMENT_PROCESS.md §4.5` gains a "Feature removal sweep"
checklist item (UI in all templates → routes → config → deps → schema →
sitemap/og/CSP → docs, and record the decision here); `docs/PRIVACY_COMPLIANCE.md`
§2.2 OAuth row corrected; retro entry added (2026-08-31 batch, PR #270).

## [2026-09-07] One-off Semgrep deep scan caught a real XSS regression the guardrail missed

**Context**: a rare idiom in `summer_school.html` rendered four project fields
(`description`, `repo`, `demos`, `advisors`) through a bare `| safe` filter
(with a space), bypassing the render-time `nh3` sanitization policy
(see [2026-08-15]). The in-repo `TestRawHtmlGuardrail` should have caught it
but matched only the literal substring `|safe` and skipped `| safe`. A one-off
local Semgrep scan (`uvx semgrep scan --config p/python --config p/security-audit --config p/owasp-top-ten --oss-only`, run as cleanup
discipline over `src tests e2e scripts`) surfaced it among 69 findings.

**Decision**: (1) fix the four fields to `safe_html` and harden the guardrail
to tokenize `{{ }}` expressions and reject a standalone `safe` filter token,
spaced or not (PR #303); (2) follow up with a hardening pass on the remaining
actionable `var-in-script-tag` sites — `tojson` for the Yandex Metrica id in
the 4 base templates and for `thesis.title` in the three practice/admin
`document.title` assignments — plus an http→https editorial cleanup of
non-vendor template links; (3) do **not** bulk-edit the ~65 false-positive
findings (generic `html-templates` rules vs Jinja autoescape + strict
nonce-CSP + sanitizing filters) and do not wire Semgrep into CI (cost +
noise).

**Rationale**: deep, occasionally-run scans are cleanup discipline — they catch
what naive structural guards rot past. Verified-real findings are rare but
cheap to fix; the FP mass must be triaged against the stack's actual posture,
not silenced by edits. `tojson` (Flask's HTML-safe JSON) is the correct
in-script encoding; vendored third-party files stay untouched.

**Consequences**: `docs/TOOLING.md` gains an "Occasional deep scans (cleanup
discipline)" section with the repeatable command and triage rules; guardrail
test now catches spaced/standalone `safe`; retro entry added (2026-09-07,
PR #303/#305).

## [2026-09-10] Duplicate-area disambiguation is display-only (code-level), DB untouched

**Context**: two seeded `AreasOfStudy` rows share the name "Программная инженерия"
(bachelor/master), so every area dropdown shows two identical options. Rather than
normalize the data, display is disambiguated in code: `se_constants.AREA_PROGRAM_OVERRIDES`
maps ids `3`/`7` to suffixes `(бак)`/`(маг)`, applied by `area_display_name()` in every
area-option builder (admin CRUD FK dropdowns, review submit/edit forms, practice selects)
and by the CRUD FK labeler. No DB writes, ids and FKs untouched, other rows unaffected.

**Rationale**: a safe additive migration was deferred ("not touching existing data");
the id-keyed override is applied only while the row still carries the expected plain name
(stale-mapping guard), falling back to plain/generic disambiguation otherwise.

**Consequences / tech debt**: code-level override for a data-modeling defect. Normalize
later via an additive `AreasOfStudy.code` column (backfill the two rows) or a reviewed row
merge; `area_display_name()` then degenerates to the plain label and the override map is
deleted. Nav-sidebar area lists in practice-admin still render plain names (follow-up).

## [2026-09-10] Supervisor eligibility is a single-source query (active staff), enforced in dropdowns + validation

**Context**: `DiplomaThemes.supervisor_id`/`supervisor_thesis_id` are FKs to `users.id`,
so the generic `CrudView` FK dropdown listed every account (students, reviewers, deleted);
`CurrentThesis.supervisor_id` (FK to `staff.id`) listed inactive staff. The student-facing
supervisor picker already restricted to `Staff.still_working`, so the rule existed but was
duplicated (or absent) elsewhere.

**Decision**: one eligibility rule — `Staff.active_query()` (`still_working`) and its
user-level counterpart `Users.eligible_supervisors_query()` (active staff users) — used by
the admin FK dropdowns (new `CrudView.form_fk_query` hook + `_ActiveStaffSupervisorMixin`),
server-side `form_change_error` validation (reject a *change* to an ineligible id, allow
keeping an existing one), and the student supervisor pickers plus the static/bachelor staff
lists. `author_id` and `consultant_id` stay open — a consultant may be non-staff.

**Rationale**: reusing one query keeps the rule from drifting across surfaces, and
filtering the dropdown alone would still allow a crafted POST. An already-stored supervisor
who is no longer eligible is preserved (shown by name), so existing/finished rows are never
silently rewritten.

**Consequences**: `CrudView` gains the `form_fk_query` hook and now calls
`form_change_error` on create as well as edit; `flask_se_static.py`/`flask_se_bachelor.py`
staff lists share `Staff.active_query()`. Tests: `tests/test_admin_supervisor_eligibility.py`.

## [2026-09-10] Registration hardening: strict name/e-mail validation + config-gated SmartCaptcha

**Context**: an automated scanner stored SSTI/SSRF/blind-XSS probe payloads (the
`bxss.me` set) as `Users` first/last names, which then surfaced in admin FK
dropdowns. Ingress: `/register_basic.html` and `/profile.html` accepted any
1+ character name, and the e-mail was only length-checked; SQLite does not
enforce `VARCHAR(255)`, so a multi-KB name was stored.

**Decision**:

- `se_validation.py` is the single source of truth: `validate_person_name`
  (Unicode letters + ` -.'`, ≤100 chars, rejects control chars, `<>`, quotes,
  braces and shell metacharacters), `validate_email` (regex, ≤254), and
  `clean_person_name` for external providers.
- Applied in `register_basic`, `user_profile`, and the VK/Google imports
  (OAuth names are sanitized, not rejected).
- Yandex SmartCaptcha on registration, gated on **both** a public `SITEKEY` and
  a private `SECRET` (env or gitignored `configs/flask_se_smartcaptcha.conf`).
  Neither set → no CAPTCHA (dev/tests/un-provisioned hosts unchanged); both set
  → server-side verify that fails closed without ever raising. CSP adds
  `smartcaptcha.yandexcloud.net` to `script-src`/`connect-src` and adds `frame-src`.

**Rationale**: the charset rule is the actual block (payloads carry quotes,
newlines and `<>`); CAPTCHA raises the cost of automated signups. Config-gating
means one deploy works in every environment — ops enable it by provisioning
keys, no code change or release.

**Consequences / tech debt**: e-mail verification (and the linked TTL cleanup of
unverified accounts) is **deferred** — it needs a better staging-mail flow
(`send_mail` no-ops under `SE_STAGING`) and a VK-signup design. The app-level
rate limiter is in-memory per worker, so an nginx `limit_req` on
`/register_basic.html` is still recommended (ops). Investigation/cleanup of the
existing prod rows is covered by the ops report in `.tmp/`. Tests:
`tests/test_registration_validation.py`, `tests/test_smartcaptcha.py`.
