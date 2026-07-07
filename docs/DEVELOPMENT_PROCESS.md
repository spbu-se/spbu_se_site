# Development Process

<!-- encoding: utf-8 -->

Flask-based website for the SPbSU System Programming Department. See `AGENTS.md` for pre-flight and setup quirks, `docs/GIT_FLOW.md` for version control, and `docs/OPENSE_CONFIG.md` for AI tooling.

All doc management rules (creation, formatting, encoding, integrity checks) are in `docs/DOCS.md`.

## Process Identity

This project blends agile practices suited for single-agent development:

| From | We use | We deliberately reject |
|---|---|---|
| **XP** | TDD (test-first from specs), CI, coding standards (ruff), collective ownership, zero bugs | Pair Programming (replaced with batched staging review), fixed cadence |
| **Kanban** | Continuous flow, pull-based work selection (priority ladder), WIP-limited (one task) | Cycle time tracking, explicit board |
| **Shape Up** | Shaping phase (planning + doc-first), appetite sizing (S/M/L estimates) | 6-week cycles, betting table |

Design decisions about deliberate deviations are recorded in `docs/ARCHITECTURE.md -> Design Decisions`.

Covers: planning, testing, linting, code review, release, dependencies, session lifecycle, workflow discipline. Does not cover: CLI commands, architecture design, AI tooling, version control — see `docs/GIT_FLOW.md`.

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

## 0.5 Planning Phase

Before any implementation: enter **planning phase** (read-only analysis). Always:

1. Check CI status — if `origin/staging` is red, stop and fix first
1. Apply the priority ladder: CI failures -> PRs -> backlog -> icebox
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

## 0.6 Workflow Discipline

### Architecture first

Write design decisions in `docs/ARCHITECTURE.md -> Design Decisions` before implementation.

### Doc first

Update docs that describe code that does not exist yet, commit, then implement.

### Mid-sprint violation

If architecture-first or doc-first step was skipped, create a `TODO.md` Backlog entry. Fixing it (document decision, rearrange code if needed) is a **must-have** before the next feature.

### TDD

Write tests from docs → implement → format → test → commit.

### Enforcement self-check

Before staging→current gate, audit each decision from this session:

- Can it be automated? → tool config (layer 1)
- Can it be CI-checked? → add a workflow step (layer 2)
- Is documentation the only option? → document (layer 3)
- Is its git tracking status correct? → every new file must be either `.gitignored` (local-only) or tracked (shared). Verify intent before commit.
- If a rule is documented WITHOUT checking layers 1-2 first, the session is incomplete. Add the automated check before proceeding to the gate.

### Pre-merge refresh

Before proposing merge to current, ensure `requirements.txt` matches lockfile. See `docs/GIT_FLOW.md §8` for the command.

### Pre-staging validation

Before staging after bulk doc edits, run the `mdformat` command that CI will use — not just `--check`. This catches missing files and path errors early. See `docs/DOCS.md §7.1` for the command.

### Context compaction

Before compacting context or ending session:

- Update `docs/ARCHITECTURE.md` Design Decisions with new choices
- Update `TODO.md` (remove completed, reorder backlog)
- Run AI instructions drift check (see `docs/DOCS.md §5.3`)
- Audit cross-references: scan every `.md` file under `docs/` and `.skills/` for hardcoded step numbers. Replace with section-title references.

### Task management

- **TODO.md**: every unimplemented idea MUST live in TODO.md Backlog or Icebox. Removing from Icebox requires explicit user request. Document rejection reasons in `docs/ARCHITECTURE.md` Design Decisions when declining a feature.
- **Priority ladder**: CI fixes > PRs > stale branches > backlog > icebox.

### Process docs during code work

Do not update process documentation while implementing features or fixing bugs on a feature branch. Instead, gather observations and suggest improvements. Process doc changes happen during staging→current gate or on dedicated `docs/` branches.

**Exception**: if the architecture-first or doc-first cycle was violated (code before doc), add a `TODO.md` debt entry mid-sprint — this is a violation record, not a doc change.

### Stop signal

When any commit requires user review (AI instruction change, process change, non-trivial decision), output a visible stop banner and do NOT proceed:

```
🟡 STOP — <reason>
```

Do not commit, stash, or proceed without user approval. This overrides all automation rules — if in doubt, STOP.

### .editorconfig sync

Every new file type should have an `.editorconfig` entry. Keep `.editorconfig` in sync with formatter configs (dprint, ruff).

## 0.7 Session Lifecycle

### Session start

**Why**: Every session starts from a known state — no orphaned WIP, no stale assumptions, no format drift.

**What**:

1. Sync with remote and check for lingering work from the last session
1. Read `.unfinished.plan.md` to understand what was interrupted
1. Sync staging and verify it is not ahead of current unexpectedly
1. Verify pre-commit hooks pass before touching any code
1. Branch from staging

The exact commands for each step are in `docs/GIT_FLOW.md §3` (Guardrails — Session start).

### Session end

**Why**: Unfinished work must be preservable across sessions without polluting history.

**What**:

1. Check working tree for dirty or untracked files
1. Write `.unfinished.plan.md` with date/time, focus task, branch, last commit hash, dirty files, completed and remaining steps, undocumented decisions
1. If on a feature branch with unfinished code: commit WIP, create `_UNFINISHED.md` as the final commit
1. `_UNFINISHED.md` is always the last commit — stripped automatically by squash-merge
1. `.unfinished.plan.md` is never committed (see `.gitignore`)
1. Refresh `requirements.txt` if dependencies changed
1. Verify working tree is clean

