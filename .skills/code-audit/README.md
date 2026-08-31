# code-audit

<!-- encoding: utf-8 -->

Code quality and security audit: detect secrets in logs, validate redirects, scan deprecations, check crash safety and file safety, maintain bug inventory, and run repo-wide review patterns. Does not fix bugs — reports and saves for future work.
Not doc health (see `.skills/docs-audit/`), not process improvement (see `.skills/retrospective-analysis/`). For a deep security audit (GitHub security surface + three-pass authz/XSS/SQLi review), load `.skills/security-audit/` instead.

## When to load

- Before `staging→current` gate (protects users and product)
- After any session touching 5+ source files (proactive, not reactive)
- On user request for code audit

## Workflow

### 1. Secrets in logs

Scan CI output and application logs for values that look like secrets (API keys, tokens, passwords, `urandom` output):

```bash
gh run view <run-id> --log | Select-String -Pattern "(secret|key|token|password)"
```

If found, classify:

- **Ephemeral** (regenerated on every restart, e.g., `os.urandom(16).hex()`) → P2 — the pattern trains developers to ignore ERROR output
- **Persistent** (same value across restarts, committed or configured) → P0 security issue

Reference: `docs/CODE_ISSUES.md` SECRET_KEY_THESIS entry.

### 2. Redirect validation

Scan source for unvalidated `next`-parameter redirects:

```bash
rg "redirect.*next" src/ --include "*.py"
rg "redirect_next_url" src/
```

Verify `next` URL is validated (relative URL check, whitelist, or `url_parse`). If unvalidated, add entry to `docs/CODE_ISSUES.md` if not already tracked.

Reference: `docs/CODE_ISSUES.md` P2 redirect entry.

### 3. Deprecation scanning

Check each P4 entry in `docs/CODE_ISSUES.md` against current dependency versions:

```bash
uv run python -c "import flask_admin; print(flask_admin.__version__)"
```

If a deprecation is now breaking (e.g., Flask-Admin dropped `db.session`), escalate priority from P4 to P0/P1 and add to `TODO.md` backlog.

### 4. Bug inventory freshness

Walk all `[OPEN]` entries in `docs/CODE_ISSUES.md`. For each:

1. Can you reproduce the bug with a quick test or code inspection?
1. If reproducible → leave as `[OPEN]`
1. If fixed (code changed, bug gone) → mark `[FIXED]` with session reference
1. If no longer reproducible but root cause unknown → mark `[UNCONFIRMED]` — do not delete, the pattern may recur

Nothing is silently dropped. Every status change is logged.

### 5. Test health

Check for xpassed tests (expected to fail but now passing):

```bash
uv run pytest -n 2 --tb=no -q 2>&1 | Select-String "xpassed"
```

For each xpassed test:

- Bug was fixed but xfail marker wasn't removed → remove the marker
- Test is accidentally passing (false positive) → flag for investigation
- Report findings to `TODO.md` backlog

Reference: `docs/TESTING.md` §5.

### 6. Crash safety

Scan for patterns that cause 500 errors at runtime:

- **Bare `except:`** — swallows all errors, makes debugging impossible
  ```bash
  rg "^\s*except\s*:" src/ --include "*.py"
  ```
- **`sys.exit()` in non-CLI modules** — kills the WSGI process
  ```bash
  rg "sys\.exit" src/ --include "*.py"
  ```
- **Routes with no DB error handling** — uncaught `SQLAlchemyError` returns 500
- **`.get()` without default on `request.form`** — `None.strip()` crashes
  ```bash
  rg 'request\.form\.get\("[^"]*"\)\.strip\(\)' src/ --include "*.py"
  ```
- **`str + None` in URL/string concatenation** — `base_url + old_text_uri` crashes when `old_text_uri` is `None`
  ```bash
  rg '\+\s*\w+\s*\+\s*\w+' src/ --include "*.py"
  ```
  Fix: use `(var or "")` to guard against None.

Report findings to `TODO.md` backlog. Reference fixed patterns from session 4 (`flask_se_review.py:215` fix).

### 7. File safety

Scan for file-handling patterns that could hurt users or the product:

- **Upload path traversal** — filename contains `../` that escapes upload directory
  ```bash
  rg "save\(|open\(.*filename" src/ --include "*.py"
  ```
- **Missing extension validation** — user uploads `.txt` where `.pdf` required
- **Unsafe `send_file` paths** — user-controlled filename passed to `send_file()` without path sanitization
- **File I/O without `try/finally`** — temp files left on crash

Report all findings to `TODO.md` backlog. Existing mitigations (extension checks in practice routes) are noted but not assumed complete.

### 8. Repo review

Load and run `docs/REPO_REVIEW.md` checklist. Report any unchecked items not yet addressed. If new findings from sections 1-7 suggest checklist additions, propose them.

### 9. Reporting

Output a table:

| Finding | Source | Severity | Action |
|---------|--------|----------|--------|
| ... | ... | Harm / Concern / Cleanup | Report → TODO.md / Fix now / Investigate |

**Severity levels**:

| Level | Meaning | Action |
|-------|---------|--------|
| **Harm** | Hurts users or product (Supreme I/II) | Report → `TODO.md` backlog immediately |
| **Concern** | Theoretical risk or code quality gap | Report → `CODE_ISSUES.md` entry |
| **Cleanup** | Style, stale markers, config drift | Fix or report — low urgency |

Append new entries to `docs/CODE_ISSUES.md` for findings not yet tracked. Cross-reference `TODO.md` backlog entries to the relevant `CODE_ISSUES.md` item.

### 10. Universal-safe transformations — use replaceAll

When a fix is universally safe (applies the same transformation everywhere without risk), use `replaceAll` instead of context-matching individual sites.

**Example**: `base_url + old_text_uri` → `base_url + (old_text_uri or "")`. The `or ""` is a no-op when `old_text_uri` is already a string, making it safe across all 17 occurrences. Context-matching each site wasted 5 minutes.

**Signal**: If the transformation is equivalent to adding a default (`or 0`, `or ""`, `or []`) or wrapping in a no-op call, it's safe to `replaceAll`. If it changes behavior (adds/removes logic, changes types, renames), match individually.

### 11. SPbU regulation spot-check

After any session touching 5+ source files, re-verify the site still satisfies the СПбГУ website regulation clauses that affect the UI — canonical source `docs/SPBU_REGULATIONS.md`:

- header link to `https://spbu.ru` (§3.1.9) — navbar SPbU logo;
- accessibility mode or font ≥ 14 pt (§3.1.6) — footer «Версия для слабовидящих» toggle + `a11y.css`;
- footer copyright format (§3.1.15) — «© Санкт-Петербургский государственный университет, \<год>» present.

**Docs-first**: skills are generated from docs — if a rule here and the doc disagree, fix the doc first, then re-sync this skill.

## Dependencies

- `rg` (ripgrep) — for fast source scanning
- Read access to `docs/CODE_ISSUES.md` — bug inventory
- Read access to `docs/REPO_REVIEW.md` — repo checklist
- Read access to `docs/TESTING.md` — xfail policy
- Read access to `docs/SPBU_REGULATIONS.md` — СПбГУ website-regulation compliance posture
