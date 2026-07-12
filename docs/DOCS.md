# Docs Management

<!-- encoding: utf-8 -->

Meta-documentation for the SE Site project: how, why, and where we document things. The canonical source for all doc-related conventions, policies, and checks.

Covers: doc creation rules, update rules, canonical source discipline, encoding policy, formatting conventions, integrity checks, document catalog, and recurring anti-patterns. Does not cover: general development process — see `docs/DEVELOPMENT_PROCESS.md`, git workflow — see `docs/GIT_FLOW.md`, tool-specific knowledge — see `docs/TOOLING.md`, technology decisions — see `docs/DESIGN_DECISIONS.md`.

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
| `.tooling.md` | Local quirks | GPG keylocker, host-specific workarounds | Cross-platform knowledge | Local-only workarounds |
| `TODO.md` | Tasks | Backlog, known bugs, coverage | Process improvement ideas | Task tracking |

### docs/ directory

| File | Scope | Covers | Does Not Cover | Canonical For |
|------|-------|--------|----------------|---------------|
| `DOCS.md` | Doc management | (this file) | (everything else) | Doc conventions, checks, catalog |
| `DEVELOPMENT_PROCESS.md` | Process | Planning, testing, linting, code review, release, deps, session lifecycle | CLI, architecture, AI tooling, git | Process workflow, session lifecycle |
| `GIT_FLOW.md` | Git | Branching, merge strategy, commit discipline, signoff, versioning | Planning, testing, process | Git workflow |
| `RETROSPECTIVES.md` | History | Retrospective entries from prior sessions | Git workflow, development process | Process gap history |
| `ARCHITECTURE.md` | Code design | Module map, data flow, conventions | Technology choices, schema | Module responsibilities, design rationale |
| `API_REFERENCE.md` | Routes | All endpoints, methods, view functions | Models, architecture | Route registry |
| `SCHEMA.md` | Database | Tables, fields, relationships | Endpoints, architecture | DB schema |
| `REQUIREMENTS.md` | Features | Feature specs, user roles, navigation | Implementation, schema | Feature definition |
| `TESTING.md` | Testing | Discipline, targets, xfail policy, long-term gaps | Fixture patterns, methodology | Testing strategy |
| `TOOLING.md` | Tools | Portable tooling knowledge | Local quirks, project errors | Cross-platform tool patterns |
| `CODE_ISSUES.md` | Bugs | Known production bugs | Process gaps | Bug inventory |
| `REPO_REVIEW.md` | Audit | Health checklist | — | Repo health audit |
| `REVERSE_ENGINEERING.md` | RE | Re-engineering cycle | Dev workflow, testing | RE methodology |
| `AI_AGENTS.md` | AI config | AI tooling config, permissions, output format conventions, skills architecture and catalog | Process, git | AI tool setup |
| `QUALITY_MANAGEMENT.md` | Quality | Quality philosophy, tiers motivation, agent protocol reasoning, CI discipline motivation, artifact catalog | Tool configs, agent instructions, testing discipline | Quality policy |
| `DESIGN_DECISIONS.md` | Decisions | Technology choices, framework-specific decisions, implementation patterns | Architecture, testing | Framework/tech decisions |
| `AI_AGENT_EXPERIENCE.md` | Experience | Dead ends, debugging trails, agent-specific tool limitations | Process, config, tooling | Agent-collected experience |

### Skills directory (.skills/)

For skills catalog, vendor stubs, and commands, see `docs/AI_AGENTS.md` §Skills.

## 2a. Document Disciplines

Each doc has a knowledge discipline — what goes in, what stays out, how information is structured. This section serves as the template for recreating any doc from scratch when only `DEVELOPMENT_PROCESS.md` is available.

### Root docs

| Doc | Discipline | Typical sections | Section anatomy | Recovery if missing |
|-----|-----------|-----------------|-----------------|---------------------|
| `AGENTS.md` | Commands + pre-flight + quirks — actionable agent instructions only | Pre-flight checklist, Before committing, Testing quirks, Environment quirks | Bullet lists of if-then rules; code blocks for commands | Extract from relevant `docs/` — each line must cross-reference a canonical source |
| `CLAUDE.md` | Skill registry — which skills exist, when to load them | Skills table | Table: name, "load when" description | Rebuild from `.skills/*/README.md` headings |
| `TODO.md` | Task tracking — backlog, bugs, coverage | Batch notes, Planned (table), Blocked (table), Module Coverage (table), Known bugs | Tables with priority/effort/depends-on columns | Restore from `docs/RETROSPECTIVES.md` state-at-handoff sections |

### docs/ directory

