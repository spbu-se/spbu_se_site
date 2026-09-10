# Role & feature matrix

<!-- encoding: utf-8 -->

Covers: the permission surfaces per role, the seeded local accounts that exercise them, and the feature availability matrix. Does not cover: feature specs — see `docs/REQUIREMENTS.md`; endpoint details — see `docs/API_REFERENCE.md`.

Deterministic, code-derived map of the permission surfaces on the site and the
local accounts that exercise them. Every account below is seeded by
`src/se_seed_data.py` (single source of truth for accounts) with password `1`
(dev only, never used in prod), and each has a `Staff` row where the surface
requires staff membership rather than a numeric role.

## Permission model

Two orthogonal gates control access:

- **`Users.role` (integer)** — numeric tier, checked as `role >= level`:
  - `0` — regular user (default).
  - `2` — thesis contributor + the `/admin/` hub entrance (`THESIS_ROLE_LEVEL`).
  - `3` — reviewer: diploma-theme review queue and thesis-on-review flows (`REVIEW_ROLE_LEVEL`).
  - `5` — administrator: full CRUD admin views + bulk archive/reopen + `/logs` (`ADMIN_ROLE_LEVEL`).
- **`Staff` row membership** — orthogonal flag; gates the practice staff and
  practice admin areas (`flask_se_practice_staff.py`, `flask_se_practice_admin.py`).

Role levels `1` and `4` are unused.

## Accounts → surfaces

| Account | role | Staff | Surfaces it exercises |
|---------|------|-------|------------------------|
| `user@se.dev` | 0 | – | Public site, register/login/profile, own practice theses (as author) |
| `thesis@se.dev` | 2 | – | Thesis submission/upload, `/admin/` hub (no admin CRUD) |
| `review@se.dev` | 3 | – | Diploma-theme review queue, thesis-on-review review |
| `staff@se.dev` | 3 | ✓ | Practice staff + practice admin areas (Staff-gated, not role-gated) |
| `admin@se.dev` | 5 | ✓ | Everything: admin CRUD views, bulk archive/reopen, `/logs`, practice admin |

## Representative flows per surface

The E2E and role-journey suites (see `docs/TESTING.md`) derive their coverage
checklist from this table together with the feature journeys in
`docs/BUSINESS_FEATURES.md`:

- role `0` — register, edit own profile, list/search theses, read news.
- role `2` — submit and upload a thesis, own diploma themes.
- role `3` — review queued diploma themes; approve/reject; review theses.
- `Staff` — view/manage student practice theses and reports.
- role `5` — manage users/staff/news/theses/themes, bulk archive + reopen
  (incl. `prev_status` restore), view `/logs`.

A missing account or tier here is a seed bug — add it to `src/se_seed_data.py`,
not to a fixture (single source of truth).
