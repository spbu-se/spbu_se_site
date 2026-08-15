<!-- encoding: utf-8 -->

# Code Issues Discovered During Test Coverage

Known production bugs and security findings, prioritized by severity, with fix status. FIXED entries are removed once their fix is merged — `git history` and `docs/RETROSPECTIVES.md` preserve the details; this file tracks what is still open, pending, or intentionally deferred.

Covers: known production bugs and security findings, prioritized by severity, with fix status. Does not cover: process gaps — see `docs/RETROSPECTIVES.md`, testing strategy — see `docs/TESTING.md`.

## P0 — Production Bugs (crash on missing form fields)

None open. Historical crash-on-missing-form-field bugs (`register_basic`, `user_profile`, `submit_thesis_on_review`) were fixed in sessions 3-4 of the 2026-07 coverage run.

## P1 — Edge Cases (may crash under specific conditions)

None open. Historical edge cases (`post_ranking_score` negative args, `get_thesis_type_id_string` bounds) fixed in the 2026-07 coverage run.

## P2 — Code Quality Issues

### Practice file-upload routes — high cyclomatic complexity

Routes like `practice_preparation` have deeply nested `if/elif` blocks (`src/flask_se_practice.py`). Measured 2026-07: `practice_preparation` = F (74), `get_remaining_time` = D (26), `practice_goals_tasks` = C (19); average file = C (12.2). Requires refactoring before additional tests can be written. Open — no owner.

## Security work — status

All findings from the 2026-08-01 sweep (#187), the 2026-08-02 full audit (#193, phases 1-5 incl. SQLite path alignment), the 2026-08-14 release fixes (#212: deploy-on-publish, upload DoS guard), and the 2026-08-15 markdown/safe-html render-time sanitization (#214) are **FIXED and merged**. Regression tests live in `tests/test_auth_views.py` (`TestSecurityCritical`, `TestSecurityMedium`) and `tests/test_app.py` (`TestMarkdownFilter`, `TestSafeHtmlFilter`, `TestRawHtmlGuardrail`).

### Open / intentional

- **Practice admin vs staff role separation** — both use the same `user_is_staff` guard by design; staff are the operators. Deferred; revisit if a curator-only role is needed.
- Dependabot Pillow + Flask alerts still show open in the GH UI but the manifest is already patched (Pillow 12.3.0, Flask 3.1.3) — auto-resolve on the next Dependabot scan of `current`.

### Dismissed (vendored/client-side, "won't fix")

- 58 × Unsafe jQuery plugin — Bootstrap 4 dist bundle in `src/static/assets/libs/`
- 4 × Unsafe jQuery plugin — jquery.mask-plugin dist bundle
- 2 × DOM text reinterpreted as HTML — jQuery template, server-provided content
- Secret-scanning google_api_key — public Google Maps JS browser key (referrer-restricted, client-side)
- CodeQL #173 (clear-text storage at `flask_se_auth.py` avatar write) — verified false positive (writes image bytes, not the token), dismissed with reason
