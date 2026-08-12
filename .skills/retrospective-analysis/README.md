# retrospective-analysis

<!-- encoding: utf-8 -->

Analyze a session or merge to identify process gaps, classify root causes, and suggest improvements.

## When to load

> See `docs/AI_AGENTS.md` §Skills → Efficiency modes for the general principle.

### Light retro

| Trigger | Why light |
|---------|-----------|
| After merge-gate (routine) | Catch drift, low ceremony |
| User says "quick retro" | Explicit request for light |
| `skill-for-skills` finds minor violations | Self-heal violations, report summary |

### Full retro

| Trigger | Why full |
|---------|----------|
| After user says "retrospective" / "lessons learned" | Full analysis expected |
| After doc restructuring | High risk of scope violations |
| Pattern recurrence detected | Needs escalation ladder |
| `skill-for-skills` finds structural violations | Requires full gap classification |

> **Note**: The light/full split is provisional — it will be reviewed and adjusted after the first full retro that runs with this split (see Step 10).

## Light workflow

For quick retro after routine merge-gate. Covers only efficiency audit and self-improvement — no gap classification.

1. **Collect changes** — `git log`, categorize files (source/tests/docs/config/tooling)
1. **Check for gaps** — run step 8a efficiency audit (all questions in §8a). Any "yes" → classify as gap
1. **Store lessons** — append to `docs/RETROSPECTIVES.md` if gaps found
1. **Self-improve** — run step 9 checklist (mixed-concern? pattern extraction? skill self-check?)
1. **Generate prevention rules** — for any "yes" in efficiency audit, write rule in canonical doc (step 8b)

If gaps suggest pattern recurrence or value contradiction, escalate to full retro.

## Full workflow

### 1. Collect changes

```bash
git log --oneline --since="<last-merge-or-session-start>"
```

List all files touched and categorize: source code, tests, docs, config, tooling.

### 2. Trace provenance per change

For each change, ask:

| Question | If yes → |
| ---------------------------------------------- | -------------------------------------------------------- |
| Was this planned (pro-active)? | No fix needed — record as completed work |
| Was this re-active (fixing something missing)? | **Classify the gap** (next step) |
| Was this a user request? | Record as completed work |
| Could this rule have been automated? | It was left at doc-only — **classify as missing config** |
| Was knowledge imported from another project? | **Check for cross-project leaks** — verify no private references, proprietary names, or source-repo mentions leaked into docs. Document adaptation decisions. |

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

Scan previous retrospective entries in the relevant target document (see §5a). If this gap or a similar one was already fixed, the fix was incomplete — propose a stronger solution.

**Escalation ladder**: each recurrence requires a minimum layer fix:

| Recurrence count | Minimum escalation | Example |
|---|---|---|
| 1st | Layer 3 — documentation | Add rule to canonical doc |
| 2nd | Layer 2 — CI check | Add CI step that catches the gap |
| 3rd+ | Layer 1 — tool config | Pre-commit hook, linter rule, structural guard |

A fix that stays at the same layer across recurrences is not escalated — it's repeated. The layer must increase with each recurrence.

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

Scan the session's changed docs for signal patterns. Doc-health-only signals (freshness, cross-refs, scope discipline, encoding, SPDX) now live in `.skills/docs-audit/` — load it separately for a full doc audit. For code-related concerns (secrets, deprecations, crash safety, redirects), load `.skills/code-audit/`.

| Pattern | How to detect | Action |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------- |
| **Self-evident rule** | Rule describes standard git/developer practice (e.g., "never commit to main", "stash before branching") | Delete. If the rule was added because someone violated it, keep as a retrospective entry instead. |
| **Directory collision** | New directory was created during the session — check if a similarly-named directory already exists (e.g., `ls docs/` before creating `doc/`) | Merge unique content, delete duplicate directory. Add pre-creation audit check to the relevant skill. |
| **Missing catalog entry** | A new `.md` file was created in `docs/` — grep `docs/DOCS.md` for its filename | Add row to DOCS.md catalog table. The file exists on disk but isn't listed — cross-references can't find it. |

### 5c. Improve skills used during the session

