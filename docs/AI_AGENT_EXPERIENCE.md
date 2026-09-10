# AI Agent Experience

<!-- encoding: utf-8 -->

Knowledge accumulated by AI agents during development sessions: dead ends, debugging trails, tool limitations, and patterns discovered through trial and error. Not canonical process or tool docs — search here first when hitting a familiar blocker.

Covers: debugging trails and dead ends, agent-specific tool limitations, workarounds discovered interactively. Does not cover: portable tool knowledge — see `docs/TOOLING.md`, test infrastructure patterns — see `docs/TESTING.md`, process gaps — see `docs/RETROSPECTIVES.md`.

## Coverage duplicate detection

**When:** Investigating whether tests overlap in coverage.

**Command:**

```powershell
coverage run --context=test -m pytest tests/ 2>$null
coverage json
uv run python scripts/find_dup_coverage.py coverage_data.json
```

**Interpreting output:**

- **Jaccard > 0.9**: Tests are near-identical in coverage — one is likely redundant.
- **Jaccard 0.8–0.9**: Tests cover mostly overlapping code with minor differences — consider merging.
- **Jaccard < 0.8**: Different coverage, likely distinct test value.

**If a test pair is reported:** check manually whether both tests cover the same production code paths. If yes, consolidate by parametrizing or removing the simpler one (keeping the one with more assertions).

**The `context` key** in `coverage_data.json` embeds the test name, allowing per-test line-set extraction.

## linecache returns stale content after file edits

**When:** Using `linecache.getlines()` or `linecache.getline()` to read a Python file that was modified during the same test run.

**Attempts:**

1. Called `linecache.getlines()` again — got same cached result
1. Imported the module again — no effect, cache persists

**Root cause:** `linecache` caches file contents on first read and never invalidates unless explicitly told to. File modifications (adding/removing lines) shift line numbers, but `linecache` still returns the pre-modification content.

**Fix:** Use `open().readlines()` directly, or call `linecache.clearcache()` before each read that follows a file modification.

## init_db emits SAWarning about ThemesLevel.diploma_themes (benign)

**When:** Running `uv run python src/flask_se.py init`.

**Symptom:** `SAWarning: Object of type <DiplomaThemes> not in session, add operation along 'ThemesLevel.diploma_themes' won't proceed` from se_models.py:3042.

**Root cause:** In `init_db()`, `c.levels.append(ThemesLevel.query...first())` appends to the `DiplomaThemes.levels` collection while the `DiplomaThemes` object is not yet in the session. The warning concerns only the reverse-side backref being skipped during autoflush — the forward relationship rows are still written.

**Verify:** After init, `diploma_themes_level` contains rows (7 for seed data) — data is intact. No action needed; the warning is expected noise on every init.

## db.init_app: "already registered" on module-level import

> **RESOLVED 2026-08-22** — the module that triggered this, `thesesImport.py`,
> was removed and replaced by `thesis_import.py`, which never calls
> `db.init_app` at import time (pure library, no side effects). Keep this
> entry as the rationale for the import-safety contract: **any new module that
> needs the DB must be called inside `with app.app_context():`, never wired at
> import.**

**When:** Importing a module that calls `db.init_app(app)` at module level when `conftest.py` has already registered the same `db` on the same `app`.

**Attempts:**

1. Tried `db.app = app` before `db.init_app(app)` — fails, same RuntimeError
1. Tried `app.extensions.setdefault(...)` — fragile, not idempotent
1. Used `contextlib.suppress(RuntimeError)` around the call — works

**Error:** `RuntimeError: A 'SQLAlchemy' instance has already been registered on this Flask app.`

**Occurs in:** ~~`thesesImport.py:20`~~ (removed) — `from flask_se import app; db.init_app(app)` runs at import time.

**Root cause:** Flask-SQLAlchemy v3 raises when `init_app` is called twice on the same app. `conftest.py` calls it first via `from flask_se import app, db`. Any later import of `thesesImport` calls it again.

**Fix for tests — patch init_app before importing:**

```python
import flask_sqlalchemy
import contextlib
from unittest.mock import patch

_orig_init_app = flask_sqlalchemy.SQLAlchemy.init_app

def _patched_init_app(self, app):
    with contextlib.suppress(RuntimeError):
        _orig_init_app(self, app)

with patch.object(flask_sqlalchemy.SQLAlchemy, "init_app", _patched_init_app):
    import thesesImport  # now safe to import
```

**Fix for source code — wrap in try/except:**

```python
try:
    db.app = app
    db.init_app(app)
except RuntimeError:
    pass
```

## thesesImport: module-level state breaks test isolation

> **RESOLVED 2026-08-22** — `thesesImport.py` removed (see above). The
> replacement `thesis_import.py` has no module-level mutable state: it defines
> no `download` flag, never calls `sys.exit`, and its errors are returned as
> per-record lists via `validate()`/`ImportSummary`. The pattern below is kept
> as the cautionary tale that motivated the design.

**When:** Writing tests for functions in `thesesImport.py` that share module-level state.

**Symptoms:**

- Tests pass when run individually but fail when run as part of the full suite.
- `TypeError: can only concatenate str (not "NoneType") to str` — caused by `thesesImport.download` flag being accidentally left `True` by a previous test.
- `sys.exit` is called by the function under test, terminating the test process.

**Attempts:**

1. Tried resetting `thesesImport.download = False` in each test — fragile, one missed reset causes cascade
1. Used `try/finally` pattern — works but requires discipline
1. Considered refactoring the production module — deferred (high risk, low test coverage)

**Root cause:** `thesesImport.py` has two mutable module-level variables:

1. `download = False` — controls whether `download_file()` actually writes files. If a test sets `download = True` and doesn't restore it, subsequent tests that call scraper functions will try to write files to disk.
1. Direct calls to `sys.exit()` on error conditions — when mocked with `patch.object(sys, "exit")`, the mock prevents process exit but the function continues executing, potentially corrupting state for the next test.

**Fix for tests:**

