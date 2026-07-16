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

## db.init_app: "already registered" on module-level import

**When:** Importing a module that calls `db.init_app(app)` at module level when `conftest.py` has already registered the same `db` on the same `app`.

**Attempts:**

1. Tried `db.app = app` before `db.init_app(app)` — fails, same RuntimeError
1. Tried `app.extensions.setdefault(...)` — fragile, not idempotent
1. Used `contextlib.suppress(RuntimeError)` around the call — works

**Error:** `RuntimeError: A 'SQLAlchemy' instance has already been registered on this Flask app.`

**Occurs in:** `thesesImport.py:20` — `from flask_se import app; db.init_app(app)` runs at import time.

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
1. Read `docs/TODO.md` Blocked section — known blockers
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
2. Failed strings: manually reconstruct from context (byte 0x98 unmapped, apostrophe corruption)
3. Also scan test files — assertions may contain mojibake from copy-paste

**Known limitation:** `ftfy` doesn't catch all cp1251 patterns (unmapped bytes, character substitution). Manual verification needed.