Identify which `.skills/<name>/README.md` were loaded during the analyzed session. For each:

- Did the session reveal a gap or improvement in the skill's workflow?
- Does the skill reference tooling patterns that changed during the session?
- Should a "Lessons Learned" section or updated step be added?

If yes, update the skill README immediately as part of the retrospective commit.

### 5d. Extract reusable techniques

Scan the session for patterns, code snippets, and workarounds that are:

- Not already documented in `docs/TROUBLESHOOTING.md` (retired, now in `docs/TOOLING.md`, `docs/TESTING.md`, or `docs/AI_AGENT_EXPERIENCE.md`) or `docs/TOOLING.md`
- Likely to be needed again (e.g., patching patterns, fixture setups, encoding workarounds)
- Discovered as a fix for a bug or a workaround for a module-level side effect

For each, add an entry to the appropriate doc with the exact code or command. Do not bury techniques in the retrospective entry — they must be searchable independently.

Examples of what to extract:

- `contextlib.suppress(RuntimeError)` for catching double `db.init_app()` — in `docs/AI_AGENT_EXPERIENCE.md`
- `try/finally` for restoring module-level flags like `thesesImport.download` — in `docs/AI_AGENT_EXPERIENCE.md`
- `[System.IO.File]::WriteAllText()` for PowerShell UTF-8 encoding — in `TOOLING.md`

**Check after extraction**: If a future session encounters the same problem, would a `grep` or `AI_AGENT_EXPERIENCE.md` search find the fix? If not, improve the entry's discoverability (better section title, more keywords, cross-reference from related docs).

### 6. Suggest improvements

Present findings in a structured table:

| Change | Trigger | Root gap | Fix |
| ------------------------- | ------------- | ------------------- | -------------------- |
| `docs/XXX.md` | User request | Missing template | Added §0.7 checklist |
| `.pre-commit-config.yaml` | Retro finding | No formatting guard | Added mdformat hook |

Include concrete file paths and exact changes needed.

### 7. Store lessons

Append a structured retrospective entry to `docs/RETROSPECTIVES.md`.
**Every classified gap must have a corresponding retrospective entry** — even if the fix was already applied directly (code changes, doc updates, config changes). The entry records why the gap existed, not just what was done about it.

If no existing heading matches, create a new one: `### Retrospective — <title>` in `docs/RETROSPECTIVES.md`. Also update the mistake journal table in `.tooling.md` if the gap is tooling-related:

