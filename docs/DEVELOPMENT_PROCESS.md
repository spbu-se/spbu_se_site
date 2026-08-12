# Development Process

<!-- encoding: utf-8 -->

Covers: planning, session lifecycle, code review, release management, dependency management, and discipline policies. Does not cover: version control workflow — see `docs/GIT_FLOW.md`, testing strategy — see `docs/TESTING.md`, architecture — see `docs/ARCHITECTURE.md`.

Flask-based website for the SPbSU System Programming Department. See `AGENTS.md` for pre-flight and setup quirks, `docs/GIT_FLOW.md` for version control, and `docs/AI_AGENTS.md` for AI tooling.

All doc management rules (creation, formatting, encoding, integrity checks) are in `docs/DOCS.md`.

## Process Identity

Foundational principles that shape every decision. See `docs/DEVELOPMENT_PROCESS.md` for the full doctrine.

### Pattern recurrence escalation

When a gap appears in consecutive retrospectives, the fix must escalate:

| Recurrence | Minimum escalation | Example |
|---|---|---|
| 1st | Layer 3 — documentation | Add rule to canonical doc |
| 2nd | Layer 2 — CI check | Add CI step that catches the gap |
| 3rd+ | Layer 1 — tool config | Pre-commit hook, linter rule, structural guard |

A fix at the same layer as the previous recurrence is not escalation — the layer must increase.

This project blends agile practices suited for single-agent development:

| From | We use | We deliberately reject |
|---|---|---|
| **XP** | TDD (test-first from specs), CI, coding standards (ruff), collective ownership, zero bugs | Pair Programming (replaced with batched staging review), fixed cadence |
| **Kanban** | Continuous flow, pull-based work selection (priority ladder), WIP-limited (one task) | Cycle time tracking, explicit board |
| **Shape Up** | Shaping phase (planning + doc-first), appetite sizing (S/M/L estimates) | 6-week cycles, betting table |

## Project Doctrine

Four layers guide every decision. A lower layer never violates a higher one.

### Layer 1 — Supreme Directives (inviolable)

| # | Directive | Meaning |
|---|-----------|---------|
| I | Never hurt the user | Students, staff, faculty. No technical choice degrades their experience, loses their data, or breaks their workflow. |
| II | Never hurt the product | Codebase, docs, infra, tests are long-term assets. Architectural debt, test gaps, missing docs erode them. |

### Layer 2 — Strategic Priorities (ordered, drive product success)

| Priority | Meaning |
|----------|---------|
| 1. Zero bugs | Any behavior deviating from documented specs blocks feature work |
| 2. Robust | CI gates, staging flow, pre-commit, test coverage — safety over convenience |
| 3. Clean history | Linear git, squash-merges, conventional commits, no stale branches |
| 4. Low effort | Automate, simple solutions, fast feedback — remove friction from all aims |

### Layer 3 — Operational Heuristics (cross-cutting, all apply simultaneously)

Like special ops: each has its mission, they coordinate, no single one dominates.

- **Document first** — intelligence before action. Write the decision, spec, or design before implementing.
- **Automate toil** — logistics. Anything done twice gets scripted. Manual steps are a risk vector.
- **Fail fast** — reconnaissance. Validate the riskiest assumption first. Break it on purpose in isolation before integrating.
- **Prefer simple** — KISS. The simplest correct solution wins. Over-engineering is the #1 repeated gap.
- **Save attempts, not screen space** — Re-running is the most expensive operation in the feedback loop. Optimize every command to produce complete diagnostics on the first attempt. Prefer full logs over clean output, batch-fix siblings before re-running, baseline before investigating new errors.

### Layer 4 — Practices (concrete, changeable)

Everything in `docs/GIT_FLOW.md`, `docs/TESTING.md`, `docs/TOOLING.md`, `.pre-commit-config.yaml`, CI workflows. Each practice traces upward to one or more Heuristics or Priorities.

Design decisions about deliberate deviations are recorded in `docs/DESIGN_DECISIONS.md`.

