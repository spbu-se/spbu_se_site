# OPEN_QUESTIONS

Unresolved questions from this session — to be answered by user review.

## Resolved

- `password_recovery.html` 500 on production — fixed with stub template
- Python version mismatch: postpone Docker update, keep prod on 3.9
- Signoff: no signoff for 12 hours, commit unsigned to staging
- **`post_ranking_score` negative args bug** — fixed with input validation (clamp to >=0)
- **`get_thesis_type_id_string` out-of-range bug** — fixed with bounds check
