# Development Process

<!-- encoding: utf-8 -->

Flask-based website for the SPbSU System Programming Department. See `AGENTS.md` for commands, `doc/GIT_FLOW.md` for version control, and `doc/OPENSE_CONFIG.md` for AI tooling.

## Process Identity

This project blends agile practices suited for single-agent development:

| From | We use | We deliberately reject |
|---|---|---|
| **XP** | TDD (test-first from specs), CI, coding standards (ruff), collective ownership, zero bugs | Pair Programming (replaced with batched staging review), fixed cadence |
| **Kanban** | Continuous flow, pull-based work selection (priority ladder), WIP-limited (one task) | Cycle time tracking, explicit board |
| **Shape Up** | Shaping phase (planning + doc-first), appetite sizing (S/M/L estimates) | 6-week cycles, betting table |

Design decisions about deliberate deviations are recorded in `doc/ARCHITECTURE.md -> Design Decisions`.

Covers: planning, testing, linting, code review, release, dependencies. Does not cover: CLI commands, architecture design, AI tooling, version control.

## 0. CLI Quick Reference

```bash
uv sync                                       # install dependencies (dev + main)
uv run python src/flask_se.py                 # run dev server (http://127.0.0.1:5000)
uv run python src/flask_se.py init            # initialize database
uv run python src/wsgi.py                     # run via WSGI
uv run pytest                                 # run tests
uv run ruff check src/                        # lint
uv run ruff format src/                       # format
uv run python flask_se.py build               # build static site (Frozen-Flask)
```

## 0.1 Doc-to-Code Sync

When docs describe code that does not yet exist:

1. Add a `# TODO` comment in the doc
1. Implement in a `feat:` or `fix:` commit
1. Run tests before merging

Every `.md` file under `doc/` must start with a one-sentence aim description after the H1 title, explaining what the file documents and who it serves.

## 0.5 Planning Phase

Before any implementation: enter **planning phase** (read-only analysis). Always:

1. Check CI status
1. Apply the priority ladder (see `doc/GIT_FLOW.md`): CI failures -> PRs -> backlog -> icebox
1. Present findings and top candidate tasks to the user, each with effort estimate (S/M/L) and brief rationale
1. User reviews, adjusts, approves
1. **Check existing first** — before creating a new skill, doc, or tool, verify existing ones don't already cover the need. Over-engineering (solving completeness over practicality) is the #1 repeated gap.
1. Load relevant `.skills/<name>/` skill if available (e.g., `test-writer` for test tasks)
1. Discuss approach, confirm scope, get approval
1. Only then branch and implement

**Effort sizing:**

- **S**: Single-file change, no new deps, ~1h
- **M**: Multi-file, 2-3 modules, ~half day
- **L**: Multi-module, new patterns/deps, ~1d+

Planning phase is non-negotiable. Never jump to implementation without prior discussion.

## 0.6 Skill Conventions

Skills live in `.skills/<name>/README.md` (vendor-agnostic). Per-vendor stubs in `.claude/skills/`, `.opencode/skills/`, `.agents/skills/` point to the canonical skill. The `name` must be lowercase alphanumeric with hyphens and match the directory name.

### Adding a new skill

1. **Canonical source** — create `.skills/<name>/README.md`
1. **Vendor stubs** — create `SKILL.md` in `.opencode/skills/<name>/`, `.claude/skills/<name>/`, `.agents/skills/<name>/`
1. **Register** — add to `CLAUDE.md` skills table
1. **Cross-reference** — add to `AGENTS.md` if needed, reference in relevant process docs

## 0.7 New Artifact Checklist

When creating any new file, directory, or tooling config:

1. **Scope** — What does it cover? What does it explicitly not cover? Write a one-sentence aim at the top.
1. **Vendor lock-in** — Does it reference a specific AI tool? If yes, create a canonical vendor-agnostic version first, then thin wrappers per tool.
1. **Convention** — Does an existing pattern apply? (e.g., all `.md` under `doc/` need aim + scope, skills go in `.skills/`, formatting via ruff+mdformat)
1. **Canonical source** — If this could be referenced from multiple places, where does the one true version live? Other locations should be derived cross-references.

