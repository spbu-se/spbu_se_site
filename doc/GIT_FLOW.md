# Git Flow

Version control workflow, branching model, commit conventions, and guardrails for the SE Site project.

Covers: branching, commit rules, staging workflow, session start/end rituals, guardrails, stale branch audit. Does not cover: planning phase, testing requirements, code review — see `doc/DEVELOPMENT_PROCESS.md`.

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
1. `git checkout -b <prefix>/<name>`

### Stale branch awareness

List stale branches before new tasks: `git branch -r --no-merged origin/current` + `git branch -r --no-merged origin/staging`.

### Rebase policy

Feature branches only, pre-stage only, solo branches only, `--force-with-lease`.

### When to hotfix

Only for production-blocking bugs or broken CI. Never for improvements.

## 4. Commit Sequence

Pre-commit hooks run automatically (see `.pre-commit-config.yaml`). Conventional Commits enforced by commitlint.

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

## 5. Staging Phase

Staging is a permanent branch — never deleted.

**Two-tier quality gate**: Feature -> staging (tests pass). Staging -> current (100% coverage, docs sync).

**Rules**: Every non-hotfix branch merges into staging first. Direct-to-current forbidden (exception: hotfix).

## 6. Versioning

SemVer: MAJOR (breaking), MINOR (feat), PATCH (fix, docs, etc.). Tag every merge to current: `git tag v<version>`.

## 7. Retrospectives

### Retrospective — session-start ritual violated

During a documentation extraction session, the agent committed a docs commit directly to `current` (bypassing staging) and later attempted git write operations (`reset`, `checkout -b`, `add`, `commit`) while explicitly in plan mode.

**What went wrong**: The plan mode guard was documented in the session prompt but had no automated enforcement. A single user approval to "proceed" unlocked all subsequent git write commands. The session-start ritual (fetch, status, branch) was also skipped — orphaned WIP from a prior session (ruff formatting + accidentally deleted workflow files) was present but not handled at session start.

**Root causes**:

1. No tool-level deny for git write operations during plan mode — the guard was human-enforced only
1. Orphaned WIP was visible at session start (`git status`) but was not branched or committed before new work began

**Fix**: Added bash permission rules to the AI tooling config (`.opencode/opencode.json` or equivalent) that explicitly deny `git reset`, `git checkout`, `git commit`, `git add`, `git merge`, `git push`, `git tag` during plan mode. Only read-only git commands (`log`, `status`, `diff`, `branch`) are allowed. See `doc/OPENSE_CONFIG.md` for the permission configuration.