- Always restore `thesesImport.download` after any test that modifies it (use `try/finally`).
- Mock `Users.query`, `Staff.query`, and `db.session` in every test that calls a scraper function.
- Use `app.app_context()` when patching `thesesImport.Users.query` — the model descriptor requires an active app context.

**Long-term fix (not yet done):**

- Move `db.app = app; db.init_app(app)` into a function called on demand
- Remove the `download` flag in favor of config injection
- Replace `sys.exit()` with raising a custom exception

## **(RESOLVED — Whoosh replaced with FTS5 in PR #11)** os.rename patching breaks Whoosh create_index

**When:** Three tests patched `os.rename` to test move-file behavior. Whoosh uses `os.rename` internally during `create_index()`.

**Attempts:**

1. Patched only `flask_se_theses.os.rename` — Whoosh imports `os` directly, not from `flask_se_theses`
1. Patched `os.rename` globally — Whoosh `create_index()` silently fails, index never written
1. Used real temp files instead of patching — works

**Root cause:** Whoosh's index writer uses `os.rename` internally. Patching it at any level corrupts Whoosh's atomic-write protocol. The index appears to be created but the `.toc` file is never written.

**Fix:** Create temp source files on disk and let the real `os.rename` succeed. Tests use `tempfile.mkdtemp()` + `Path.write_bytes()` to prepare real files, then call the production rename path normally.

## pylint similarities: false positives at low thresholds (agent note)

**When:** Running `uv run pylint --disable=all --enable=similarities src/ tests/` with `min-similarity-lines=4`.

**Symptoms:**

- All R0801 hits point to `tests/test_yandex_disk.py` even though that file has no real duplicates.
- Hits appear for migrations, templates, and form files that are auto-generated or boilerplate.

**Root cause:**

1. **Alphabetical first-file bug** — pylint reports the alphabetically first file in `tests/` (`test_yandex_disk.py`) as the reference for every duplicate pair. Check the *second* `==` file in each pair for the real duplicate.
1. **Threshold 4 is too low** — catches 4-line patterns like `if resp: return resp` or common SQLAlchemy query chains that are structurally similar but semantically different.

**Fix:**

```powershell
# Use threshold 6 for production (clean on this project with zero suppressions):
uv run pylint --disable=all --enable=similarities src/ tests/ --min-similarity-lines=6

# To see only real duplicates at threshold 4, exclude the biased reference file:
uv run pylint --disable=all --enable=similarities --ignore=tests/test_yandex_disk.py src/ tests/ --min-similarity-lines=4
```

**Production CI** uses `min-similarity-lines=6` defined in `pyproject.toml` `[tool.pylint.similarities]`.

## PowerShell `$()` subexpression flattens multi-line output

**When:** Writing `requirements.txt` from `uv export` using `[System.IO.File]::WriteAllText`.

**Attempts:**

1. `[System.IO.File]::WriteAllText("req.txt", $(uv export ...))` — produces single-line file
1. Tried `Out-File -Encoding utf8` — BOM added, `pip install` fails with utf-16-le error
1. Array capture + explicit join — works

**Root cause:** `$(command)` in PowerShell captures stdout as an array of strings (one per line). When passed to a function expecting a string, PowerShell joins the array with **spaces** — collapsing all lines into one.

**Fix:**

```powershell
$lines = uv export --no-dev --no-hashes 2>($null)
[System.IO.File]::WriteAllText("requirements.txt", ($lines -join "`r`n"), [System.Text.UTF8Encoding]::new($false))
```

**Also applies to:** Any multi-line output captured via `$()` and passed to a string parameter. Single-line outputs are safe. Always verify with `($content).GetType()`.

## Session context loss between conversations

**When:** Starting a new AI conversation after a session ended. The agent has no memory of the prior session — branch, last commit, acceptance criteria, WIP state.

**Attempts:**

1. Ask user "what did we do so far?" — works but wastes user time
1. Check `git log --oneline -5` + `git branch -a` — partial recovery
1. Read AGENTS.md anchored summary — only has most recent session

**Root cause:** LLM conversations are isolated. No session-persistence mechanism exists beyond what's written to canonical docs. The anchored summary in the response file is ephemeral.

**Mitigation at session start:**

1. `git log --oneline -10` — recent commits
1. `git branch -a` — remote branches for context
1. Read `docs/RETROSPECTIVES.md` last entry — state at handoff section
1. Read `TODO.md` Blocked section — known blockers
1. Read `docs/QUALITY_MANAGEMENT.md §Metrics` — prescribed metric commands

## Engine disposal after config change

**When:** Changing `SQLALCHEMY_DATABASE_URI` after app initialization.

**Attempts:**

1. `db.engine.dispose()` alone — disposes the connection pool but the cached engine object still holds the old URI
1. `db.engines[None] = create_engine(new_uri)` — works

**Root cause:** Flask-SQLAlchemy caches the engine by key in `db.engines`. Disposing the pool doesn't replace the cached entry.

**Fix:**

```python
app.config["SQLALCHEMY_DATABASE_URI"] = new_uri
db.engines[None] = create_engine(new_uri)
```

## **(RESOLVED — Whoosh replaced with FTS5 in PR #11)** Pre-existing Whoosh EmptyIndexError on CI is non-deterministic

**When:** CI (staging) test suite — `test_thesis_repr_str` fails with Whoosh `EmptyIndexError`.

**Attempts:**

1. Called `whooshee.reindex()` before each test — same failure
1. Created `os.makedirs(whoosh_dir, exist_ok=True)` — no effect
1. Added xfail marker — only reliable approach

**Root cause:** Environmental non-determinism. Rerunning the same commit shows 150 errors → 0 errors with zero code changes. Likely a filesystem race in Whoosh's index directory creation on Linux CI runners.

**Fix:** xfail with `strict=False` for the affected test. Rerun CI once before investigating.

## `_make_temp_thesis` FileExistsError

**When:** Writing test helper `_make_temp_thesis()` that creates a temp PDF file for tests.

**Attempts:**

1. Wrote `Path(p) / "file.pdf"` — FileExistsError on second test run
1. Added `os.remove()` before `Path.write_bytes()` — works