## 0.8 Tool Source of Truth

Python tools (ruff, pytest, mdformat, pre-commit) are installed via `uv` — managed in `pyproject.toml` `[dependency-groups]`. Non-Python tools (dprint, commitlint) are managed via pre-commit repo hooks. Never install linting/formatting tools globally — always use `uv run`.

To upgrade a Python tool: bump the version in `pyproject.toml` → `uv lock` → commit. No pre-commit config update needed.

## 0.9 Decision Enforcement

Every process rule is enforced at one of three layers:

| Layer | Mechanism | Example |
|---|---|---|
| 1 — Tool config | Automated guard in tooling | Pre-commit hooks, ruff rules, commitlint |
| 2 — CI check | Fails in CI pipeline | Staging CI verifies requirements.txt freshness |
| 3 — Documentation | Documented, manually enforced | Planning phase, doc-first cycle |

When adding a new rule: enforce at the lowest possible layer. Only document (layer 3) what cannot be automated (layers 1-2). Add CI checks (layer 2) to verify layer-1 configs are honored.

## 0.10 Tooling Parity

Every CI check must have a corresponding local check that behaves identically.
A CI check with no local equivalent, or a local check that silently passes while
CI fails, creates false confidence and wastes server time.

### Parity rules

1. **Match entry points** — pre-commit hook `entry:` must match the CI workflow
   command exactly (minus `--check` flag). If CI runs `uv run mdformat --check docs/`,
   the hook must run `uv run mdformat docs/`.
1. **Test locally** — after adding or modifying a pre-commit hook, verify it
   actually runs and catches violations:
   ```bash
   uv run pre-commit run <hook-id> --all-files
   ```
   If this passes, but the file violates the hook's rule, the hook is broken.
1. **Same paths** — if CI uses explicit file paths, the local check must use the
   same paths. A hook that uses `mdformat .` while CI uses `docs/ AGENTS.md ...`
   will work on Linux (no `.venv/` traversal issue) but silently fail on Windows.
1. **No silent failures** — every pre-commit hook must exit non-zero on
   violation. If a hook can crash (UnicodeDecodeError, missing tool, path issue),
   fix the entry point rather than ignoring the failure.

### What to do when adding a new CI step

1. Add the check to the CI workflow file
1. Add a matching pre-commit hook in `.pre-commit-config.yaml`
1. Run the hook locally to verify it catches a deliberate violation
1. Run the CI workflow to verify it produces the same result

### Diagnosis: pre-commit hook not catching what CI catches

If CI fails on a check that pre-commit should have caught:

1. Run the hook manually: `uv run pre-commit run <hook-id> --all-files`
1. Does it crash? (check exit code + error output)
1. Does it use different paths/arguments than the CI workflow?
1. Does it work on one platform but not another?
1. Fix the entry point so the local check matches the CI check exactly.

## 0.11 Encoding Policy

All source files (`.py`, `.md`, `.yaml`, `.json`, `.toml`, `.cfg`) **must be UTF-8**. No exceptions unless explicitly documented.

Every file that supports encoding declarations must declare it at the very beginning:

| Format | Declaration | Position |
|--------|-------------|----------|
| `.py` | `# -*- coding: utf-8 -*-` | Line 1 (before SPDX header) |
| `.md` | `<!-- encoding: utf-8 -->` | Line 2 (after H1 title, before content) |
| Others | Format doesn't support inline declaration | Exception documented here |

On Windows, PowerShell `Set-Content`/`Out-File` default to Windows-1252, not UTF-8. Always use `[System.IO.File]::WriteAllText()` with explicit UTF-8 encoding. See `docs/TOOLING.md §PowerShell encoding`.

## 1. Version Control

See `doc/GIT_FLOW.md` — branching, guardrails, commit sequence, staging.

## 2. Testing

```bash
pytest
```

- Aim for 100% line coverage where feasible. New modules: tests before first commit — aim for ≥50% initial coverage.
- **Test-first**: tests are authored before implementation where possible
- Tests live alongside source code under `tests/`
- Run before every commit
- **Zero bugs policy**: any bug found during development blocks all feature work until fixed
- **Edge case thinking**: during test writing, audit empty inputs, corrupt data, boundary values, failure modes. Where edge cases emerge, improve process documentation (what was missed and how to catch it next time).

