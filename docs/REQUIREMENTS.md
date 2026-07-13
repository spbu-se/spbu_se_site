# Requirements — SE Site (SPbSU System Programming Department)

<!-- encoding: utf-8 -->

Full feature specification for the department website. The site serves as an information portal, thesis archive, practice management system, and peer review platform.

Covers: feature modules, page descriptions, user roles, navigation structure. Does not cover: implementation details, database schema — see `docs/SCHEMA.md`, route documentation — see `docs/API_REFERENCE.md`.

## 1. User Roles

| Role | Permissions |
|---|---|
| **Guest** | Browse public pages, search theses, read news |
| **Authenticated User** | Submit news, manage own diploma themes, submit theses for review, participate in practice |
| **Staff** | Supervise practice students, view advisee reports, review theses |
| **Admin** | Full CRUD via custom admin panel, manage practice, archive theses, moderate diploma themes |

## 2. Feature Modules

### 2.1 Public Information Pages

Static and semi-static pages describing the department:

- Homepage with top 10 news, research directions links, contact info
- Staff listing (dynamically loaded from DB)
- Research directions overview
- Contacts page
- FAQ page
- Sitemap XML for SEO
- Custom 404 page

### 2.2 Educational Programs

Curriculum information for bachelor and master programs:

- **Bachelor**: Admission info, Programming Technology curriculum, Software Engineering curriculum, Application info
- **Master**: Information Systems Administration, Software Engineering
- Curriculum data managed via DB seed data

### 2.3 News System

Community-driven news platform:

- Users can submit news posts with title, text, optional external URI
- Posts ranked by a weighted algorithm (votes + views)
- Upvote/downvote system
- Users can delete own posts
- Admin can manage all posts via admin panel
- Homepage shows top 10 active posts

### 2.4 Thesis Archive

Searchable repository of graduate works (coursework, bachelor, master):

- Full-text search across title, description, author, extracted text
- Filter by work type, course, area of study, year
- Download PDFs (tracks download count)
- Admin/manual approval flow via "temporary" status
- Tags for categorization
- Supervisor and reviewer attribution

### 2.5 Diploma Themes

Marketplace for diploma thesis topics:

- Browse, search, and filter available themes
- Users can propose their own themes (with supervisor, company, or self-proposed)
- Status workflow: new -> needs update -> approved -> archived/rejected
- Admin review and moderation
- Archive/unarchive own themes

### 2.6 Practice System

Three-tier educational practice management:

**Student features** (4 semesters: 2nd-4th year + pre-graduate):

- Create and manage practice thesis
- Choose topic and supervisor
- Set goals and tasks
- Submit weekly progress reports
- Upload materials (text, presentation, reviews)
- View defense information

**Staff/Supervisor features**:

- Dashboard listing advisees
- View thesis details and reports
- Comment on reports
- Send notifications

**Admin/Curator features**:

- Dashboard organized by area and work type
- Full CRUD on active theses
- Archive completed works to main thesis repository
- Export to Excel
- Yandex Disk upload integration

### 2.7 Thesis Peer Review

External review workflow for thesis quality assessment:

- Students submit theses for external review
- External reviewers sign up via promo code
- Review rubric with 6 criteria scored 0-5 with comments
- Verdict and overall comment
- Review result visible to student

### 2.8 Internship Board

Job/internship marketplace:

- Browse and filter internships by format, technology, company
- Add, edit, delete internships (authenticated users)
- Company profiles with logos

### 2.9 Summer Schools

Archive of summer school projects (2021, 2022, 2024, 2026):

- List of all summer schools
- Individual project pages with description, technology stack, repo links, demos
- Admin-managed via custom admin interface

### 2.10 Scholarships

13 static information pages about available scholarships and grants.

### 2.11 Authentication

Multi-provider auth system:

- Email/password registration and login (pbkdf2:sha256)
- VK OAuth login
- Google OAuth login
- Password recovery (stub)
- User profile with avatar upload
- Session management via Flask-Login

## 3. Navigation Structure

```
Home (/)
  |-- Research Directions
  |-- Bachelor Programs
  |     |-- Admission
  |     |-- Programming Technology
  |     |-- Software Engineering
  |     |-- Application
  |-- Master Programs
  |     |-- Information Systems Administration
  |     |-- Software Engineering
  |-- Students
  |     |-- Scholarships
  |-- Staff
  |-- Thesis Archive
  |-- News
  |-- Diploma Themes
  |-- Internships
  |-- Summer Schools
  |-- FAQ
  |-- Contacts
  |-- Login / Profile
  |-- Practice (authenticated)
  |-- Thesis Review (authenticated)
```

## 4. Scheduled Jobs

| Job | Schedule | Description |
|---|---|---|
| RecalculatePostRank | Every hour | Recalculate news ranking based on votes and views |
| SendMailNotification | Every 10 seconds | Process email queue for notifications |
| SendDiplomaThemesOnReviewNotification | Every 24 hours | Alert moderators about unmoderated themes |

## 5. Deployment

- **Web server**: nginx (reverse proxy) -> uWSGI -> Flask
- **Application server**: uWSGI (4 processes, 2 threads, socket :8080)
- **Database**: SQLite (`se.db`)
- **Static content**: served directly by nginx
- **Static site generation**: Frozen-Flask for full static export
- **Containerization**: Docker (Flask container + nginx container)
- **File storage**: Local filesystem under `src/static/`
