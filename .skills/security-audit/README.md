# security-audit

<!-- encoding: utf-8 -->

Structured security audit workflow: survey the GitHub security surface, run a three-pass deep code review, verify every finding before acting, and dismiss alerts only with proof. Does not fix bugs — reports and saves for future work.

Not a general code-quality audit (see `.skills/code-audit/`), not doc health (see `.skills/docs-audit/`), not process analysis (see `.skills/retrospective-analysis/`).

## When to load

- On user request for a security review / audit
- Before a release or staging→current gate with security implications
- After any session that touched authentication, authorization, file uploads, or rendering of user HTML
- When triaging Dependabot, CodeQL, or security-advisory alerts

## Workflow

### 1. Survey the GitHub security surface

Query live state — never assume:

```bash
# Dependabot
gh api repos/<owner>/<repo>/dependabot/alerts --jq '.[] | select(.state=="open") | {number, package: .dependency.package.name, severity: .security_advisory.severity, ghsa: .security_advisory.ghsa_id}'
# Code scanning
gh api repos/<owner>/<repo>/code-scanning/alerts --jq '.[] | {number, rule: .rule.id, severity: .rule.severity, state, path: .most_recent_instance.location.path, start_line: .most_recent_instance.location.start_line}'
# Private advisories (may include unreported CVEs)
gh api repos/<owner>/<repo>/security-advisories --jq '.[] | {ghsa_id, severity, summary}'
```

**Stale-alert check**: Dependabot alerts for packages whose manifest version is already patched (e.g. Pillow `<12.3.0` while `pillow==12.3.0` is pinned) are stale — they auto-resolve on the next scan of the default branch. Verify the pinned version in `pyproject.toml`/`requirements.txt` before treating them as real. Do NOT dismiss them; document and move on.

### 2. Three-parallel-pass deep review

Launch three explore agents in parallel, one per concern, with explicit "read-only, report file:line" instructions:

| Pass | Focus | Typical findings |
|------|-------|------------------|
| **Authz / CSRF / OAuth** | Session signing key, secret handling, CSRF coverage, GET-vs-POST mutations, OAuth `state` validation, login enumeration, auth decorators, IDORs | Forgeable sessions (SECRET_KEY = path), commented-out `@login_required`, GET mutations, missing OAuth state, user enumeration |
| **XSS** | Markup library defaults, `\|safe` sinks, JS-context interpolation, `innerHTML`/`.html()`, raw HTML storage | `textile`/`markdown` unsanitized defaults, `\|safe` on user HTML, stored XSS on public pages |
| **SQLi / file handling** | Raw SQL parameterization, FTS query-language escaping, upload validation (extension + content + size), path traversal (read + write), zip-slip, unsafe deserialization, unbounded downloads | FTS5 query injection, arbitrary-extension uploads served from `static/`, name-derived path traversal, `r.content` memory DoS |

Each agent must return severity (CRITICAL/HIGH/MEDIUM/LOW), file:line, data flow, and a suggested fix — and must NOT modify anything.

### 3. Verify before acting (mandatory)

Every finding that leads to a fix or a dismissal must be proven first:

- **Grep the claim**: for "SECRET_KEY is a path", `grep -rn "flask_se_secret" src/` and confirm the file *contents* are never read; for "extension whitelist accepts .html", read the regex; for "sink exists", `git log -S '<sink>'` over the file's history.
- **Empirically test library behavior**: `uv run python -c "...nh3.clean(...)"` before relying on a sanitizer; check `textile.textile` signature for a `sanitize` kwarg (4.x has none at module level).
- **Check current line numbers**: CodeQL/scanning alerts reference line numbers that drift; an alert's sink may no longer exist.

### 4. Classify and fix in severity order

1. **CRITICAL** — session forgery, stored XSS on public pages, auth bypass → fix first, with regression tests.
1. **HIGH** — CSRF, upload validation, secret-in-UI, broken access control → fix second.
1. **MEDIUM** — path traversal, DoS, IDORs, enumeration, rate limiting → fix third.
1. **LOW / defensive** — FTS escaping, CSV injection, page_size caps → fix as time allows.

For each fix: add a regression test that reproduces the old behavior (e.g. `TestSecurityCritical`, `TestSecurityMedium` classes), then run the affected suite, then the full suite.

### 5. Dismiss alerts only with proof

| Alert | Dismissal rule |
|-------|----------------|
| **Vendored/client-side** (jQuery bundles, public browser API keys) | Dismiss with reason citing the vendor bundle or referrer-restricted key |
| **False positive** (sanitizer not modeled by CodeQL, custom validator) | Dismiss with the actual data flow as the reason (e.g. "#173: the flagged `f.write(r.content)` writes avatar image bytes, not the OAuth token") |
| **Fixed in code** | Do NOT dismiss — the alert auto-closes after merge; verify with a rescan |

Always verify the current line's code before dismissing; a dismissal rationale is only as good as the code it describes.

### 6. Reporting

Output a table:

| Finding | Severity | File:line | Status | Action |
|---------|----------|-----------|--------|--------|
| ... | CRITICAL/HIGH/MEDIUM/LOW | ... | FIXED / OPEN / DISMISSED | Fix + test / Report / Dismiss with reason |

Append the full findings to `docs/CODE_ISSUES.md` under a dated "Security audit <date>" section with severity, file:line, and status. Cross-reference new design decisions to `docs/DESIGN_DECISIONS.md` and reusable lessons to `docs/AI_AGENT_EXPERIENCE.md`.

### 7. Phase the delivery

Prefer small, stackable PRs by severity (critical → high → medium → stale-issue sweep → docs) on a single stacked fork branch. Each phase is independently mergeable and testable; docs land last so `[FIXED]` statuses are accurate.

## Reusable patterns (extracted from 2026-08-02 audit)

- **Config secrets are file *contents*, never paths** — `SECRET_KEY = os.path.join(..., ".conf")` (the path string) fed to Flask = forgeable sessions. Read via a `read_secret_from_file()` helper; persistent secrets never come from `os.urandom()` at module scope (regenerates per import → inconsistent across uWSGI workers).
- **`static_url_path=""` catch-all returns 404, not 405** for wrong-method requests — app's static rule `/<path:filename>` swallows unmatched GETs. Allow 404 in route-accessibility tests.
- **GET→POST conversions read `request.values`** (merged args+form) to stay compatible with both `url_for` query-string POSTs and form-data POSTs.
- **djLint pre-commit reformats ALL html** — run `pre-commit run djlint --all-files` to normalize before staging template edits, or commits abort.
- **Endpoint contracts**: some views return HTTP 200 with status in a JSON body — check the contract before asserting `status_code`.

## Dependencies

- `gh` (GitHub CLI) — for the security-surface survey
- Read access to `docs/CODE_ISSUES.md` — findings inventory
- Read access to `docs/DESIGN_DECISIONS.md`, `docs/AI_AGENT_EXPERIENCE.md` — where decisions/lessons land
- Read access to `tests/` — regression-test conventions