## 3. Styling & Linting

```bash
ruff check src/
ruff format src/
mdformat docs/ AGENTS.md CLAUDE.md README.md TODO.md .skills/ .opencode/commands/ .claude/ .agents/
```

Ruff and mdformat are enforced via pre-commit hooks. See `.pre-commit-config.yaml`.

The mdformat pre-commit hook uses **explicit paths** matching the CI workflow:
`docs/ AGENTS.md CLAUDE.md README.md TODO.md .skills/ .opencode/commands/ .claude/ .agents/`.
Never use `mdformat .` — on Windows it traverses `.venv/` which contains
vendor `.md` files with non-UTF-8 bytes, causing a silent crash and allowing
unformatted files through.

## 3.5 Code Review Checklist

Every item must pass before staging -> current merge:

| # | Check | What to verify |
|---|---|---|
| 1 | **Tests pass** | `pytest` green — run locally AND verify against CI environment (fresh DB, no stale artifacts) |
| 2 | **Lint** | `ruff` clean |
| 2a | **Types** (future) | `mypy strict` passes, no new `# type: ignore[code]` — required once mypy is configured |
| 3 | **Format** | `ruff format` + `mdformat` applied |
| 4 | **Edge cases** | Empty/null inputs, boundary values, failure modes tested |
| 5 | **Error messages** | Actionable, follow existing pattern (field → reason) |
| 6 | **Docs sync** | ARCHITECTURE.md, API_REFERENCE.md, SCHEMA.md updated — and every `.md` file has H1 → aim → scope |
| 7 | **AI instructions** | New quirks added? Existing ones still accurate? Verify no unique content — every claim cross-references a canonical doc. |
| 8 | **requirements.txt current** | Run `uv export --no-dev --no-hashes > requirements.txt` — committed if changed |
| 9 | **Backward compat** | Existing behavior unchanged |
| 10 | **No secrets** | No hardcoded keys, tokens, or production URLs |
| 11 | **Conventions** | Code style matches existing patterns |
| 12 | **Process compliance** | Architecture-first cycle followed? Zero bug policy respected? Any violations documented in `TODO.md`? |

## 4. Dependencies

Production dependencies in `requirements.txt` (pinned versions, generated by uv):

```bash
pip install -r requirements.txt
```

Development uses uv (see `doc/ARCHITECTURE.md` § Design Decisions for rationale):

```bash
uv add <package>                       # add a new dependency
uv sync                                # install all deps (dev + main)
uv export --no-dev --no-hashes > requirements.txt  # update prod requirements
```

## 5. Release

1. Determine SemVer bump from commit log since last tag
1. Update version references if any
1. Tag: `git tag v<version>`
1. Build static site if needed: `python flask_se.py build`
1. Update Dockerfile if dependency changes

### Open Source Recommendations

For public deployment, consider: `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `CHANGELOG.md`, `CITATION.cff` (academic citation metadata), `.github/FUNDING.yml` (funding channels).

## 6. Process Improvements Backlog

Acknowledged process improvement ideas that are not yet implemented. These are process-debt items, not project tasks — they live here rather than `TODO.md`.

| # | Topic | Description |
|---|-------|-------------|
| 1 | **Recovery procedures** | Document `git reflog`, `git revert`, `git reset` guidance for recovery from bad merges or lost commits |
| 2 | **Conflict resolution strategy** | Define how to handle merge conflicts in staging and during staging→current merge |
| 3 | **Push cadence** | Rule for when to push branches to remote (after every commit? only at staging merge?) |
| 4 | **Definition of Done** | Rename §3.5 checklist to "Definition of Done" for clarity, add any missing items |
| 5 | **CI pipeline documentation** | Document what runs in CI (same as pre-commit + tests? additional steps?) |
| 6 | **.editorconfig sync** | Auto-detect new file types and add editorconfig entries |
| 7 | **Branch protection** | Set up GitHub branch protection on `current` (require status checks, block direct pushes). Requires repo admin access — discuss with repo owner. |
