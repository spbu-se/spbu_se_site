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
- Check `origin/staging` CI — if red, stop and fix first
- Follow `docs/GIT_FLOW.md` and `docs/DEVELOPMENT_PROCESS.md` for branch naming, staging rules, and GPG signoff
- Before using `2>&1`, flatten ErrorRecords with `| ForEach-Object { "$_" }` or suppress stderr with `2>($null)` — see `docs/TOOLING.md` §PowerShell
- Before writing piped/chained commands, read `docs/TOOLING.md` §PowerShell
- Before editing any doc, re-read its first 5 lines (scope/aim header). Verify your changes match that scope. If existing content doesn't match, flag it.
- After any command that produces error output or non-zero exit, ask: "Was this expected?" If unexpected, stop and investigate.
- Before merge: verify TODO.md has no completed items that belong in commit messages instead
- Before merge: if session involved doc restructuring, propose retrospective as the final step (do not run mid-session)
- Before any session summary or handoff: scan `docs/AI_AGENTS.md` §Output Format for the prescribed format — comply with timing, state, and section structure
- When running tests: default to `--tb=long` for full diagnostics on first run. Only use `-q` for the final green confirmation when zero failures are expected. See `docs/TESTING.md` §3a.
- Always learn, never forget — encode patterns before session ends

## Quality gates

Three tiers of quality, from local convenience to production gate:

### Pre-commit (fast, ~1s, changed files only)

Run automatically on `git commit`. Auto-fix formatting on touched files.
Not a quality gate — local commits can be imperfect. Using `git commit --no-verify` is acceptable if a hook genuinely blocks you for a non-formatting reason.

### Pre-push (strict, ~33s, all files, fail-fast)

Run automatically on `git push`. Checks: format (all files, no auto-fix) → mypy.
Failure at any step aborts — format failure skips mypy. This is the real local quality gate.

**Never use `git push --no-verify`** unless the user gives a direct, unbiased instruction.
An unbiased instruction states the goal without suggesting the method. "Push now, CI will catch it" is biased. "I need this on staging urgently" is unbiased — the agent may then propose `--no-verify` with a clear risk statement.

### CI discipline

See `docs/AI_AGENTS.md` §CI discipline for the trigger table. See `docs/QUALITY_MANAGEMENT.md` §4 for motivation.

### Staging merge

Every push to staging should be publishable. The pre-push gate is the minimum bar for staging. CI must be green before merging to staging.

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
- **GPG keylocker** — if `commit.gpgsign` is true, always use `--no-gpg-sign` on feature/auto branches (see `.tooling.md`)
