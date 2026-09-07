# TOOLING

<!-- encoding: utf-8 -->

Covers: portable cross-platform tool patterns (uv, pytest, SQLAlchemy, pre-commit, GitHub CLI, PowerShell, Python, Ruff, etc.). Does not cover: host-local quirks — see `.tooling.md`.

## uv

### Universal lockfile resolution

`uv lock` resolves for ALL platforms by default. If a dependency is source-only and can't build on one platform, `uv lock` fails even with platform markers. **Remove such deps from pyproject.toml entirely** and install separately (e.g., in Dockerfile).

### Cross-platform export differences

`uv export` output differs between platforms — wheel comment hashes for platform-specific packages (e.g., `msgpack`, `cachecontrol`) vary. CI checks that `diff` the exported output against a committed file are inherently fragile.

### Windows PowerShell encoding trap

`uv export > requirements.txt` in PowerShell defaults to UTF-16 LE encoding, corrupting the file for pip. Always use:

```powershell
uv export --no-dev --no-hashes --format requirements-txt 2>$null | Set-Content requirements.txt -Encoding utf8
```

### Build artifacts

If `[build-system]` is present, `uv sync` builds the project and creates `*.egg-info/` directories. Add to `.gitignore`.

### Purged/minified assets: regenerate on template class changes

`src/static/assets/css/quick-website.min.css` is **purged against the templates** (`scripts/build-assets.mjs`): any class that no template uses is stripped from the committed CSS. Introducing a **new CSS class in a template** therefore changes the purge output, and the CI `assets` drift job fails until the minified file is regenerated and committed:

```bash
npm run build     # regenerates quick-website.min.css + quick-website.min.js
git add src/static/assets/css/quick-website.min.css src/static/assets/js/quick-website.min.js
```

Hit twice on 2026-08-31: PR-1 added `.custom-checkbox` (consent), PR-2 added `.d-none` (recovery banner) — both tripped the drift job. The purge-completeness guard test (`tests/test_asset_pipeline.py::TestPurgeCompleteness`) fails locally with the same signal, so regenerate before the full-suite run.