Covers: planning, testing, linting, code review, release, dependencies, session lifecycle, workflow discipline. Does not cover: CLI commands, architecture design, AI tooling, version control — see `docs/GIT_FLOW.md`.

## 0. CLI Quick Reference

```bash
uv sync                                       # install dependencies (dev + main)
uv run python src/flask_se.py                 # run dev server (http://127.0.0.1:5000)
uv run python src/flask_se.py init            # initialize database
uv run python src/wsgi.py                     # run via WSGI
uv run pytest                                 # run tests (full suite ~600s with -n auto)
uv run ruff check src/                        # lint
uv run ruff format src/                       # format
uv run python src/flask_se.py build               # build static site (Frozen-Flask)
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
1. Load relevant skill from `docs/AI_AGENTS.md` §Skills if available (e.g., `test-writer` for test tasks)
1. Discuss approach, confirm scope, get approval
1. Only then branch and implement

**Effort sizing:**

- **S**: Single-file change, no new deps, ~1h
- **M**: Multi-file, 2-3 modules, ~half day
- **L**: Multi-module, new patterns/deps, ~1d+

Planning phase is non-negotiable. Never jump to implementation without prior discussion.

## 0.6 Workflow Discipline

### Architecture first

Write design decisions in `docs/DESIGN_DECISIONS.md` before implementation.

### Doc first

Update docs that describe code that does not exist yet, commit, then implement.

### Check existing first

Before proposing any new tool, script, workflow, or process change — follow this required sequence:

1. **State the problem** in one sentence
1. **List existing tools** that might already solve it (and why they don't fit)
1. **Only then propose** new solutions

Over-engineering (solving completeness over practicality) is the #1 repeated gap — flagged in 4 consecutive retros.

This applies to all problem-solving modes (planning, troubleshooting, ad-hoc suggestions), not just formal planning. Examples:

- **CI fails on requirements.txt format** → check if pip itself validates (`pip install --dry-run`) before proposing a new script or workflow
- **Need to format code** → check what formatters are already configured (ruff, mdformat, dprint) before adding a new one
- **Need a test pattern** → check `docs/AI_AGENTS.md` §Skills and existing test files before creating a new fixture template

If the existing tool covers the need, use it. If not, prefer the simplest addition that closes the gap.

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

Before proposing merge to current:

1. Ensure `requirements.txt` matches lockfile. See `docs/GIT_FLOW.md §8` for the command.
1. Scan `docs/CODE_ISSUES.md` for stale [OPEN] entries — any bug whose fix was already committed but status not updated to [FIXED]. Update before merging.

### Pre-staging validation

Before staging after bulk doc edits, run the `mdformat` command that CI will use — not just `--check`. This catches missing files and path errors early. See `docs/DOCS.md §7.1` for the command.

### Pre-push discipline

Three tiers of quality, from local convenience to production gate:

#### Pre-commit (fast, ~1s, changed files only)

Auto-fix formatting on touched files. Runs on every `git commit`.
Not a quality gate — local commits can be imperfect. Using `git commit --no-verify` is acceptable.

#### Pre-push (strict, all files, fail-fast)

Checks (in order): requirements format → actionlint → `uv lock --check` → format + lint (mdformat, ruff format `--check`, ruff check on `src/ tests/`, via PowerShell) → basedpyright. Runs on every `git push`.

Failure at any step aborts. Format failure skips later checks.
This is the local quality gate that prevents unformatted or type-unsafe code from reaching staging.

**Platform caveat:** the format+lint step's entry is `powershell -Command "..."` (`.pre-commit-config.yaml` `pre-push-fast-checks`) — Windows-only. On Linux the pre-push hook fails with `Executable 'powershell' not found`; run the equivalent checks manually (see `AGENTS.md` §Pre-push) and log the `--no-verify` in the retrospective.

The pre-push gate exists because the agent has a documented pattern of skipping fast local checks to save seconds, costing minutes in CI round-trips. The fail-fast chain ensures that a format failure wastes at most ~3s instead of triggering a full check cycle.

An agent may propose `git push --no-verify` only when:

1. The user gives a direct, unbiased instruction (states a goal, not a method)
1. The agent clearly documents the risk before proceeding

#### CI (async, ~10min)

pytest runs on CI, not in pre-push. See `docs/AI_AGENTS.md` §CI discipline for when to check CI status.

#### Staging merge

Every push to staging should be publishable. The pre-push gate is the minimum bar for staging. CI must be green before merging to staging.

### Context compaction

Before compacting context or ending session:

- Update `docs/DESIGN_DECISIONS.md` with new choices
- Update `TODO.md` (remove completed — implemented work belongs in commit messages, not TODO; reorder backlog)
- Run AI instructions drift check (see `docs/DOCS.md §5.3`)
- Audit cross-references: scan every `.md` file under `docs/` and `.skills/` for hardcoded step numbers. Replace with section-title references.
- If session involved doc restructuring, propose retrospective as the finalization step (do not run mid-session)

### Task management

- **TODO.md**: every unimplemented idea MUST live in TODO.md Backlog or Icebox. Removing from Icebox requires explicit user request. Document rejection reasons in `docs/DESIGN_DECISIONS.md` when declining a feature.
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

The exact commands for each step are in `AGENTS.md` §Pre-flight checklist and `docs/GIT_FLOW.md` §1.2 (Rules — branch from staging).

### Session end — wrap-up protocol

**Why**: Knowledge must persist across sessions. Every session produces new decisions, dead ends, and metric changes — these must be captured before they are lost.

**What**:

1. **Update `docs/DESIGN_DECISIONS.md`** — any new tech/framework decision made during the session? Append dated entry.
1. **Update `docs/AI_AGENT_EXPERIENCE.md`** — any dead ends, debugging trails, or workarounds discovered? Append entry (also write immediately when hitting the dead end, not only at end).
1. **Refresh `requirements.txt`** if dependencies changed.
1. **Run docs-review for drift**:
   - Load the docs-audit skill (see `docs/AI_AGENTS.md` §Skills)
   - Run doc health checks (freshness, cross-references, scope, encoding)
   - EXCLUDE frequently changed knowledge docs: `AI_AGENT_EXPERIENCE.md`, `TODO.md`, `CODE_ISSUES.md`, `AGENTS.md` (these are expected to drift)
1. **Self-improvement check** — any new guardrails needed?
   - Process rules → `docs/DEVELOPMENT_PROCESS.md`
   - Pre-flight items → `AGENTS.md`
1. **Run the session retrospective — mandatory before any PR** — load the `retrospective-analysis` skill (light or full) and append the entry to `docs/RETROSPECTIVES.md` before opening a PR. If a PR was opened without it, add the retro as the last commit and update the PR description. This replaces the old "retro is not part of wrap-up" rule — every shipped session gets a retro entry. See `docs/RETROSPECTIVES.md`.
1. Write `.unfinished.plan.md` with date/time, focus task, branch, last commit hash, dirty files, completed and remaining steps, undocumented decisions.
1. If on a feature branch with unfinished code: commit WIP, create `_UNFINISHED.md` as the final commit. `_UNFINISHED.md` is always the last commit — stripped automatically by squash-merge. `.unfinished.plan.md` is never committed (see `.gitignore`).
1. Verify working tree is clean.

### Staging green rule

**Why**: Broken CI hides regressions from everyone. A red staging blocks all work until fixed.

**What**:

- CI on `origin/staging` must be green at all times
- Never commit to `staging` directly — all work goes to feature branches (or `staging-auto-*` in batch mode)
- Before every push: tests, lint, format, pre-commit, secrets check — all must pass
- After every push: wait for CI, fix immediately if red

The full pre-flight checklists are in `AGENTS.md` (Pre-flight checklist). The push command reference is in `docs/GIT_FLOW.md` §8.2 (CI status) and §2.1 (merge strategy).

## 0.8 Skill Conventions

Skills live in `.skills/<name>/README.md` (canonical). Per-vendor stubs in `.opencode/skills/`, `.claude/skills/`, `.agents/skills/`.
Skills architecture (definition, delegation chain, extraction triggers, creation checklist, lifecycle, maintenance) is in `docs/AI_AGENTS.md` §Skills.

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

### CI job vs step separation

Sequential steps in a single job use fail-fast (`bash -e` by default) — a failed step aborts the job, masking later results. This is acceptable for local pre-push (fast iteration, fix and retry in seconds).

For CI, use separate jobs with `needs: [...]` + `if: always()` so lint/type failures do not block test execution. Both results are visible in the CI summary. See `docs/QUALITY_MANAGEMENT.md §4` for rationale and pattern.

### Diagnosis: pre-commit hook not catching what CI catches

If CI fails on a check that pre-commit should have caught:

1. Run the hook manually: `uv run pre-commit run <hook-id> --all-files`
1. Does it crash? (check exit code + error output)
1. Does it use different paths/arguments than the CI workflow?
1. Does it work on one platform but not another?
1. Fix the entry point so the local check matches the CI check exactly.

## 0.13 Error triage

After every command that produces error output or a non-zero exit, ask:

"Was this expected? Would I have been surprised if it succeeded?"

- If yes (expected) → proceed, the error is a known path
- If no (unexpected) → stop and investigate. Root cause first, fix second, skip third.

## 0.14 Encoding Policy

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
| 2a | **Types** (active) | `basedpyright src/` passes, no new `# pyright: ignore[code]` — per-module overrides in pyproject.toml |
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
| 13 | **Crash safety scan** | No bare `except:`, no `sys.exit()` in non-CLI modules, routes handle DB errors, `request.form.get(...)` has default values |
| 14 | **File safety scan** | Upload path traversal blocked, file extension validated, `send_file` paths sanitized, temp files cleaned up |
| 15 | **Secrets in logs** | Scan CI output and application logs for leaked keys, tokens, passwords — distinguish ephemeral vs persistent |
| 16 | **Redirect validation** | Scan for unvalidated `next`-parameter redirects — verify relative URL check or whitelist |
| 17 | **Deprecation scan** | Check each P4 entry in `docs/CODE_ISSUES.md` against current dependency versions — escalate if now breaking |