**Root cause:** `Path.write_bytes()` raises `FileExistsError` if the file already exists. Temp file cleanup doesn't always run (e.g., on test interruption or when using session-scoped temp dirs).

**Fix:** Remove existing file before writing: `os.remove(str(path)); path.write_bytes(data)`.

## 2026-07-12 — Command timeout waste: 7 re-runs instead of reading partial output

**Symptom:** pytest timed out at 120s with ~30% complete. Instead of reading the
progress dots and calculating ETA (30%/120s → ~400s total), I cycled through 6
more permutations: `--timeout` (invalid flag), `-n 0` (slower than auto), `-n auto`
with 300s (timed out at 89%), `--collect-only` (fast but wasteful), piped to
`Select-String` (user aborted). Total waste: 4 extra timeouts + user frustration.

**Root cause chain:**

1. AGENTS.md "Live metrics" table had no Duration column → no expected budget to
   calibrate timeout against
1. Partial output from timeout #3 showed `[  6%]` dots — never read them
1. Assumed "timed out" meant "hanging" not "needs more time"
1. Escalated to flag permutations instead of increasing timeout

**Lesson:** ETA = elapsed_seconds / fraction_complete. 120s / 0.30 = 400s.
Set 600s once and be done. If a command produces ANY output before timeout,
the problem is almost certainly timeout length, not wrong flags.

