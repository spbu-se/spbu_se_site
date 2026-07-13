# Schema Reference — Database Model Definitions

<!-- encoding: utf-8 -->

All SQLAlchemy models used by the SE Site. Database: SQLite (`se.db`).

Covers: table schemas with field types and relationships, seed data structure. Does not cover: endpoint documentation — see `docs/API_REFERENCE.md`, module architecture — see `docs/ARCHITECTURE.md`.

## Core Tables

### Users (`users`)

| Field | Type | Constraints | Description |
|---|---|---|---|
| `id` | Integer | PK, auto | Unique user ID |
| `email` | String(255) | Unique, nullable | Email address |
| `password_hash` | String(255) | nullable | pbkdf2:sha256 hash |
| `first_name` | String(255) | nullable=False | First name |
| `middle_name` | String(255) | nullable | Middle name (patronymic) |
| `last_name` | String(255) | nullable | Last name |
| `avatar_uri` | String(512) | default="empty.jpg" | Avatar image path |
| `role` | Integer | default=0 | 0=default, 5=admin |
| `how_to_contact` | String(512) | default="" | Contact info |
| `vk_id` | String(255) | nullable | VK social ID |
| `fb_id` | String(255) | nullable | Facebook social ID |
| `google_id` | String(255) | nullable | Google social ID |

Relationships: `staff`, `news` (posts), `thesises`, `current_thesises`, `reviewer`, `all_user_votes`, `internship_author`, `thesis_on_review_author`, diploma theme relations (4 FKs).

### Staff (`staff`)

| Field | Type | Constraints | Description |
|---|---|---|---|
| `id` | Integer | PK, auto | Unique staff ID |
| `user_id` | Integer | FK -> users.id, nullable=False | Linked user account |
| `official_email` | String(255) | Unique, nullable=False | SPbU email |
| `position` | String(255) | nullable=False | Academic position |
| `science_degree` | String(255) | nullable | Degree info |
| `still_working` | Boolean | default=False | Active status |

Relationships: `supervisor` -> Thesis, `adviser` -> Thesis, `current_thesises`.

### Thesis (`thesis`) — Main Archive

| Field | Type | Constraints | Description |
|---|---|---|---|
| `id` | Integer | PK, auto | Unique ID |
| `type_id` | Integer | FK -> worktype.id, nullable=False | Coursework, Bachelor, Master, etc. |
| `course_id` | Integer | FK -> courses.id, nullable=False | Educational program |
| `area_id` | Integer | FK -> areas_of_study.id | Research area |
| `name_ru` | String(512) | nullable=False | Russian title |
| `name_en` | String(512) | nullable | English title |
| `description` | String(4096) | nullable | Abstract |
| `text_uri` | String(512) | nullable | PDF path |
| `old_text_uri` | String(512) | nullable | Previous PDF path |
| `presentation_uri` | String(512) | nullable | Slides path |
| `supervisor_review_uri` | String(512) | nullable | Supervisor review PDF |
| `reviewer_review_uri` | String(512) | nullable | Reviewer review PDF |
| `source_uri` | String(512) | nullable | Source code URI |
| `author` | String(512) | nullable=False | Author name |
| `author_id` | Integer | FK -> users.id | Linked user |
| `supervisor_id` | Integer | FK -> staff.id | Supervisor |
| `reviewer_id` | Integer | FK -> staff.id | Reviewer |
| `publish_year` | Integer | nullable=False | Year of defense |
| `recomended` | Boolean | default=False | Recommended flag |
| `temporary` | Boolean | default=False | Temp/unpublished |
| `text` | Text | nullable | Full extracted text |
| `review_status` | Integer | default=10 | Review workflow state (0=success, 1=need review, 2=in progress, 3=failed) |
| `download_thesis` | Integer | default=0 | Download counter |
| `download_presentation` | Integer | default=0 | Download counter |

Full-text search via SQLite FTS5 virtual table `thesis_fts` on `name_ru`, `description`, `author`, `text`. Auto-sync triggers on INSERT/UPDATE/DELETE of `thesis` table. See `se_models.py` `thesis_fts_search()` helper.

### Posts (`posts`) — News