The reverse trap hit on 2026-09-06 (#280): reusing a **stock Bootstrap class that no template had used yet** (`btn-outline-success`) also fails the drift job — the purge strips rules whose *class appears nowhere in templates*, even if it ships with Bootstrap. Two safe options: reuse only classes already present in the committed templates/CSS (grep the min css or a template for the class first), or regenerate via `npm run build`. After any template CSS-class change, run the purge guard locally (`uv run pytest tests/test_asset_pipeline.py`) — it reproduces the CI `assets`+`test` signal in seconds.

Because both PRs touch the same single-line minified file, run `npm run build` **after** rebasing onto the merged base, never before — otherwise the squash-merge conflicts on that one line.

### First pre-commit run

`uv run pre-commit run --all-files` downloads environments on first run (2-3 min). Pre-warm with:

```bash
uv run pre-commit install --install-hooks
```

### uv lock fails with "No solution found"

**When:** Adding a new dependency with `requires-python` constraints.
**Cause:** `pyproject.toml` `requires-python` includes versions the dep doesn't support.
**Fix:** Run `uv lock --python <version>` or narrow `requires-python`.

### uv sync: "Failed to build uwsgi"

**When:** `uwsgi` is in `pyproject.toml` dependencies on Windows.
**Cause:** uWSGI is source-only, uses Unix-only `os.uname()`.
**Fix:** Remove from pyproject; install via `RUN pip install uwsgi` in Dockerfile only.

## pytest + SQLAlchemy

### Flask app test setup (application factory)

`flask_se.py` exposes `create_app(config_overrides=None, start_scheduler=None)`; the module-level `app = create_app()` singleton keeps `from flask_se import app` working for scripts/tests. To build a differently-configured test instance without import-time monkeypatching:

```python
from flask_se import create_app
app = create_app(config_overrides={"SQLALCHEMY_DATABASE_URI": "sqlite:///..."})
```

Prefer `config_overrides` over patching `flask_se_config` module globals. The one remaining global patch in `tests/conftest.py` (`flask_se_config.SQLITE_DATABASE_*`) exists only because `init_db()` reads those globals directly (backup path), not because of app construction. The scheduler must be disabled in tests via `SE_START_SCHEDULER=0` before `import flask_se` (see §APScheduler below).

### Auto-migrate on boot (`SE_AUTO_MIGRATE`)

Schema self-heal runs in **two** places so model↔DB drift can never surface as `no such column` 500s:

1. **App boot** — `flask_se.py` calls `ensure_schema()` at import (after `app = create_app()`) when `SE_AUTO_MIGRATE != "0"`. Wrapped in `try/except` so a failure (e.g. SQLite `database is locked` from concurrent gunicorn worker boots) logs and continues instead of crashing the worker. This is the **primary** mechanism and is deploy-agnostic — it runs whether production is webhook-driven, Docker, or bare uWSGI.
1. **`docker/entrypoint.sh`** — runs `python flask_se.py migrate` on boot (default on; set `SE_AUTO_MIGRATE=0` in compose to opt out and run the same command manually).

`ensure_schema()` is also reachable as `python flask_se.py migrate`, and a **`flask db` CLI group** (`flask db upgrade` / `migrate` / `revision`) delegates to it — the production deploy webhook historically invoked `flask db <subcommand>` (Flask-Migrate convention), and that command failed with "No such command 'db'" after Alembic was removed (2026-08-25 incident: 15h outage because the migration step silently no-op'd). The CLI group keeps legacy webhook commands working.

`ensure_schema()`:

- **Fresh DB** (no `databases/se.db`) → `init_db()` (`db.create_all()` + seed). Models are the schema source of truth — no Alembic.
- **Existing DB** → backs up `se.db` to `se_backup_<date>.db` (**best-effort**), then `ensure_schema()`: `db.create_all()` for missing tables + per-table `PRAGMA table_info` diff against the model, `ALTER TABLE ... ADD COLUMN` for each missing column. If the backup `shutil.copyfile` fails (e.g. the `databases/` dir is read-only for app workers while the webhook's migration user can write it — a real prod `PermissionError` that silently disabled the whole self-heal), the migration **continues** with a warning; the backup must never block schema repair.
- **Column-addability**: a missing column is auto-added when nullable OR has a `server_default`; otherwise a constant default is synthesized by type (Boolean→0, Integer→0, Float/Numeric→0.0, String/Text→''); exotic non-nullable types (DateTime) → added nullable with a warning. A missing column with UNIQUE/PK/FK → fail-loud (SQLite cannot `ADD COLUMN` constraints); the developer fixes the model, never ops.

No version table and no ops pre-flight: column-presence IS the version marker, checked against the real DB every boot. `Users.deleted` must keep `server_default=sa.false()` so `ADD COLUMN ... NOT NULL` can backfill rows. See `docs/DESIGN_DECISIONS.md` [2026-08-21] for the full rationale.

### Opt-in error log viewer (`/logs`)

The `/logs` endpoint and its file-backed log handler (`src/flask_se_logviewer.py`) are **disabled by default** — an operator must opt in, otherwise the route 404s, no handler is attached and no file is ever written:

| Env var | Default | Effect |
| ------- | ------- | ------ |
| `SE_LOGS_ENABLED` | `0` | `1` registers `/logs` and attaches the JSONL handler. `0`/unset = feature fully off (no endpoint, no file, no root-logger `setLevel` side effect). |
| `SE_LOGS_PUBLIC` | `0` | When the feature is enabled: `1` shows the anonymous "last error" preview; `0`/unset = anonymous gets 404, only `role >= 5` sees the full table (error-oracle guard). |
| `SE_SCRATCH_DIR` | system temp | Override the scratch dir. Default is `tempfile.gettempdir()/se-logs` (OS temp — never `.tmp` in the repo, never the app dir); created only when enabled. |

- **File**: `server-errors.log` in the scratch dir, one JSON object per line, WARNING+ from the `flask_se` logger and root. Size-based rotation at 1 MB, keeps `.1`/`.2` (3 files total).
- **Sanitizer** (applied on write): filesystem paths → `<deploy-path>`, IPv4 → `x.x.x.x`, IPv6 → `x:x:x:x:x:x:x:x` (timestamps like `10:29:47` are kept), emails → `***@domain`, 16+ hex tokens → `<token>`, token-shaped base64 (digit + mixed case or url-safe chars, ≥16 chars) → `<token>`, `https://sqlalche.me/e/<n>/<code>` → `sqlalche.me/e/<code>` (the base-36 error code is kept — it identifies the exception class and is not secret).
- **Rate limit**: public preview 10 req/min/IP, in-memory **per gunicorn worker** (×workers effective budget, reset on restart). Admin full-log reads are not rate-limited but are gated by `role >= 5` and append an `ADMIN_LOG_VIEWED` audit line to the same stream.
- **Why opt-in**: default-on both wasted disk space (unbounded file) and exposed an unauthenticated error oracle; `SE_LOGS_ENABLED` gives ops an explicit switch, `SE_LOGS_PUBLIC` keeps even the enabled preview admin-only by default.

### Per-test temp directories

Each test fixture that needs a database must create its own `tempfile.mkdtemp()`. Shared global paths cause cross-test pollution — one test's teardown breaks the next test's setup.

### NamedTemporaryFile on Linux

`tempfile.NamedTemporaryFile` on Linux keeps the file descriptor open. SQLAlchemy gets "attempt to write a readonly database" on CREATE TABLE. Always use `tempfile.mkdtemp()` and let SQLAlchemy create the `.db` file.

### Windows SQLite URI path format

On Windows, SQLite URIs with forward slashes (`sqlite:///C:/Users/.../test.db`) silently fail — `db.create_all()` does NOT create the file and raises no error. Use backslash paths from `str(Path() / ...)` instead:

```python
# Works on all platforms:
_p = str(Path(_dir) / "test.db")
uri = f"sqlite:///{_p}"

# Does NOT work on Windows (silent failure):
_p = Path(_dir).as_posix() + "/test.db"
uri = f"sqlite:///{_p}"
```

### Engine caching

Changing `app.config["SQLALCHEMY_DATABASE_URI"]` after the app is initialized requires replacing the cached engine directly. `db.engine.dispose()` alone does NOT reset the cached engine — it only disposes the connection pool.

**Correct pattern:**

```python
from sqlalchemy import create_engine

app.config["SQLALCHEMY_DATABASE_URI"] = new_uri
db.engines[None] = create_engine(new_uri)
```

This replaces the engine in Flask-SQLAlchemy's internal engine cache, so subsequent calls to `db.engine`, `db.create_all()`, etc. use the new URI.

### Test data seeding is slow

Seeded DB tests (`init_db()`) take 10-15s each due to seed data insertion. Mitigate by creating a session-scoped template and copying it per test:

```python
@pytest.fixture(scope="session")
def _seeded_db_path():
    ...  # create + seed once
    yield _p

@pytest.fixture
def seeded_client(_seeded_db_path):
    _p = str(Path(_dir) / _db_name)
    shutil.copy2(_seeded_db_path, _p)
    uri = "sqlite:///" + _p
    app.config["SQLALCHEMY_DATABASE_URI"] = uri
    db.engines[None] = create_engine(uri)
    ...
```

### Login-required test fixture (session injection)

When testing `@login_required` routes and the password hash is unavailable (e.g., scrypt unsupported on Python 3.13), inject the user ID directly into the Flask session instead of going through the login POST:

```python
@pytest.fixture
def logged_client(seeded_client):
    from se_models import Users
    u = Users.query.first()
    with seeded_client.session_transaction() as sess:
        sess["_user_id"] = str(u.id)
    return seeded_client
```

This works because Flask-Login reads `session["_user_id"]` on every request to load the current user via `user_loader`.

## pytest config

`pytest` reads `[tool.pytest.ini_options]` from `pyproject.toml` directly — no separate `pytest.ini` or `setup.cfg` needed.

`addopts` enables coverage (`--cov=src --cov-report=term-missing --cov-fail-under=80 -n auto`). For targeted subset runs (a single file or `-k` filter), the `fail-under=80` gate fails on partial coverage — pass `--no-cov` to check only pass/fail (the full-suite reference run is the only one that must meet the 80% gate): `uv run pytest tests/test_app.py --no-cov 2>&1 | tee .tmp/test_app.log`.

## pre-commit

### Hook listing

The following hooks block obvious garbage (defined in `.pre-commit-config.yaml`):

| Hook | Blocks |
|---|---|
| `check-added-large-files` | Files > 500 KB |
| `check-case-conflict` | Case conflicts on case-insensitive FS |
| `check-json` / `check-yaml` | Invalid syntax in structured files |
| `commitlint` | Non-conventional commit messages |

### Hook ordering

Run formatters before linters. `ruff-format` before `ruff check --fix` avoids formatting-then-linting false positives.

### System hooks

`language: system` hooks run whatever is on PATH. Use `uv run <tool>` as the entry point to ensure the project's venv version is used.

### First run performance

First invocation downloads and caches hook environments. Install hooks early to make repeated runs fast.

### Remote-hook env stall on blocked networks (dprint first run)

The `dprint` pre-commit hook (remote repo, `language: python` via `dprint fmt`) downloads its wasm plugins from `plugins.dprint.dev` on first run. On a network where that host is unreachable the hook hangs with **no output** (2026-09-07 — commit blocked for >10 min, `AppData\Local\dprint\cache` held only locks, no plugins). This is a runtime environment fetch, not a hook failure: `dprint.json` only includes `yaml,yml,toml,json`, so Python-only commits aren't even formatted by it. If it stalls on such a commit, `git commit --no-verify` is justified (AGENTS: non-formatting hook blocker); first verify the hooks that DO apply (`ruff-format`, `ruff`) pass via `uv run pre-commit run <hook> --files <file>`.

### CLI conciseness

When a CLI option or path is implied by another option or glob, omit the redundant part. A directory path covers all files within it; listing a child file explicitly is noise. Keep commands short and clear — every redundant token distracts from the real structure.

### Restoring vendor files that bypass hooks

Formatters (trailing-whitespace, dprint) can modify vendor/static files. `git checkout HEAD -- path/to/dir` restores files and bypasses pre-commit hooks entirely — no need to disable hooks.

## GitHub CLI

```bash
# Quick CI status on a branch
gh run list --branch staging --json status,conclusion,databaseId

# Only failed steps
gh run view <run-id> --log-failed

# Block until complete
gh run watch <run-id>

# Get latest run ID as a variable
gh run list --branch staging --limit 1 --json databaseId --jq ".[0].databaseId"
```

### Deleting remote branches via the API

`git push --delete` cannot reach a remote whose push URL is `no-push-to-upstream`, and runs the pre-push gate. `gh api` uses the gh token directly and skips hooks — 204 (no output) is success:

```bash
gh api -X DELETE repos/<owner>/<repo>/git/refs/heads/<branch>
```

Works for any branch the token can write, including on protected repos (non-protected branches only) and dependabot heads.

### `FETCH_HEAD` is overwritten by the next fetch

`git fetch <url> <ref>` writes the fetched commit to `FETCH_HEAD`, but **any** subsequent fetch (even `git fetch upstream`) overwrites it. Never use `git checkout FETCH_HEAD -- <paths>` after another fetch has run — it silently stages the wrong ref (often a no-op). Capture the SHA immediately or use the explicit commit:

```powershell
git fetch https://github.com/spbu-se/spbu_se_site.git dependabot/npm_and_yarn/esbuild-0.28.1
$sha = git rev-parse FETCH_HEAD   # read it NOW, before any other fetch
git checkout $sha -- package.json package-lock.json
```

### Dependabot PR repair (stale head + regenerated assets)

Dependabot branches are cut from the base tip at creation and never rebase when the base moves; GitHub PR metadata (`gh pr view --json changedFiles`) is cached against the stale base and **underreports the real delta** (a head four squashed merges behind `current` reported `changedFiles=2` while the live two-dot diff showed 27 files). Before merging any dependabot PR, verify the live diff:

```powershell
git fetch https://github.com/spbu-se/spbu_se_site.git dependabot/<branch>
git diff --stat upstream/current..FETCH_HEAD   # two-dot: only intended files may appear
```

If the head is not a descendant of `current` (reversions of current work appear in the two-dot diff), rebuild the PR on `current`. CI gate: `.github/workflows/dependabot-gate.yml` fails a dependabot head that does not contain the base.

1. `git checkout -b chore/<dep-bump> upstream/current`
1. Take only the intended files from the dependabot head: `git checkout <dependabot-sha> -- package.json package-lock.json`
1. Dep bumps that feed the asset pipeline (`esbuild`, `terser`, `purgecss`) change the minifier output — run `npm ci` + `npm run build` and commit the regenerated `quick-website.min.css`/`.min.js`, or the CI `assets` drift job fails
1. Run the pre-push gate, then push to the canonical dependabot head with an explicit-oid lease (see `docs/GIT_FLOW.md`, "Pushing a branch to the canonical repo directly"):
   `git push --force-with-lease=<dependabot-branch>:<expected-oid> https://github.com/spbu-se/spbu_se_site.git <local>:<dependabot-branch>`
1. Wait for CI green (incl. `assets`), then `gh pr merge <n> --admin --squash`; the canonical dependabot branch is auto-deleted on merge

### `gh --jq` quoting: inner double-quotes are stripped by PowerShell

When a `--jq` expression contains **inner double-quotes** (e.g. `join(",")`, `"text"`), PowerShell strips them when passing the argument to the native `gh` executable — jq then sees `join(,)` and fails with `unexpected token ","`. `\t` and `\n` escapes also get mangled.

**Fixes**, in preference order:

1. Avoid inner double-quotes entirely — use `@tsv` (tab-separated) and `tostring` for arrays:
   ```powershell
   gh pr list --json number,title --jq '.[] | [.number, .title] | @tsv'
   gh issue list --json number,labels --jq '.[] | [.number, (.labels|map(.name)|tostring)] | @tsv'
   ```
1. Or parse JSON in PowerShell instead of jq:
   ```powershell
   $data = gh api "repos/owner/repo/issues?state=open" | ConvertFrom-Json
   $data | ForEach-Object { "$($_.number) $($_.title)" }
   ```
1. If jq is unavoidable, pass the query via a file (single-quoted here-string) rather than inline.

**Also**: `gh api graphql` on Windows needs a BOM-free query file (`[System.IO.File]::WriteAllText(..., UTF8Encoding($false))`) and `--input` expects a JSON object with a `query` key, not raw GraphQL.

### `gh pr view --json` field names (merge triage)

`mergeable_state` does **not** exist — the field is `mergeStateStatus` (`BLOCKED`/`MERGEABLE`/`CLEAN`). For cross-repo PRs `headRepository` is `null` (use `headRepositoryOwner.login`). To see why a merge is blocked, query `mergeStateStatus`, `reviewDecision`, and `mergeQueueEntry` via GraphQL rather than guessing at REST field names.

### Diagnosis: mdformat failure with truncated path

When CI mdformat fails and the filename is truncated in logs, use:

```powershell
gh run view <run-id> --log | Select-String -Pattern "not formatted" -Context 0,1
```

### `gh run watch` times out

`gh run watch` exits after ~5 minutes even if CI is still running. Use non-blocking polling:

```powershell
gh run list --branch staging --workflow "CI (staging)" --limit 1 --json conclusion
```

### Rate limits

Rapid `gh run list` calls may hit GitHub API rate limits. Space polling calls 10-15 seconds apart.

## PowerShell

### `&&` / `||` not available

```powershell
# Wrong:
cmd1 && cmd2

# Correct:
cmd1; if ($?) { cmd2 }
```

### No `grep`

Use `Select-String` instead.

### `curl` is an alias

`curl` maps to `Invoke-WebRequest`, not the real `curl`. Use `curl.exe` for actual HTTP requests.

### `uv` on PATH is registry-only until the parent shell is restarted

`uv` installs to `C:\Users\yurii\.local\bin` and this is on the **user** PATH (registry persists it), but a shell started *before* the install (e.g. an always-open agent shell) doesn't have it on its process PATH — `git push` then fails the pre-push hook with `Executable 'uv' not found` even though `uv` is on the user PATH. Symptoms + fix (prefix `$env:PATH` for the current process):

```powershell
$env:PATH = "C:\Users\yurii\.local\bin;" + $env:PATH
```

Applies to any freshly-installed CLI (uv, cargo, etc.) picked up by pre-commit `language: system` hooks. Verify with `Get-Command uv`; if empty but the exe exists under `C:\Users\yurii\.local\bin`, apply the prefix.

### `||` not available

```powershell
# Wrong:
cmd1 || cmd2

# Correct:
cmd1; if (-not $?) { cmd2 }
```

### Inline Python quoting

`-c "..."` uses PowerShell string rules (double quotes interpolate `$`). Escape `$` with backtick or use single quotes on the outside:

```powershell
uv run python -c 'import os; print(os.name)'
```

### `2>&1` wraps stderr in noisy ErrorRecord objects

`2>&1` redirects stderr to stdout, but PowerShell wraps each stderr line in an `ErrorRecord` object. Console output looks like an error even when the command succeeds:

```
git : To https://github.com/...
At line:1 char:...
+ ... git push ...
+     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : NotSpecified: (To https://github.com/...:String) [], RemoteException
    + FullyQualifiedErrorId : NativeCommandError

   abc123..def456  staging -> staging
```

The push **succeeded** — the `git :` block is just PowerShell rendering an ErrorRecord. To flatten:

```powershell
# Noisy — ErrorRecord wrappers:
cmd 2>&1

# Clean — ErrorRecords flattened to plain strings:
cmd 2>&1 | ForEach-Object { "$_" }
```

Applies to any native command (git, gh, uv) whose stderr output is informative but not an actual error.

## Python

### datetime.timezone.UTC vs datetime.timezone.utc

**When:** Using `datetime.timezone.UTC` on Python 3.13.
**Cause:** Python 3.13 removed the deprecated `timezone.UTC` alias. Only `timezone.utc` (lowercase) is available.
**Fix:** Replace `timezone.UTC` with `timezone.utc`.

### `# pyright: ignore` not suppressing errors

**When:** A `# pyright: ignore[code]` comment on a line produces a "suppression comment is unused" warning.
**Cause:** `enableTypeIgnoreComments = true` is not set; or the error code in the comment doesn't match the actual error.
**Fix:** Run `uv run basedpyright src/` and verify the error code matches exactly. If the issue is a framework pattern (SQLAlchemy `__init__`, WTForms `choices`), the standard set is:

- `reportCallIssue` — for dynamic constructor kwargs
- `reportAttributeAccessIssue` — for SQLAlchemy dynamic attributes/backrefs
- `reportOptionalMemberAccess` — for access after `.first()` without None check
- `reportAssignmentType` — for framework-level type mismatches

## Ruff

### N801 (class name convention) suppressed for tests

`pyproject.toml` has `"tests/*.py" = ["N801"]` — test class names don't need to follow PascalCase conventions (e.g., `test_basic_auth` as a class is acceptable). This is intentional: test classes often describe scenarios rather than being named after the class under test.

### Unsafe fixes

`--unsafe-fixes` enables rules that safe mode skips:

- E722 — bare `except`
- E711 — `!= None` comparison
- F841 — unused variable assignment

Run: `ruff check --fix --unsafe-fixes`

### Target version

Set `target-version` in `[tool.ruff]` to match minimum supported Python. Affects which syntax is flagged as invalid.

## vulture (dead-code gate)

Gated in pre-push + both CI workflows (parity). The `--min-confidence 100` level is deliberate: at default confidence vulture flags hundreds of framework false positives (SQLAlchemy model columns, Flask route functions, WTForms fields) that it cannot resolve statically — gating there would make the check noise and get disabled. At 100% only true positives surface (currently only unused callback params).

```bash
uv run vulture src/ --min-confidence 100 --ignore-names is_created
```

- `is_created` is a framework-contract callback param (Flask-Admin `on_model_change`) that ruff already suppresses with `# noqa: ARG002`.
- To add new dead code to the exclusion, widen `--ignore-names` or `--exclude` with a documented reason, not to hide real findings.

## pylint (duplicate-code gate)

`uv run pylint --disable=all --enable=similarities src/ tests/` runs in pre-push + both CI workflows. `min-similarity-lines = 6` in `pyproject.toml` `[tool.pylint.similarities]`; templates/static are ignored. Keeps the test consolidation honest — consolidation removes duplication, never adds it.

## General

### Never use pip.\_vendor

Importing from `pip._vendor` is fragile — it depends on pip being installed and its internal structure being stable. Always install vendored packages as explicit dependencies.

### Generated artifact diff fragility

`diff` on generated files (requirements.txt, lockfiles) across platforms is unreliable. Comments and platform-specific hashes differ. Prefer CI checks that tolerate minor variations, or run the generation step in CI to verify consistency.

### Coverage exclusions

Exclude one-shot scripts (importers, entrypoints) from coverage for realistic metrics:

```toml
[tool.coverage.run]
omit = ["src/wsgi.py", "src/extract_text.py", "src/static/files/*"]
```

### Coverage metrics accumulate across runs

**When:** Running `pytest --cov` multiple times.
**Cause:** `.coverage` file appends data, not replaces. Subsequent runs include old data.
**Fix:** Delete `.coverage` before each session, or use `coverage erase`.

## Commit signing

Signoff policy is defined in `docs/GIT_FLOW.md §4`. This doc only adds cross-cutting notes.

### Never touch global git config

Global git options (`git config --global`) are user-specific and should never be modified by automation without explicit user approval.

### Auto-branch commits: disable GPG signoff

Auto/batch mode branches (`staging-auto-*`) must use `--no-gpg-sign` — they are throwaway branches that are squash-merged and never appear as individual commits in permanent history.

```bash
git commit --no-gpg-sign -m "..."
```

## Scrypt mock for tests on Python 3.13+

Python 3.13 OpenSSL builds may lack scrypt support, causing `check_password_hash` to raise `ValueError: unsupported hash type scrypt`. Mock at conftest module level before any auth module is imported:

```python
import werkzeug.security as _ws
_ws.check_password_hash = lambda pwhash, password: True
_ws.generate_password_hash = lambda password, method="pbkdf2:sha256": f"mock:{password}"
```

This is safe for testing view logic and route behavior, but means password security logic is never exercised in tests.

## APScheduler in tests (env-gated, not shutdown)

`BackgroundScheduler` jobs (e.g. `SendMailNotification` every 10s) would fire against the test DB which may not have the `notification` table, causing `sqlite3.OperationalError: no such table: notification`. Since the application-factory refactor, the scheduler is gated by the `SE_START_SCHEDULER` env var — production leaves it unset (jobs run), tests set it to `0` BEFORE importing `flask_se`:

```python
import os
os.environ["SE_START_SCHEDULER"] = "0"
from flask_se import app, db
```

This replaces the old `scheduler.shutdown(wait=False)` at conftest module level. Do not reintroduce shutdown — the env gate is set before import so the scheduler never starts.

## PowerShell encoding

See `docs/AI_AGENTS.md` §Skills (`.skills/encoding-audit/`) for detection scripts, git recovery workflow, fix patterns, and encoding declaration templates.

### `Set-Content` / `Out-File` default to Windows-1252 on en-US systems

PowerShell's `Set-Content` and `Out-File` cmdlets default to the system's active ANSI code page (Windows-1252 on en-US Windows), NOT UTF-8. This corrupts any file containing non-ASCII characters when the file is expected to be UTF-8.

```powershell
# WRONG — writes Windows-1252
Set-Content -Path file.md -Value $content

# WRONG — also Windows-1252
$content > file.md

# WRONG — also Windows-1252
Out-File -FilePath file.md -InputObject $content

# CORRECT — writes UTF-8 without BOM
[System.IO.File]::WriteAllText($path, $content, [System.Text.UTF8Encoding]::new($false))

# CORRECT — reads UTF-8
[System.IO.File]::ReadAllText($path, [System.Text.Encoding]::UTF8)

# CORRECT — writes bytes as UTF-8
[System.IO.File]::WriteAllBytes($path, [System.Text.Encoding]::UTF8.GetBytes($content))
```

**Applies to**: Any `.py`, `.md`, `.yaml`, `.json`, `.toml`, `.cfg` file — anything that should be UTF-8.

### `Get-Content` with `-Raw` still defaults to Windows-1252

Even `Get-Content -Path file.md -Raw` uses Windows-1252. Always use the .NET overload.

### Read side: `Select-String` / `Get-Content` mojibake on UTF-8 Cyrillic

`Select-String` and `Get-Content` **read** files as the ANSI code page (Windows-1251 on a Russian system) unless `-Encoding UTF8` is passed, and the console `OutputEncoding` is typically `cp866` — so UTF-8 Cyrillic becomes garbage even when the file is valid UTF-8 (verify with `uv run python` decode, not the shell). This looks like file corruption but is purely a read/console-encoding artifact.

```powershell
# CORRECT — read as UTF-8 and re-encode the console to UTF-8
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Get-Content -LiteralPath file.html -Encoding UTF8
```

Prefer the dedicated `read`/`grep` tools (they decode UTF-8 correctly) for real analysis; use the shell only when a tool requires it.

### `$(...)` subexpression flattens multi-line output to space-joined string

`$(command)` in PowerShell captures stdout as an **array of strings** (one per line). When passed to a function expecting a `string` (like `WriteAllText`), PowerShell joins the array with **spaces** — collapsing all lines into one.

This corrupts files like `requirements.txt` that must retain line breaks:

```powershell
# WRONG — collapses to single line
[System.IO.File]::WriteAllText("requirements.txt", $(uv export --no-dev --no-hashes), [System.Text.UTF8Encoding]::new($false))

# CORRECT — capture as array, join explicitly
$lines = uv export --no-dev --no-hashes 2>($null)
[System.IO.File]::WriteAllText("requirements.txt", ($lines -join "`r`n"), [System.Text.UTF8Encoding]::new($false))
```

This quirk does NOT apply when the output is a single line (no `\n` in the captured text). Always verify multi-line output with `($content).GetType()` before passing to a string parameter.

### pip install: "UnicodeDecodeError: 'utf-16-le'"

**When:** `pip install -r requirements.txt` on Linux CI.
**Cause:** `requirements.txt` written with UTF-8 BOM on Windows.
**Fix:** Use `[System.IO.File]::WriteAllText()` with `UTF8Encoding($false)` to omit BOM.

### mdformat doesn't show file path on UnicodeDecodeError

When `uv run mdformat .` encounters a non-UTF-8 file, the error message omits the file path. To find the offending file:

```powershell
Get-ChildItem -Recurse -Include "*.md" | ForEach-Object {
    try { $null = [System.Text.UTF8Encoding]::UTF8.GetString([System.IO.File]::ReadAllBytes($_.FullName)) }
    catch { Write-Host $_.FullName }
}
```

## Quality Tool Catalog

All quality tools used in this project, their exact configuration, and adoption status.
See `docs/QUALITY_MANAGEMENT.md` for quality philosophy and policy.

### Active tools

| Tool | Purpose | Where it runs | Flags / config | Adopted |
|------|---------|---------------|----------------|---------|
| `ruff format` | Python formatter | Pre-commit (auto-fix) + CI (`--check`) | Default config | ✅ |
| `ruff check` | Python linter | Pre-commit (auto-fix) + CI (`--check`) | `--fix` for pre-commit | ✅ |
| `mdformat` | Markdown formatter | Pre-commit (changed files, auto-fix) + Pre-push/CI (`--check` all) | `types: [markdown]` in pre-commit | ✅ |
| `basedpyright` | Static type checker | Pre-push (gate) | `pyproject.toml` config, `# pyright: ignore[code]` per-line | ✅ |
| `dprint` | JS/JSON/TOML formatter | Pre-commit | Config in `dprint.json` | ✅ |
| `pre-commit-hooks` | Trailing whitespace, EOF, JSON, large files | Pre-commit | Config in `.pre-commit-config.yaml` | ✅ |
| `djlint` | HTML/Jinja formatter | Pre-commit | `--reformat` | ✅ |
| `commitlint` | Commit message format | Pre-commit (commit-msg stage) | Conventional commits | ✅ |
| `actionlint` | GHA workflow validator | Pre-push | Default config | ✅ |
| `packaging.Requirement` | requirements.txt syntax validation | Pre-push | `encoding='utf-8-sig'`, skip `-e` lines | ✅ |
| `uv lock --check` | Lockfile consistency | Pre-push | Default | ✅ |
| `pytest` | Test suite | CI | `-n auto` (xdist) | ✅ |
| `coverage` | Code coverage | CI (via pytest) | `--cov=src --cov-fail-under=80` | ✅ |
| `pylint` (similarities) | Code duplicate detection | CI (lint job) | `--disable=all --enable=similarities src/ tests/` | ✅ |
| `scripts/find_dup_coverage.py` | Coverage-based duplicate test detection | Manual (advisory) | Requires `coverage run --context=test` first | ✅ |

### Proposed tools (agent suggested, user may adopt)

| Tool | Purpose | Where it would run | Proposed reason |
|------|---------|-------------------|-----------------|
| ~~`bandit`~~ | ~~Python security scanner~~ | Replaced by ruff S rules (2026-07) | ruff `"S"` in `[tool.ruff.lint] select` covers the same surface (hardcoded secrets, debug configs, `eval()`) + more. See `pyproject.toml`. |
| `codespell` | Spelling in source | Manual / CI (non-blocking) | Captures typos that survive code review — was in pre-commit, removed as not cleanup |

### Occasional deep scans (cleanup discipline)

Not a standing gate — Semgrep is run ad-hoc as cleanup discipline when a
broader net than the committed linters is wanted (see the success story in
`docs/DESIGN_DECISIONS.md` [2026-09-07]). It caught a real XSS regression
the naive in-repo guardrail had missed. Run on demand, triage carefully,
batch genuine fixes into one PR:

```bash
mkdir -p .tmp/semgrep
uvx semgrep scan --config p/python --config p/security-audit \
  --config p/owasp-top-ten --metrics=off --oss-only \
  src tests e2e scripts 2>&1 | tee .tmp/semgrep/scan.log
```

- `--config auto` requires metrics; use the explicit OSS packs above for an
  offline/OSS run. `uvx` avoids adding a permanent dependency.
- **Triage, don't bulk-edit**: the generic `html-templates`/`html` rules
  (`var-in-href`, `var-in-script-tag`, `unquoted-attribute-var`) are
  false-positive-heavy against this stack's posture (Jinja autoescape,
  strict nonce-CSP, render-time `nh3` sanitization behind the only allowed
  output filters). Verify a hit against that posture before changing code;
  `tojson` (not quoting) is the correct encoding for values inside inline
  `<script>` blocks. `safe_html`/`markdown` filter uses are by design.
- **Vendor files are excluded**: `src/static/assets/libs/*` demo pages are
  third-party; do not edit them to silence a rule.
- Expected benign families on this codebase: `flask-url-for-external-true`
  (absolute mail links), `logger-credential-disclosure` (function-context FP),
  `plaintext-http-link` (content/email URLs).

### Encoding declaration policy

See `docs/DOCS.md §6` for the project's encoding declaration policy.

## Staging environment

- **Staging URL** (single source — a change touches exactly one line): `https://se.math.spbu.ru/staging/` — served by the deploy host under the `/staging/` path prefix of the production hostname. **May change**; if a stale link is suspected, ask ops.
- **Deploy mechanics**: every push to `current` triggers the CD webhook (`.github/workflows/deploy_to_staging.yml`). GitHub deployments for environment `deploy_environment` on the upstream repo are the source of truth — a merge is NOT deployed until the latest deployment points at the merged SHA with `state == success`:
  ```
  gh api "repos/spbu-se/spbu_se_site/deployments?per_page=1" --jq '.[0] | "\(.sha) \(.created_at)"'
  ```

### Signed-commit verification

`current` accepts only signed, verifiable commits (see `docs/GIT_FLOW.md` §2.3a). After any merge, assert the head commit verifies before proceeding — an unverified result means a direct push or rebase-merge leaked into `current` (counter-example `446e39f`, 2026-09-02):

```
gh api "repos/spbu-se/spbu_se_site/commits/<sha>" --jq '.commit.verification | "\(.verified) \(.reason)"'
# must print: true valid
```

PR squash-merges verify automatically (GitHub-signed); the hotfix direct lane must use `git commit -S` with a GitHub-registered key.

- **nginx `/staging/` prefix is reserved (ops rule)**: the deploy host's nginx intercepts `/staging/*` and routes it to the staging backend; **Flask routes must never be defined under `/staging/`** — they never reach uWSGI/Flask. Use another prefix if a staging-scoped route is ever needed.
- **DB is not guaranteed prod-like**: a fresh boot self-seeds demo users with random passwords (`init_db`); a prod-like restore is an ops decision. Live rate limiters apply (10 login attempts / 5 min per IP, 5 registrations / hour per IP).
- **Smoke** (mirror `docs/RELEASE_CHECKLIST.md` B17): `curl -s -o /dev/null -w "%{http_code}"` on `/staging/` and key routes must be 200.

## Static asset build pipeline (npm)

The production theme assets are built from committed sources and the outputs are
committed (build-and-commit). CI job `assets` (ci.yml) re-runs the build and
fails if the committed outputs drift.

- Sources: `src/static/assets/css/quick-website.css` (595 KB theme),
  `src/static/assets/js/quick-website.js`.
- `npm run build` → `scripts/build-assets.mjs`: purgecss (content = all
  templates + all JS under assets; greedy safelist for dynamic JS class
  families) → esbuild minify → `quick-website.min.css` (~140 KB); terser →
  `quick-website.min.js`.
- The 4 bases + `admin/master.html` reference the min files only. Guardrail
  tests: `tests/test_asset_pipeline.py` (stale-build rule floor, every
  template class survives the purge, every `asset()` reference resolves).

**Windows notes**: never edit the bases with `Set-Content`/PowerShell 5.1
`-Encoding UTF8` (adds a BOM + re-encodes Cyrillic → mojibake). Use
`[System.IO.File]::WriteAllText($path, $text, (New-Object System.Text.UTF8Encoding($false)))` instead.
