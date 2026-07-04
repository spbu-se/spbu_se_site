# Git Flow

Version control workflow, branching model, commit conventions, and guardrails for the SE Site project.

Covers: branching, commit rules, staging workflow, session start/end rituals, guardrails, stale branch audit, commit conventions. Does not cover: planning phase, testing requirements, code review — see `doc/DEVELOPMENT_PROCESS.md`.

## 1. Branching

| Prefix | Purpose |
|---|---|
| `feat/` | New features |
| `fix/` | Bug fixes |
| `refactor/` | No behavior change |
| `docs/` | Documentation |
| `test/` | Test-only |
| `experiment/` | Throwaway ideas — never merged to staging or current |
| `hotfix/` | Emergency production bug fixes or broken CI (bypasses staging) |
| `ci/` | CI workflow changes |
| `chore/` | Maintenance, deps, build config |

**Guardrail — branch creation**: before `git checkout -b`, commit or stash all working tree changes. Never branch with a dirty tree.

## 2. Workflow

1. **Branch** — `git checkout -b <prefix>/<name>` from `staging`.
1. **Architecture first** — write design decisions in `doc/ARCHITECTURE.md -> Design Decisions` before implementation.
1. **Doc first** — update docs that describe code that does not exist yet, commit, then implement.
1. **TDD**: write tests from docs -> implement -> format -> test -> commit.
1. Suggest merge into **staging** after every commit.
1. Fail -> `git branch -D experiment/<name>`.
1. **Hotfix lane** (production-blocking bugs or broken CI only):
   - Branch from `current`: `git checkout -b hotfix/<name>`
   - Test first, fix, commit `hotfix: <message>`
   - Merge directly to current (bypasses staging)
   - Tag `git tag v<version>`
   - Sync staging: `git checkout staging && git merge current`
1. **Merge into staging** — `git merge --squash <branch>` into `staging`. Tests must pass. Staging CI runs automatically.
1. **Enforcement self-check** — can it be automated (layer 1)? CI-checked (layer 2)? Or only documented (layer 3)?
1. **Pre-merge refresh** — before proposing merge to current, run `uv export --no-dev --no-hashes > requirements.txt` and commit if changed.
1. **Staging->current gate** — full verification against the checklist in `doc/DEVELOPMENT_PROCESS.md`.
1. **Propose finalization** — show diff, await user approval, run gate, merge `--ff-only`.
1. **Context Compaction** — update ARCHITECTURE.md, TODO.md, verify docs sync.
1. **Retrospective & stale branch audit** — after each merge to current.
1. **Task priority ladder**: CI fixes > PRs > stale branches > backlog > icebox.

## 3. Guardrails

### Session start

1. `git fetch --prune origin`
1. `git status` — check for orphaned WIP
1. `git checkout staging && git pull --ff-only origin staging` — sync staging
1. `git log --oneline origin/staging ^origin/current` — check staging ahead of current
1. `uv run pre-commit run --all-files` — verify all hooks pass before starting new work (catches repo-wide format/lint drift)
1. `git checkout -b <prefix>/<name>`

### Stale branch awareness

List stale branches before new tasks: `git branch -r --no-merged origin/current` + `git branch -r --no-merged origin/staging`.

### Rebase policy

Feature branches only, pre-stage only, solo branches only, `--force-with-lease`.

### When to hotfix

Only for production-blocking bugs or broken CI. Never for improvements.

## 4. Commit Sequence

### 4.1 Staging discipline

Never use `git add .` or `git add -A` without reviewing what is staged. Always stage files explicitly:

```bash
git add src/flask_se.py tests/test_smoke.py
```

Before committing, verify only source files are staged:

```bash
git diff --cached --name-only
```

**Reject any staged file that is:**

- A build artifact (`.coverage`, `*.egg-info/`, `*.pyc`, `.ruff_cache/`, `.pytest_cache/`)
- A generated binary/dump (`.db`, `.sqlite`, `.log`)
- A vendored dependency that should be managed elsewhere

### 4.2 Adding a new tool

When introducing a new linter, formatter, or build tool that produces files:

1. Add its artifact patterns to `.gitignore` **before** running the tool
1. Verify with `git status --short` that nothing unexpected appeared
1. Only then commit the tool config

**Default pattern for any new tool:** `git check-ignore <path>` should return a rule. If it doesn't, the artifact is not protected.

### 4.3 Rescue

If an artifact was committed by accident:

```bash
git rm --cached <path/to/artifact>
echo "<pattern>" >> .gitignore
git add .gitignore
git commit -m "chore: remove <artifact> from tracking"
```

### 4.4 Pre-commit hooks

Pre-commit hooks run automatically (see `.pre-commit-config.yaml`). The following hooks block obvious garbage:

| Hook | Blocks |
|---|---|
| `check-added-large-files` | Files > 500 KB |
| `check-case-conflict` | Case conflicts on case-insensitive FS |
| `check-json` / `check-yaml` | Invalid syntax in structured files |

Conventional Commits enforced by commitlint.

### 4.5 Branch prefix to commit type