```markdown
### Retrospective — <title>

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
- **Did I load any skills during this session?** If not, distinguish:
  - *Couldn't load* — the skill exists on disk but the `skill` tool doesn't surface it (structural gap). Document in `docs/AI_AGENTS.md` §Tool Quirks and add a retro entry.
  - *Didn't load* — the skill was loadable but skipped because "custom is faster" (behavioral gap). Escalate this recurring pattern.
- **Was this skill loadable via the `skill` tool?** If not, update `docs/AI_AGENTS.md` §Tool Quirks with the loading gap, and update AGENTS.md skill-loading instruction to say "read manually" instead of "load with `skill` tool".
- **Did the retrospective itself violate any process rules?** (creating standalone files instead of appending, skipping skill loading, committing without testing, etc.) The retrospective must model the behavior it enforces.
- **Did the session include user imperatives that should be encoded as permanent rules?** (e.g., "do X instead of Y", "always Z when W") — each imperative is a training signal. Encode in the relevant canonical doc or skill before session closes. Do not treat as one-time instruction.
- **Did any rule I wrote during this session govern my own behavior?** If yes, add a retrieval cue at the decision boundary (pre-flight step, AGENTS.md checklist, trigger in relevant skill) — doc-only rules are invisible when the decision point arrives.

#### 8a. Session efficiency audit

Ask these questions to surface waste and optimization opportunities:

| Question | What it catches |
|----------|----------------|
| Did any single mistake propagate across multiple files? | Missing validation step before commit — should have run the breaking command earlier |
| **What ELSE could be affected by the same root cause?** | Fix narrowed to one symptom; systemic scope not checked. The user asked "what else was broken?" — 42 files, not 1. |
| **How do you verify nothing was silently lost?** | Fix applied but no completeness check. The user asked "is any mojibake left?" — uncovered remaining corruption in mixed-content files. |
| Did I edit the same logical change in more than 3 files by hand? | Should have been a single grep/replace or a script |
| Did I discover a structural issue mid-edit that should have been caught pre-edit? | Missing pre-flight scan (duplicate sections, stale refs, renumbering gaps) |
| Was there a long feedback loop between writing and validating? | Could have validated incrementally instead of batch-writing everything first |
| Did `git diff --stat` show unexpected files changed? | Formatting noise or unintended edits hiding real changes |
| **Did you skip any pre-flight step?** (fetch, CI check, branch naming, `--no-gpg-sign`) | Branch created without checking CI status first — wasted work if CI is red |
| **Did any new rule land outside its canonical doc?** | Scope boundary violation — e.g., universal knowledge in `.tooling.md`, process rules in config files |
| **Could any change harm users or the product?** (Supreme Directive I/II) | Edge cases that aren't bugs but degrade UX, lose data, or incur technical debt |
| **Did practice conflict with a Strategic Priority in the Project Doctrine?** | E.g., a rule we said was "low-effort" turned out high-effort in this context. Classify as **value contradiction** in step 3 — flag to user, do not fix autonomously. |
| Did AGENTS.md grow 4+ lines vs branch point? | `git diff --stat origin/staging...HEAD AGENTS.md` — if +4+, run step 5b AI-instruction-file bloat audit |
| Did CLAUDE.md grow vs branch point? | Any new line in CLAUDE.md is suspicious — must delegate to AGENTS.md, never expand |
| Is this a docs/ branch finalization? | Mandatory — run step 5b bloat audit on both AGENTS.md and CLAUDE.md regardless of delta |
| What was going another way that we definitely expected? | Identify decisions or commands whose outcome differed from expectation. Each divergence is either a bug, a process gap, or new knowledge. |
| **Did any doc contain stale numbers or expired constraints?** | README test count, CODE_ISSUES.md 90% guard, doc table gaps — metrics drift silently between sessions |
| **Did any test use hardcoded line numbers or byte offsets to find code?** | Formatters shift line counts — `lines[589:]` broke when ruff format + coding-line removal shifted the file by 3 lines. Slice by sentinel pattern instead (`next(i for i,l in enumerate(lines) if l.startswith("if __name__"))`). |
| **Did CI's sequential fail-fast chain mask pre-existing test failures?** | Basedpyright stopped CI before pytest ran — 11 pre-existing failures were invisible for multiple pushes. Split lint+type checks into separate CI jobs from tests, or use `continue-on-error`. |
| **Did any ruff rule require multiple rounds of configuration tuning?** | RUF001 `allowed-confusables` needed 3 rounds adding characters. Single-pass would have saved time. Complete list for bilingual projects: all Cyrillic-Latin homoglyphs + typographic punctuation. |
| **Did local vs CI environment diverge for any tool?** | basedpyright `reportInvalidCast` triggered on CI but not locally — version pin mismatch or cache staleness. Verify tool versions match between environments. |
| **Did any test failure trace to a transitive dependency version rather than direct code changes?** | Flask-Admin 2.2.0 `create_view()` cls arg incompatible with newer Jinja2/Werkzeug. Lockfile age check needed before assuming code changes caused the failure. |
| **Did a pre-commit auto-fix hook (djLint, ruff format, etc.) conflict with staged changes?** | Hooks that reformat ALL files (not just staged) abort commits when staged edits differ from the hook's output ("Stashed changes conflicted with hook auto-fixes"). Fix: run `pre-commit run <hook> --all-files` to normalize BEFORE staging. |
| **Did you test an endpoint's HTTP status when its contract is a JSON body?** | Two test-design false starts traced to contract misread: news-XSS test asserted `"<script" not in body` (failed on legit GTM tags — assert the payload marker instead); upload-whitelist test expected HTTP 500 while the endpoint returns HTTP 200 + status in JSON. Verify the response contract (status vs body) before writing the assertion. |
| **Did you verify the active branch before every commit?** | Commits landed on `current` instead of the intended feature branch (3rd recurrence). `git branch --show-current` before each commit is the cue — if missed, the fix is `git cherry-pick -n` + `git commit --no-gpg-sign`. |
| **Did a refactor change what a test's xfail marker reports?** | `strict=False` markers on intermittently-failing tests XPASS whenever the flaky path passes — xfail/xpass *counts* drift between runs without any real fix. Re-verify drift is stability, not flakiness, before removing a marker. |
| **Did a move into functions break a linter/type check that module-level code passed?** | Moving `@app.route`-decorated views into `_register_*` helpers triggered basedpyright `reportUnusedFunction`; moving a re-export triggered ruff F401. Module-level opt-out (`# pyright: reportUnusedFunction=false`) and `__all__` re-export are the fixes. |

