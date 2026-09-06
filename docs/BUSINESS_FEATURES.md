# Business Features — User Workflows

<!-- encoding: utf-8 -->

User-facing feature journeys are the site's primary business value. This doc maps each role's end-to-end workflow to its entry routes, the "useful result" a user must be able to achieve, and the tests that guard the journey.

Covers: role journeys, entry routes, UX contracts, business value, parity-test guards. Does not cover: the full endpoint registry (route methods/params) — see `docs/API_REFERENCE.md`; module responsibilities — see `docs/ARCHITECTURE.md`; feature specs/roles as implementation input — see `docs/REQUIREMENTS.md`; database — see `docs/SCHEMA.md`.

## Why this doc exists

Prior to 2026-09-06 the site had no canonical statement of *which user journeys are the product* and no maintained map from journey → routes → expected result. The consequence was issue #274: the admin theme-review editing flow silently regressed (Flask-Admin → custom CrudView, PR #11) and was only noticed when a user complained that the queue was a dead, non-clickable table. Doctrine Layer 2 priority #1 ("Business workflows are the product") and this map are the response.

## Maintenance discipline

- A change to any user-facing route, page, or flow **must** update the matching journey rows here (entry routes, methods, UX contract) in the same change.
- A route/flow **removal or narrowing** additionally requires a `docs/DESIGN_DECISIONS.md` entry stating the deliberate deviation and its user impact.
- Route-parity tests keep the map executable: `tests/test_theme_route_parity.py` and `tests/test_admin_review_ux.py` assert the theme-review journeys below. Extend parity coverage when a new journey is mapped.
- Enforcement level (2026-09-06, user decision): documentation + existing parity tests. No CI gate yet — escalate to a per-workflow CI smoke gate if a journey regresses again (see `docs/DEVELOPMENT_PROCESS.md` §Process Identity → Project Doctrine and the escalation ladder in `.skills/retrospective-analysis`).

## Coverage status

| Journey | Status | Guarded by |
|---|---|---|
| Theme proposal → review → accept (DiplomaThemes) | Mapped (2026-09-06, from the #274/#277 audit) | `test_theme_route_parity.py`, `test_admin_review_ux.py` |
| Thesis (ВКР) peer review (`/review/*`) | Mapped (reachability) | `test_theme_route_parity.py` |
| Practice student flow (choose/edit topic, reports) | Mapped (reachability) | `test_theme_route_parity.py` |
| News, internships, thesis archive, auth/profile | Not yet mapped | — |

## Journeys

### 1. Propose a theme (faculty, external partner, student)

Authenticated user turns a research/industry idea into a catalog theme.

| Step | Entry route | Useful result (UX contract) |
|---|---|---|
| Propose | `GET/POST /diplomas/add_theme.html` | Form with title/description/requirements, level, "from whom" (company); valid submit creates the theme with status "на проверке" |
| My themes | `GET /diplomas/user_themes.html` | List of own themes with status and the reviewer's `comment`; empty state redirects to the catalog |
| View a theme | `GET /diplomas/theme.html?id=N` | Public theme card; the author additionally sees edit/delete/archive controls on their own themes |
| Edit own theme | `GET/POST /diplomas/edit_theme.html?theme_id=N` | Author edits title/description/requirements/level/company; a save re-submits the theme (status → "на проверке") |
| Delete / archive / unarchive own theme | `POST /diplomas/delete_theme.html`, `archive_theme`, `unarchive_theme` | State change only via POST (CSRF policy). **Legacy GET links are dead** — a GET returns the 404 page (catch-all); see `API_REFERENCE.md` §Legacy method changes. Archive is **status-preserving** (#280): unarchive returns an approved theme straight to the catalog (`status 2`), never resets it to the review queue |

Author-facing e-mails ("тема отклонена" / "необходимо доработать") link to `user_themes.html`.

### 2. Review and accept themes (department reviewer, role ≥ 3)

The acceptance gate of the theme pipeline.

| Step | Entry route | Useful result (UX contract) |
|---|---|---|
| Open queue | `GET /admin/reviewdiplomathemes/?search=&status=` | Table of themes with `status < 2`, each theme reachable from its title/row (**restored #275**); text search + status filter (**added #276**) |
| Review a theme | `GET/POST /admin/reviewdiplomathemes/edit/?id=N` | Form to edit the theme and set status: "на проверке" / "требуется доработка" / "одобрена" / "отклонена" + comment; reject/redo mails the author. FK fields (author/consultant/supervisors/company) are dropdowns, not raw id inputs (**#276**) |
| Details | `GET /admin/reviewdiplomathemes/details/?id=N` | Read-only summary that links on to the edit form |
| Queue reminders | count e-mail → `/admin/reviewdiplomathemes/` | Scheduled mail points reviewers at the queue |

Remaining gaps (issue #70 umbrella): full edit of approved themes incl. `levels`
multi-select (#279), bulk semester reset (#281), and a Company/sources admin
CRUD (#282). Resolved: FK dropdowns + queue search/status filter (#276),
single approved-theme archive/re-open with author notification,
status-preserving (#280).

### 2b. Admin theme archive / re-open (role ≥ 5)

| Step | Entry route | Useful result (UX contract) |
|---|---|---|
| Archive a theme (e.g. an obsolete or already-selected approved theme) | `POST /admin/diplomathemes/archive/` (id) | `status` → archive (`3`), previous status preserved in `prev_status`; the author is notified by mail (#280) |
| Re-open | `POST /admin/diplomathemes/reopen/` | restores the preserved status — an approved theme returns straight to the public catalog; legacy archived rows fall back to the queue |

### 3. Practice student flow (choose/edit a practice topic)

| Step | Entry route | Useful result (UX contract) |
|---|---|---|
| Dashboard | `GET/POST /practice/` | Student dashboard + notifications |
| Choose topic + supervisor | `GET/POST /practice/choosing_topic/` | Student records their chosen practice topic |
| Edit thesis topic | `GET/POST /practice/edit_theme/` | Student edits the recorded topic |
| Reports/goals/defense | `GET/POST /practice/{goals_tasks,workflow,add_new_report,preparation_for_defense}/`, `GET /practice/defense/` | Weekly report loop and defense materials |

### 4. Thesis (ВКР) peer review (`/review/*`)

| Step | Entry route | Useful result (UX contract) |
|---|---|---|
| Dashboard | `GET /review/`, `/review/index.html` | Reviewer dashboard of works on review |
| Submit for review | `GET/POST /review/submit` | Student submits a work |
| Enter a review | `GET/POST /review/review` | Reviewer fills the rubric; submission is POST |
| Completed review | `GET/POST /review/reviewed` | Review stored; author later sees the result |
| View result | `GET /review/review_result` | Author reads the final review |
| Become reviewer / confirm | `GET /review/become_thesis_reviewer`; `POST /review/become_thesis_reviewer_confirm` | **Confirm is POST-only** (legacy GET dead); see `API_REFERENCE.md` §Legacy method changes |
