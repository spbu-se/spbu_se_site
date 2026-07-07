# retrospective-analysis

<!-- encoding: utf-8 -->

Analyze a session or merge to identify process gaps, classify root causes, and suggest improvements.

## When to load

- After every merge to current (see `docs/GIT_FLOW.md` §2 — Merge staging → current)
- At session end, during context compaction (see `docs/DEVELOPMENT_PROCESS.md §0.6` — Context compaction)
- When the user says "retrospective" or "lessons learned"
- When a bug or mistake reveals a process gap

## Workflow

### 1. Collect changes

```bash
git log --oneline --since="<last-merge-or-session-start>"
```

List all files touched and categorize: source code, tests, docs, config, tooling.

### 2. Trace provenance per change

For each change, ask:

| Question | If yes в†’ |
| ---------------------------------------------- | -------------------------------------------------------- |
| Was this planned (pro-active)? | No fix needed вЂ” record as completed work |
| Was this re-active (fixing something missing)? | **Classify the gap** (next step) |
| Was this a user request? | Record as completed work |
| Could this rule have been automated? | It was left at doc-only вЂ” **classify as missing config** |
| Was knowledge imported from another project? | **Check for cross-project leaks** вЂ” verify no private references, proprietary names, or source-repo mentions leaked into docs. Document adaptation decisions. |

### 3. Classify the gap

| Gap type | Root cause | Fix action | Also check skill? |
| ---------------------- | ------------------------------------------ | ---------------------------------------------------- | ------------------------------- |
| **Missing convention** | No rule described how to do this | Add rule to `docs/DEVELOPMENT_PROCESS.md` | Could this be a `.skills/` workflow? |
| **Missing template** | No template existed for this artifact type | Add template or checklist (e.g., §0.7) | Could this be a skill README? |
| **Missing config** | Toolchain didn't catch this | Add linter, pre-commit hook, CI step | No — tool config, not skill |
| **Human error** | Process was documented but not followed | Add guardrail or automation | Could a skill have prevented this? |
| **Pattern recurrence** | Same gap appeared in a previous retro | Previous fix was insufficient — revisit and escalate | Was the skill updated last time? |
| **Value contradiction** | Practice contradicts a Strategic Priority from the Project Doctrine (see `docs/DEVELOPMENT_PROCESS.md` §Process Identity → Project Doctrine) | Flag to user — do NOT fix autonomously. The user decides whether to adjust the value or change the practice. | No — values are user-domain |

### 4. Check for pattern recurrence

Scan previous retrospective entries in the relevant target document (see В§5a). If this gap or a similar one was already fixed, the fix was incomplete вЂ” propose a stronger solution.

### 5. Classify target document

All retrospective entries go to `docs/RETROSPECTIVES.md`. Depending on the gap's area, the entry may also cross-reference:

| Gap category | Also update |
| ----------------------------------------------------------------- | ------------------------------------------- |
| Git flow, branching, commits, staging, guardrails, hotfixes | `docs/GIT_FLOW.md` if a git rule changed |
| Planning, TDD, testing, types, release, dependencies, conventions | `docs/DEVELOPMENT_PROCESS.md` if a process rule changed |
| Tooling, environment, PowerShell, local config, platform quirks | `.tooling.md` (mistake journal) |
| Doc management, cross-references, encoding policy | `docs/DOCS.md` if a doc rule changed |

If gaps span multiple categories, split across entries within `docs/RETROSPECTIVES.md`.

### 5b. Audit doc health

Scan the session's changed docs for signal patterns:

| Pattern | How to detect | Action |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------- |
| **Config duplication** | Rule is described in doc AND enforced by `.pre-commit-config.yaml`, `.github/workflows/ci.yml`, `.gitignore`, `pyproject.toml`, or `dprint.json` | Remove from doc. Cross-reference the config file. |
| **Cross-doc duplication** | Same rule appears in 2+ non-trivial docs (e.g., `GIT_FLOW.md` + `DEVELOPMENT_PROCESS.md`). **Exempt from cross-doc duplication only**: `README.md` (user-facing, different audience). `AGENTS.md` and `CLAUDE.md` are NOT exempt — see the AI-instruction-file bloat pattern below. | Keep in one canonical doc. Replace others with cross-reference (`See X.md §Y`). |
| **Self-evident rule** | Rule describes standard git/developer practice (e.g., "never commit to main", "stash before branching") | Delete. If the rule was added because someone violated it, keep as a retrospective entry instead. |
| **Directory collision** | New directory was created during the session — check if a similarly-named directory already exists (e.g., `ls docs/` before creating `doc/`) | Merge unique content, delete duplicate directory. Add pre-creation audit check to the relevant skill. |
| **AI instruction file bloat** | AGENTS.md or CLAUDE.md content duplicates a canonical doc or, for CLAUDE.md, duplicates/expands content that AGENTS.md already covers. Hierarchy: CLAUDE.md → AGENTS.md → docs/. Each layer delegates down, never down-copies. | Delete from the instruction file. Replace with a one-line cross-reference to the lower layer. |