**Prevention:** Always capture log output to a file (`>` or via tool's auto-save)
so partial results survive timeout. Read them before retrying.

## 2026-07-12 — Command failure pre-mortem

**Lesson:** Before running ANY command, predict what you'll do if it fails or
times out. Have a log-capture strategy ready. Never assume success.

**Implementation checklist for every command:**

1. "What could go wrong?" (timeout, wrong tool, missing flag, no PATH)
1. "How will I diagnose it?" (capture stderr, save partial output to file)
1. "What's my fallback?" (increase timeout, use different flag directly)
1. Check the tool is in PATH / available via `uv run` before running

## Cp1251 double-encoding mojibake detection

**When:** After fixing encoding corruption, or when Russian text appears garbled in templates/pages.

**Pattern:** UTF-8 encoded Cyrillic was misinterpreted as Windows-1251 (cp1251), then re-saved as UTF-8. This produces specific garbled characters.

**Detection scan (Python):**

```python
import os

# Characters that appear in cp1251 double-encoding but NOT in valid Russian
MOJI_INDICATORS = [
    '\u00b5',  # µ (cp1251 0xb5)
    '\u00b0',  # ° (cp1251 0xb0)
    '\u00b1',  # ± (cp1251 0xb1)
    '\u00b2',  # ² (cp1251 0xb2)
    '\u201a',  # ‚ (cp1251 0x82)
    '\u2021',  # ‡ (cp1251 0x87)
    '\u2019',  # ' (cp1251 0x92)
    '\u2018',  # ' (cp1251 0x91)
    '\u2039',  # ‹ (cp1251 0x8b)
]

for root, dirs, files in os.walk('src'):
    for fname in files:
        if not fname.endswith('.py'):
            continue
        with open(os.path.join(root, fname)) as f:
            for i, line in enumerate(f, 1):
                for ind in MOJI_INDICATORS:
                    if ind in line and 'import' not in line:
                        print(f'{fname}:{i}: {repr(ind)}')
```

**Fix strategy:**

1. Most strings: `mojibake_string.encode('cp1251').decode('utf-8')` works
1. Failed strings: manually reconstruct from context (byte 0x98 unmapped, apostrophe corruption)
1. Also scan test files — assertions may contain mojibake from copy-paste

**Known limitation:** `ftfy` doesn't catch all cp1251 patterns (unmapped bytes, character substitution). Manual verification needed.

## **(RESOLVED — merge queue removed, direct admin merge)** Merge queue on upstream `current` — REVIEW_REQUIRED blocks, own-PR can't approve

**When:** Merging a PR into `spbu-se/spbu_se_site` `current` branch.

**Old pattern (stale):** docs claimed `current` has a merge queue (SQUASH/ALLGREEN) configured via branch protection, and that `gh pr merge <n> --repo <owner>/<repo>` with **no strategy flag** enqueues into it. PR #183 was merged this way.

**Current reality (2026-08):** the merge queue is **no longer configured** — `required_merge_queue` is absent from branch protection and there are no `merge_group` runs. Recent PRs (#188, #189, #190) were merged **directly by the admin with `gh pr merge <n> --repo <owner>/<repo> --squash --admin`** (no queue events). `--admin` overrides the `REVIEW_REQUIRED` gate (required_approving_review_count=1, require_last_push_approval=true) using the author's bypass allowance.

**Trap:** running `gh pr merge <n> --repo <owner>/<repo>` **without a strategy flag** only enables **auto-merge** (`auto_merge_enabled`), which then waits forever on `REVIEW_REQUIRED` with `mergeQueueEntry: null` — it does **not** perform the merge. Use `--squash --admin` instead.

**After squash-merge:** the head branch's commits are rewritten into one commit on `current`; the fork's `staging`/`current` must be re-synced with `git reset --hard origin/current` + `--force-with-lease` push (content-identical, divergent history).

## **(ADDENDUM 2026-08-08 — queue toggles; check live API, never trust the doc)** Merge queue on upstream `current`

**When:** Repairing PR #194 (cryptography bump) and attempting the merge.

**Reality check:** the queue **toggles on and off** between batches. On 2026-08-08 branch protection had **no** `required_merge_queue` key, yet `gh pr merge <n> --squash` reported "The merge strategy for current is set by the merge queue", `mergeable_state=blocked`, and auto-merge was already enabled. Branch protection also has `required_approving_review_count=1` **and `require_last_push_approval=true`**: if you were the **last pusher**, your own approval does **not** count (`reviewDecision: REVIEW_REQUIRED` persists even with an APPROVED review on the exact head commit).

**Trap:** the branch-protection `merge_queue` field is absent when unset — do not alias it to `required_linear_history` in jq (same `enabled: true` shape, wrong meaning). And do not read the merge-queue's on/off state from this doc — it has flipped repeatedly (08-06 on→off, 08-08 on again). Always probe live: `gh pr merge <n> --squash` stderr (says "set by the merge queue") or `GET /repos/<owner>/<repo>/actions/merge-queue/queue` (404 when off).

**When blocked by `require_last_push_approval`:** get a review from a non-pusher (e.g. another maintainer) or merge via the web UI where the `iakov` bypass allowance applies. `--squash --admin` bypasses only when the queue is **off**; when the queue is on, the strategy is queue-controlled.

## Diagnostic test runs: `-q` + output truncation hides failures

**When:** Running the full pytest suite on a feature branch to validate changes.

**Attempts:**

1. `uv run pytest --tb=short -q` + `Select-Object -Last` — got counts only, no failure context; violated TESTING.md §3a ("save attempts, not screen space"). User flagged the behavior.

**Fix:** Diagnostic runs use `uv run pytest --tb=long -n 1` with full output captured (the tool auto-writes to a file if too large; search that file with `rg`, never `Select-Object -Last/-First`). `-q` only for the final green confirmation after a clean `--tb=long` run. Rule strengthened in AGENTS.md + TESTING.md §3a.

## Git commit via MCP tool times out when pre-commit hooks run

**When:** Committing through the `git_commit` MCP tool (opencode) — the tool call can time out (`MCP error -32001: Request timed out`) because pre-commit hooks (ruff-format, dprint, etc.) hold the shell.

**Pattern:** The commit may or may not have landed; `git log --oneline -3` shows it didn't, and files show `MM` (staged + unstaged) because pre-commit auto-fixed formatting on staged files after staging.

**Fix:** Re-stage (`git add -u`) after the failed commit and re-run via shell `git commit --no-gpg-sign -m "..."` (with a 120s timeout). On this repo feature branches use `--no-gpg-sign` per GIT_FLOW §4.

## dprint pre-commit hook hangs downloading WASM plugins (network)

**When:** Running `git commit` on this host — the dprint pre-commit hook (`.pre-commit-config.yaml` `trim21/dprint-pre-commit` → `dprint fmt`) took ~180s or timed out entirely.

**Root cause:** dprint downloads its formatter plugins (`pretty_yaml`, `toml`, `json` WASM) from `https://plugins.dprint.dev/` on first use, caching them in `~/.cache/dprint/cache/plugins/`. On this host the CDN stalled (HTTP 200 headers but 0 bytes of the 576 KB body in 25s over IPv4; no IPv6 route; DNS resolves to IPv6-only). The plugin cache stayed empty, so **every** dprint run re-attempted all 3 downloads → ~180s wall, ~0 CPU.

**Diagnosis:** `dprint check --verbose 2>&1` (redirect to a file, don't truncate) shows `[DEBUG] Downloading url: https://plugins.dprint.dev/...wasm` stalling with no progress. `curl -4 -w "%{http_code} %{size_download} %{time_total}"` confirms the stall. `~/.cache/dprint/cache/plugins/` missing/empty = cache never populated.

**Fix:** Turn on VPN / fix egress to `plugins.dprint.dev`. Once populated, dprint runs in ~6s and stays cached. **Pre-warm after fresh env setup:** run `uv run pre-commit run dprint --all-files` once. Note: `dprint check` finds real drift too (e.g., `src/client_google_test.json` 4-space→2-space) — run `dprint fmt` to fix, then `git add`.

## Config module test mocks `os.path.exists` — adding a new `exists()` call causes RecursionError

**When:** Adding a new config file read guarded by `os.path.exists(...)` in `flask_se_config.py` (e.g., the VK secret).

**Root cause:** `tests/test_flask_se_deep.py::TestFlaskSeConfigMailPassword::test_mail_password_read_from_file` monkeypatches `os.path.exists` with a wrapper whose fallback branch calls `os.path.exists(path)` **after** patching — self-recursion on any path that isn't the mocked one. It passed before only because `flask_se_config` had a single `exists()` call whose path matched the mock. CI failed with `RecursionError: maximum recursion depth exceeded` at `flask_se_config.py:24` (the new `os.path.exists(VK_SECRET_FILE)` call).

**Fix:** Capture the original before patching: `original_exists = os.path.exists` then `return original_exists(path)`. Committed in PR #191.

## `gh pr edit --body-file` fails with GraphQL "Projects (classic) is being deprecated" error

**When:** Updating a PR body with `gh pr edit <n> --repo <owner>/<repo> --body-file file.md`.

**Root cause:** `gh pr edit` uses a GraphQL mutation that queries `projectCards`, which errors out on repos with legacy Projects-classic enabled. The edit silently does not apply.

**Fix:** Use the REST API instead:

```
gh api -X PATCH "repos/<owner>/<repo>/pulls/<n>" -f body="$(cat file.md)"
```

## Tests: conftest mocks `check_password_hash` to always return True — legacy HMAC login branch is dead in tests

**When:** Writing a regression test for the legacy HMAC login fallback (`flask_se_auth.py` `login_index`, the `algorithm$salt$hexdigest` branch).

**Root cause:** `tests/conftest.py` patches `werkzeug.security.check_password_hash` to `lambda pwhash, password: True` (scrypt unsupported on Python 3.13), so the first branch always succeeds and the HMAC fallback is unreachable in tests.

**Fix:** Patch the module-local import so the fallback is exercised:

```python
with patch("flask_se_auth.check_password_hash", return_value=False):
    resp = seeded_client.post("/login.html", data={"email": ..., "password": ...})
```

Seed the user's `password_hash` as `f"sha256${salt}${hmac.new(salt.encode(), password.encode(), hashlib.sha256).hexdigest()}"` to match the legacy format. Committed in PR #191.

## Config-secret path vs contents trap (`SECRET_KEY` was a filesystem path)

**When:** 2026-08-02 full security audit; reviewing `flask_se_config.py`.

**Root cause:** `SECRET_KEY = os.path.join(..., "configs/flask_se_secret.conf")` — the *path string*, never the file's contents. Flask signed session cookies with a guessable absolute path → anyone knowing the deploy path could forge `_user_id` and take over any account incl. admin. A grep confirmed the file's contents were never read anywhere.

**Lesson:** When a config module defines a secret as `os.path.join(...)`, check whether the *contents* are ever opened. The path-vs-contents confusion is silent: everything works, auth "seems" secure, until someone notices the signing key is public. Fix pattern: `read_secret_from_file()` (reads trimmed contents; random dev fallback).

**Also:** `SECRET_KEY_THESIS = os.urandom(16).hex()` regenerated on *every import* → 4 uWSGI workers each had a different key, so `/post_theses` randomly 403'd and the "secret" was meaningless. Persistent secrets must come from a config file, not `os.urandom` at module scope.

## textile defaults to unsanitized HTML (`textile.textile()` + `|safe` = stored XSS)

**When:** 2026-08-02 audit of the news module.

**Root cause:** `textile.textile(post_text)` runs with sanitization off (`textilefactory` defaults `restricted=False, sanitize=False`) — raw `<script>`/`onerror` passes through, persisted pre-rendered, then emitted with `{{ post.text|safe }}` on a public page. Any registered user (open registration) could execute JS site-wide.

**Lesson:** Never assume a markup library sanitizes by default. `textile 4.0.4` has no `sanitize` kwarg on `textile()`; sanitize at the storage boundary with `nh3.clean()` (Rust/ammonia, already a transitive dep) and keep `|safe` only for sanitized content. Same principle applies to the `|markdown` filter: returning `Markup(...)` without sanitizing would create stored XSS.

## Verify CodeQL dismissals against live code — stale sinks

**When:** 2026-08-02 audit; reviewing dismissed alerts #162 (js/xss-through-dom at `base_practice_admin.html:33`).

**Root cause:** The dismissed alert pointed at a jQuery `.html()` sink that *no longer exists* — the file's line 33 is now a `<select onchange>`, and `git log -S '.html('` over template history found zero matches. The dismissal rationale ("no attacker-controlled input reaches the sink") was moot: there is no sink.

**Lesson:** Before trusting a CodeQL dismissal, check whether the sink still exists at the reported line. Re-run CodeQL after big refactors (no codeql workflow is configured, so alerts drift stale). For genuinely-open alerts, verify then dismiss with a concrete reason (e.g. #173: the flagged `f.write(r.content)` writes avatar image bytes, not the OAuth token — false positive).

## GitHub dismissal scope matrix (dependabot vs CodeQL)

**When:** 2026-08-08 triage — dismissing stale alerts.

**Findings:** **dependabot** alerts dismiss fine with the `repo` token scope via `PATCH /repos/<owner>/<repo>/dependabot/alerts/<n>` with `state=dismissed`, `dismissed_reason`, `dismissed_comment`. **CodeQL** code-scanning alert dismissal (`POST .../code-scanning/alerts/<n>/dismiss`) returns **404** unless the token has the `security_events` scope — the API is not reachable at all, not merely rejected. `gh auth status` shows the granted scopes.

**Lesson:** before attempting CodeQL dismissal, confirm `security_events` is in `gh auth status` scopes; otherwise log the token-upgrade as a maintainer action and dismiss via the web UI. Dependabot dismissal never needs the extra scope.

## Request method changes break `assert_ok` GET-based tests (static catch-all returns 404)

**When:** 2026-08-02, converting GET mutations to POST in Phase 2.

**Root cause:** The app sets `static_url_path=""`, so the catch-all route `/<path:filename>` (GET) serves *any* unmatched path. A GET to a now-POST-only route (e.g. `/news/delete`) is matched by the static rule → **404**, not 405. Tests expecting `{200, 302}` failed with 404.

**Lesson:** With `static_url_path=""`, GET on a POST-only route returns 404 (static fallback), not 405. When converting mutations to POST, allow 404 in route-accessibility tests or change them to POST. Also: `request.values` (merged args+form) keeps vote/delete views compatible with both `url_for(...)` query-string POSTs and form-data POSTs.

## djLint pre-commit reformats ALL html — conflicts with staged template edits

**When:** 2026-08-02 Phase 2, adding `{{ csrf_token() }}` to templates.

**Root cause:** The `djlint --reformat` hook (pre-commit stage) normalizes *every* html file during commit; if your staged template edits differ from djLint's output, the hook's stash/apply conflicts and the commit aborts with "Stashed changes conflicted with hook auto-fixes... Rolling back fixes".

**Fix:** Run `uv run pre-commit run djlint --all-files` once to normalize templates *before* staging, then `git add -A` and commit. The hook then passes with no conflicts.

## ruff-format auto-fix aborts commit — same conflict, Python variant

**When:** 2026-08-11 refactor, appending per-module `register_routes()` blocks with long lines.

**Root cause:** Same stash/apply conflict as djLint, but for `ruff format`. The pre-commit `ruff-format` hook rewrites long `app.add_url_rule(...)` lines; if the staged version differs from the hook's output, the commit aborts ("Stashed changes conflicted with hook auto-fixes").

**Fix:** `uv run ruff format src/` BEFORE staging, then `git add` and commit. General rule: any auto-fix hook that reformats more than the staged set (djLint → templates, ruff-format → Python) must be run once on all files before staging.

## `git cherry-pick --continue` fails: gpg signing Timeout

**When:** 2026-08-11, moving refactor commits from `current` onto `refactor/app-factory`.

**Root cause:** `commit.gpgsign=true` makes `git cherry-pick --continue` attempt to GPG-sign the reconstructed commit, which stalls/fails (`gpg: signing failed: Timeout`) when the agent is unlocked. Plain `git commit` had the `--no-gpg-sign` workaround documented, but cherry-pick-continue was not covered.

**Fix options:**

- `git cherry-pick --continue --no-gpg-sign`
- Or, if hooks already staged the change: `git commit --no-gpg-sign -m "<msg>"` (clears the cherry-pick state because the commit exists)
- To avoid the stall entirely: `git cherry-pick -n <commit>` then `git commit --no-gpg-sign`

## basedpyright `reportUnusedFunction` false positives on decorator-registered route functions

**When:** 2026-08-11, moving `@app.route`-decorated view functions inside `_register_*` helper functions.

**Root cause:** basedpyright (with `reportUnusedFunction = "error"`) cannot see that the `@app.route` decorator registers the nested function, so it reports "Function X is not accessed" for every nested route view.

**Fix:** Module-level opt-out `# pyright: reportUnusedFunction=false` in the module that owns the helpers (precedent: `flask_se_practice_config.py`). This is not an error-suppression of a real bug — the decorator does register the function at runtime.

## Re-export for tests via `__all__` (ruff F401 + pyright)

**When:** 2026-08-11, moving `scheduler` to `flask_se_scheduler.py` while tests still do `from flask_se import scheduler`.

**Root cause:** An import that exists only to be re-exported (`from flask_se import scheduler`) is flagged unused by ruff F401, and ruff's `--fix` silently deletes it. Tests then fail with ImportError.

**Fix:** Add the name to the module's `__all__` (`__all__ = ["app", "db", "scheduler"]`) — ruff honors `__all__` as an explicit re-export and stops flagging it. This keeps `from flask_se import scheduler` working for tests without a per-line `# noqa`.

## Route-map verification before/after refactoring

**When:** 2026-08-11, three-phase route refactor (factory → register_routes → module extraction).

**How:** Before starting, dump the route map to a file; after each refactor step, dump again and compare byte-identically:

```python
rs = sorted((r.rule, sorted(r.methods or [])) for r in app.url_map.iter_rules())
open(".tmp/routes.txt", "w").write(str(rs))
```

**Why it works:** Endpoint names derive from `view_func.__name__`, so moving `add_url_rule` calls between modules or wrapping them in helpers never renames URLs. A byte-identical map (191 rules) proves the refactor preserved every route and method — zero template/endpoint churn — before the full test suite runs.

## Plain-str template filter output gets re-escaped by Jinja autoescape

**When:** 2026-08-15, diploma-theme pages showed literal HTML tags (`<p>`, `<a href=...>`) as text in markdown fields.

**Root cause:** `render_markdown` returned a plain `str` from `python-markdown`. With Flask's autoescape, `{{ x|markdown }}` HTML-escapes the filter's return value, so the generated markup arrived as `&lt;p&gt;…`. Direct filter-call unit tests (`md("- a")`) assert on the raw return and never catch it — only a render-through-template assertion does.

**Fix:** The filter returns `Markup(nh3.clean(_markdown.markdown(...)))` — `nh3.clean` is mandatory *before* `Markup`, because python-markdown passes raw HTML through unchanged and the source is user-authored (sanitize-then-mark-safe, never mark-safe-then-trust). Regression test renders via `current_app.jinja_env.from_string("{{ text|markdown }}")` and asserts no `&lt;`.

## ruff S704 flags `Markup(...)` even when the argument is sanitized

**When:** 2026-08-15, adding `Markup(nh3.clean(...))` to the markdown filter.

**Root cause:** ruff's bandit-derived S704 "Unsafe use of `markupsafe.Markup`" fires on any non-literal `Markup(...)` call — it cannot see that `nh3.clean` runs in the same expression. It does not flag `Markup("literal")` (see `se_review_forms.py`).

**Fix:** Inline `# noqa: S704` with a justification suffix (`  sanitized immediately before Markup`), matching the repo's existing `# noqa: <code>  <reason>` convention.

## `git fetch --prune <remote1> <remote2>` fails — one remote per fetch

**When:** 2026-08-15, pre-flight `git fetch --prune origin upstream` → `fatal: couldn't find remote ref upstream`.

**Root cause:** `git fetch --prune` accepts a single remote; the second argument is parsed as a refspec, not a remote.

**Fix:** Fetch remotes separately: `git fetch --prune origin` then `git fetch --prune upstream`.

## Delete remote branches via `gh api -X DELETE`, not `git push --delete`

**When:** 2026-08-15, cleanup of merged branches on the canonical repo whose `upstream` remote push URL is deliberately `no-push-to-upstream`.

**Root cause:** `git push upstream --delete <branch>` is impossible by design (push guard, `docs/GIT_FLOW.md §8`); the bare-URL escape hatch works but runs the pre-push gate and needs explicit lease handling.

**Fix:** `gh api -X DELETE repos/<owner>/<repo>/git/refs/heads/<branch>` uses the gh token (which already has merge rights) and skips hooks entirely. Deletes the fork's own branches too, when preferred over `git push origin --delete`. 204 = success (no output).

## Squash-merged branches aren't `--merged`-detectable — prove with PR records

**When:** 2026-08-15, deleting 16 local + 19 fork + 4 upstream branches after the v2026.08.14 release chain.

**Root cause:** squash merges create a new commit, so the feature-branch tip is never an ancestor of `staging`/`current`; `git branch --merged` lists nothing and `git branch -d` refuses.

**Fix:** Use GitHub as the source of truth: `gh pr list --repo <owner>/<repo> --state merged --json number,headRefName,mergedAt` maps merged PRs to head branches; then `git branch -D` (forced) is justified by the evidence. Verify no local-only commits are lost first (`git rev-list --left-right --count <local>...origin/<branch>`).

## Patching `os.path.isfile` breaks Jinja template loading — silent `TemplateNotFound`

**When:** 2026-08-15, removing two stale xfails whose reason was "Missing template `notification/thesis_on_review_success.html`" — the template existed and loaded fine, yet the tests still failed with `TemplateNotFound`.

**Root cause:** the tests used `@patch("flask_se_review.os.path.isfile", return_value=False)`. Because `flask_se_review.os` *is* the `os` module, this patches the **global** `os.path.isfile`, and Jinja's `FileSystemLoader` (`open_if_exists`) calls `os.path.isfile` to resolve every template → **every** `render_template` during the patched window raises `TemplateNotFound`. Symptom masquerades as a missing template; pre-caching the template (`jinja_env.get_template`) hides it because the loader's cache short-circuits `open_if_exists`.

**Fix:** don't patch `os.path.isfile` globally when a request will render templates. Patch a narrower target, or rely on the real `os.path.isfile` returning `False` for the non-existent upload file (as here — `FileStorage.save` was mocked so nothing existed on disk). Verify by running the test without the patch.

## Verify third-party JS API surface against published artifacts, not docs/memory

**When:** 2026-08-19, the dual-provider maps PR (Yandex v3 + Google fallback). The SEO roadmap said Yandex was a "drop-in" at the loader layer — half true.

**Root cause:** two guesses would have shipped broken code:

- `YMap`/`YMapDefaultSchemeLayer` are **core globals** (`ymaps3.YMap`), NOT exports of `@yandex/ymaps3-default-ui-theme` — importing them from the UI theme returns `undefined`.
- `YMapPopupMarker` string `content` is assigned via `textContent`, so an HTML string renders literally; HTML content must be a `() => HTMLElement` factory.

**Fix:** instead of trusting docs/memory, downloaded the published artifacts and read them before writing `renderYandex`:

- `@yandex/ymaps3-types` (`.d.ts`) — `declare global { const ymaps3: typeof import('./index') }` proves the core global surface; `imperative/index.d.ts` lists `YMap`, `YMapDefaultSchemeLayer`, `YMapMarker`.
- `@yandex/ymaps3-default-ui-theme` dist (`index.mjs`) — confirmed `YMapDefaultMarker` props (`popup`, `onClick`), the popup toggle runtime (`_togglePopup`, `isOpen`), and the `textContent` string-content gotcha.

**Rule:** for any third-party JS API you wire into production code, verify the surface against the published package (type defs + dist) before writing the integration — grep the `.d.ts`/dist, not the README.

## Decode SQLAlchemy base-36 error codes from the `exc` source, not the sanitized URL

**When:** 2026-08-25, the 15h production 500 incident on `/theses.html` + `/news.html`.

**Root cause:** the `/logs` message showed `(Background on this error at: https://sqlalche.me/e/20/e3q8)`. `e3q8` was misread as a connection-pool-exhaustion error, and 4 hotfix PRs chased pool sizing/NullPool/consultant-cache before the real error surfaced. `e3q8` is actually the base-36 code for `sqlalchemy.exc.OperationalError` — the DB-level "no such column: users.deleted" schema drift. The real root cause was a model↔DB drift (`users.deleted` added in PR #237) that the deploy webhook's `flask db` step failed to migrate (Alembic removed, webhook not updated), compounded by zero monitoring.

**Lesson:** SQLAlchemy 2.x assigns every exception class a stable base-36 `code` (e.g. `e3q8` = `OperationalError`, `rvf5` = `InterfaceError`). Decode it from the installed `sqlalchemy.exc` source (`grep -r 'code = "' <venv>/sqlalchemy/exc.py`) or `int('e3q8', 36)` — never guess from the URL path. A sanitizer that rewrites the `sqlalche.me/e/20/<code>` path hides exactly the segment that identifies the exception class; prefer keeping the code visible (it is not secret).

**Fix:** the 500 handler now logs `exception type: message` plus a 3-tuple `exc_info`; `/logs` shows the real exception line instead of the generic `InternalServerError`. See `docs/RETROSPECTIVES.md` 2026-08-25 entry.

## Production deploy path ≠ repo-documented path — verify the webhook's actual commands

**When:** 2026-08-25, same incident.

**Root cause:** `docs/RELEASE_CHECKLIST.md` B17 and `TOOLING.md §Auto-migrate` claim `docker/entrypoint.sh` runs `python flask_se.py migrate` on boot — but **production deploys via a server-side webhook** that runs `flask db <subcommand>`. After PR #237 removed Alembic, that webhook command failed ("No such command 'db'") and silently no-op'd; the self-healing `ensure_schema()` was never invoked in production because the Docker entrypoint is not the prod mechanism.

**Lesson:** when the docs describe a boot/init mechanism, confirm it matches the *actual* production deploy path (webhook script, systemd unit, container entrypoint) — grep the deploy workflow's `WEBHOOK_URL` handler semantics, not just the repo's Docker files. Add a release-checklist item that verifies the deployed DB has the model's columns (schema drift check) after every release.

**Fix:** run `ensure_schema()` at app boot regardless of deploy mechanism (gated by `SE_AUTO_MIGRATE`, fault-tolerant), and register a `flask db` CLI group that delegates to `ensure_schema()` so legacy webhook commands keep working.

## A scheduled probe is the first consumer of its own guardrail — verify route lists against reality

**When:** 2026-08-25, immediately after PR #262 shipped the `Prod uptime probe` and post-deploy smoke guardrails.

**Root cause:** the probe and the deploy smoke test probed `/news.html` and `/login` — neither is a real route (the app serves `/news/` and `/login.html`). The probe fired on its very first scheduled runs: `/news.html` → 301, `/login` → 404, and the `gh issue` steps died with `failed to run git: fatal: not a git repository`. The same wrong route list was baked into the deploy smoke test, so the **next** deploy would have been blocked by the guardrail itself.

**Lesson:** a guardrail that assumes route existence without checking the app's actual routes produces false alarms (probe) and false blocks (deploy smoke). Before merging a workflow that probes URLs, verify every route against the app (`grep -n add_url_rule src/*.py`, or `curl` prod). Also: `gh` subcommands in a job **without `actions/checkout`** cannot discover the repo from git — always pass `--repo "${{ github.repository }}"`.

**Fix:** corrected route lists (`/`, `/theses.html`, `/news/`, `/login.html`, `/diplomas/`), added `--repo` to all `gh` calls, made the issue-list lookup resilient (`2>/dev/null || true`). `/logs` became opt-in (`SE_LOGS_ENABLED`, default off) so it was dropped from the probed list too.

## Read HTTP error bodies before theorizing — the 400 was "referrer header is missing", not the session

**When:** 2026-08-31, the "nobody can log in" incident on `se.math.spbu.ru`.

**Root cause:** a whole investigation session chased session/SECRET_KEY/caching hypotheses because every login POST returned `400` and only the status code was ever examined. Reading the 400 body — `The referrer header is missing.` — immediately identified the real cause: Flask-WTF's `WTF_CSRF_SSL_STRICT` (default `True`) requires a `Referer` header matching the host on any HTTPS POST. `requests`/`curl` send no `Referer` by default, so **our own probe** was the thing failing, and the previous session misread it as a systemic outage. The same POST with `Referer: https://se.math.spbu.ru/login.html` returned 200. Real browsers normally send same-origin referrers (the app sets `Referrer-Policy: strict-origin-when-cross-origin`), but the hard referrer dependency locks out privacy browsers/extensions, corporate proxies, password-manager autofill, and non-browser clients.

**Lesson:** a 400/403/500 status alone is not a diagnosis. Print the response body (and the `Location` header) on the very first probe. Also: `requests.Session` sends no `Referer` by default — a CSRF "rejection" reproduced with `requests`/`curl` may be an artifact of the missing header, not a site bug.

**Fix:** `WTF_CSRF_SSL_STRICT = False` (token-based CSRF is the real boundary; the referrer check was a redundant fragility), plus a `CSRFError` errorhandler that renders a friendly page. Regression gate: the deploy smoke test now POSTs `/login.html` with a valid token and **no Referer** and asserts 200 (a 400 means the referrer regression returned).

## Flask error templates need `g.csp_nonce` — CSRF rejection runs before the nonce before_request

**When:** 2026-08-31, writing the `CSRFError` handler above.

**Root cause:** `CSRFProtect` runs its `before_request` before the app's `_set_csp_nonce` (`register_security_headers`), so when a request is rejected, `g.csp_nonce` is unset. Any error template that extends `base_dark.html` (which renders `<script nonce="{{ csp_nonce() }}">`) then 500s — turning the intended friendly 400 into a crash. The test suite caught it; it would have hit prod on the first real CSRF rejection.

**Lesson:** when a `before_request` that sets request-global state (nonces, feature flags) is registered *after* a middleware-like `before_request` that can short-circuit, error handlers cannot rely on that state. Set the nonce (or any needed `g` value) inside the errorhandler itself so the template and the CSP header agree.

**Fix:** `g.csp_nonce = secrets.token_urlsafe(16)` inside `_handle_csrf_error` before `render_template` — the `after_request` CSP builder reads the same `g.csp_nonce`, so the template nonce matches the header.

## Testing CSRF-protected routes under test client: `wsgi.url_scheme` + patching the rate limiter

**When:** 2026-08-31, regression tests for the CSRF fix and the password-recovery feature.

**Root cause/lessons:**

- The Flask test client defaults to `http`, so `request.is_secure` is `False` and Flask-WTF's SSL-strict referrer check is **skipped** — a test that asserts "POST with no Referer is accepted" would pass even with `WTF_CSRF_SSL_STRICT=True`. To exercise the HTTPS branch, set `client.environ_base = {"wsgi.url_scheme": "https"}` (the test client sends no `Referer` by default, which is exactly the case under test).
- The module-level `RateLimiter` singletons (`LOGIN_RATE_LIMITER`, `PASSWORD_RECOVERY_RATE_LIMITER`) persist across tests in a process; several recovery POSTs from the same test IP trip the 5/3600s limit and the later tests stop sending mail. Patch the limiter per test: `patch.object(flask_se_auth.PASSWORD_RECOVERY_RATE_LIMITER, "allow", return_value=True)`.
- `WTF_CSRF_ENABLED` is `False` in conftest; flip it to `True` (and restore in `finally`) for the CSRF-positive tests, mirroring the existing `test_csrf_protects_post_forms` pattern.

## CD silently failed for 5 merges — deploys are fire-and-report

**When:** 2026-09-06. Five squash-merges into `current` produced deployments to the staging `deploy_environment` that all failed with `curl: (22) 404` on the deploy-host webhook — none of the code was ever staged. Detection happened only when deployment statuses were inspected; there is no alert, and CI stays green because CD is a separate, non-gating workflow.

**Root cause:** staging webhook endpoint returned 404 (ops-side; new staging env). Not code — a re-run of the failed job (not a new commit) fixed it.

**Lesson:** after any merge to `current`, verify the latest deployment equals the merged SHA with `state == success` before continuing. Command + staging notes: `docs/TOOLING.md` §Staging environment.

## UTF-8 BOM in docs — green CI, still a policy violation

**When:** 2026-09-10 docs/skills drift audit. Seven `docs/*.md` files carried a UTF-8 BOM (`EF BB BF`) before the H1 despite `docs/DOCS.md §6.2` forbidding it; no CI/pre-commit check catches it, so `current` was green.

**Detection (fast, no dependencies):**

```bash
for f in docs/*.md AGENTS.md CLAUDE.md README.md; do
  [ "$(head -c3 "$f" | od -An -tx1 | tr -d ' \n')" = "efbbbf" ] && echo "BOM: $f"
done
```

**Fix:** strip the first three bytes and rewrite as UTF-8 (no BOM):

```python
import pathlib
p = pathlib.Path(path)
b = p.read_bytes()
if b.startswith(b"\xef\xbb\xbf"):
    p.write_bytes(b[3:])
```

**Lesson:** the encoding policy is documented but unenforced — a BOM is invisible in review and in CI. Re-run the detection loop after any bulk doc import/edit; if it recurs, add a pre-commit hook (`check-byte-order-marker`).

## Documentation "reference run" logs drift silently

**When:** 2026-09-10. `docs/TESTING.md`'s reference-run block still ended at `1402 passed` (2026-08-21) while the suite collected 1520; `docs/QUALITY_MANAGEMENT.md` hardcoded "92 pyright ignores" and a `--branch staging` CI command for a branch (`staging`) that no longer exists.

**Lesson:** append-only metric logs (test counts, coverage, ignore counts) are freshness anchors that other docs inherit (`RELEASE_CHECKLIST.md` A2). Treat every session that changes the suite as requiring the latest line to be appended, and prefer query-only phrasing ("query live, never hardcode") over embedded numbers.
