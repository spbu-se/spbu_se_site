# API Reference — Flask Routes

<!-- encoding: utf-8 -->

All routes, methods, view functions, and descriptions for the SE Site.

Covers: all route endpoints, HTTP methods, view function names, descriptions. Does not cover: database models — see `docs/SCHEMA.md`, architecture — see `docs/ARCHITECTURE.md`, feature requirements — see `docs/REQUIREMENTS.md`.

## Public Pages

| Route | Method | View Function | Description |
|---|---|---|---|
| `/` | GET | `index` | Homepage with top 10 news |
| `/index.html` | GET | `index_html` | **301** redirect to `/` |
| `/research-directions` | GET | `research_directions` | Research areas listing |
| `/contacts.html` | GET | `contacts` | Contact page |
| `/department/staff.html` | GET | `department_staff` | Staff listing from DB |
| `/frequently-asked-questions.html` | GET | `frequently_asked_questions` | FAQ page |
| `/nooffer` | GET | `nooffer` | No-offer page |
| `/404.html` | GET | `status_404` | Custom 404 page |
| `/robots.txt` | GET | static | Crawler rules; disallows admin/AJAX/auth paths |
| `/humans.txt` | GET | static | Site/team credits |
| `/llms.txt` | GET | static | Agent-facing site index (LLM-friendly) |
| `/sitemap.xml` | GET | `sitemap` | Sitemap index referencing `sitemap-static.xml` + `sitemap-theses-<year>.xml` |
| `/Sitemap.xml` | GET | `sitemap` | Case-sensitive alias for `sitemap.xml` |
| `/sitemap-static.xml` | GET | `sitemap_static` | Static pages, `lastmod` = deploy constant |
| `/sitemap-theses-<year>.xml` | GET | `sitemap_theses` | Published `thesis_card` URLs for a year, `lastmod` = year date; 404 for empty years |

## Agent-Facing / SEO Endpoints

| Route | Method | View Function | Description |
|---|---|---|---|
| `/.well-known/llms.txt` | GET | `well_known_llms` | 301 to `/llms.txt` (single source; for tooling that only probes `.well-known`) |
| `/security.txt` | GET | `security_txt` | 301 to `/.well-known/security.txt` (RFC 9116 root alias) |
| `/.well-known/security.txt` | GET | static | RFC 9116 security contact (`mailto:dluciv@spbu.ru`) |
| `/opensearch.xml` | GET | static | OpenSearch description → `theses.html?search={searchTerms}`; autodiscovered via `<link rel="search">` in the base templates |
| `/bachelor/` | GET | legacy redirect | 301 to `/bachelor/software-engineering.html` (section index) |
| `/master/` | GET | legacy redirect | 301 to `/master/software-engineering.html` (section index) |
| `/department/` | GET | legacy redirect | 301 to `/department/staff.html` (section index) |
| `/students/` | GET | legacy redirect | 301 to `/students/index.html` (section index) |

## Student Pages

| Route | Method | View Function | Description |
|---|---|---|---|
| `/students/index.html` | GET | `students` | Students overview |
| `/students/scholarships.html` | GET | `scholarships` | Scholarships listing |

## Bachelor Programs

| Route | Method | View Function | Description |
|---|---|---|---|
| `/bachelor/admission.html` | GET | `bachelor_admission` | Admission info with random thesis samples |
| `/bachelor/programming-technology.html` | GET | `bachelor_programming_technology` | PT curriculum page |
| `/bachelor/software-engineering.html` | GET | `bachelor_software_engineering` | SE curriculum page |
| `/bachelor/application.html` | GET | `bachelor_application` | Application info |

## Master Programs

| Route | Method | View Function | Description |
|---|---|---|---|
| `/master/information-systems-administration.html` | GET | `master_information_systems_administration` | ISA program page |
| `/master/software-engineering.html` | GET | `master_software_engineering` | SE master page |

## Authentication

| Route | Method | View Function | Description |
|---|---|---|---|
| `/login.html` | GET, POST | `login_index` | Login form |
| `/register_basic.html` | GET, POST | `register_basic` | Register with email/password |
| `/password_recovery.html` | GET, POST | `password_recovery` | Password recovery (stub) |
| `/profile.html` | GET, POST | `user_profile` | Edit user profile |
| `/upload_avatar` | GET, POST | `upload_avatar` | Upload avatar image |
| `/logout` | GET | `logout` | Logout |
| `/vk_login` | GET | `vk_login` | VK OAuth redirect (mints + stores `state`) |
| `/vk_callback` | GET | `vk_callback` | VK OAuth callback |
| `/google_login` | GET | `google_login` | Google OAuth redirect |
| `/google_callback` | GET | `google_callback` | Google OAuth callback |