Signal strength: high-confidence finds are config-duplicates (the config IS the truth). Low-confidence are self-evident rules (may be project-specific вЂ” ask if unsure).

**Pre-commit vs CI parity** вЂ” verify every check that runs in CI also runs locally via pre-commit hooks. If CI catches something that pre-commit doesn't flag, either add a pre-commit hook or document the gap (and accept that CI will catch it).

**SPDX/licensing audit** вЂ” verify every new or modified source file has an SPDX header matching the repo's LICENSE file. If LICENSE is missing, flag it. If multiple licenses exist, document coverage per directory.

### 5c. Improve skills used during the session

Identify which `.skills/<name>/README.md` were loaded during the analyzed session. For each:

- Did the session reveal a gap or improvement in the skill's workflow?
- Does the skill reference tooling patterns that changed during the session?
- Should a "Lessons Learned" section or updated step be added?

If yes, update the skill README immediately as part of the retrospective commit.

### 5d. Extract reusable techniques

Scan the session for patterns, code snippets, and workarounds that are:

- Not already documented in `docs/TROUBLESHOOTING.md` or `docs/TOOLING.md`
- Likely to be needed again (e.g., patching patterns, fixture setups, encoding workarounds)
- Discovered as a fix for a bug or a workaround for a module-level side effect

For each, add an entry to the appropriate doc with the exact code or command. Do not bury techniques in the retrospective entry — they must be searchable independently.

Examples of what to extract:

- `contextlib.suppress(RuntimeError)` for catching double `db.init_app()` — in `TROUBLESHOOTING.md`
- `try/finally` for restoring module-level flags like `thesesImport.download` — in `TROUBLESHOOTING.md`
- `[System.IO.File]::WriteAllText()` for PowerShell UTF-8 encoding — in `TOOLING.md`

**Check after extraction**: If a future session encounters the same problem, would a `grep` or `TROUBLESHOOTING.md` search find the fix? If not, improve the entry's discoverability (better section title, more keywords, cross-reference from related docs).

### 6. Suggest improvements

Present findings in a structured table:

| Change | Trigger | Root gap | Fix |
| ------------------------- | ------------- | ------------------- | -------------------- |
| `docs/XXX.md` | User request | Missing template | Added В§0.7 checklist |
| `.pre-commit-config.yaml` | Retro finding | No formatting guard | Added mdformat hook |

Include concrete file paths and exact changes needed.

### 7. Store lessons

Append a structured retrospective entry to `docs/RETROSPECTIVES.md`.
**Every classified gap must have a corresponding retrospective entry** — even if the fix was already applied directly (code changes, doc updates, config changes). The entry records why the gap existed, not just what was done about it.

If no existing heading matches, create a new one: `### Retrospective — <title>` in `docs/RETROSPECTIVES.md`. Also update the mistake journal table in `.tooling.md` if the gap is tooling-related:

```markdown
### Retrospective вЂ” <title>

<Brief description of what happened>

**What went wrong**: <root cause analysis>
**Root cause**: <gap type>
**Fix**: <what was done to prevent recurrence>
```

### 8. Self-improve retrospective

The retrospective itself is a tool. Every time it runs, check if it revealed a gap in the retrospective process:

- Was any classification ambiguous? (Step 3)
- Was the target document unclear? (Step 5a)
- Did the session include user corrections that the retrospective should track? (e.g., "do X instead of Y" — classify as **task ambiguity** or **over-engineering**)
- Was a skill used during the session that should be updated? (Step 5c) — did that actually happen?
- **Did I load any skills during this session?** If not, list which relevant skills were available (`test-writer`, `retrospective-analysis`, `unattended-mode`, etc.) and why they weren't loaded. This surfaces "custom is faster" bias.
- **Did the retrospective itself violate any process rules?** (creating standalone files instead of appending, skipping skill loading, committing without testing, etc.) The retrospective must model the behavior it enforces.