| Branch prefix | Commit type |
|---|---|
| `feat/` | `feat:` |
| `fix/` | `fix:` |
| `refactor/` | `refactor:` |
| `docs/` | `docs:` |
| `test/` | `test:` |
| `hotfix/` | `hotfix:` |
| `ci/` | `ci:` |
| `chore/` | `chore:` |

### Signoff policy

Only merge commits to `current` require GPG signoff:

- `staging → current` merge
- `hotfix/ → current` merge
- `git tag v<version>` (tagged merge commit)

Regular commits to staging or feature branches use `--no-gpg-sign` (no signoff).
This avoids GPG agent timeouts when password storage (KeePass) is locked.

**Guardrail — never touch global git config** (`git config --global`).
Signoff policy is enforced via commit flags, not global settings.

## 5. Staging Phase

Staging is a permanent branch — never deleted.

**Two-tier quality gate**: Feature -> staging (tests pass). Staging -> current (100% coverage, docs sync).

**Rules**: Every non-hotfix branch merges into staging first. Direct-to-current forbidden (exception: hotfix).

## 6. Commit Rules & Versioning

### Linter-only commits

Commits that only touch formatters/linters (ruff, mdformat, dprint) and pass all checks need no user review. The agent may commit and push directly to staging.

### AI instruction changes

Facts must originate in canonical docs (`doc/*.md`) before being referenced in AI instructions (`AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md`). Never author facts directly in AI instructions. Confirm with user before committing AI instruction changes.

### .editorconfig sync

Every new file type should have an `.editorconfig` entry. Keep `.editorconfig` in sync with formatter configs (dprint, ruff).

## 7. Session End Ritual

When pausing or ending a session with unfinished work:

1. Check `git status --short` for dirty/uncommitted files
1. Write `.unfinished.plan.md` with: date/time, focus task, branch, last commit hash, dirty files, completed steps, remaining actions, undocumented decisions, next steps
1. If on feature branch with unfinished code: `git add -A && git commit -m "wip: <description>"`, create `_UNFINISHED.md` summarizing state, commit it
1. Run `uv export --no-dev --no-hashes > requirements.txt` if deps changed
1. Verify working tree is clean

## 8. Versioning

SemVer: MAJOR (breaking), MINOR (feat), PATCH (fix, docs, etc.). Tag every merge to current: `git tag v<version>`.

## 9. Retrospectives

### Retrospective — 2026-07-04: cross-doc duplication, CI mismatch, over-engineering recurrence

This session touched 22 files across docs, tests, config, and skills. Gaps found:

| Gap | Root cause | Fix |
| --- | ---------- | ---- |
| GPG/signoff rule duplicated across GIT_FLOW.md, TOOLING.md, .tooling.md, CLAUDE.md | Cross-doc duplication | Canonical source is GIT_FLOW.md §4 — other docs cross-reference instead |
| Test expectations failed in CI (test data mismatched) | Missing config — no CI environment parity check | Added to DEVELOPMENT_PROCESS.md §3.5 code review checklist |
| Vendor libs, .coverage, .ruff_cache, egg-info tracked in git | Missing config — .gitignore incomplete | Fixed during session |
| Pre-existing code didn't pass new pre-commit hooks | Missing config — hooks added retroactively, no bulk-format step | Added `pre-commit run --all-files` to session-start ritual |
| User correction: unattended-mode over-engineered twice | Pattern recurrence — same over-engineering from previous retro | Added "check existing first" guard to planning phase (DEVELOPMENT_PROCESS.md §0.5) |

**Pattern recurrence**: YES — over-engineering pattern appears in 2nd consecutive retro. Escalated with planning-phase guard.

**What went wrong**: Multiple config gaps (gitignore, linter exclusions, CI parity) accumulated because tooling was added incrementally without a systematic artifact audit. The over-engineering pattern recurred despite being flagged in the previous retro — the fix was too weak (skill documentation) and needed a process-level guard.

**Root causes**: Missing config (4 gaps), pattern recurrence (1 gap), cross-doc duplication (1 gap).

**Fix**: Session-start ritual now includes pre-commit --all-files check. Code review checklist now includes CI parity check. Planning phase now includes "check existing" guard. GPG policy consolidated to GIT_FLOW.md only.

### Retrospective — session-start ritual violated

During a documentation extraction session, the agent committed a docs commit directly to `current` (bypassing staging) and later attempted git write operations (`reset`, `checkout -b`, `add`, `commit`) while explicitly in plan mode.

**What went wrong**: The plan mode guard was documented in the session prompt but had no automated enforcement. A single user approval to "proceed" unlocked all subsequent git write commands. The session-start ritual (fetch, status, branch) was also skipped — orphaned WIP from a prior session (ruff formatting + accidentally deleted workflow files) was present but not handled at session start.

**Root causes**:

1. No tool-level deny for git write operations during plan mode — the guard was human-enforced only
1. Orphaned WIP was visible at session start (`git status`) but was not branched or committed before new work began

**Fix**: Added bash permission rules to the AI tooling config (`.opencode/opencode.json` or equivalent) that explicitly deny `git reset`, `git checkout`, `git commit`, `git add`, `git merge`, `git push`, `git tag` during plan mode. Only read-only git commands (`log`, `status`, `diff`, `branch`) are allowed. See `doc/OPENSE_CONFIG.md` for the permission configuration.
