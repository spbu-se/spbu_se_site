# test-writer

<!-- encoding: utf-8 -->

Write hermetic pytest tests with coverage, mocking, and tempfile fixtures.

**Load this skill at the start of every implementation task, before writing any implementation code.**

## General Patterns

- All tests are hermetic — no network calls, no real API
- Mock `requests.Response` with `Mock(spec=requests.Response)`
- CLI tests use `capsys` fixture
- Temp files: `NamedTemporaryFile(mode="w", ...)` + `path.unlink(missing_ok=True)` in `finally`
- Parametrize with `@pytest.mark.parametrize`
- Group tests in classes: `TestFoo`, `TestFooAdditional`

## SE Site Patterns

### Available Fixtures (from `tests/conftest.py`)

| Fixture | Scope | Purpose |
|---------|-------|---------|
| `client` | function | Empty DB, Flask test client |
| `app_ctx` | function | DB-only operations, no web client |
| `seeded_client` | function | Pre-seeded DB (users, staff, areas, worktypes, etc.) |
| `logged_client` | function | Seeded DB + logged-in as `a.terekhov@spbu.ru` |

Shared role/entity fixtures (`make_theme`, `admin_client`, `reviewer_client`, …) are defined **once** in `tests/conftest.py` — never copy a fixture into a new test module (duplicates trip the CI pylint-similarities check R0801). Canonical policy: `docs/TESTING.md` §1 "Shared fixtures live in conftest".

### Test Helpers

```python
def assert_ok(client, path, methods=None, data=None, code=None):
    """GET (or POST) a path, assert status matches. Default: GET 200."""

def assert_ok_or_redirect(client, path):
    """GET a path, assert 200 or 302 (redirect)."""
```

### Writing Tests

**Route test pattern** (public page):

```python
class TestPublicPages:
    def test_index_loads(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
```

**Route test pattern** (authenticated page):

```python
class TestAuthPages:
    def test_profile_loads(self, logged_client):
        resp = logged_client.get("/profile.html")
        assert resp.status_code == 200
```

**Parametrized route tests**:

```python
@pytest.mark.parametrize("path,code", [
    ("/login.html", {200}),
    ("/profile.html", {200, 302}),  # depends on auth state
])
def test_public_routes(self, client, path, code):
    assert_ok(client, path, code=code)
```

**DB interaction tests** (no web client needed):

```python
def test_some_query(self, app_ctx):
    from se_models import Users
    u = Users.query.filter_by(email="a.terekhov@spbu.ru").first()
    assert u is not None
    assert u.first_name == "Андрей"
```

**Session injection** (bypass login for authenticated routes):

```python
def test_with_logged_in_user(self, seeded_client):
    from se_models import Users
    u = Users.query.filter_by(email="a.terekhov@spbu.ru").first()
    with seeded_client.session_transaction() as sess:
        sess["_user_id"] = str(u.id)
    resp = seeded_client.get("/practice")
    assert resp.status_code == 200
```

### Known Test Quirks

- `init_db()` must not be called twice without `db.session.remove()` in between
- FTS5 index is inside the SQLite DB — copying the DB file also copies the search index
- APScheduler is env-gated in tests (`SE_START_SCHEDULER=0` in conftest before importing `flask_se`) to avoid `no such table: notification` errors
- Use `logged_client` fixture instead of login POST to avoid scrypt hash issues on Python 3.13
- Assert `resp.status_code` against a set: `{200}` not `200`, to allow easy widening

### CSRF-protected routes (login, POST forms)

- Tests default to `WTF_CSRF_ENABLED=False` (conftest). To assert CSRF behavior, flip `app.config["WTF_CSRF_ENABLED"] = True` and restore in `finally` (see `test_csrf_protects_post_forms`).
- The test client defaults to HTTP, so Flask-WTF's SSL-strict referrer check is **skipped** (`request.is_secure` is False). Exercise the HTTPS branch with `client.environ_base = {"wsgi.url_scheme": "https"}`; the test client sends no `Referer` by default — which is exactly the no-referrer case under test.
- Module-level `RateLimiter` singletons (`LOGIN_RATE_LIMITER`, `PASSWORD_RECOVERY_RATE_LIMITER`, `REGISTER_RATE_LIMITER`) persist across tests in a process and throttle repeated POSTs from the same test IP. Patch `.allow` per test: `patch.object(flask_se_auth.PASSWORD_RECOVERY_RATE_LIMITER, "allow", return_value=True)`.

