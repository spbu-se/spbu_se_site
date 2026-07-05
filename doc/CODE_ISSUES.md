# Code Issues Discovered During Test Coverage

Found during the coverage-first phase (2026-07-04/05 auto run). **Do not fix until coverage reaches 90%.**

## P0 — Production Bugs (crash on missing form fields)

### `flask_se_auth.py:197` — `register_basic` crashes on missing `first_name`

```
first_name = request.form.get("first_name").strip()
AttributeError: 'NoneType' object has no attribute 'strip'
```

When `register_basic` receives a POST without `first_name` in the form data, `.get()` returns `None`, and `.strip()` throws `AttributeError`. The route then returns 500 (handled by Flask error handler).

**Fix**: Replace `.get("first_name").strip()` with `.get("first_name", "").strip()` (same pattern for `last_name`, `middle_name`, `how_to_contact`).

**Affected**: `test_auth_views.py::TestAuth::test_register_missing_fields` — currently marked `xfail`.

### `flask_se_auth.py:239-242` — `user_profile` crashes on missing form fields

```
last_name = request.form.get("last_name").strip()
first_name = request.form.get("first_name").strip()
middle_name = request.form.get("middle_name").strip()
how_to_contact = request.form.get("how_to_contact").strip()
```

Same `None.strip()` bug as `register_basic`. Any form submission missing one of these fields causes a 500 error.

**Fix**: Same pattern — use `.get(field, "")` for all four fields.

### `flask_se_review.py` — `submit_thesis_on_review` crashes on missing `title`

```
title = request.form.get("title").strip()
```

Same `None.strip()` bug when POSTing to `/review/submit` without `title` field.

**Affected**: `test_review.py::TestReviewSubmitFlow::test_review_submit_post` — currently marked `xfail`.

## P1 — Edge Cases (may crash under specific conditions)

### `flask_se_config.py:88` — `post_ranking_score` negative args (FIXED)

Already fixed in Week 1 of this auto run. Keeping for documentation completeness.

### `flask_se_config.py:122` — `get_thesis_type_id_string` bounds (FIXED)

Already fixed in Week 1 of this auto run.

## P2 — Code Quality Issues

### `se_models.py:278-281` — `CurrentThesis.__init__` doesn't accept all columns

```python
def __init__(self, author_id, worktype_id, area_id):
    self.author_id = author_id
    self.worktype_id = worktype_id
    self.area_id = area_id
```

The custom `__init__` overrides SQLAlchemy's default constructor, which normally accepts all columns as keyword arguments. This forced tests to use attribute assignment after construction.

**Fix**: Either remove the custom `__init__` (let SQLAlchemy generate it) or add `**kwargs` passthrough.

### `se_models.py:321-323` — `ThesisTask.__init__` uses positional args

```python
def __init__(self, task_text, current_thesis_id):
    self.task_text = task_text
    self.current_thesis_id = current_thesis_id
```

Same issue — custom `__init__` prevents keyword argument usage. Tests had to use positional style.

### `se_models.py:343-347` — `ThesisReport.__init__` uses positional args

Same issue as `ThesisTask`.

### `flask_se_practice.py` — File upload routes have high cyclomatic complexity

Routes like `practice_preparation` have deeply nested `if/elif` blocks (lines 442-659). Hard to test each branch without file upload fixtures.

### `flask_se_auth.py:48-53` — `redirect_next_url` helper returns `Any`

```python
def redirect_next_url(fallback=url_for("index")):
```

The `next` URL pattern is handled in a fragile way — no validation of the redirect target. Potential open redirect vulnerability if `next` parameter contains an external URL.

## P3 — Test Infrastructure Issues

### `conftest.py` — Mocks scrypt for all tests

```python
_ws.check_password_hash = lambda pwhash, password: True
```

This is safe for testing but means password security logic is never exercised. Consider a dedicated `secure_password_test` marker or fixture for password-specific tests.

### `conftest.py` — `practice_thesis` fixture has hardcoded user ID

```python
ct = CurrentThesis(author_id=1, worktype_id=1, area_id=1)
```

Uses `author_id=1` directly, which couples to seed data ordering. Should use a query to find the test user's ID instead.

## P4 — Deprecations

### `flask_se.py:413-427` — `AdminModelView` passes `db.session` instead of `db`

Flask-Admin 3.0 will require `db` instead of `db.session`. All 8 `admin.add_view(..., db.session)` calls need updating.

### `flask_se_auth.py:49` — `Users.query.get()` is legacy SQLAlchemy 1.x

```python
return Users.query.get(int(user_id))
```

`Query.get()` is deprecated in SQLAlchemy 2.0. Replace with `db.session.get(Users, int(user_id))`.

### `flask_se_practice_admin.py:152,258` — `send_file(download_name=...)` vs `attachment_filename=...`

The `download_name` parameter is for newer Flask. With older stubs, `attachment_filename` may be needed.
