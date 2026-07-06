# Schema Reference — Database Model Definitions

<!-- encoding: utf-8 -->

All SQLAlchemy models used by the SE Site. Database: SQLite (`se.db`).

Covers: table schemas with field types and relationships, seed data structure. Does not cover: endpoint documentation — see `doc/API_REFERENCE.md`, module architecture — see `doc/ARCHITECTURE.md`.

## Core Tables

### Users (`users`)

| Field | Type | Constraints | Description |
|---|---|---|---|
| `id` | Integer | PK, auto | Unique user ID |
| `email` | String(256) | Unique, nullable | Email address |
| `password_hash` | String(256) | nullable | pbkdf2:sha256 hash |
| `first_name` | String(128) | nullable | First name |
| `middle_name` | String(128) | nullable | Middle name (patronymic) |
| `last_name` | String(128) | nullable | Last name |
| `avatar_uri` | String(256) | nullable | Avatar image path |
| `role` | Integer | default=0 | 0=default, 5=admin |
| `how_to_contact` | String(256) | nullable | Contact info |
| `vk_id` | Integer | nullable | VK social ID |
| `google_id` | String(256) | nullable | Google social ID |

Relationships: `staff`, `news` (posts), `thesises`, `current_thesises`, `reviewer`, `all_user_votes`, `internship_author`, diploma theme relations (4 FKs).

### Staff (`staff`)

| Field | Type | Constraints | Description |
|---|---|---|---|
| `id` | Integer | PK, auto | Unique staff ID |
| `user_id` | Integer | FK -> users.id | Linked user account |
| `official_email` | String(128) | nullable | SPbU email |
| `position` | String(128) | nullable | Academic position |
| `science_degree` | String(128) | nullable | Degree info |
| `still_working` | Boolean | default=True | Active status |

Relationships: `supervisor` -> Thesis, `adviser` -> Thesis, `current_thesises`.

### Thesis (`thesis`) — Main Archive

| Field | Type | Constraints | Description |
|---|---|---|---|
| `id` | Integer | PK, auto | Unique ID |
| `type_id` | Integer | FK -> worktype.id | Coursework, Bachelor, Master, etc. |
| `course_id` | Integer | FK -> courses.id | Educational program |
| `area_id` | Integer | FK -> areas_of_study.id | Research area |
| `name_ru` | String(256) | nullable | Russian title |
| `name_en` | String(256) | nullable | English title |
| `description` | Text | nullable | Abstract |
| `text_uri` | String(256) | nullable | PDF path |
| `presentation_uri` | String(256) | nullable | Slides path |
| `supervisor_review_uri` | String(256) | nullable | Supervisor review PDF |
| `reviewer_review_uri` | String(256) | nullable | Reviewer review PDF |
| `author` | String(128) | nullable | Author name |
| `author_id` | Integer | FK -> users.id | Linked user |
| `supervisor_id` | Integer | FK -> staff.id | Supervisor |
| `reviewer_id` | Integer | FK -> staff.id | Reviewer |
| `publish_year` | Integer | nullable | Year of defense |
| `recomended` | Boolean | default=False | Recommended flag |
| `temporary` | Boolean | default=False | Temp/unpublished |
| `text` | Text | nullable | Full extracted text |
| `review_status` | Integer | nullable | Review workflow state |
| `download_thesis` | Integer | default=0 | Download counter |
| `download_presentation` | Integer | default=0 | Download counter |

Full-text search via Whooshee on `name_ru`, `description`, `author`, `text`.

### Posts (`posts`) — News

| Field | Type | Constraints | Description |
|---|---|---|---|
| `id` | Integer | PK, auto | Unique ID |
| `title` | String(256) | nullable | Post title |
| `uri` | String(256) | nullable | External URI (if cross-post) |
| `domain` | String(256) | nullable | Source domain |
| `text` | Text | nullable | Post content |
| `votes` | Integer | default=0 | Upvote count |
| `views` | Integer | default=0 | View count |
| `created_on` | DateTime | nullable | Creation timestamp |
| `updated_on` | DateTime | nullable | Last update |
| `rank` | Float | default=0.0 | Computed ranking |
| `author_id` | Integer | FK -> users.id | Author |
| `type_id` | Integer | FK -> post_type.id | Post type |

### CurrentThesis (`current_thesis`) — Active Practice Works

| Field | Type | Constraints | Description |
|---|---|---|---|
| `id` | Integer | PK, auto | Unique ID |
| `author_id` | Integer | FK -> users.id | Student author |
| `area_id` | Integer | FK -> areas_of_study.id | Research area |
| `title` | String(256) | nullable | Thesis title |
| `supervisor_id` | Integer | FK -> staff.id | Supervisor |
| `worktype_id` | Integer | FK -> worktype.id | Work type |
| `consultant` | String(256) | nullable | Consultant name |
| `goal` | Text | nullable | Goal description |
| `text_uri` | String(256) | nullable | Thesis text path |
| `supervisor_review_uri` | String(256) | nullable | Review path |
| `reviewer_review_uri` | String(256) | nullable | Review path |
| `presentation_uri` | String(256) | nullable | Slides path |
| `account_name` | String(256) | nullable | Git/account name |
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
|---|---|
| `thesis_report` | Weekly practice reports (`was_done`, `planned_to_do`, `time`, `comment`) |
| `thesis_task` | Practice tasks (`task_text`, FK to current_thesis) |
| `deadline` | Deadlines per worktype+area combo |
| `notification_practice` | Practice notifications (recipient, content, viewed) |
| `diploma_themes` | Diploma themes with status workflow (new/needs update/approved/archived/rejected) |
| `company` | Companies offering themes |
| `internships` | Internship vacancies |
| `internship_company` | Companies offering internships |
| `thesis_on_review` | Theses in peer review workflow |
| `thesis_review` | Completed reviews with rubric scores |
| `reviewer` | External reviewers |
| `curriculum` | Curriculum data per course+year |
| `summer_school` | Summer school projects |
| `notification` | Email notification queue |
| `post_vote` | Vote records (user_id + post_id composite PK) |
| `promo_code` | Reviewer signup codes |
| `diploma_themes_tags` | Tag definitions for diploma themes |
