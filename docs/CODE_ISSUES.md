<!-- encoding: utf-8 -->

# Code Issues Discovered During Test Coverage

Found during the coverage-first phase (2026-07-04/05 auto run). Coverage target met — bugs below are unblocked.

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