| Field | Type | Constraints | Description |
|---|---|---|---|
| `id` | Integer | PK, auto | Unique ID |
| `title` | String(2048) | nullable=False | Post title |
| `uri` | String(1024) | nullable | External URI (if cross-post) |
| `domain` | String(512) | nullable | Source domain |
| `text` | String(4096) | nullable | Post content |
| `votes` | Integer | default=1 | Upvote count |
| `views` | Integer | default=1 | View count |
| `created_on` | DateTime(timezone=True) | server_default=now() | Creation timestamp |
| `updated_on` | DateTime(timezone=True) | server_default=now(), onupdate=now() | Last update |
| `rank` | Float | default=0.0 | Computed ranking |
| `author_id` | Integer | FK -> users.id, nullable=False | Author |
| `type_id` | Integer | FK -> post_type.id | Post type |

### CurrentThesis (`current_thesis`) — Active Practice Works

| Field | Type | Constraints | Description |
|---|---|---|---|
| `id` | Integer | PK, auto | Unique ID |
| `author_id` | Integer | FK -> users.id | Student author |
| `area_id` | Integer | FK -> areas_of_study.id | Research area |
| `title` | String(512) | nullable | Thesis title |
| `supervisor_id` | Integer | FK -> staff.id | Supervisor |
| `worktype_id` | Integer | FK -> worktype.id, nullable=False | Work type |
| `consultant` | String(2048) | nullable | Consultant name |
| `goal` | String(2048) | nullable | Goal description |
| `text_uri` | String(512) | nullable | Thesis text path |
| `supervisor_review_uri` | String(512) | nullable | Review path |
| `reviewer_review_uri` | String(512) | nullable | Review path |
| `presentation_uri` | String(512) | nullable | Slides path |
| `text_link` | String(2048) | nullable | External text link |
| `presentation_link` | String(2048) | nullable | External slides link |
| `code_link` | String(2048) | nullable | External code link |
| `account_name` | String(512) | nullable | Git/account name |
| `archived` | Boolean | default=False | Archived flag |
| `deleted` | Boolean | default=False | Deleted flag |
| `status` | Integer | default=1 | 1=active, 2=past |

Relationships: `reports` -> ThesisReport, `tasks` -> ThesisTask.

## Lookup Tables

| Table | Fields | Purpose |
|---|---|---|
| `worktype` | `id`, `type` | Work types (Coursework, Bachelor, Master, etc.) |
| `courses` | `id`, `name`, `code` | Educational programs (09.03.04, 02.03.03, etc.) |
| `areas_of_study` | `id`, `area` | Research areas |
| `post_type` | `id`, `type`, `name` | News post categories |
| `themes_level` | `id`, `level` | Diploma theme difficulty levels |
| `thesis_on_review_worktype` | `id`, `type` | Review work types |
| `internship_format` | `id`, `format` | Internship formats (In-person, Remote) |
| `internship_tag` | `id`, `tag` | Internship technology tags |
| `tags` | `id`, `name` | Thesis keyword tags |

## Association Tables

| Table | Connected Tables | Purpose |
|---|---|---|
| `tag` | Thesis \<-> Tags | Thesis-to-tag mapping |
| `diploma_themes_tag` | DiplomaThemes \<-> DiplomaThemesTags | Theme-to-tag mapping |
| `diploma_themes_level` | DiplomaThemes \<-> ThemesLevel | Theme-to-level mapping |
| `internships_format` | Internships \<-> InternshipFormat | Internship-to-format |
| `internships_tag` | Internships \<-> InternshipTag | Internship-to-tag |

## Supporting Tables

| Table | Description |
|---|---|---|
| `thesis_report` | Weekly practice reports (`author_id`, `current_thesis_id`, `was_done`, `planned_to_do`, `time`, `comment`, `comment_time`, `deleted`) |
| `thesis_task` | Practice tasks (`task_text`, `deleted`, FK to current_thesis) |
| `deadline` | Deadlines per worktype+area combo |
| `notification_practice` | Practice notifications (recipient, content, viewed) |
| `diploma_themes` | Diploma themes with status workflow (new/needs update/approved/archived/rejected) |
| `company` | Companies offering themes (`name`, `logo_uri`, `status`) |
| `internships` | Internship vacancies |
| `internship_company` | Companies offering internships |
| `thesis_on_review` | Theses in peer review workflow (`name_ru`, `text_uri`, `presentation_uri`, `source_uri`, `review_status`) |
| `thesis_review` | Completed reviews with rubric scores |
| `reviewer` | External reviewers |
| `curriculum` | Curriculum data per course+year |
| `summer_school` | Summer school projects |
| `notification` | Email notification queue (`type`, `recipient`, `title`, `content`) |
| `post_vote` | Vote records (user_id + post_id composite PK, `upvote`, `timestamp`) |
| `promo_code` | Reviewer signup codes |
| `diploma_themes_tags` | Tag definitions for diploma themes |
