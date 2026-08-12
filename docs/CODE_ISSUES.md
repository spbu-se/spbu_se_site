<!-- encoding: utf-8 -->

# Code Issues Discovered During Test Coverage

Found during the coverage-first phase (2026-07-04/05 auto run). Coverage target met — bugs below are unblocked.

Covers: known production bugs and security findings, prioritized by severity, with fix status. Does not cover: process gaps — see `docs/RETROSPECTIVES.md`, testing strategy — see `docs/TESTING.md`.

## P0 — Production Bugs (crash on missing form fields)

### `flask_se_auth.py:197` — `register_basic` crashes on missing `first_name` [FIXED]

Already fixed in session 3 — `""` default added to `request.form.get()`. CODE_ISSUES.md was stale.

### `flask_se_auth.py:239-242` — `user_profile` crashes on missing form fields [FIXED]

Same fix — `""` defaults on all 4 fields.

### `flask_se_review.py` — `submit_thesis_on_review` crashes on missing `title` [FIXED]

Fixed in this session — added `""` default to `request.form.get("name_ru", "", type=str)`.

**Affected**: `test_review.py::TestReviewSubmitFlow::test_review_submit_post` — xfail may need removal.

## P1 — Edge Cases (may crash under specific conditions)

### `flask_se_config.py:88` — `post_ranking_score` negative args (FIXED)

Already fixed in Week 1 of this auto run. Keeping for documentation completeness.

### `flask_se_config.py:122` — `get_thesis_type_id_string` bounds (FIXED)

Already fixed in Week 1 of this auto run.

## P2 — Code Quality Issues

### `se_models.py:278-281` — `CurrentThesis.__init__` doesn't accept all columns [FIXED]

Fixed in this session — replaced with `**kwargs` + `super().__init__(**kwargs)`.

### `se_models.py:321-323` — `ThesisTask.__init__` uses positional args [FIXED]

Fixed in this session — same fix as CurrentThesis.

### `se_models.py:343-347` — `ThesisReport.__init__` uses positional args [FIXED]

### `flask_se_practice.py` — File upload routes have high cyclomatic complexity

Routes like `practice_preparation` have deeply nested `if/elif` blocks (lines 442-659). Hard to test each branch without file upload fixtures.

Measured: `practice_preparation` = F (74), `get_remaining_time` = D (26), `practice_goals_tasks` = C (19). Average file complexity = C (12.2). Requires refactoring before additional tests can be written.

### `flask_se_auth.py:48-53` — `redirect_next_url` helper returns `Any` [FIXED]

```
def redirect_next_url(fallback=url_for("index")):
```

No open redirect vulnerability — `url_for()` only generates internal URLs, rejecting external targets. Fixed missing `return` on line 65 and added `url_for(next_url)` validation before storing in session.

### `flask_se.py:360` — SECRET_KEY_THESIS logged at ERROR level on every startup [FIXED]

Fixed in session 5 — downgraded from `app.logger.error` to `app.logger.debug`. This is an ephemeral secret (regenerated on every restart), so DEBUG level is appropriate.

## P3 — Test Infrastructure Issues

## P4 — Deprecations

### `flask_se.py:413-427` — `AdminModelView` passes `db.session` instead of `db` [RESOLVED — Flask-Admin removed in PR #11]

Flask-Admin 3.0 may require `db` (SQLAlchemy instance) instead of `db.session` (scoped session). Current version 2.2.0 accepts both. Verify on upgrade.

### `flask_se_auth.py:49` — `Users.query.get()` is legacy SQLAlchemy 1.x [FIXED]

Replaced with `db.session.get(Users, int(user_id))` in `src/`. Only test files remain — not production code.

### `flask_se_practice_admin.py:152,258` — `send_file(download_name=...)` vs `attachment_filename=...` [FIXED]

Flask 2.3.3 supports both. `download_name` is the correct modern parameter. No action needed.

