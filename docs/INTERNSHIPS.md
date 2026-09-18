# Internships — Removed Feature Architecture Note

<!-- encoding: utf-8 -->

Covers: the removed internship feature — its data model, routes, business rules, and the scope of its removal. Does not cover: the general practice/thesis workflows — see `docs/ARCHITECTURE.md`; the database schema — see `docs/SCHEMA.md`.

## Status

The internship feature ("Поиск IT-стажировок") was removed from the application in PR #1 (branch `feat/remove-internships`). The feature was unused: no nav entry, no routes, no templates, no JS, no tests remain. The database tables and ORM models were **kept** as tech debt — removing them would require a migration and risk breaking existing rows; they are documented here so future work can decide their fate.

## Data model (kept, untouched)

The ORM models live in `src/se_models.py` and are still created by `init_db`; seed data for the lookup tables is still inserted by `src/se_seed_data.py`.

| Table | Model | Key fields |
|-------|-------|------------|
| `internship_format` | `InternshipFormat` | `id`, `format` (e.g. online, offline) |
| `internship_tag` | `InternshipTag` | `id`, `tag` (e.g. Python, Go) |
| `internship_company` | `InternshipCompany` | `id`, `name`, `logo_uri` |
| `internships` | `Internships` | `id`, `name_vacancy`, `salary`, `company_id`, `requirements`, `date`, `more_inf`, `description`, `location`, `author_id`; many-to-many `format` (via `internships_format`) and `tag` (via `internships_tag`) |

`Users.internship_author` (one-to-many) also remains on the model.

## Removed routes

All seven routes were registered by `register_routes(app)` in `src/flask_se_internships.py` (deleted):

| Route | Methods | View |
|-------|---------|------|
| `/internships/index` | GET | `old_internships_index` — 301 redirect to the index |
| `/internships/internships_index.html` | GET | `internships_index` — list + filter page |
| `/internships/fetch_internships` | GET | `fetch_internships` — AJAX partial (pagination + filters) |
| `/internships/add` | GET, POST | `add_internship` — create vacancy |
| `/internships/<int:id>` | GET, POST | `page_internship` — vacancy detail |
| `/internships/<int:id>/delete` | POST | `delete_internship` |
| `/internships/<int:id>/update` | GET, POST | `update_internship` |

Related references removed in the same change: the `/internships` → `internships_index` redirect in `src/flask_se_static.py`, the four sitemap entries in `src/sitemap.py`, the `llms.txt` entry, the nav/footer links in the base templates, the internship JS block in `src/static/assets/js/se_scripts.js`, the `internship_author` admin exclusion in `src/flask_se_admin.py`, and the GDPR export entry in `src/flask_se_auth.py`.

## Business rules (historical)

- **Tag matching** — tag lookup was case-insensitive; a submitted tag was matched against `InternshipTag` by lowercased name and auto-created if absent.
- **Company** — a company was auto-created from the submitted name if it did not exist.
- **Format** — multi-select (`SelectMultipleField`, coerced to `int`); formats were seeded lookup rows.
- **Auth** — all CRUD routes required `@login_required`; anonymous users were redirected to login.
- **Listing** — the index rendered via AJAX (`fetch_internships`), paginated 10 items per page, filterable by format/company/tag.

## Removal scope

Deleted files: `src/flask_se_internships.py`, `src/se_internship_forms.py`, `src/templates/internships/` (7 templates), `tests/test_internships_deep.py`. Internship-only tests were trimmed from `tests/conftest.py`, `tests/test_auth_views.py`, `tests/test_jsonld.py`, `tests/test_og_cards.py`, `tests/test_se_forms.py`, `tests/test_se_models_deep.py`, `tests/test_init_db.py`.

Not removed (tech debt): the four tables/models above, `Users.internship_author`, and the seed data for `internship_format`/`internship_tag`. A future cleanup may drop them via a migration.