| Doc | Discipline | Typical sections | Section anatomy | Recovery if missing |
|-----|-----------|-----------------|-----------------|---------------------|
| `DOCS.md` | Meta — doc conventions, checks, catalog | §1-9 numbered (Why We Document, Catalog, §2a Disciplines, Creation, Update, Canonical Sources, Encoding, Formatting, Integrity, Anti-Patterns) | Self-describing — defines its own patterns | Rebuild from `docs/DEVELOPMENT_PROCESS.md` §Context Compaction and §Doc-first cycle |
| `DEVELOPMENT_PROCESS.md` | Process workflow — planning, session lifecycle, code review, disciplines | §0.x workflow steps, §1-6 major areas | §0.x: numbered planning steps. Other §: Why→What→How per section with command blocks | **Cannot be rebuilt** — user-designated exception, all other docs cross-reference here |
| `GIT_FLOW.md` | Git — branching, merge, commit, signoff, versioning | §1-8 numbered (Branching, Merge Strategy, Commit, Signoff, Rebase, Stale Branches, Versioning, GitHub) | Heading → **Why** (italicized) → **What** (table/rules) → **How** (command blocks) | Rebuild from `docs/DEVELOPMENT_PROCESS.md` §Version Control cross-reference + `.gitignore` + `.pre-commit-config.yaml` |
| `RETROSPECTIVES.md` | Process gap history — chronological entries | Dated H3 entries per session | Consistent template: Changes analyzed, Gaps found (table), Pattern recurrence, What went well, What went wrong, Root causes, Fix, State at handoff | Rebuild from `git log` and session notes — but Gap table detail is unrecoverable |
| `ARCHITECTURE.md` | Code design — module map, data flow, conventions | Module map, Data flow, Conventions | Module map: table of module→responsibility. | Rebuild from source code via reverse-engineering |
| `DESIGN_DECISIONS.md` | Tech decisions — framework/technology choices | Per-decision dated entries | Decision: date→context→decision→rationale→consequences→alternatives | Rebuild from `docs/ARCHITECTURE.md` Design Decisions (moved session 9) |
| `AI_AGENT_EXPERIENCE.md` | Agent experience — debugging trails, dead ends, workarounds | Per-symptom H2 sections | Symptom→Attempts→Root cause→Fix table with commands | Recovery from `docs/AI_AGENTS.md` + retro entries |
| `API_REFERENCE.md` | Routes — all endpoints, methods, view functions | Grouped by feature area (News, Theses, Practice, etc.) | Table: route, methods, params, returns, auth requirement | Rebuild from source code (`flask_se_*.py` route decorators) |
| `SCHEMA.md` | Database — tables, fields, relationships | Grouped by model area | Table: column, type, constraints, FK target, notes | Rebuild from `se_models.py` SQLAlchemy definitions |
| `REQUIREMENTS.md` | Feature specs — user roles, navigation, feature descriptions | Per-feature sections | User story → acceptance criteria → notes | Rebuild from templates + user interviews |
| `TESTING.md` | Testing strategy — discipline, targets, xfail policy, gaps | §1-6 numbered (Discipline, Coverage Targets, Execution, xfail, Gaps, Exclusions) | Tables for targets/xfails/gaps. § follows Why→What→How | Rebuild from `conftest.py`, test files, `pyproject.toml` coverage config |
| `TOOLING.md` | Portable tooling knowledge — cross-platform quirks per tool | Tool-name H2 sections (uv, pytest, SQLAlchemy, pre-commit, GitHub CLI, PowerShell, Python, Ruff, etc.) | Tool section: heading → "correct/wrong" code blocks with explanation. No process rules, only mechanics | Rebuild from `.pre-commit-config.yaml`, `pyproject.toml`, CI workflow files |
| `CODE_ISSUES.md` | Bug inventory — known production bugs | Per-module H2 sections | Table: bug, module, impact, status | Rebuild from `TODO.md` Known bugs + retro entries |
| `REPO_REVIEW.md` | Audit checklist — repo health evaluation | Numbered phases (Legal, Architecture, Code Quality, etc.) | Phase: checklist items with status column | Rebuild from GitHub repo settings + `.github/` + CI workflows |
| `REVERSE_ENGINEERING.md` | RE methodology — cycle description, source types | Cycle steps, Source types | Methodology description: steps numbered, types in tables | Rebuild from `.skills/js-bundle-analysis/README.md` patterns |
| `AI_AGENTS.md` | AI-agent-specific — permissions, tool quirks, cross-references, output format conventions, skills architecture, skills catalog, commands | Permission Recommendation, Tool Quirks, Output Format, Communication, Skills (definition, boundaries, delegation, source of truth, extraction triggers, creation, lifecycle, maintenance, directory, vendor stubs, commands) | Permissions: JSON block. Tool Quirks: per-quirk ### subsections with wrong/correct examples. Output Format: compliance rules, timing, prescribed formats. Communication: ask-when-ambiguous rule. Skills: definition, boundaries, delegation chain, source of truth, extraction triggers, creation checklist, lifecycle, maintenance, directory table, vendor stubs, commands | Rebuild from `.opencode/opencode.json` + tool behavior observation |

## 2b. Skills Architecture (moved to `docs/AI_AGENTS.md` §Skills)

For skills architecture — definition, delegation chain, extraction triggers, creation checklist, and lifecycle — see `docs/AI_AGENTS.md` §Skills.

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
- **Exception**: new findings during implementation (bugs, quirks, workarounds) go to `TOOLING.md` or `AI_AGENT_EXPERIENCE.md` immediately, not at session end. See "Document as you go" in `docs/AI_AGENTS.md` §Skills (`.skills/unattended-mode/`).

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