#### 8b. Generate prevention rules

For every "yes" in §8a, write a concrete prevention rule in the appropriate canonical doc. Examples:

- "Before staging after bulk doc edits, run `uv run mdformat` with the exact CI command string" → `docs/DEVELOPMENT_PROCESS.md §0.6`
- "Before editing a section-heavy file, `grep -c '^## '` to detect structural anomalies" → `docs/DOCS.md §8.1`
- "For section renumbering, write the mapping and validate against `grep '^## '` before editing" → `docs/DOCS.md §8.1`
- "Before merge or batch finalization: diff AGENTS.md (+4 guard) and CLAUDE.md (any growth) line count against branch point. Run AI-instruction-file bloat audit. CLAUDE.md must delegate, not duplicate." → `docs/DOCS.md §7.1`

Append an entry to the `## Self-improvement log` for each new prevention rule generated.

### 9. Self-improve the skill

After completing the retrospective, check if the process revealed gaps in THIS skill document:

1. Review step 8 answers — any "no" or "manual" answer may indicate a skill gap
1. Review user corrections during the session — did the user redirect the retrospective process itself?
1. Review the gap table from step 3 — were any gaps **missed** by the retrospective and only found when you presented to the user?
1. **Mixed-concern litmus**: For any multi-rule section proposed during the session, check each rule against its section heading. If a rule's concern differs ("when to ask" vs "how to format"), it belongs in a separate section.
1. **Pattern extraction**: Did this session reveal a structural pattern (not just a bug) that should be encoded as a prevention rule rather than applied once? If yes, add to the appropriate skill or doc.
1. If gaps found, add a self-improvement log entry AND update the relevant step(s) in this skill immediately

The retrospective skill must model the behavior it enforces. If it asks "did you load skills?" it must be loadable. If it asks "did you check existing tools?" it must first check if the `skill` tool itself works.

### 10. Review retro skill against docs

Since the retro skill is derived from docs, every full retro audits the retro skill itself:

1. **Does the retro skill still match its canonical docs?**
   - `docs/DEVELOPMENT_PROCESS.md` §2 — is procedure defined there?
   - `docs/AI_AGENTS.md` §Skills — are boundaries and principles followed?
   - `docs/DOCS.md` §Skills directory — is catalog entry accurate?
1. **Were docs updated when the skill changed this session?**
   - If a step was added/modified in the skill → was the corresponding canonical doc updated?
   - If not, add the missing info to the doc (skill is derivable, not source)
1. **Were skills updated when docs changed?**
   - If a doc section that the retro skill references was modified → does the skill need updating?
1. **Is the light/full split still appropriate?**
   - Did the light workflow miss anything this session? Did the full workflow include unnecessary steps?
   - Propose adjustments if needed — the split is subject to change after each full retro.

## Self-improvement log

### [2026-07-04] Add step 8 — self-improve retrospective

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
workarounds, and fixes, and ensures they land in `TOOLING.md` or `AI_AGENT_EXPERIENCE.md`
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

### [2026-07-07] Document PowerShell pipe error pattern

The agent repeatedly used Unix pipe syntax (`head`, `grep`, `&&`) in
PowerShell. Procedural guard added to AGENTS.md pre-flight checklist:
read `.tooling.md` §PowerShell 5.1 before writing piped commands.

**Escalation**: If this pattern recurs, replace procedural guard with
structural fix (command wrapper that validates syntax).