## Security sweep 2026-08-01 — CodeQL + secret-scanning findings [FIXED]

Fixed on `fix/security-sweep` (PR #187) — path traversal, open redirects, secret logging, workflow permissions.

- `flask_se_theses.py` — author-derived filename now sanitized with `secure_filename()`; upload extensions whitelisted via `_safe_extension()` (CodeQL 152-155)
- `flask_se_auth.py` — avatar upload extensions whitelisted to `{jpg,jpeg,png,bmp}`; `request.url` self-redirects replaced with `url_for("upload_avatar")` (CodeQL 153, 74)
- `flask_se_news.py` — Referer host validated before redirect, fallback to `index` (CodeQL 144-147)
- `flask_se_review.py` — `request.url` self-redirects replaced with named endpoints (CodeQL 148-150)
- `flask_se.py` — removed `SECRET_KEY_THESIS` DEBUG log (CodeQL 151)
- Workflows — `permissions: contents: read` on ci.yml, ci-staging.yml, serviceability.yml, deploy_to_staging.yml, deploy_to_production.yml (CodeQL 137-138, 156-166)
- pyasn1 0.6.3 → 0.6.4 via PR #183 — resolved 2 high-severity dependabot alerts (CVE-2026-59884/59885/59886)

## P2 — SQLite runtime URI vs init path mismatch [FIXED]

`app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + SQLITE_DATABASE_NAME` (flask_se.py:172) was **CWD-relative** — the runtime app resolved `se.db` against the current working directory, while `init_db()` targeted `databases/se.db` (se_models.py:2859). So `flask_se.py init` populated a different file than the dev server read, and in Docker (WORKDIR `/app`, volume mounted at `/app/databases`) the DB landed at `/app/se.db` — **outside the volume** (data lost on recreate) and the entrypoint's `databases/se.db` check never matched (re-seed every boot). The `init_db()` backup path also concatenated `SQLITE_DATABASE_PATH + SQLITE_DATABASE_NAME` with no separator (`databases` + `se.db` = `databasesse.db`), so backups never ran.

Fixed in this session (`fix/sqlite-db-path`): `SQLITE_DATABASE_URI` built from the absolute path (`"sqlite:///" + Path(SQLITE_DATABASE_PATH, SQLITE_DATABASE_NAME).as_posix()`), used by `flask_se.py`; `init_db()` backup paths now use `Path(...)` joins; `flask_se.py` ensures `databases/` exists before connecting. Root cause of issue #126 step 2 resolved.

## Security audit 2026-08-02 — full-code review + GH security surface [FIXED]

Senior-dev review of the entire `src/` (authz/CSRF/OAuth, XSS, SQLi/file-handling)
plus the GitHub security surface (Dependabot, CodeQL, private advisory). All
findings below fixed in the stacked fork PR (#193). Regression tests live in
`tests/test_auth_views.py` (`TestSecurityCritical`, `TestSecurityMedium`).

### Phase 1 — Critical

| Finding | Status | Fix |
|---------|--------|-----|
| `SECRET_KEY` was a **filesystem path string**, never the config file contents → forgeable session cookies = full takeover | FIXED | `flask_se_config.read_secret_from_file()` reads `flask_se_secret.conf`; random dev fallback |
| Stored XSS on the public news page: `textile.textile()` (sanitize off) + `{{ post.text\|safe }}` | FIXED | `nh3.clean()` at the storage boundary |
| `delete_internship` had `@login_required` commented out → anonymous delete | FIXED | decorator restored |
| `theses_tmp`/`theses_delete_tmp`/`theses_add_tmp` unauthenticated → anyone could publish/destroy temp theses | FIXED | login + role>=2 gate |

### Phase 2 — High hardening

| Finding | Status | Fix |
|---------|--------|-----|
| No CSRF protection; GET-based mutations (`post_vote`, delete/archive, etc.) | FIXED | global `CSRFProtect`; csrf tokens on all POST forms; GET mutations moved to POST |
| Upload extension whitelist accepted `.html/.svg` served from `static/` → stored XSS | FIXED | allowlist (pdf/doc/docx/ppt/pptx/txt/md) + `MAX_CONTENT_LENGTH` 64MB |
| `SECRET_KEY_THESIS = os.urandom(16)` regenerated per uWSGI worker (inconsistent API key) + shown in admin UI | FIXED | persistent config file; removed from UI |
| Google OAuth missing `return` + no state check; VK/Yandex no `state` (login-CSRF) | FIXED | explicit state validation; new VK `/vk_login` with state + POST exchange |
| `OAUTHLIB_INSECURE_TRANSPORT=1` unconditional | FIXED | gated behind `SE_DEV_OAUTH_INSECURE` |
| Session cookie without `Secure`/`SameSite` | FIXED | HttpOnly + SameSite=Lax + Secure (env-gated) |

### Phase 3 — Medium hardening

| Finding | Status | Fix |
|---------|--------|-----|
| Path-traversal **write** via unsanitized usernames in upload paths (practice + review) | FIXED | `secure_filename()` on all name-derived components |
| Zip-slip on practice archive export (`arcname` from DB `text_uri`) | FIXED | `_safe_uri()` validation (regex `[A-Za-z0-9_.-]+`) |
| `theses_add_tmp` `os.rename` with DB-controlled URI | FIXED | `_safe_uri()` gate |
| Untrusted PDFs parsed by MuPDF without size/page caps; orphaned files on parse failure | FIXED | `get_text()` tolerant; `MAX_CONTENT_LENGTH`; temp cleanup |
| Unbounded avatar download (`r.content`) — memory DoS | FIXED | streamed `_download_avatar()` with 2MB budget |
| `DecompressionBombError` not caught (not an `OSError`) → 500 + tmp leak | FIXED | broad except + `finally` unlink |
| Login brute-force + account enumeration via distinct error messages | FIXED | in-memory `RateLimiter` (login 10/5min, register 5/h); unified error message |
| Weak password policy (min 5) | FIXED | min 8 |
| Practice IDORs: task/report delete+edit not scoped to owner thesis; notification read not scoped | FIXED | scoped by `current_thesis.id` / `recipient_id` |
| Review IDORs: result readable by anyone (author check commented out); any reviewer could submit for any thesis | FIXED | author-or-reviewer gate; `thesis.reviewer_id == user_reviewer.id` |
| FTS5 query-language injection via embedded quotes | FIXED | quote escaping in `thesis_fts_search` |
| CSV export formula injection; unbounded `page_size` | FIXED | `'` prefix on control chars; cap 200 |

### Open / intentional

- **Practice admin vs staff role separation** — both use the same `user_is_staff` guard by design; staff are the operators. Deferred; revisit if a curator-only role is needed.
- **SQLite URI mismatch** (see P2 above) — root cause of issue #126; not part of this audit.
- Dependabot Pillow (9 alerts) + Flask (1) alerts still show open in GH UI but the manifest is already patched (Pillow 12.3.0, Flask 3.1.3) — auto-resolve on the next Dependabot scan of `current`.

### CodeQL

- #171/#172 (weak SHA256 hashing in tests) — FIXED: tests now use a precomputed HMAC digest.
- #173 (clear-text storage at `flask_se_auth.py` avatar write) — verified false positive (writes image bytes, not the token), dismissed with reason.

### Dismissed (vendored/client-side, "won't fix")

- 58 × Unsafe jQuery plugin — Bootstrap 4 dist bundle in `src/static/assets/libs/`
- 4 × Unsafe jQuery plugin — jquery.mask-plugin dist bundle
- 2 × DOM text reinterpreted as HTML — jQuery template, server-provided content
- Secret-scanning google_api_key — public Google Maps JS browser key (referrer-restricted, client-side)
