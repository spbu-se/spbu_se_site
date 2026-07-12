# SE Site

<!-- encoding: utf-8 -->

Сайт кафедры системного программирования СПбГУ.
`docs/DEVELOPMENT_PROCESS.md` for full workflow. `docs/GIT_FLOW.md` for branching.
`docs/TESTING.md` for testing strategy.

Available skills: `docs/AI_AGENTS.md` lists all `.skills/<name>/` workflows.
Read the matching `.skills/<name>/README.md` manually before starting a task — the `skill` tool does not surface project skills.

Every line must answer: "Would an agent likely miss this without help?" If not, cut it.
CLAUDE.md defers to this file. This file defers to `docs/`.

## Pre-flight checklist

- `git fetch --prune origin`
- Create a branch BEFORE any work: `git checkout -b <prefix>/<short-desc> origin/staging`
  Prefixes: feat/, fix/, refactor/, docs/, test/, chore/, ci/, staging-auto-<timestamp>
  (see `docs/GIT_FLOW.md` §1.1). Never commit directly to `staging`.
- Verify current branch is NOT `staging` or `current`: `git branch --show-current`
  If you are on `staging`, checkpoint and re-branch.
- Check `origin/staging` CI — if red, stop and fix first
- Before using `2>&1`, flatten ErrorRecords with `| ForEach-Object { "$_" }` or suppress stderr with `2>($null)` — see `docs/TOOLING.md` §PowerShell
- Before writing piped/chained commands, read `docs/TOOLING.md` §PowerShell
- Before editing any doc, re-read its first 5 lines (scope/aim header). Verify your changes match that scope. If existing content doesn't match, flag it.
- After any command that produces error output or non-zero exit, ask: "Was this expected?" If unexpected, stop and investigate.
- Before merge: verify CI shows test results, not just lint results — inspect the CI run log to confirm pytest actually ran, not just basedpyright
- Before merging a pushed feature branch: CI won't trigger on the branch. Create a PR first, wait for CI green, then squash-merge via `gh pr merge --squash --delete-branch`
- Before merge: verify TODO.md has no completed items that belong in commit messages instead
- Before merge: if session involved doc restructuring, propose retrospective as the final step (do not run mid-session)
- Before any session summary or handoff: scan `docs/AI_AGENTS.md` §Output Format for the prescribed format — comply with timing, state, and section structure
- When running tests: default to `--tb=long` for full diagnostics on first run. Only use `-q` for the final green confirmation when zero failures are expected. See `docs/TESTING.md` §3a.
- Proactively use `git-history_git_wrapup_instructions` at session start (orientation snapshot), mid-session (checkpoint against acceptance criteria), and pre-merge (readiness gate) — not just at the end. See `docs/GIT_FLOW.md` §Wrap-up protocol.
- Always learn, never forget — encode patterns before session ends

## Quality gates

Three tiers of quality, from local convenience to production gate:

### Pre-commit (fast, ~1s, changed files only)

Run automatically on `git commit`. Auto-fix formatting on touched files.
Not a quality gate — local commits can be imperfect. Using `git commit --no-verify` is acceptable if a hook genuinely blocks you for a non-formatting reason.

### Pre-push (strict, ~33s, all files, fail-fast)

Run automatically on `git push`. Checks: format (all files, no auto-fix) → basedpyright.
Failure at any step aborts — format failure skips basedpyright. This is the real local quality gate.

Before every `git push`, verify locally: `uv run pre-commit run --all-files --hook-stage pre-push` and fix any failures. A clean local run means the push will not waste CI time on pre-push failures.

**Never use `git push --no-verify`** unless the user gives a direct, unbiased instruction.
An unbiased instruction states the goal without suggesting the method. "Push now, CI will catch it" is biased. "I need this on staging urgently" is unbiased — the agent may then propose `--no-verify` with a clear risk statement. Every `--no-verify` must be logged in the retrospective as a process violation.

### CI discipline

See `docs/AI_AGENTS.md` §CI discipline for the trigger table. See `docs/QUALITY_MANAGEMENT.md` §4 for motivation.

### Staging merge

Never push directly to `staging`. Only squash-merge from a branch:
`git merge --squash <branch> && git commit -m "<type>: <summary>"`
CI must be green before merging (see `docs/QUALITY_MANAGEMENT.md` §CI discipline).

### First-time setup

```powershell
uv run pre-commit install --install-hooks --hook-type pre-commit --hook-type pre-push
```

## Testing quirks

- **Whoosh isolated** — per-fixture WHOOSHEE_DIR tempdirs eliminate the filesystem race. `-n auto` is safe.
- **No Flask factory** — `app` is a module-level global. Patch configs BEFORE `from flask_se import app`
- **scrypt unsupported on Python 3.13** — conftest.py mocks `check_password_hash` at module level
- **APScheduler fires in tests** — `scheduler.shutdown(wait=False)` called at conftest module level
- **Session-scoped DB template** — `_seeded_db_path` fixture creates + seeds once; per-test fixtures copy it (~ms)
- **Login bypass fixture** — `logged_client` injects `session["_user_id"]` instead of POST login (avoids scrypt)

## Environment quirks

- **Main branch**: `current` (not `main`)
- **Config files** (never committed): `flask_se_secret.conf`, `flask_se_mail.conf`, `flask_se_practice_yandex_secret.conf`
- **requirements.txt staleness** — CI runs `pip install -r` on every push. Must match `uv.lock`. Always regenerate before pushing
- **mdformat CI vs local** — CI uses Linux (LF). Always run `uv run mdformat ...` (not `--check`) before committing on Windows
- **GPG keylocker** — if `git config commit.gpgsign` is true, use `git commit --no-gpg-sign` on all branches (only `current` gets signed commits)

## Gotchas

- **Flask-Admin `query_factory=lambda:`** — `query_factory=Staff.query.all` (without `lambda:`) fails because SQLAlchemy model query attributes are not available at admin-import time. The `lambda:` defers evaluation to render time. Never pass the method directly or call it (`lambda: Staff.query.all()` would also crash). Affects 6 views in `src/flask_se_admin.py:55,60,65,70,76,182`.