### [2026-07-07] Add escalation ladder, instruction truth signal, scope gap signal, loadability distinction, and step 9 — gaps found during retro that the skill missed

The 2026-07-07 retrospective ran the full workflow but still missed 5 gaps that were only found when the user challenged "are you sure we've done enough?":

1. **No escalation ladder** — step 4 said "revisit and escalate" but had no definition of what escalation means (layer increase per recurrence count). The over-engineering pattern recurred 4 times with layer-3-only fixes.
1. **No instruction truth check** — AGENTS.md said "load skill via `skill` tool" but the tool doesn't surface project skills. Step 5b checked for bloat but not for executability.
1. **No scope gap check** — pre-flight was scoped "(auto/batch mode)" but the gap it prevents applies universally. Step 5b had no signal for this.
1. **"Couldn't load" vs "didn't load"** — step 8 asked "did you load skills?" but treating both reasons the same. Structural blocker → doc fix; behavioral skip → escalate.
1. **No step 9** — the skill had no mechanism to improve itself based on gaps found during its OWN execution.

**Fix**:

- Added escalation ladder table to step 4 (1st→L3, 2nd→L2, 3rd+→L1)
- Added "Instruction truth" signal pattern to step 5b
- Added "Scope gap" signal pattern to step 5b
- Split step 8 self-check into "couldn't load" (structural) vs "didn't load" (behavioral)
- Added step 9 "Self-improve the skill" — explicit post-retro audit of the skill itself

### [2026-07-07] Add "unexpected outcome" retro question

Agent ignored repeated error output because there was no reactive
triage rule. Added procedural guard to AGENTS.md and `.tooling.md`.
Retro step 8a now asks "What was going another way that we definitely
expected?" — covers errors, surprises, and divergences in both directions.

### [2026-07-08] Add systemic-scope questions to step 8a

Encoding corruption fix session: the user asked "what else was affected?" and "what is still broken?" — two questions that uncovered systemic scope (42 files, not 1) and silent-incompleteness (remaining mojibake in mixed-content lines). The retrospective skill had no prompt to ask these.

**Fix**: Added two new questions to step 8a:

- "What ELSE could be affected by the same root cause?" — prevents single-symptom fixes
- "How do you verify nothing was silently lost?" — adds completeness verification to every fix

### [2026-07-08] Mixed-concern rules in section proposals

When proposing a section with multiple rules, the agent grouped a communication-protocol rule ("ask if ambiguous") under a format-conventions heading because they appeared in the same proposal. User had to correct.

**Signal**: A rule's concern (when to communicate) differs from its section's scope (how to format) — litmus test: "If this rule were in its own section, what would that section be called?" If different, split.

**Fix**: Added to step 9 self-improvement checklist: after proposing any multi-rule section, run the litmus test on each rule. If any rule belongs to a different concern, split into separate sections before presenting.

### [2026-07-08] Add stale metrics and expired guardrail signals to step 5b

Doc freshness audit revealed: README test count was 47% vs actual 92%, CODE_ISSUES.md "do not fix until 90%" constraint expired 2 sessions ago, and the doc table was missing 6 entries. Step 5b had 8 structural signals but zero freshness signals.

**Fix**: Added "Stale metrics" and "Expired guardrail" patterns to step 5b table. Added "Did any doc contain stale numbers or expired constraints?" to step 8a efficiency audit.

### [2026-07-08] Skill extraction lifecycle — sections accumulate concerns, split proactively

Doc health and code audit signals accumulated in retro step 5b until the section became a catch-all. Rather than noticing the growth and proposing a split, I waited for the user to prompt. The same pattern recurred across two extractions: `docs-audit` first, then `code-audit` separately — a full inventory before refactoring would have revealed both gaps at once.

**Signal**: When a section has 8+ rows or grew 50%+ since creation, run a concern audit — does every item still share the section's original purpose?

**Fix**: Added "Pattern extraction" to step 9 checklist. Added "Always learn, never forget — encode patterns before session ends" to AGENTS.md pre-flight.

### [2026-07-08] Add light/full retro split + Step 10