#### 8a. Session efficiency audit

Ask these questions to surface waste and optimization opportunities:

| Question | What it catches |
|----------|----------------|
| Did any single mistake propagate across multiple files? | Missing validation step before commit — should have run the breaking command earlier |
| Did I edit the same logical change in more than 3 files by hand? | Should have been a single grep/replace or a script |
| Did I discover a structural issue mid-edit that should have been caught pre-edit? | Missing pre-flight scan (duplicate sections, stale refs, renumbering gaps) |
| Was there a long feedback loop between writing and validating? | Could have validated incrementally instead of batch-writing everything first |
| Did `git diff --stat` show unexpected files changed? | Formatting noise or unintended edits hiding real changes |
| **Did practice conflict with a Strategic Priority in the Project Doctrine?** | E.g., a rule we said was "low-effort" turned out high-effort in this context. Classify as **value contradiction** in step 3 — flag to user, do not fix autonomously. |
| Did AGENTS.md grow 4+ lines vs branch point? | `git diff --stat origin/staging...HEAD AGENTS.md` — if +4+, run step 5b AI-instruction-file bloat audit |
| Did CLAUDE.md grow vs branch point? | Any new line in CLAUDE.md is suspicious — must delegate to AGENTS.md, never expand |
| Is this a docs/ branch finalization? | Mandatory — run step 5b bloat audit on both AGENTS.md and CLAUDE.md regardless of delta |

#### 8b. Generate prevention rules

For every "yes" in §8a, write a concrete prevention rule in the appropriate canonical doc. Examples:

- "Before staging after bulk doc edits, run `uv run mdformat` with the exact CI command string" → `docs/DEVELOPMENT_PROCESS.md §0.6`
- "Before editing a section-heavy file, `grep -c '^## '` to detect structural anomalies" → `docs/DOCS.md §8.1`
- "For section renumbering, write the mapping and validate against `grep '^## '` before editing" → `docs/DOCS.md §8.1`
- "Before merge or batch finalization: diff AGENTS.md (+4 guard) and CLAUDE.md (any growth) line count against branch point. Run AI-instruction-file bloat audit. CLAUDE.md must delegate, not duplicate." → `docs/DOCS.md §7.1`

Append an entry to the `## Self-improvement log` for each new prevention rule generated.

## Self-improvement log

### [2026-07-04] Add step 8 вЂ” self-improve retrospective

The retrospective analyzed every process and skill but had no mechanism to improve itself. Added step 8 and this log.

### [2026-07-04] Add "user correction" pattern to classification

The user redirected output 3 times in one session (test SLOC, doc split, unattended mode rules). The root cause was over-engineering (solving completeness over practicality). Added to unattended-mode skill principles and retrospective step 3 classification.

### [2026-07-04] Add cross-project knowledge transfer + SPDX audit steps

Session extracted process ideas from another private repo. Agent accidentally referenced the source repo by name in docs. Also discovered 60 Python files with no SPDX headers despite LICENSE existing. Added cross-project leak check to step 2 and SPDX/licensing audit to step 5b.

### [2026-07-04] Add pre-commit vs CI parity check

CI repeatedly caught `mdformat` issues that pre-commit didn't flag. Root cause: pre-commit only checked STAGED files (`pass_filenames: true`), CI checked ALL files (`mdformat --check .`). This gap affected 3 different push attempts. Added "Pre-commit vs CI parity" check to step 5b. Pre-commit hook fixed with `pass_filenames: false` so mdformat now checks all markdown files on every commit.

### [2026-07-06] Add skill-loading and process-violation self-checks

The 2026-07-06 retrospective revealed two gaps in the retrospective process itself:

1. "Custom is faster" bias — relevant skills (`retrospective-analysis`, `test-writer`, `unattended-mode`) existed but were not loaded during the session. The retro never asked "did you load skills?"
1. The retro itself violated process rules — created standalone `docs/RETROSPECTIVE_*.md` instead of appending to `GIT_FLOW.md` §9. The retro had no self-check for rule compliance.