### Schema/DDL tests: swap the engine per test

For schema-management code (`ensure_schema()`, auto-migrate), tests need their own DB state without touching the fixture DB. Swap the engine the same way `conftest._set_db_uri()` does, and restore it in `finally`:

```python
import flask_se_config as fsc
from sqlalchemy import create_engine, inspect, text
from flask_se import app, db

_dir = tempfile.mkdtemp()
try:
    with app.app_context():
        old_name, old_path = fsc.SQLITE_DATABASE_NAME, fsc.SQLITE_DATABASE_PATH
        old_uri = app.config["SQLALCHEMY_DATABASE_URI"]
        old_engine = db.engines.get(None)
        try:
            fsc.SQLITE_DATABASE_NAME = "auto.db"                     # ensure_schema reads these globals
            fsc.SQLITE_DATABASE_PATH = _dir
            app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{Path(_dir) / 'auto.db'}"
            db.engines[None] = create_engine(f"sqlite:///{Path(_dir) / 'auto.db'}")  # db.engines is a dict at runtime
            ensure_schema()
            assert "users" in inspect(db.engine).get_table_names()
        finally:
            fsc.SQLITE_DATABASE_NAME, fsc.SQLITE_DATABASE_PATH = old_name, old_path
            app.config["SQLALCHEMY_DATABASE_URI"] = old_uri
            if old_engine is not None:
                db.engines[None] = old_engine
            else:
                db.engines.pop(None, None)
finally:
    shutil.rmtree(_dir, ignore_errors=True)
```

Notes: `db.engines[None] = ...` is a runtime dict (the type stub says `Mapping`, ignore the checker noise — basedpyright only gates `src/`); `current_app` must be accessed inside `app.app_context()`; use `tempfile.mkdtemp()` (never `NamedTemporaryFile` — see §Per-test temp directories).

### Filter-output tests (autoescape regression)

A template filter that returns a plain `str` gets **re-escaped by Jinja autoescape** when used as `{{ x|filter }}` — direct filter-call assertions (`md("- a")`) never catch this. Assert through the Jinja environment:

```python
def test_filter_renders_unescaped(self, app_ctx):
    from flask import current_app
    tmpl = current_app.jinja_env.from_string("{{ text|markdown }}")
    out = tmpl.render(text="[x](https://example.org)\n\n- a")
    assert '<a href="https://example.org"' in out
    assert "<ul>" in out
    assert "&lt;" not in out
```

If the filter marks output safe (`Markup`), also assert the XSS guard separately (sanitize-before-Markup is mandatory for user-authored content).

### Targeted subset runs: use `--no-cov`

`pyproject.toml` `addopts` sets `--cov-fail-under=80`. A targeted run (`pytest tests/test_x.py`) fails the coverage gate at ~40% and masks pass/fail. Add `--no-cov` for red/green iteration (never `-q`; log the run): `uv run pytest tests/test_app.py --no-cov 2>&1 | tee .tmp/test_app.log`. Only the full-suite reference run must meet the 80% gate.

### Template-output guardrail

Enforce a raw-HTML policy structurally: scan every template and fail if `|safe` is used without the sanitizing filter:

```python
def test_no_raw_safe_output(self):
    from pathlib import Path
    root = Path(__file__).resolve().parent.parent / "src" / "templates"
    bad = []
    for p in root.rglob("*.html"):
        for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            if "|safe" in line and "|safe_html" not in line:
                bad.append(f"{p.relative_to(root)}:{i}: {line.strip()}")
    assert not bad, "raw |safe without |safe_html:\n" + "\n".join(bad)
```

### Structural source guards (CSP, autocomplete, exception swallowing)

Source-scanning guards in `tests/test_template_guards.py` (PR-3, 2026-08-31) enforce policies that a browser-based test can't: no inline `onX=` handlers or `javascript:` hrefs (dead under the strict nonce CSP), `autocomplete` on credential inputs, and no silent `except: pass` unless `# noqa`-annotated. When adding a template feature that needs JS wiring, extend these guards rather than adding per-endpoint assertions — the scan runs in seconds and fails at the source.