## Thesis Archive

| Route | Method | View Function | Description |
|---|---|---|---|
| `/theses.html` | GET | `theses_search` | Thesis search with filters. **Server-rendered** (cards + pagination in initial HTML; JS progressively enhances filtering). Full-text search uses SQLite FTS5 virtual table `thesis_fts` (columns: name_ru, description, author, text). OG: when `search` param present, og:title = `Результаты поиска: "<query>"`. |
| `/fetch_theses` | GET | `fetch_theses` | AJAX paginated thesis list fragment (same query as `theses_search`, shared `_query_theses()` helper). Query params: `worktype`, `supervisor`, `consultant` (free-text substring), `course`, `startdate`, `enddate`, `search`, `page` |
| `/post_theses` | GET, POST | `post_theses` | Upload new thesis |
| `/theses_tmp.html` | GET | `theses_tmp` | List temp theses for review |
| `/theses_delete_tmp` | POST | `theses_delete_tmp` | Delete temp thesis |
| `/theses_add_tmp` | POST | `theses_add_tmp` | Approve/publish temp thesis |
| `/thesis_download` | GET | `download_thesis` | Download thesis PDF (tracks count) |
| `/thesis_card` | GET | `thesis_card` | Shareable card for a single non-temporary thesis (OG: title = work name + year, type article, canonical). Query param: `thesis_id`. Redirects to `/theses.html` on 0/missing/temporary. |

## News

| Route | Method | View Function | Description |
|---|---|---|---|
| `/news/` | GET | `list_news` | News listing (paginated by rank) |
| `/news/index.html` | GET | `list_news` | Alias for `/news/` |
| `/news/item.html` | GET | `get_post` | Single news post (OG: title = post title, type article, description = plain-text excerpt) |
| `/news/submit.html` | GET, POST | `submit_post` | Submit news |
| `/news/post_vote` | POST | `post_vote` | Upvote/downvote news |
| `/news/delete` | POST | `delete_post` | Delete own news post |

## Diploma Themes

| Route | Method | View Function | Description |
|---|---|---|---|
| `/diplomas/` | GET | `diplomas_index` | Browse approved themes — **server-rendered** list (JS progressively enhances filtering) |
| `/diplomas/index.html` | GET | `diplomas_index` | Alias for `/diplomas/` |
| `/diplomas/theme.html` | GET | `get_theme` | View single theme (OG: title = theme title, type article, description = plain-text `_og_description` of theme description or title) |
| `/diplomas/add_theme.html` | GET, POST | `add_user_theme` | Add new theme |
| `/diplomas/user_themes.html` | GET | `user_diplomas_index` | User own themes |
| `/diplomas/delete_theme.html` | POST | `delete_theme` | Delete own theme |
| `/diplomas/edit_theme.html` | GET, POST | `edit_user_theme` | Edit own theme |
| `/diplomas/fetch_themes` | GET | `fetch_themes` | AJAX paginated themes |
| `/diplomas/archive_theme` | POST | `archive_theme` | Archive own theme |
| `/diplomas/unarchive_theme` | POST | `unarchive_theme` | Unarchive own theme |

