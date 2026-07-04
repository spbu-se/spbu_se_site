# OPEN_QUESTIONS

Unresolved questions from this session — to be answered by user review.

## Current

- **`post_ranking_score` negative args bug** — `flask_se_config.py:84`: passing negative upvotes with zero age produces complex numbers; `(0 / 0) / (views+1)` raises `ZeroDivisionError`. Needs input validation.
- **`get_thesis_type_id_string` out-of-range bug** — `flask_se_config.py:120`: `type_id_string[id - 1]` raises `IndexError` for IDs < 1 or > 10. Needs bounds check.

## Resolved

- `password_recovery.html` 500 on production — fixed with stub template
- Python version mismatch: postpone Docker update, keep prod on 3.9
- Signoff: no signoff for 12 hours, commit unsigned to staging