Retro was always run as full workflow (~15 min) even for routine merge-gate checks. Split into light (efficiency audit + self-improve only, ~5 min) and full (all 10 steps, including new Step 10 — review retro skill against docs). Step 10 also reviews whether the split is still appropriate, making it self-correcting.

**Fix**: Added "## When to load" with trigger table. Renamed original workflow to "## Full workflow". Added "## Light workflow" with 5 condensed steps. Added "### 10. Review retro skill against docs" to full workflow. Added provisional caveat that split is subject to change after each full retro.

## Output template

At the end, produce:

```
## Retrospective Summary

Changes analyzed: <N>
Gaps found: <M>
- <gap 1> → <fix>
- <gap 2> → <fix>
No action needed: <planned changes, user requests>

Pattern recurrence: <yes/no — if yes, escalate>
```

### [2026-07-12] Add 6 missing efficiency audit questions from ruff-strict session

Session surfaced several process gaps not covered by existing 8a questions:

1. **Hardcoded test offsets** — `lines[589:]` in `test_flask_se_deep.py` broke when ruff format shifted line numbers. No question asked "did any test use hardcoded file offsets?"
1. **CI fail-fast masking** — basedpyright failure stopped CI before pytest, hiding 11 pre-existing failures for multiple pushes. No question asked about sequential fail-fast chains drowning deeper results.
1. **Multi-round config tuning** — RUF001 `allowed-confusables` took 3 rounds of add→check. No question asked "did any rule require multiple tuning rounds?"
1. **Local-vs-CI tool divergence** — basedpyright `reportInvalidCast` on CI only. No question asked about environment parity.
1. **Transitive dependency failures** — Flask-Admin `cls` arg traced to Jinja2/Werkzeug version, not code changes. No question asked about dependency version investigation.

**Fix**: Added 6 new rows to §8a covering all gaps. Added "Verify CI shows test results, not just lint results" to AGENTS.md pre-flight checklist.

### [2026-08-02] Add hook-conflict and JSON-contract questions to §8a

2026-08-02 security-audit session surfaced two repeated false starts not covered by §8a:

1. **Pre-commit auto-fix hooks conflicting with staged changes** — djLint reformats ALL html files during commit; staged template edits differing from its output caused 2 aborted commits before the normalize-then-stage fix. No question asked about hooks that reformat more than the staged set.
1. **Endpoint-contract misreads** — news-XSS test asserted on a too-broad marker (failed on legit GTM `<script>` tags); upload-whitelist test expected HTTP 500 while the endpoint returns HTTP 200 + status in a JSON body. No question asked "is the response contract status-based or body-based?"

**Fix**: Added 2 rows to §8a covering both, with the normalize-before-stage workaround and the contract-check rule.

### [2026-08-11] Add branch-verification, xfail-drift, and function-move questions to §8a

2026-08-11 refactor session (application factory + route decentralization) surfaced three gaps the retro's §8a did not ask about:

1. **Branch-discipline violation (3rd recurrence)** — 4 refactor commits landed on `current` instead of the feature branch. The retro had no "did you verify the active branch before committing?" question, so the pattern kept recurring across sessions despite the escalation ladder.
1. **xfail/xpass count drift** — `post_theses` `strict=False` markers XPASS whenever the flaky CI path passes; counts drifted 5→3 xfailed / 7→9 xpassed between two green full-suite runs. The retro had no prompt to distinguish stability from flakiness before touching markers.
1. **Move-into-function lint/type breakage** — moving decorated views into helpers triggered basedpyright `reportUnusedFunction`; moving a re-export triggered ruff F401. Both fixed with module-level patterns, but undocumented.

**Fix**: Added 4 rows to §8a (branch-before-commit, xfail-drift, linter-on-move, plus route-map-verification as the prevention technique). Self-improvement log entry added; `.tooling.md` gained the `git cherry-pick --continue` GPG workaround.

## Dependencies

- `git` — to inspect commit history
- Read access to `docs/RETROSPECTIVES.md` — to check previous retros
- Read access to `docs/GIT_FLOW.md` — to check git rules
- Read access to `docs/DEVELOPMENT_PROCESS.md` — to check process rules
- Read access to `.tooling.md` — to check mistake journal