> **Legacy**: in the Flask-Admin era (pre-PR #11) `delete_theme.html`,
> `archive_theme`, and `unarchive_theme` accepted any method (the author pages
> linked to them with plain GET anchors). They are POST-only since
> (state-changing, CSRF/POST policy); a GET never reaches them — the site
> catch-all rule `/<path:filename>` matches first and returns the 404 page.
> The flows still work via the POST forms in `theme.html`/`user_themes.html`.
> See the §Legacy method changes table at the end.

## Thesis Review

| Route | Method | View Function | Description |
|---|---|---|---|
| `/review/` | GET | `thesis_review_index` | Review dashboard — **server-rendered** list (JS progressively enhances filtering) |
| `/review/index.html` | GET | `thesis_review_index` | Alias for `/review/` |
| `/review/submit` | GET, POST | `submit_thesis_on_review` | Submit thesis for review |
| `/review/edit` | GET, POST | `edit_thesis_on_review` | Edit submitted thesis |
| `/review/delete` | POST | `delete_thesis_on_review` | Delete own submission |
| `/review/review` | GET, POST | `review_thesis_on_review` | Enter/submit review form |
| `/review/reviewed` | GET, POST | `review_submit_review` | Submit completed review |
| `/review/review_result` | GET | `review_result_thesis_on_review` | View review result |
| `/review/fetch_thesis_on_review` | GET | `fetch_thesis_on_review` | AJAX filtered list |
| `/review/become_thesis_reviewer` | GET | `review_become_thesis_reviewer_ask` | Reviewer signup |
| `/review/become_thesis_reviewer_confirm` | POST | `review_become_thesis_reviewer_confirm` | Confirm reviewer signup |

> **Legacy**: in the Flask-Admin era (pre-PR #11) `delete` and
> `become_thesis_reviewer_confirm` accepted GET (plain links). They are
> POST-only since (state-changing, CSRF/POST policy); a GET never reaches them
> — the site catch-all rule `/<path:filename>` matches first and returns the
> 404 page. `/review/review` additionally accepts POST (form submission). See
> the §Legacy method changes table at the end.

## Internships

| Route | Method | View Function | Description |
|---|---|---|---|
| `/internships/internships_index.html` | GET | `internships_index` | Browse internships |
| `/internships/index` | GET | `old_internships_index` | Old redirect endpoint |
| `/internships/fetch_internships` | GET | `fetch_internships` | AJAX filtered list |
| `/internships/add` | GET, POST | `add_internship` | Add internship |
| `/internships/<int:id>` | GET, POST | `page_internship` | View single internship (OG: title = vacancy name, type article, canonical fixed to `/internships/<id>`) |
| `/internships/<int:id>/delete` | POST | `delete_internship` | Delete internship |
| `/internships/<int:id>/update` | GET, POST | `update_internship` | Update internship |

## Practice — Student

| Route | Method | View Function | Description |
|---|---|---|---|
| `/practice` | GET, POST | `practice_index` | Student dashboard + notifications |
| `/practice/` | GET, POST | `practice_index` | Alias for `/practice` |
| `/practice/guide/` | GET | `practice_guide` | Practice guide |
| `/practice/new/` | GET, POST | `practice_new_thesis` | Create new practice/thesis |
| `/practice/data_for_practice/` | GET, POST | `practice_data_for_practice` | Edit worktype/area |
| `/practice/choosing_topic/` | GET, POST | `practice_choosing_topic` | Choose topic + supervisor |
| `/practice/edit_theme/` | GET, POST | `practice_edit_theme` | Edit thesis topic |
| `/practice/goals_tasks/` | GET, POST | `practice_goals_tasks` | Set goal + tasks |
| `/practice/add_new_report/` | GET, POST | `practice_add_new_report` | Submit weekly report |
| `/practice/workflow/` | GET, POST | `practice_workflow` | View/edit reports |
| `/practice/preparation_for_defense/` | GET, POST | `practice_preparation` | Upload materials for defense |
| `/practice/defense/` | GET | `practice_thesis_defense` | Defense info page |

## Practice — Staff/Supervisor

| Route | Method | View Function | Description |
|---|---|---|---|
| `/practice_staff` | GET | `index_staff` | Staff dashboard (advisees) |
| `/practice_staff/` | GET | `index_staff` | Alias for `/practice_staff` |
| `/practice_staff/thesis/` | GET, POST | `thesis_staff` | View/send notifications to student |
| `/practice_staff/reports/` | GET, POST | `reports_staff` | View/comment reports |
| `/practice_staff/finished_thesises/` | GET | `finished_thesises_staff` | Completed theses |

## Practice — Admin/Curator

| Route | Method | View Function | Description |
|---|---|---|---|
| `/practice_admin` | GET, POST | `index_admin` | Admin dashboard |
| `/practice_admin/` | GET, POST | `index_admin` | Alias for `/practice_admin` |
| `/practice_admin/choose_area_worktype` | GET | `choose_area_and_worktype_admin` | Area/worktype redirect |
| `/practice_admin/finished_thesises` | GET | `finished_thesises_admin` | Completed works |
| `/practice_admin/thesis` | GET, POST | `thesis_admin` | View/edit single thesis |
| `/practice_admin/yandex_code` | GET | `yandex_code` | Yandex OAuth callback |
| `/practice_admin/thesis_to_archive` | GET, POST | `archive_thesis` | Archive thesis to main repository |

## Summer Schools

| Route | View Function |
|---|---|
| `/summer_school_2021.html` | `create_summer_school_view(2021)` |
| `/summer_school_2022.html` | `create_summer_school_view(2022)` |
| `/summer_school_2024.html` | `create_summer_school_view(2024)` |
| `/summer_school_2026.html` | `create_summer_school_view(2026)` |
| `/summer_school_list.html` | `summer_school_list` |

## Scholarships

| Route | View Function |
|---|---|
| `/scholarships/{1..13}.html` | `get_scholarships_{1..13}` (13 individual pages) |

## Admin

| Route | Description |
|---|---|
| `/admin/` | custom admin dashboard (thesis upload API info; the API key itself is stored server-side in `configs/flask_se_thesis.conf` and never shown in the UI). Access: role >= 2 |
| `/admin/user/` | Users CRUD. Access: role >= 5 |
| `/admin/staff/` | Staff CRUD. Access: role >= 5 |
| `/admin/thesis/` | Thesis CRUD. Access: role >= 5 |
| `/admin/summerschool/` | Summer school projects CRUD. Access: role >= 5 |
| `/admin/posts/` | News CRUD. Access: role >= 5 |
| `/admin/companies/` | Company (theme sources) CRUD. Delete is blocked while a company is referenced by themes or reviewers. Access: role >= 5 |
| `/admin/diplomathemes/` | Diploma themes CRUD. Access: role >= 5. Full edit of any status incl. `levels` multi-select and FK dropdowns; list status filter `?status=` (0-4, incl. archive) |
| `/admin/diplomathemes/archive/` | POST archive one theme (status → 3, previous status preserved in `prev_status`); author notified by mail when the theme was in 0/1/2. Access: role >= 5 |
| `/admin/diplomathemes/reopen/` | POST restore an archived theme to its preserved status (legacy rows without `prev_status` → 0). Access: role >= 5 |
| `/admin/diplomathemes/bulk-archive/` | POST archive all themes in status 0/1/2 (`prev_status` preserved); rejected and already-archived untouched; one deduped notification per author. Access: role >= 5 |
| `/admin/diplomathemes/bulk-reopen/` | POST restore every archived theme to its preserved status (legacy rows → 0). Access: role >= 5 |
| `/admin/reviewdiplomathemes/` | Review/moderate diploma themes (queue of `status < 2`). Access: role >= 3. Rows/title link into the review form (restored #275); text search (`?search=`) over title/description/requirements and a status filter (`?status=`) added #276; FK fields on the edit form render as dropdowns (generic CrudView behavior). Details at `/admin/reviewdiplomathemes/details/?id=N`, edit form at `/admin/reviewdiplomathemes/edit/?id=N` (role >= 3) |
| `/admin/currentthesis/` | Current theses CRUD. Access: role >= 5 |

## Legacy method changes (Flask-Admin era → current)

The theme-reporting and review/acceptance URL paths themselves did not change
with PR #11 (Flask-Admin → custom `CrudView`); only HTTP methods and the
admin-review interaction surface changed. Every row is locked by
`tests/test_theme_route_parity.py`.

| Route | Old (Flask-Admin era) | Current | Why |
|---|---|---|---|
| `/diplomas/delete_theme.html` | any method (GET anchor) | POST | State change under CSRF/POST policy — GET now returns the 404 page (catch-all `/<path:filename>` shadows Werkzeug's 405) |
| `/diplomas/archive_theme` | any method (GET anchor) | POST | Same |
| `/diplomas/unarchive_theme` | any method (GET anchor) | POST | Same |
| `/review/delete` | GET | POST | Same |
| `/review/become_thesis_reviewer_confirm` | GET | POST | Same |
| `/review/review` | GET | GET, POST | Form submission added (not a removal) |
| `/admin/reviewdiplomathemes/` | Flask-Admin list (`?search`/filters/`page_size`) | CrudView table: `?search` (text) + `?status=` filter + `page_size`/`sort` | Navigation fixed in #275; text search + status filter restored in #276; FK fields are dropdowns instead of raw ids (#276) |

All other theme paths — the `/diplomas/` propose/edit pages, the `/practice/*`
student/staff/admin flows (incl. `choosing_topic/`, `edit_theme/`), and the
`/review/` dashboard/submit/edit/reviewed/result pages — are method- and
path-identical between the old and current site.

## Error Handling

All errors render HTML pages. No JSON API endpoints exist.
`@app.errorhandler(404)` renders the same template as the `/404.html` route listed in Public Pages.
