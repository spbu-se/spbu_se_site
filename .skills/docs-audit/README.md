# docs-audit

<!-- encoding: utf-8 -->

Doc health checks: freshness, cross-references, scope discipline, encoding, and structural integrity.
Not process improvement (see `.skills/retrospective-analysis/`).

## When to load

- After doc restructuring or content moves between docs
- Before a staging→current gate (as part of finalization)
- When a session touches 3+ `.md` files
- On user request for doc audit

## Workflow

### 1. Config parity

Does every CI check have a matching pre-commit hook or manual step in `AGENTS.md` §Before committing?
Is every tool rule described in both doc AND enforced in config? → remove from doc, cross-reference config file.

### 2. Cross-reference integrity

- Scan all `.md` files for **hardcoded step numbers** (`§N`, `§N.M`, `step N`) → replace with section-title references
- Check for **same rule in 2+ non-trivial docs** → pick canonical source, replace others with `See X.md §Y`
- Check **CLAUDE.md delegates to AGENTS.md, AGENTS.md delegates to docs/** — never copy content up the chain
- Check `docs/DOCS.md` catalog: every `.md` file listed? All listed files still exist on disk?
- Check **every cross-reference** (`see X.md`) still points to a valid file and section

### 3. Scope discipline

- Every `.md` file has a **scope header** (first 5 lines matching `docs/DOCS.md` §3.1 template: title, encoding, scope, covers, does-not-cover)
  - Check each doc specifically for `Covers:` and `Does not cover:` lines — 4 docs are missing these as of session 6
  - If missing, add them matching the doc's actual scope
- No content violates its doc's stated scope (e.g., encoding commands in a doc about encoding policy, not in a tooling doc)
- New rules placed in the **correct canonical doc**, not the closest one at hand

### 4. Freshness

- **Hardcoded metrics**: test count, coverage %, file counts — verify against `pytest`, `coverage`, or `ls`
- **Expired guardrails**: conditional constraints ("do X until Y") — check if condition Y is now met
- **Stale statuses**: OPEN/FIXED/PENDING markers on bugs — check each against actual codebase state
- **Documentation table**: any table enumerating project files, docs, or modules — count vs reality on disk

### 5. Encoding

- Every source file (`.py`, `.md`, `.yaml`, `.json`, `.toml`, `.cfg`) has an encoding declaration — see `docs/DOCS.md` §6.2
- No UTF-8 BOM (EF BB BF) in any file — CI catches this, but verify locally before push
- Count Python files with `# -*- coding: utf-8 -*-` declaration
- Count markdown files with `<!-- encoding: utf-8 -->` declaration

### 6. SPDX / licensing

- Every new or modified source file has an SPDX header matching the repo's `LICENSE` file
- If `LICENSE` is missing, flag it
- If multiple licenses exist, document coverage per directory

## Output template

```
## Doc Audit Results

Config parity violations: <N>
Cross-reference issues: <N>
Scope violations: <N>
Freshness issues: <N>
Encoding issues: <N>
SPDX issues: <N>

### Action items

| File | Issue | Fix |
|------|-------|-----|
| ... | ... | ... |
```