**Fix**: Added two new questions to step 8: "Did I load any skills?" and "Did the retrospective itself violate any process rules?" This creates a feedback loop for the retro process itself.

### [2026-07-07] Add session efficiency audit (step 8a-8b)

Session restructuring GIT_FLOW.md and creating TESTING.md revealed several efficiency patterns:

- Path mistake (`TESTING.md` vs `docs/TESTING.md`) propagated across 6 files — no early validation
- Duplicate `## pre-commit` section in TOOLING.md caused 3+ failed edit attempts — no pre-flight structural scan
- Section renumbering required fixing AGENTS.md cross-refs retroactively — no renumbering map written first

**Fix**: Added step 8a (session efficiency audit — 5 questions) and step 8b (generate prevention rules in canonical docs). Added prevention rules to DOCS.md §8.1 (pre-flight structural scan, renumbering map) and DEVELOPMENT_PROCESS.md §0.6 (pre-staging validation step).

### [2026-07-06] Add step 5d — extract reusable techniques

This batch session discovered the `contextlib.suppress(RuntimeError)` pattern for patching
`db.init_app`, the `try/finally` pattern for restoring module-level flags, and 5 production
bugs in `thesesImport.py`. None of these were extracted to searchable docs during the
retrospective — they were only mentioned in the retro entry. The user pointed out the gap
after the retro was finalized.

**Fix**: Added step 5d "Extract reusable techniques" — scans the session for code patterns,
workarounds, and fixes, and ensures they land in `TROUBLESHOOTING.md` or `TOOLING.md`
with discoverable section titles and keywords.

### [2026-07-07] Add directory-collision pattern to step 5b

Session created `doc/` directory while `docs/` already existed — 8 duplicate documentation
files, 60+ cross-references to update, CI only checked `docs/`. Root cause: no pre-creation
directory audit in any process step.

**Fix**: Added "Directory collision" as a new signal pattern in step 5b table. Also changed
the section header from "three signal patterns" to "signal patterns" (no count, may grow).

### [2026-07-07] Add value contradiction gap type and self-check question

The user pointed out that retrospections can challenge documented values, not just mechanics. Practice may reveal that a stated value (e.g., "low-effort") is impractical in a specific context, but the retro had no way to flag this.

**Fix**: Added "Value contradiction" as a new gap type in step 3 — explicitly flagged as user-domain, never fixed autonomously. Added "Did practice conflict with a documented value?" to the step 8a efficiency audit.

### [2026-07-07] Add AI instruction file bloat detection

Session compacted AGENTS.md from 89→57 lines. Established delegation
chain: CLAUDE.md → AGENTS.md → docs/. Each layer delegates down, never
copies up.

**Fix**: Added AI-instruction-file bloat pattern to step 5b (covers both
directions: AGENTS.md duplicating docs/, CLAUDE.md duplicating AGENTS.md).
Per-session cumulative guard (+4 for AGENTS.md, any growth for CLAUDE.md)
and docs/ branch mandatory check in step 8a. Changed exemption: AGENTS.md
and CLAUDE.md no longer exempt from bloat detection (only README.md
retains cross-doc duplication exemption). AGENTS.md header now
self-enforces brevity and the delegation chain.

### [2026-07-07] Replace inline values with Project Doctrine cross-reference

Session replaced scattered implicit values (clean history, robust, low-effort, zero-bugs) with a canonical four-layer Project Doctrine in DEVELOPMENT_PROCESS.md. Retro skill value-contradiction check now references the Doctrine instead of free-text examples.

**Fix**: Step 3 and step 8a value-contradiction references now point to `docs/DEVELOPMENT_PROCESS.md` §Process Identity → Project Doctrine. No more duplicate value definitions.

## Output template

At the end, produce:

```
## Retrospective Summary

Changes analyzed: <N>
Gaps found: <M>
- <gap 1> в†’ <fix>
- <gap 2> в†’ <fix>
No action needed: <planned changes, user requests>

Pattern recurrence: <yes/no вЂ” if yes, escalate>
```

## Dependencies

- `git` — to inspect commit history
- Read access to `docs/RETROSPECTIVES.md` — to check previous retros
- Read access to `docs/GIT_FLOW.md` — to check git rules
- Read access to `docs/DEVELOPMENT_PROCESS.md` — to check process rules
- Read access to `.tooling.md` — to check mistake journal
