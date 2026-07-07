# Git Flow

<!-- encoding: utf-8 -->

Version control workflow, branching model, commit conventions, and guardrails for the SE Site project. Every practice here answers: *which Strategic Priority does this serve? Which Operational Heuristic does it follow?* See `docs/DEVELOPMENT_PROCESS.md` §Process Identity → Project Doctrine.

Covers: branching, merge strategy, commit discipline, rebase policy, signoff policy, versioning. Does not cover: planning phase, development process, code review — see `docs/DEVELOPMENT_PROCESS.md`. Retrospectives — see `docs/RETROSPECTIVES.md`.

## 1. Branching

### 1.1 Prefixes

| Prefix | Purpose | Merges to | Lifecycle |
|--------|---------|-----------|-----------|
| `feat/` | New features | staging | Delete after squash-merge |
| `fix/` | Bug fixes | staging | Delete after squash-merge |
| `refactor/` | No behavior change | staging | Delete after squash-merge |
| `docs/` | Documentation | staging | Delete after squash-merge |
| `test/` | Test-only | staging | Delete after squash-merge |
| `hotfix/` | Emergency production bug or broken CI | current (direct) | Delete after merge + sync to staging |
| `ci/` | CI workflow changes | staging | Delete after squash-merge |
| `chore/` | Maintenance, deps, build config | staging | Delete after squash-merge |
| `staging-auto-*` | Auto-mode scratch space | staging (squash) | Squash-merged with clean feature-grouped commits |
| `experiment/` | Throwaway ideas | never | `git branch -D` |

### 1.2 Rules

- **Branch from staging** — always. Exception: `hotfix/` branches from `current`.
- **Dirty tree guard** — before `git checkout -b`, commit or stash all working tree changes. Uncommitted edits silently leak into the wrong commits.
- **Auto-branch naming** — in unattended mode: `git checkout -b staging-auto-<UTC-timestamp> origin/staging`.

## 2. Merge Strategy

### 2.1 Feature → staging

**Why**: Squash-merge keeps staging history linear and readable — one commit per feature, easy to review and revert. This aligns with [Strategic Priority: Low effort] and [Strategic Priority: Clean history].

**How**:

```bash
git checkout staging
git merge --squash <branch>
git commit -m "feat: <summary>"
```

**Exception for `experiment/`**: never merged. Delete with `git branch -D experiment/<name>`.

**Never continue on a squash-merged branch without explicit user instruction**. After `git merge --squash` to staging, the branch is consumed. Any further work must either start a new branch or be explicitly approved — squash-merge creates a different commit tree, and git cannot cleanly merge subsequent changes.

### 2.2 Staging → current

**Why**: Fast-forward merge guarantees `current` is always an ancestor of `staging` — history stays linear, no merge bubbles. If they diverge, something went wrong and must be investigated before proceeding. This aligns with [Strategic Priority: Robust].

**How**:

```bash
git checkout current
git merge --ff-only staging
```

### 2.3 Hotfix → current (direct lane)

**Why**: Production-blocking bugs must reach production immediately — aligns with [Strategic Priority: Zero bugs]. The debt log documents the quality tradeoff: speed now, backfill later.

**How**:

```bash
git checkout -b hotfix/<name> current
# fix, test, commit
git checkout current
git merge hotfix/<name>
git tag v<version>
git checkout staging
git merge current
```

Bypasses staging for production-blocking bugs only. After merge, log debt in `TODO.md`:

```
[HOTFIX_DEBT] Review origin of hotfix/<name>, then backfill docs, expand test coverage, and verify the fix is complete
```

### 2.4 Staging is permanent

Staging is never deleted. It is the integration branch where all features converge before the quality gate to `current`.

**Quality gate**: Feature → staging (tests pass). Staging → current (full verification via `docs/DEVELOPMENT_PROCESS.md §3.5`).

## 3. Commit Discipline

### 3.1 Staging discipline

**Why**: Explicit staging prevents accidental commits of build artifacts and generated files — these pollute history and create noise in blame and review. Keeping them out from the start avoids later cleanup cost.

**What**: Stage files explicitly, never `git add .` or `git add -A`. Reject build artifacts, generated binaries, and vendored dependencies (see `.gitignore` for the canonical deny list).

**How**:

```bash
git add <file1> <file2>
git diff --cached --name-only
```

### 3.2 Adding a new tool

When introducing a linter, formatter, or build tool that produces files:

