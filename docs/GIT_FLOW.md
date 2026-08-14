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

**Quality gate — pre-push**: Before proposing squash-merge, ensure the branch's pre-push hooks passed cleanly. The pre-push gate is the minimum bar for staging — if a branch cannot pass pre-push, it should not be merged.

**Quality gate — CI (PR gate)**: Feature branches (`feat/`, `fix/`, `refactor/`, `docs/`, `test/`, `ci/`, `chore/`) do not trigger the `CI (staging)` workflow. Before merging any pushed feature branch to staging:

1. Create a PR: `gh pr create --base staging --head <branch> --title "<summary>"`
1. Wait for CI: `gh pr checks <number> --watch`
1. If CI fails, fix on branch, push, retry
1. Only when green, merge: `gh pr merge <number> --squash --delete-branch`

**Mandatory retrospective before any PR**: every PR must have a session
retrospective entry appended to `docs/RETROSPECTIVES.md` (run
`.skills/retrospective-analysis`) before the PR is created. If a PR was opened
without one, add the retro as the last commit and update the PR description. See
`docs/DEVELOPMENT_PROCESS.md §0.7` (Session lifecycle).

**Exception**: `staging-auto-*` branches skip the PR gate — their name pattern already matches the CI workflow trigger.

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

**Quality gate**: Feature → staging (tests pass). Staging → current (full verification via `docs/DEVELOPMENT_PROCESS.md §4.5`).

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

Date-based versions: every release is tagged `vYYYY.MM.DD` (zero-filled, e.g.
`v2025.09.09`, `v2026.08.08`). Date versions are inherently ordered and
unambiguous, and they match the release cadence — there is no semantic bump to
derive. The release tag is created only when a release is actually shipped, not
on every merge to `current`.

**Release flow** (see `docs/DEVELOPMENT_PROCESS.md` §Release):

```bash
git tag -s vYYYY.MM.DD           # GPG-signed tag at current
git push <upstream> vYYYY.MM.DD  # pushes to the canonical repo
```

Pushing the `v*.*.*` tag to `upstream` **prepares** the release — it does not
deploy. When the `OPENCODE_ZEN_API_KEY` secret is configured, the `release` job
in `deploy_to_production.yml` creates a **DRAFT** GitHub release with notes
generated by the `release-notes` skill (`.skills/release-notes/`). The draft is
never auto-published: the maintainer reviews the notes and publishes manually.
Until the secret is set, draft notes are created by hand following the skill.

Production deploys only when a release is **published**: the `deploy` job in
`deploy_to_production.yml` runs on `release: published` and POSTs the production
webhook with the release tag and its pinned commit. A tag that is never released
never reaches production.

If a tag already exists and must be re-created (e.g. a mis-tag), delete it first:
`git tag -d vYYYY.MM.DD` and `git push <upstream> --delete vYYYY.MM.DD`.

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

### 8.4 PR gate for feature branches

See §2.1 — the PR gate is the standard path for all feature branches pushed to remote. Always create a PR before merging to staging.

**PR body contract** — the body documents *results and non-obvious decisions*,
not a file-by-file changelog (recoverable from `git diff`). Cover:

- **Root cause** — traced to the actual reason (missing check, missing doc,
  wrong assumption), not "various X accumulated"
- **Profit** — measurable benefit, numbers if possible
- **Trade-offs** — alternatives rejected and why
- **Verification** — proof not visible in the diff or CI
- **Out of scope** — explicit non-goals (optional but encouraged)

Do NOT list changed files, CI status, or commit hashes — all visible elsewhere.
The squash-merge body (feature → staging) carries this information forward.

Wrap-up protocol is in `docs/DEVELOPMENT_PROCESS.md §0.7` — includes DESIGN_DECISIONS.md and AI_AGENT_EXPERIENCE.md updates, docs-review for drift, self-improvement check, and the **mandatory session retrospective** (every PR must carry a `docs/RETROSPECTIVES.md` entry; if missing, add it as the last commit and update the PR description).

### 8.5 Fork workflow (contributions to upstream)

**When**: Contributing to the canonical repo (`spbu-se/spbu_se_site`) from a fork (`iakov/spbu_se_site`).

**Rules**:

1. **Work only in the fork** — never push branches to `upstream`. `origin` = fork, `upstream` = canonical.
1. **Squash-merge into fork `staging`** — each feature branch is squash-merged into the fork's `staging` (local: `git checkout staging && git merge --squash <branch> && git commit`), then pushed: `git push origin staging`.
1. **Stacked PRs to upstream `current`** — the canonical repo has **no `staging` branch**; all PRs target `current`. Open the PR from `iakov:staging`:
   ```bash
   gh pr create --repo spbu-se/spbu_se_site --base current --head iakov:staging
   ```
   Multiple phases accumulate on the same `staging` head, so the PR stays open and grows — each phase is one squash commit on top.
1. **No upstream merges by the contributor** — unless explicitly authorized, open the PR and stop; the maintainer merges.
1. **Re-sync after each upstream merge** — fast-forward fork `current` and `staging` to `upstream/current`:
   ```bash
   git fetch upstream && git checkout current && git merge --ff-only upstream/current
   git push --no-verify origin current   # and same for staging
   ```
   The next phase's PR from `iakov:staging` then carries only the new phase's diff.

**Why**: The canonical `current` is a protected production branch; working entirely inside the fork keeps CI + review on the contributor's side and avoids cluttering upstream with WIP branches.

**Gotchas**: Linux pre-push hook is PowerShell-only (`Executable 'powershell' not found`) — run the manual equivalents (ruff/mdformat/basedpyright) then `git push --no-verify` and log it. The `staging` head being shared means a PR body must be updated per phase (`gh api -X PATCH repos/spbu-se/spbu_se_site/pulls/<n> -f body="$(cat body.md)"` — the `gh pr edit` GraphQL path is deprecated).

**Pushing a branch to the canonical repo directly**: the `upstream` remote's push URL is deliberately `no-push-to-upstream`. To update a canonical branch (e.g. repairing a dependabot PR's head) push to the bare URL:
`git push --force-with-lease=<ref>:<oid> https://github.com/spbu-se/spbu_se_site.git <local>:<remote>`.
The lease **must be the explicit `<remote-ref>:<expected-oid>` form** — a tracked-ref lease fails with "stale info" because the bare URL has no remote-tracking ref. Read the current remote oid first (`git fetch <url> <ref>`) and pass it as the expected value.

**Stacked-PR merge discipline**: merge **bottom-up** (the PR whose base is
`current` first) and **gate on CI after each merge** before merging the next PR.
Never `--delete-branch` an upstream PR whose head is the shared fork `staging` —
deleting it auto-closes the next stacked PR. If a base/head branch is gone and a
stacked PR auto-closed:

1. Recreate the deleted branch from `upstream/current` (`git branch <name> upstream/current; git push origin <name>`)
1. Reopen and retarget: `gh pr reopen <N>` then `gh pr edit <N> --base current`
1. Delete the temporary base branch
1. Rebuild the head onto the latest `current`: `git reset --hard upstream/current` then `git cherry-pick <first>^..<last>` (its own commits only; skip commits already upstream)
1. `git push --force-with-lease`
