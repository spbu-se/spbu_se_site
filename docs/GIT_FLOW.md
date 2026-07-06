# Git Flow

<!-- encoding: utf-8 -->

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
| `staging-auto-*` | Auto-mode throwaway branches — scratch space for batch work, later squash-merged to staging with clean feature-grouped commits (never raw). See `.skills/unattended-mode/README.md` |

**Guardrail — branch creation**: before `git checkout -b`, commit or stash all working tree changes. Never branch with a dirty tree — uncommitted edits silently leak into the wrong commits.

## 2. Workflow

1. **Branch** — `git checkout -b <prefix>/<name>` from `staging`.
1. **Architecture first** — write design decisions in `doc/ARCHITECTURE.md -> Design Decisions` before implementation.
1. **Doc first** — update docs that describe code that does not exist yet, commit, then implement.
1. **Mid-sprint violation** — if architecture-first or doc-first step was skipped, create a `TODO.md` Backlog entry. Fixing it (document decision, rearrange code if needed) is a **must-have** before the next feature.
1. **TDD**: write tests from docs -> implement -> format -> test -> commit.
1. Suggest merge into **staging** after every commit.
1. Fail -> `git branch -D experiment/<name>`.
1. **Hotfix lane** (production-blocking bugs or broken CI only):
   - Branch from `current`: `git checkout -b hotfix/<name>`
   - Test first, fix, commit `hotfix: <message>`
   - Merge directly to current (bypasses staging)
   - Tag `git tag v<version>`
   - Sync staging: `git checkout staging && git merge current`
   - **Log debt**: add `[HOTFIX_DEBT] Review origin of hotfix/<name>, then backfill docs, expand test coverage, and verify the fix is complete` to TODO.md Backlog — P0 priority, must resolve before any new feature work
1. **Merge into staging** — `git merge --squash <branch>` into `staging`. Tests must pass. Staging CI runs automatically.
1. **Enforcement self-check** — before staging→current gate, audit each decision from this session:
   - Can it be automated? → tool config (layer 1)
   - Can it be CI-checked? → add a workflow step (layer 2)
   - Is documentation the only option? → document (layer 3)
   - Is its git tracking status correct? → every new file must be either `.gitignored` (local-only) or tracked (shared). Verify intent before commit.
   - If a rule is documented WITHOUT checking layers 1-2 first, the session is incomplete. Add the automated check before proceeding to the gate.
1. **Pre-merge refresh** — before proposing merge to current, run `uv export --no-dev --no-hashes` and commit if changed.
1. **Staging→current gate** — full verification against the checklist in `doc/DEVELOPMENT_PROCESS.md`. Before gate:
   - Check every `.md` file has: H1 → one-sentence aim → scope note covering what it does and does not document
   - Verify no content duplicates another doc — cross-reference instead
   - Fix hidden issues, improve process docs, add retrospective findings
1. **Propose finalization** — show diff (`git log --oneline current..staging`), await user approval, run gate, merge `--ff-only`. If CI fails on current after merge → stop, don't push, fix in a branch.
1. **Context Compaction** — before compacting context or ending session:
   - Update ARCHITECTURE.md Design Decisions with new choices
   - Update TODO.md (remove completed, reorder backlog)
   - **AI instructions drift check**: verify no unique content in AI instructions — every claim must cross-reference a canonical source. If a new quirk is needed, write the full version in the canonical doc first, then extract a condensed cross-reference.
   - Audit cross-references: scan every `.md` file under `doc/` and `.skills/` for hardcoded step numbers. Replace with section-title references (e.g. `§2 — Task selection priority ladder` instead of `step 50`).
1. **Retrospective & stale branch audit** — after each merge to current. Run `git branch --merged current | Select-String -NotMatch "current"` and auto-delete. If 5+ merges since last doc audit, run a doc health check (verify scope, no cross-doc duplication). If tasks are needed, optionally run `repo-review` skill to generate backlog.
1. **TODO management** — every unimplemented idea MUST live in `TODO.md` Backlog or Icebox. Removing from Icebox requires explicit user request. Document rejection reasons in ARCHITECTURE.md Design Decisions when declining a feature. The product includes what is NOT implemented — document why.
1. **Task priority ladder**: CI fixes > PRs > stale branches > backlog > icebox.

## 3. Guardrails

### Session start

1. `git fetch --prune origin`
1. **Read `.unfinished.plan.md`** — if it exists, it contains the previous focus task, dirty files, and next steps. Read it BEFORE checking git status so you know what was interrupted.
1. `git status` — check for orphaned WIP. If dirty: branch and commit. Also check for new untracked dotfiles not in `.gitignore` — they may need an exception.
1. `git checkout staging && git pull --ff-only origin staging` — sync staging
1. `git log --oneline origin/staging ^origin/current` — check staging ahead of current
1. `uv run pre-commit run --all-files` — verify all hooks pass before starting new work (catches repo-wide format/lint drift)
1. `git checkout -b <prefix>/<name>`

