# SE Site

<!-- encoding: utf-8 -->

РЎР°Р№С‚ РєР°С„РµРґСЂС‹ СЃРёСЃС‚РµРјРЅРѕРіРѕ РїСЂРѕРіСЂР°РјРјРёСЂРѕРІР°РЅРёСЏ РЎРџР±Р“РЈ вЂ” Flask-based website.

## AI Instructions

See `AGENTS.md` for commands, quirks, and workflow. See `docs/` for full process docs: `docs/DEVELOPMENT_PROCESS.md`, `docs/GIT_FLOW.md`, `docs/ARCHITECTURE.md`, `docs/API_REFERENCE.md`, `docs/SCHEMA.md`.

## Skills

Load skill workflows from `.skills/<name>/README.md` when the task matches:

| Skill | Load when ... |
|---|---|
| `test-writer` | Writing hermetic pytest tests вЂ” load before coding |
| `retrospective-analysis` | Analyzing process gaps after merges or sessions |
| `api-client` | Implementing/modifying HTTP client with retry |
| `model-definer` | Defining/modifying SQLAlchemy models or WTForms |
| `gh-todo-sync` | Syncing TODO.md from GitHub / CI |
| `js-bundle-analysis` | Reverse-engineering JS bundles |
| `unattended-mode` | Running autonomously вЂ” no questions, no signoff, fix CI first |
| `repo-review` | Evaluating repo health against docs/REPO_REVIEW.md checklist вЂ” load to audit and create backlog |
| `encoding-audit` | Detect and fix non-UTF-8 encoding in source files on Windows — load when mdformat/re rejects files or text shows garbled characters |
| `flask-test-patterns` | Reusable fixture templates for Flask + SQLAlchemy + pytest with xdist — load when adding test infrastructure |
| `readme-generator` | Generating/updating project README вЂ” load to create a polished project-specific README |