## 5. Dependencies

Production dependencies in `requirements.txt` (pinned versions, generated by uv):

```bash
pip install -r requirements.txt
```

Development uses uv (see `docs/DESIGN_DECISIONS.md` §Dual Dep Management for rationale):

```bash
uv add <package>                       # add a new dependency
uv sync                                # install all deps (dev + main)
uv export --no-dev --no-hashes > requirements.txt  # update prod requirements
```

## 6. Release

Versioning is date-based — every release is tagged `vYYYY.MM.DD` (see
`docs/GIT_FLOW.md` §Versioning). Releasing:

1. Determine the previous release tag: `gh release list --repo spbu-se/spbu_se_site`
1. Run the `release-notes` skill (`.skills/release-notes/`) to generate
   `.tmp/release-notes.md` — Part 1 plain-English user summary, Part 2 developer
   changelog (dependencies table, major changes, contributors, compare link).
   Drafts live in `.tmp/` (gitignored) — never at the repo root.
1. Update version references if any
1. Build static site if needed: `uv run python src/flask_se.py build`
1. Update Dockerfile if dependency changes
1. Tag and push to the canonical repo (GPG-signed):
   ```bash
   git tag -s vYYYY.MM.DD && git push <upstream> vYYYY.MM.DD
   ```
1. CI (`deploy_to_production.yml`): the `deploy` job POSTs the production
   webhook; the `release` job (when `OPENCODE_ZEN_API_KEY` is set) creates a
   **draft** GitHub release with the generated notes
1. **Review the draft release, edit notes if needed, and publish manually** —
   drafts are never auto-published. Until the secret is configured, create the
   draft notes by hand following the skill.

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
