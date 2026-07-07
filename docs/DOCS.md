# Docs Management

<!-- encoding: utf-8 -->

Meta-documentation for the SE Site project: how, why, and where we document things. The canonical source for all doc-related conventions, policies, and checks.

Covers: doc creation rules, update rules, canonical source discipline, encoding policy, formatting conventions, integrity checks, document catalog, and recurring anti-patterns. Does not cover: general development process — see `docs/DEVELOPMENT_PROCESS.md`, git workflow — see `docs/GIT_FLOW.md`, tool-specific knowledge — see `docs/TOOLING.md`, error troubleshooting — see `docs/TROUBLESHOOTING.md`.

## 1. Why We Document

This is an AI-assisted, single-agent project. Documentation is how we persist knowledge across sessions:

- Each session starts from the collective past, not zero.
- "Never trust memory — encode every finding in docs" (AGENTS.md).
- Recurring failures (over-engineering, path drift, stale refs) are eliminated by documenting the fix, not just applying it.
- A documented process is a debuggable process. An undocumented fix is a future bug waiting to be rediscovered.

## 2. Document Catalog

Every `.md` file in the project, its scope, and what it is canonical for.

### Root docs

| File | Scope | Covers | Does Not Cover | Canonical For |
|------|-------|--------|----------------|---------------|
| `README.md` | Project | Setup, badges, overview | Implementation details | Project entry point |
| `AGENTS.md` | AI instructions | Commands, pre-flight checks, quirks | Full process docs | Quick reference for agent |
| `CLAUDE.md` | AI instructions | Skills table | Commands, process | Skill registry |
| `TODO.md` | Tasks | Backlog, known bugs, coverage | Process improvement ideas | Task tracking |

### docs/ directory

| File | Scope | Covers | Does Not Cover | Canonical For |
|------|-------|--------|----------------|---------------|
| `DOCS.md` | Doc management | (this file) | (everything else) | Doc conventions, checks, catalog |
| `DEVELOPMENT_PROCESS.md` | Process | Planning, testing, linting, code review, release, deps, session lifecycle | CLI, architecture, AI tooling, git | Process workflow, session lifecycle |
| `GIT_FLOW.md` | Git | Branching, merge strategy, commit discipline, signoff, versioning | Planning, testing, process | Git workflow |
| `RETROSPECTIVES.md` | History | Retrospective entries from prior sessions | Git workflow, development process | Process gap history |
| `ARCHITECTURE.md` | Code design | Module map, data flow, Design Decisions | Endpoints, schema | Module responsibilities, design rationale |
| `API_REFERENCE.md` | Routes | All endpoints, methods, view functions | Models, architecture | Route registry |
| `SCHEMA.md` | Database | Tables, fields, relationships | Endpoints, architecture | DB schema |
| `REQUIREMENTS.md` | Features | Feature specs, user roles, navigation | Implementation, schema | Feature definition |
| `TESTING.md` | Testing | Discipline, targets, xfail policy, long-term gaps | Fixture patterns, methodology | Testing strategy |
| `TOOLING.md` | Tools | Portable tooling knowledge | Local quirks, project errors | Cross-platform tool patterns |
| `TROUBLESHOOTING.md` | Errors | Common errors, root causes, fixes | Portable tooling | Fix recipes |
| `CODE_ISSUES.md` | Bugs | Known production bugs | Process gaps | Bug inventory |
| `REPO_REVIEW.md` | Audit | Health checklist | — | Repo health audit |
| `REVERSE_ENGINEERING.md` | RE | Re-engineering cycle | Dev workflow, testing | RE methodology |
| `OPENSE_CONFIG.md` | AI config | AI tooling config, permissions | Process, git | AI tool setup |

### Skills directory (.skills/)

| File | Scope | Covers | Canonical For |
|------|-------|--------|---------------|
| `.skills/retrospective-analysis/README.md` | Analysis | Process gap identification and classification | Retrospective workflow |
| `.skills/test-writer/README.md` | Testing | Hermetic pytest test patterns | Test writing methodology |
| `.skills/encoding-audit/README.md` | Encoding | UTF-8 detection and repair on Windows | Encoding fix recipes |
| `.skills/unattended-mode/README.md` | Automation | Autonomous batch run rules | Auto-mode workflow |
| `.skills/flask-test-patterns/README.md` | Fixtures | Reusable Flask/SQLAlchemy/pytest fixtures | Test infrastructure patterns |
| `.skills/repo-review/README.md` | Audit | Repository health evaluation | Repo audit workflow |
| `.skills/api-client/README.md` | API | HTTP client with retry | API client patterns |
| `.skills/model-definer/README.md` | Models | SQLAlchemy model and WTForms definitions | Model patterns |
| `.skills/gh-todo-sync/README.md` | Sync | TODO.md sync from GitHub/CI | Todo sync workflow |
| `.skills/js-bundle-analysis/README.md` | JS | Reverse-engineering JS bundles | Bundle analysis |
| `.skills/readme-generator/README.md` | README | Generating polished project READMEs | README generation |