1. Add its artifact patterns to `.gitignore` **before** running the tool
1. Verify with `git status --short` that nothing unexpected appeared
1. Only then commit the tool config

**Default pattern**: `git check-ignore <path>` should return a rule. If it doesn't, the artifact is not protected.

### 3.3 Rescue

**Why**: Accidents happen. A documented rescue pattern saves debugging time and prevents further corruption (like accidentally committing the fix instead of removing the artifact). This aligns with [Strategic Priority: Low effort].

**What**: If an artifact was committed by accident, remove it from tracking and add its pattern to `.gitignore`.

**How**:

```bash
git rm --cached <path/to/artifact>
echo "<pattern>" >> .gitignore
git add .gitignore
git commit -m "chore: remove <artifact> from tracking"
```

### 3.4 Branch prefix → commit type

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

### 3.5 Linter-only commits

**Why**: Formatting-only changes are mechanical — they carry no behavioral risk and blocking the author for review wastes time. This aligns with [Strategic Priority: Low effort].

**What**: Commits that only touch formatters or linters (ruff, mdformat, dprint) and pass all checks need no user review. May be committed and pushed directly to staging.

**How**: After such a commit lands on staging, add its hash to `.git-blame-ignore-revs` (create if missing). Run `git blame --ignore-revs-file .git-blame-ignore-revs` to skip formatting noise.

## 4. Signoff Policy

| Merge type | Signoff | Why |
|-----------|---------|-----|
| Feature → staging | `--no-gpg-sign` | Avoids GPG agent unlock during frequent commits |
| `staging-auto-*` commits | `--no-gpg-sign` | Required for unattended automation |
| Interactive staging merges | GPG signoff | Merges to permanent integration branch |
| `staging` → `current` | GPG signoff | Production gate |
| `hotfix/` → `current` | GPG signoff | Production gate |
| `git tag v<version>` | GPG signoff | Tagged merge commit |

**Guardrail**: signoff policy is enforced via per-command flags, not global git config. Never set `commit.gpgsign` globally — automation branches must not trigger keylocker dialogs.

## 5. Rebase Policy

- **When allowed**: feature branches only, pre-stage only, solo branches only.
- **How**: use safe force-push (see git documentation for the correct flag — never bare `--force`).
- **When recommended**: if a stale branch has 10+ commits or 5+ file conflicts, rebasing onto staging before squash-merging turns a single huge conflict resolution into manageable per-commit steps.

## 6. Stale Branch Audit

**Why**: Stale branches accumulate and create confusion — which branches are active? which were abandoned? Cleaning after each merge keeps the branch list trustworthy and reduces cognitive load. This aligns with [Strategic Priority: Low effort].

**What**: After each merge to current, delete merged local branches. Before new tasks, list stale remote branches.

**How**:

```bash
git branch --merged current | Select-String -NotMatch "current"
```

Delete all listed branches. List stale remote branches before new tasks:

```bash
git branch -r --no-merged origin/current
git branch -r --no-merged origin/staging
```

## 7. Versioning

SemVer: MAJOR (breaking), MINOR (feat), PATCH (fix, docs, etc.). Tag every merge to current:

```bash
git tag v<version>
```

## 8. GitHub Integration

### 8.1 Branch protection (aspirational)

**Why**: Prevents accidental pushes to `current` and ensures CI quality gates are enforced before production merges. This aligns with [Strategic Priority: Robust] — no bypass of the staging→current gate.

**What**: Protect `current` from direct pushes and enforce status checks. Requires repo admin access.

### 8.2 CI status

**Why**: Fast CI feedback reduces debugging cost — catching a failure seconds after push is cheaper than finding it hours later. This aligns with [Strategic Priority: Low effort].

**What**: Before starting new work, verify CI on staging is green. After push, wait for CI completion.

**How**:

```bash
gh run list --branch staging --json status,conclusion,databaseId
gh run view <run-id> --log-failed
gh run watch <run-id>
```

### 8.3 Pre-merge refresh

**Why**: `requirements.txt` is the production install source — if it doesn't match the lockfile, CI fails and blocks the merge. Checking before proposing saves a CI cycle and avoids a blocking failure at the gate.

**What**: Before proposing merge to current, ensure `requirements.txt` matches the lockfile.

```bash
uv export --no-dev --no-hashes > requirements.txt
```

Commit if changed. CI on `staging` validates freshness automatically.