See `docs/TOOLING.md` §PowerShell encoding for the correct `[System.IO.File]::WriteAllText` pattern and the `$(...)` subexpression trap.

This applies to any operation that writes `.py`, `.md`, `.yaml`, `.json`, `.toml`, or `.cfg` files. For detection scripts, git recovery workflow, and fix patterns, see `docs/AI_AGENTS.md` §Skills (`.skills/encoding-audit/`).

### 6.4 Verification

```bash
# Count Python files with encoding declaration
Get-ChildItem -Recurse -Include "*.py" | Select-String -Pattern "^# -\*- coding: utf-8 -\*-" | Measure-Object

# Count markdown files with encoding declaration
Get-ChildItem -Recurse -Include "*.md" | Select-String -Pattern "encoding: utf-8" | Measure-Object
```

### 6.5 Recovery

If the working tree is corrupted by encoding bugs, use `git checkout <clean-sha> -- <file>` to restore from the last clean commit. For recovery workflows, see `docs/AI_AGENTS.md` §Skills (`.skills/encoding-audit/`).

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
| 13 | Stale metrics | Hardcoded test count, coverage %, file counts — verify against `pytest`, `coverage`, or `ls` | Every gate |
| 14 | Expired guardrails | Conditional constraints ("do X until Y") — verify condition Y is not yet met. If met, remove the guardrail. | Every retro |
| 15 | Bug status freshness | Verify OPEN/FIXED/PENDING markers in `CODE_ISSUES.md` and `TODO.md` against actual codebase state | Every retro |
| 16 | Doc table freshness | Any table enumerating project files, docs, or modules — item count matches reality on disk | Every gate |
| 17 | Content-scope alignment | For each changed `.md` file, verify no section violates the doc's stated "Covers"/"Does not cover" boundary | Every gate |
| 18 | No UTF-8 BOM | No `EF BB BF` byte order mark in any source file — CI catches this, verify locally before push | Every gate |

### 8.2 Check Automation Status

These checks are currently manual (layer 3 — documented, manually enforced). Future automation candidates:

| Check | Could Be Automated As | Currently |
|-------|----------------------|-----------|
| #1 H1 → aim → scope | Custom pre-commit hook (Python script) | Manual |
| #3 Broken skill paths | Custom pre-commit hook (validate paths exist) | Manual |
| #4 Stale TODO | Custom pre-commit hook (grep past-tense verbs) | Manual |
| #5 Cross-refs resolve | Custom pre-commit hook (verify `see docs/X.md` links) | Manual |
| #6 Encoding declarations | CI step counting declarations vs file count | Manual |
| #13 Stale metrics | CI step verifying test count/coverage against committed values | Manual |
| #18 UTF-8 BOM check | Pre-commit hook (`file --mime-encoding` check) | Manual |

## 9. Anti-Patterns

Recurring failures identified through retrospective analysis. Each anti-pattern has a corresponding guard to prevent recurrence.

| Anti-pattern | Example from retros | Guard |
|-------------|--------------------|-------|
| **Scope collision** | Created `doc/` when `docs/` already existed — 8 duplicate files, 60+ stale cross-references | Pre-creation directory audit (§3.3) |
| **Stale references** | README and cross-references still pointed to `doc/` after rename to `docs/` | Cross-reference scan at every gate (§8.1 #5) |
| **Facts in AI instructions** | GPG signoff rule duplicated across 4 files (GIT_FLOW.md, TOOLING.md, .tooling.md, CLAUDE.md) instead of one canonical source | Canonical source discipline (§5) |
| **Step-number drift** | AI_AGENTS.md used hardcoded 1-9 which broke when sections were reordered | Flag hardcoded step numbers (§8.1 #2) |
| **Completed items as open** | "Fixed P0 bug" still listed in TODO.md as open task | Past-tense detection in TODO.md (§8.1 #4) |
| **Path reference rot** | Retrospective-analysis skill pointed to `.skills/retrospective-analysis/README.md` which did not exist | Pre-commit or gate check for path existence (§8.1 #3) |
| **Over-engineering** | Creating skills/docs for problems that don't exist yet — appeared in 3 consecutive retros | "Check existing first" guard in planning phase (docs/DEVELOPMENT_PROCESS.md §0.5) |
| **Code-only fixes** | Windows SQLite URI fix applied to conftest.py but never documented as a quirk — rediscovered in next session | Retro §5d: extract reusable techniques (`.skills/retrospective-analysis/README.md §5d`) |

## 10. SPDX / Licensing Policy

Every source file must have an SPDX header matching the project's `LICENSE` file.

**Format**:

- Python (`.py`): `# SPDX-License-Identifier: Apache-2.0`
- Markdown (`.md`): `<!-- SPDX-License-Identifier: Apache-2.0 -->`
- Config files: inline comment format appropriate to the file type

**Audit checks** (run during code-audit):

- Every new or modified source file has an SPDX header
- If `LICENSE` is missing from the repo, flag it
- If multiple licenses exist, document coverage per directory