### Vendor skill stubs (.opencode/skills/, .claude/skills/, .agents/skills/)

Each stub (`SKILL.md`) points to the canonical source in `.skills/<name>/README.md`. These are thin wrappers for tool-specific loading — never author skill content here.

### Commands (.opencode/commands/)

| File | Purpose |
|------|---------|
| `pause.md` | Graceful exit — save session state |
| `finalize.md` | Run staging→current gate and merge |

## 3. Doc Creation Rules

### 3.1 Required Structure

Every `.md` file under `docs/` must follow this header structure:

```
# Title

<!-- encoding: utf-8 -->

One-sentence aim describing what the file documents and who it serves.

Covers: <what this file covers>. Does not cover: <what this file explicitly does not cover> — see <related doc> for that.
```

The "Covers" / "Does not cover" pair is mandatory. It prevents scope creep and helps readers find the right doc.

### 3.1a Section Anatomy

Every section in a process or reference doc should follow this layer order when all three are present:

| Layer | Asks | Content |
|-------|------|---------|
| **Why** | Why does this matter? | Principle, value, rationale (one paragraph) |
| **What** | What must I do? | Discipline, rule, requirement — declarative statements |
| **How** | How do I do it? | Mechanics — numbered steps or procedure |

**Why** and **What** are always written inline. **How** references commands and tool options externally — either a code block within the same section or a cross-reference to `docs/TOOLING.md`. Never embed CLI flags or config syntax inside a rule statement.

This separation keeps rules scannable (read the What), steps followable (read the How), and philosophy findable (read the Why).

### 3.2 New Artifact Checklist

When creating any new file, directory, or tooling config, run through these four questions:

1. **Scope** — What does it cover? What does it explicitly not cover? Write a one-sentence aim at the top.
1. **Vendor lock-in** — Does it reference a specific AI tool? If yes, create a canonical vendor-agnostic version first, then thin wrappers per tool.
1. **Convention** — Does an existing pattern apply? (e.g., all `.md` under `docs/` need aim + scope, skills go in `.skills/`, formatting via ruff+mdformat)
1. **Canonical source** — If this could be referenced from multiple places, where does the one true version live? Other locations should be derived cross-references.

### 3.3 Pre-Creation Directory Audit

Before creating any new file or directory, verify nothing similar already exists:

```bash
ls docs/
grep -i "<name>" docs/*.md
```

Read existing content to assess scope overlap. A duplicate is harder to fix than to prevent. This rule exists because we have created duplicates before (`doc/` when `docs/` existed).

### 3.4 Doc-to-Code Sync

When docs describe code that does not yet exist:

1. Add a `# TODO` comment in the doc
1. Implement in a `feat:` or `fix:` commit
1. Run tests before merging

### 3.5 Skill Convention

Skills live in `.skills/<name>/README.md` (vendor-agnostic canonical source). Per-vendor stubs in `.claude/skills/`, `.opencode/skills/`, `.agents/skills/` point to the canonical skill. The `name` must be lowercase alphanumeric with hyphens and match the directory name.

#### Adding a new skill

1. **Canonical source** — create `.skills/<name>/README.md`
1. **Vendor stubs** — create `SKILL.md` in `.opencode/skills/<name>/`, `.claude/skills/<name>/`, `.agents/skills/<name>/`
1. **Register** — add to `CLAUDE.md` skills table
1. **Cross-reference** — add to `AGENTS.md` if needed, reference in relevant process docs

## 4. Doc Update Rules

### 4.1 When to Update

- **Doc changes belong on `docs/` branches or during staging→current gate**, not on feature branches. See `docs/DEVELOPMENT_PROCESS.md §0.6`.
- **Exception**: architecture-first or doc-first cycle was violated (code before doc) → add a `TODO.md` debt entry mid-sprint. This is a violation record, not a doc change.
- **Exception**: new findings during implementation (bugs, quirks, workarounds) go to `TOOLING.md` or `TROUBLESHOOTING.md` immediately, not at session end. See "Document as you go" in `.skills/unattended-mode/README.md §9`.

### 4.2 What Not to Update During Feature Work

- Process docs (`docs/GIT_FLOW.md`, `docs/DEVELOPMENT_PROCESS.md`) are sacred — minimize edits unless user explicitly approved. Gather observations and suggest improvements. Process doc changes happen during the staging→current gate.

### 4.3 Context Compaction (Session End)

Before compacting context or ending session:

