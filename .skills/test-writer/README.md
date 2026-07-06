# test-writer

<!-- encoding: utf-8 -->

Write hermetic pytest tests with coverage, mocking, and tempfile fixtures.

**Load this skill at the start of every implementation task, before writing any implementation code.**

## General Patterns

- All tests are hermetic вЂ” no network calls, no real API
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
    assert u.first_name == "РђРЅРґСЂРµР№"
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
- Whoosh index uses a temp dir (set via `app.config["WHOOSHEE_DIR"]` in conftest)
- APScheduler is shut down at conftest module level to avoid `no such table: notification` errors
- Use `logged_client` fixture instead of login POST to avoid scrypt hash issues on Python 3.13
- Assert `resp.status_code` against a set: `{200}` not `200`, to allow easy widening