### Stale branch awareness

List stale branches before new tasks: `git branch -r --no-merged origin/current` + `git branch -r --no-merged origin/staging`.

### Rebase policy

Feature branches only, pre-stage only, solo branches only, `--force-with-lease`.

Exception: if a stale branch has 10+ commits or 5+ file conflicts, rebasing onto staging before squash-merging is **recommended** — it turns a single huge conflict resolution into manageable per-commit steps.

### When to hotfix

Only for production-blocking bugs that prevent users from completing a critical workflow, or when a GitHub CI workflow is broken. Never for improvements — hotfix is only initiated on explicit user request. If unsure, ask the user.

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

Conventional Commits enforced by commitlint. Test manually: `pre-commit run commitlint --hook-stage commit-msg`.

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

**Auto-mode (unattended):** all commits on `staging-auto-*` branches use `--no-gpg-sign`.\
**Non-auto (interactive):** merges to `staging` require GPG signoff.

**Guardrail — never touch global git config** (`git config --global`).
Signoff policy is enforced via commit flags, not global settings.

## 5. Staging Phase

Staging is a permanent branch — never deleted.

**Two-tier quality gate**: Feature -> staging (tests pass). Staging -> current (100% coverage, docs sync).

**Self-certify process changes** — if this session added or modified an audit/check step (lint, CI, doc audit, etc.), run it against current staging before merging. Process improvements must demonstrate they find real issues in the state they're being merged into.

**Rules**: Every non-hotfix branch merges into staging first. Direct-to-current forbidden (exception: hotfix).

## 6. Commit Rules & Versioning

### Process docs during code work

Do not update process documentation while implementing features or fixing bugs on a feature branch. Instead, gather observations and suggest improvements. Process doc changes happen during **staging→current gate** (see §2) or on dedicated `docs/` branches.

**Exception**: if the architecture-first or doc-first cycle was violated (code before doc), add a `TODO.md` debt entry mid-sprint — this is a violation record, not a doc change.

### Linter-only commits

Commits that only touch formatters/linters (ruff, mdformat, dprint) and pass all checks need no user review. The agent may commit and push directly to staging.

After such a commit lands on staging, add its hash to `.git-blame-ignore-revs` (create if missing). Run `git blame --ignore-revs-file .git-blame-ignore-revs` to skip formatting noise.

### Stop signal

When any commit requires user review (AI instruction change, process change, non-trivial decision), output a visible stop banner and do NOT proceed:

```
🟡 STOP — <reason>
```

Do not commit, stash, or proceed without user approval. This overrides all automation rules — if in doubt, STOP.

### AI instruction changes

Facts must originate in canonical docs (`doc/*.md`) before being referenced in AI instructions (`AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md`). Never author facts directly in AI instructions. Confirm with user before committing AI instruction changes.

### .editorconfig sync

Every new file type should have an `.editorconfig` entry. Keep `.editorconfig` in sync with formatter configs (dprint, ruff).

## 7. Session End Ritual

When pausing or ending a session with unfinished work:

1. Check `git status --short` for dirty/uncommitted files
1. Write `.unfinished.plan.md` with: date/time, focus task, branch, last commit hash, dirty files, completed steps, remaining actions, undocumented decisions, next steps
1. If on feature branch with unfinished code: `git add -A && git commit --no-gpg-sign -m "wip: <description>"`. Then create `_UNFINISHED.md` summarizing state, commit it as a separate **final commit**.
1. `_UNFINISHED.md` is always the **last commit** on the branch. This makes it easy to strip during squash-merge into staging (squash condenses all commits, so it's naturally dropped).
1. `.unfinished.plan.md` is **never committed** — it's in `.gitignore`. It guides the next session start.
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

### Retrospective — 2026-07-04: squash-merge from auto branch, CI green, test gaps found

Merged 30 commits from `staging-auto-20260704T154021Z` into staging via squash-merge (89 files, 1120 insertions). Key findings during the merge cycle:

- **logged_client session key**: fixture used `sess["user_id"]` but Flask-Login 0.6.3 reads `sess["_user_id"]` (with underscore). All practice/review tests were returning 302 instead of 200, masking low coverage. Fixing this immediately raised coverage from 47% to 51%.
- **post_vote bug**: `render_template(url_for("index"))` passes a URL path to `render_template()` instead of a template name — raises `TemplateNotFound`. This was a real production bug found by the test suite.
- **mdformat on Linux**: CI uses Linux which has different mdformat behavior than Windows. Several markdown files that looked fine locally failed mdformat --check on CI. Fix: always run `uv run mdformat .` before pushing.
- **Squash-merge with report commits**: 2× auto-run report commits were naturally absorbed by the squash. The single commit message grouped changes by feature/module/topic for human readability.

**What went well**: Session-scoped seeded DB brought full suite from 10+ min to 3.2 min. Coverage went from 31% to 51% in one session. The squash-merge workflow (branch → work → retro → report → merge) worked end-to-end.

**What went wrong**: logged_client fixture was wrong from the start, causing all authenticated route tests to not actually authenticate. The gap was only found when coverage numbers didn't improve with more tests.

**Fix**: Updated TOOLING.md with the correct `_user_id` session key. Added `pass_filenames: false` to the mdformat pre-commit hook so it checks ALL markdown files (not just staged ones) — aligns pre-commit behavior with CI. Documented retro entry.

### Retrospective — 2026-07-06: encoding corruption, doc/docs rename, process fixes

Post-coverage session covering `doc/`→`docs/` rename, encoding policy enforcement, commit cadence clarifications, and retrospective skill updates. Does not cover code changes (see previous retro).

**Changes analyzed**: ~140 files (92 `.py` + `.md` encoding declarations, cross-reference updates, process doc fixes).

**Gaps found**:

| Gap | Type | Fix |
|-----|------|-----|
| PowerShell `Set-Content` defaulting to Windows-1252 — corrupted all `.md` during bulk replace | Missing convention | Documented in `docs/TOOLING.md §PowerShell encoding`. Added encoding declaration policy to `docs/DEVELOPMENT_PROCESS.md §0.11`. |
| mdformat doesn't show file path on `UnicodeDecodeError` | Missing template | Added detection script to `docs/TOOLING.md`. |
| mdformat `.` traverses `.venv/`, `.opencode/node_modules/` | Missing config | Updated workflow to use explicit paths only. |
| No pre-commit guard for non-UTF-8 files | Missing config | Needs `check-encoding` hook — deferred to separate commit. |
| No encoding declarations in any file | Missing convention | Added `# -*- coding: utf-8 -*-` to 86 `.py` files. Added `<!-- encoding: utf-8 -->` to 53 `.md` files. |
| Commit cadence rules conflated auto vs interactive mode | Human error | Updated `doc/GIT_FLOW.md §4.0` with mode-dependent table. Updated `.skills/unattended-mode/README.md`. |
| `doc/REPO_REVIEW.md` not updated to `docs/` in `.gitignore` | Human error | Fixed. |

**Pattern recurrence**: YES — "facts in AGENTS.md without canonical source" and "pre-creation without checking existing scope" both recurred from previous retros. Escalated with:

- Pre-creation audit step in skill workflow
- Pre-write gate for process docs
- Canonical source discipline in `DEVELOPMENT_PROCESS.md §0.10`

**What went well**:

- Cross-reference update completed across ~25 files with no manual errors.
- Encoding declarations added to 139 files across all formats.
- `git checkout --` saved the session from corruption twice.
- Pyright config added — no more false LSP import errors.

**What went wrong**:

- PowerShell encoding ambush cost ~45 min of recovery (find corruption → restore → run mdformat → hit next corruption → repeat).
- Initial `doc/`→`docs/` rename created confusion because `docs/` already existed as Flask-Freezer build output.
- Encoding `replace-all` script destroyed Russian UTF-8 text in 7 docs files before `git checkout` restored them.

**Root causes**:

1. No PowerShell encoding policy documented — `Set-Content` silently corrupted files.
1. No pre-write guard for "does this path conflict?" before file operations.
1. No pre-commit hook validating UTF-8 encoding — corruption was only caught when mdformat failed.

**Fix**: Documented PowerShell encoding policy. Added encoding declaration to every file. `_flask_freezed/` moved to `.gitignore`. Workflow updated to use `[System.IO.File]::WriteAllText()`.

**Knowledge extracted**:

- PowerShell encoding workaround → `docs/TOOLING.md`
- pyright config for uv venv → `pyproject.toml [tool.pyright]`

**Agent handoff**:

- mdformat `.` will fail on vendor files — always use explicit paths
- PowerShell `Set-Content` is Windows-1252 — use `[System.IO.File]::WriteAllText`
- `git checkout -- <paths>` is the safety net for encoding corruption
- 91.38% coverage, 912 tests — remaining gaps: Whoosh (3 xfail), OAuth (2 xfail), theses (50%)