1. Update `docs/ARCHITECTURE.md` Design Decisions with new choices
1. Update `TODO.md` (remove completed, reorder backlog)
1. **AI instructions drift check**: verify no unique content in AI instructions — every claim must cross-reference a canonical source. If a new quirk is needed, write the full version in the canonical doc first, then extract a condensed cross-reference.
1. Audit cross-references: scan every `.md` file under `docs/` and `.skills/` for hardcoded step numbers. Replace with section-title references (e.g., `§2 — Task selection priority ladder` instead of `step 50`).

## 5. Canonical Source Discipline

### 5.1 The Rule

Every fact lives in exactly **one** canonical doc. All other locations cross-reference back to it.

- **Facts live in `docs/*.md`** — never author facts directly in AI instructions (`AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md`).
- **AI instructions are extracts** — they contain condensed cross-references, not original content.
- **Skills are canonical in `.skills/<name>/README.md`** — vendor stubs are thin wrappers.

### 5.2 Cross-Reference Format

Use descriptive section references, not hardcoded step numbers:

```
See docs/X.md §Section Title
```

This survives renumbering. Hardcoded step numbers (e.g., `step 50`) break when sections are reordered.

### 5.3 AI Instructions Drift Check

At every staging→current gate:

1. Scan `AGENTS.md` and `CLAUDE.md` for any claim that looks like original content rather than a cross-reference.
1. If found, write the full version in the appropriate canonical doc, then replace the AI instruction with a condensed cross-reference.
1. Verify every "See `docs/X.md`" reference resolves to an existing file and section.

## 6. Encoding Policy

### 6.1 Mandate

All source files (`.py`, `.md`, `.yaml`, `.json`, `.toml`, `.cfg`) **must be UTF-8**. No exceptions unless explicitly documented.

### 6.2 Declarations

Every file that supports encoding declarations must declare it at the very beginning:

| Format | Declaration | Position |
|--------|-------------|----------|
| `.py` | `# -*- coding: utf-8 -*-` | Line 1 (before SPDX header) |
| `.md` | `<!-- encoding: utf-8 -->` | Line 2 (after H1 title, before content) |
| Others | Format doesn't support inline declaration | Exception documented here |

For `.md` files without an H1 title (e.g., vendor stubs starting with `___` separators), insert on line 1.

### 6.3 PowerShell Encoding Workaround

On Windows, PowerShell `Set-Content` and `Out-File` default to the system's active ANSI code page (Windows-1252 on en-US Windows), not UTF-8. This corrupts any file containing non-ASCII bytes when the file is expected to be UTF-8.

```powershell
# Correct — writes UTF-8 without BOM
[System.IO.File]::WriteAllText($path, $content, [System.Text.UTF8Encoding]::new($false))

# Correct — reads UTF-8
[System.IO.File]::ReadAllText($path, [System.Text.Encoding]::UTF8)

# Correct — writes bytes as UTF-8
[System.IO.File]::WriteAllBytes($path, [System.Text.Encoding]::UTF8.GetBytes($content))
```

This applies to any operation that writes `.py`, `.md`, `.yaml`, `.json`, `.toml`, or `.cfg` files. See `.skills/encoding-audit/README.md` for detection scripts, git recovery workflow, and fix patterns.

### 6.4 Verification

```bash
# Count Python files with encoding declaration
Get-ChildItem -Recurse -Include "*.py" | Select-String -Pattern "^# -\*- coding: utf-8 -\*-" | Measure-Object

# Count markdown files with encoding declaration
Get-ChildItem -Recurse -Include "*.md" | Select-String -Pattern "encoding: utf-8" | Measure-Object
```

### 6.5 Recovery

If the working tree is corrupted by encoding bugs, use `git checkout <clean-sha> -- <file>` to restore from the last clean commit. See `.skills/encoding-audit/README.md §git recovery safety net` for details.

## 7. Formatting Rules

### 7.1 mdformat

All `.md` files are formatted via `mdformat` with explicit paths:

```bash
uv run mdformat docs/ AGENTS.md CLAUDE.md README.md TODO.md .skills/ .opencode/commands/ .claude/ .agents/
```

Root-level `.md` files are listed explicitly. Each has a reason to live at root: `AGENTS.md` (AI instructions), `CLAUDE.md` (Claude config), `README.md` (project entry point), `TODO.md` (task tracking). All other documentation belongs under `docs/`. Adding a new root-level `.md` requires a documented justification — if it belongs to a category, put it in the appropriate subdirectory instead.

- **CI runs `mdformat --check`** with the same explicit paths.
- **Pre-commit hook** uses the same paths as CI — `pass_filenames: false` ensures all files are checked, not just staged ones.
- **Windows vs Linux parity**: CI uses Linux which formats markdown differently (LF vs CRLF). Always run `mdformat` (not just `--check`) before committing to ensure files are in CI-compatible format.

### 7.2 CI mdformat Failure Diagnosis

When CI reports `mdformat --check` failure and the filename is truncated in logs:

