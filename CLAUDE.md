# SE Site

<!-- encoding: utf-8 -->

Сайт кафедры системного программирования СПбГУ — Flask-based website.

## AI Instructions

See `AGENTS.md` for pre-flight checklist, testing quirks, and environment quirks.
See `docs/DEVELOPMENT_PROCESS.md`, `docs/GIT_FLOW.md`, `docs/TESTING.md`,
`docs/ARCHITECTURE.md`, `docs/DOCS.md` for process, branching, testing, and architecture.

## Skills

Load skill workflows from `.skills/<name>/README.md` when the task matches:

| Skill | Load when ... |
|---|---|
| `test-writer` | Writing hermetic pytest tests — load before coding |
| `retrospective-analysis` | Analyzing process gaps after merges or sessions |
| `api-client` | Implementing/modifying HTTP client with retry |
| `model-definer` | Defining/modifying SQLAlchemy models or WTForms |
| `gh-todo-sync` | Syncing TODO.md from GitHub / CI |
| `js-bundle-analysis` | Reverse-engineering JS bundles |
| `unattended-mode` | Running autonomously — no questions, no signoff, fix CI first |
| `repo-review` | Evaluating repo health against docs/REPO_REVIEW.md checklist — load to audit and create backlog |
| `encoding-audit` | Detect and fix non-UTF-8 encoding in source files on Windows — load when mdformat/re rejects files or text shows garbled characters |
| `flask-test-patterns` | Reusable fixture templates for Flask + SQLAlchemy + pytest with xdist — load when adding test infrastructure |
| `docs-audit` | Doc health checks: freshness, cross-refs, scope discipline, encoding, SPDX — load before finalization or after restructuring docs |
| `code-audit` | Code quality and security audit: secrets, redirects, deprecations, crash safety, file safety, test health — load before staging→current gate or after 5+ source file changes |
| `security-audit` | Structured security audit: GitHub security surface (Dependabot/CodeQL/advisories) + three-pass code review (authz/CSRF/OAuth, XSS, SQLi/files) with verify-before-fix — load on security review requests or before release gates |
| `readme-generator` | Generating/updating project README — load to create a polished project-specific README |
| `merge-gate` | Pre-merge workflow: audit docs, audit code, compact context, verify CI, merge with discipline — load at end of batch session or before manual merge to staging |
| `release-notes` | Generate end-user release notes + developer changelog for a `vYYYY.MM.DD` release — load before tagging a release |
| `skill-for-skills` | Maintain skills in sync with docs, enforce skills principles, self-maintain — load after doc restructuring or when a skill was created/modified |
