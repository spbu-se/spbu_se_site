# SE Site

Сайт кафедры системного программирования СПбГУ — Flask-based website.

## AI Instructions

See `AGENTS.md` for commands, quirks, and workflow. See `doc/` for full process docs: `doc/DEVELOPMENT_PROCESS.md`, `doc/GIT_FLOW.md`, `doc/ARCHITECTURE.md`, `doc/API_REFERENCE.md`, `doc/SCHEMA.md`.

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