```powershell
gh run view <run-id> --log | Select-String -Pattern "not formatted" -Context 0,1
```

Or get the run ID dynamically:

```powershell
$id = gh run list --branch staging --limit 1 --json databaseId --jq ".[0].databaseId"
gh run view $id --log | Select-String -Pattern "not formatted" -Context 0,1
```

## 8. Integrity Checks

Run during staging→current gate and during retrospectives.

### 8.1 Gate Checklist

| # | Check | How | When |
|---|-------|-----|------|
| 1 | All `.md` have H1 → aim → scope | Verify every `docs/*.md` has a line starting with "Covers:" | Every gate |
| 2 | No hardcoded step numbers in process docs | `grep -nP '^\s+\d+\.' docs/DEVELOPMENT_PROCESS.md docs/GIT_FLOW.md` — flag any that aren't in numbered lists; replace with section-title references | Every gate |
| 3 | No broken skill paths | Every entry in `CLAUDE.md` skills table must point to an existing `.skills/<name>/README.md` | Every gate |
| 4 | No TODO.md stale items | Scan TODO.md for entries whose description starts with past-tense verb ("Fixed", "Added", "Created") — likely completed but not removed | Every retro |
| 5 | All cross-references resolve | For every `see docs/X.md` pattern in committed `.md` files — verify `docs/X.md` exists | Every retro |
| 6 | Every doc has encoding declaration | Count `encoding: utf-8` occurrences vs file count under `docs/` and root `.md` files | Every gate |
| 7 | No path reference rot | Every vendor stub `SKILL.md` must reference an existing canonical path in `.skills/` | Every retro |
| 8 | No cross-doc duplication | Same rule or fact appearing in 2+ non-trivial docs. Exempt: `AGENTS.md`, `CLAUDE.md`, `README.md` — these are intentional summary extracts | Every 5 merges |
| 9 | No config duplication | Rule described in doc AND enforced by `.pre-commit-config.yaml`, CI workflow, `.gitignore`, or `pyproject.toml` — remove from doc, cross-reference the config | Every retro |
| 10 | No self-evident rules | Rule describes standard developer practice (e.g., "never commit to main") — delete, or keep as a retrospective entry if someone actually violated it | Every retro |
| 11 | No structural anomalies in heavily-edited files | Before editing a section-heavy file, `grep -c '^## '` to detect duplicate headings or stale sections | Every bulk edit |
| 12 | Renumbering map validated | Before section renumbering, write the mapping and validate against `grep '^## '` output | Before renumbering |

### 8.2 Check Automation Status

These checks are currently manual (layer 3 — documented, manually enforced). Future automation candidates:

| Check | Could Be Automated As | Currently |
|-------|----------------------|-----------|
| #1 H1 → aim → scope | Custom pre-commit hook (Python script) | Manual |
| #3 Broken skill paths | Custom pre-commit hook (validate paths exist) | Manual |
| #4 Stale TODO | Custom pre-commit hook (grep past-tense verbs) | Manual |
| #5 Cross-refs resolve | Custom pre-commit hook (verify `see docs/X.md` links) | Manual |
| #6 Encoding declarations | CI step counting declarations vs file count | Manual |

## 9. Anti-Patterns

Recurring failures identified through retrospective analysis. Each anti-pattern has a corresponding guard to prevent recurrence.

| Anti-pattern | Example from retros | Guard |
|-------------|--------------------|-------|
| **Scope collision** | Created `doc/` when `docs/` already existed — 8 duplicate files, 60+ stale cross-references | Pre-creation directory audit (§3.3) |
| **Stale references** | README and cross-references still pointed to `doc/` after rename to `docs/` | Cross-reference scan at every gate (§8.1 #5) |
| **Facts in AI instructions** | GPG signoff rule duplicated across 4 files (GIT_FLOW.md, TOOLING.md, .tooling.md, CLAUDE.md) instead of one canonical source | Canonical source discipline (§5) |
| **Step-number drift** | OPENSE_CONFIG.md used hardcoded 1-9 which broke when sections were reordered | Flag hardcoded step numbers (§8.1 #2) |
| **Completed items as open** | "Fixed P0 bug" still listed in TODO.md as open task | Past-tense detection in TODO.md (§8.1 #4) |
| **Path reference rot** | Retrospective-analysis skill pointed to `.skills/retrospective-analysis/README.md` which did not exist | Pre-commit or gate check for path existence (§8.1 #3) |
| **Over-engineering** | Creating skills/docs for problems that don't exist yet — appeared in 3 consecutive retros | "Check existing first" guard in planning phase (docs/DEVELOPMENT_PROCESS.md §0.5) |
| **Code-only fixes** | Windows SQLite URI fix applied to conftest.py but never documented as a quirk — rediscovered in next session | Retro §5d: extract reusable techniques (`.skills/retrospective-analysis/README.md §5d`) |