The exact commands for each step are in `docs/GIT_FLOW.md §7`.

### Staging green rule

**Why**: Broken CI hides regressions from everyone. A red staging blocks all work until fixed.

**What**:

- CI on `origin/staging` must be green at all times
- Never commit to `staging` directly — all work goes to feature branches (or `staging-auto-*` in batch mode)
- Before every push: tests, lint, format, pre-commit, secrets check — all must pass
- After every push: wait for CI, fix immediately if red

The full pre-flight checklists are in `AGENTS.md` (Pre-flight checklist). The push command reference is in `docs/GIT_FLOW.md §4.1`.

## 0.8 Skill Conventions

## 0.8 Skill Conventions

Skills live in `.skills/<name>/README.md` (canonical). Per-vendor stubs in `.opencode/skills/`, `.claude/skills/`, `.agents/skills/`.

## 0.9 New Artifact Checklist

Before creating new files or directories, verify scope and existing overlap.

## 0.10 Tool Source of Truth

Python tools (ruff, pytest, mdformat, pre-commit) are installed via `uv` — managed in `pyproject.toml` `[dependency-groups]`. Non-Python tools (dprint, commitlint) are managed via pre-commit repo hooks. Never install linting/formatting tools globally — always use `uv run`.

To upgrade a Python tool: bump the version in `pyproject.toml` → `uv lock` → commit. No pre-commit config update needed.

## 0.11 Decision Enforcement

Every process rule is enforced at one of three layers:

| Layer | Mechanism | Example |
|---|---|---|
| 1 — Tool config | Automated guard in tooling | Pre-commit hooks, ruff rules, commitlint |
| 2 — CI check | Fails in CI pipeline | Staging CI verifies requirements.txt freshness |
| 3 — Documentation | Documented, manually enforced | Planning phase, doc-first cycle |

When adding a new rule: enforce at the lowest possible layer. Only document (layer 3) what cannot be automated (layers 1-2). Add CI checks (layer 2) to verify layer-1 configs are honored.

## 0.12 Tooling Parity

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

## 0.13 Encoding Policy

All source files must be UTF-8. Declare encoding at the top of every file.

## 1. Version Control

See `docs/GIT_FLOW.md` — branching, merge strategy, commit discipline, signoff policy.

## 2. Retrospectives

See `docs/RETROSPECTIVES.md` — historical record of process gaps and fixes.

## 3. Testing

See `docs/TESTING.md` for testing discipline, coverage targets, xfail policy, and long-term gaps.

## 4. Styling & Linting

```bash
ruff check src/
ruff format src/
mdformat docs/ AGENTS.md CLAUDE.md README.md TODO.md .skills/ .opencode/commands/ .claude/ .agents/
```

Ruff and mdformat are enforced via pre-commit hooks. See `.pre-commit-config.yaml`.

The mdformat pre-commit hook uses **explicit paths** matching the CI workflow:
`docs/ AGENTS.md CLAUDE.md README.md TODO.md .skills/ .opencode/commands/ .claude/ .agents/`.
Never use `mdformat .` — on Windows it traverses `.venv/` which contains vendor `.md` files with non-UTF-8 bytes, causing a silent crash.

## 4.5 Code Review Checklist

Every item must pass before staging -> current merge:

| # | Check | What to verify |
|---|---|---|
| 1 | **Tests pass** | `docs/TESTING.md` — full suite green, coverage within target |
| 2 | **Lint** | `ruff` clean |
| 2a | **Types** (future) | `mypy strict` passes, no new `# type: ignore[code]` — required once mypy is configured |
| 3 | **Format** | `ruff format` + `mdformat` applied |
| 4 | **Edge cases** | `docs/TESTING.md §1` — empty inputs, boundary values, failure modes tested |
| 5 | **Error messages** | Actionable, follow existing pattern (field → reason) |
| 6 | **Docs sync** | `docs/DOCS.md §8` integrity checks applied — H1 → aim → scope on every `.md`, encoding declarations, cross-references resolved |
| 7 | **AI instructions** | New quirks added? Existing ones still accurate? Verify no unique content — every claim cross-references a canonical doc (`docs/DOCS.md §5`). |
| 8 | **requirements.txt current** | Run `uv export --no-dev --no-hashes > requirements.txt` — committed if changed |
| 9 | **Backward compat** | Existing behavior unchanged |
| 10 | **No secrets** | No hardcoded keys, tokens, or production URLs |
| 11 | **Conventions** | Code style matches existing patterns |
| 12 | **Process compliance** | Architecture-first cycle followed? Zero bug policy respected? Any violations documented in `TODO.md`? |

## 5. Dependencies

Production dependencies in `requirements.txt` (pinned versions, generated by uv):

```bash
pip install -r requirements.txt
```

Development uses uv (see `docs/ARCHITECTURE.md` § Design Decisions for rationale):

```bash
uv add <package>                       # add a new dependency
uv sync                                # install all deps (dev + main)
uv export --no-dev --no-hashes > requirements.txt  # update prod requirements
```

## 6. Release

1. Determine SemVer bump from commit log since last tag
1. Update version references if any
1. Tag: `git tag v<version>`
1. Build static site if needed: `python flask_se.py build`
1. Update Dockerfile if dependency changes

### Open Source Recommendations

For public deployment, consider: `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `CHANGELOG.md`, `CITATION.cff` (academic citation metadata), `.github/FUNDING.yml` (funding channels).

## 7. Process Improvements Backlog

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
