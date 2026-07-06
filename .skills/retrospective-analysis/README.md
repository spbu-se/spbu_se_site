# retrospective-analysis

<!-- encoding: utf-8 -->

Analyze a session or merge to identify process gaps, classify root causes, and suggest improvements.

## When to load

- After every merge to main (see `doc/GIT_FLOW.md` В§2 вЂ” Merge staging в†’ main)
- At session end, during context compaction (see `doc/GIT_FLOW.md` В§2 вЂ” Context Compaction)
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
| **Missing convention** | No rule described how to do this | Add rule to `doc/DEVELOPMENT_PROCESS.md` | Could this be a `.skills/` workflow? |
| **Missing template** | No template existed for this artifact type | Add template or checklist (e.g., В§0.7) | Could this be a skill README? |
| **Missing config** | Toolchain didn't catch this | Add linter, pre-commit hook, CI step | No вЂ” tool config, not skill |
| **Human error** | Process was documented but not followed | Add guardrail or automation | Could a skill have prevented this? |
| **Pattern recurrence** | Same gap appeared in a previous retro | Previous fix was insufficient вЂ” revisit and escalate | Was the skill updated last time? |

### 4. Check for pattern recurrence

Scan previous retrospective entries in the relevant target document (see В§5a). If this gap or a similar one was already fixed, the fix was incomplete вЂ” propose a stronger solution.

### 5. Classify target document

Determine where the retrospective belongs based on the gap's or change's area:

| Gap category | Target document |
| ----------------------------------------------------------------- | ------------------------------------------- |
| Git flow, branching, commits, staging, guardrails, hotfixes | `doc/GIT_FLOW.md` В§7 |
| Planning, TDD, testing, types, release, dependencies, conventions | `doc/DEVELOPMENT_PROCESS.md` |
| Tooling, environment, PowerShell, local config, platform quirks | `.tooling.md` (mistake journal) |

If gaps span multiple categories, split across documents. Each document is scoped to its own area вЂ” never duplicate a retrospective across docs.

### 5b. Audit doc health

Scan the session's changed docs for three signal patterns:

| Pattern | How to detect | Action |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------- |
| **Config duplication** | Rule is described in doc AND enforced by `.pre-commit-config.yaml`, `.github/workflows/ci.yml`, `.gitignore`, `pyproject.toml`, or `dprint.json` | Remove from doc. Cross-reference the config file. |
| **Cross-doc duplication** | Same rule appears in 2+ non-trivial docs (e.g., `GIT_FLOW.md` + `DEVELOPMENT_PROCESS.md`). **Exempt**: `AGENTS.md`, `CLAUDE.md`, `README.md` вЂ” these are intentional summary extracts. | Keep in one canonical doc. Replace others with cross-reference (`See X.md В§Y`). |
| **Self-evident rule** | Rule describes standard git/developer practice (e.g., "never commit to main", "stash before branching") | Delete. If the rule was added because someone violated it, keep as a retrospective entry instead. |

Signal strength: high-confidence finds are config-duplicates (the config IS the truth). Low-confidence are self-evident rules (may be project-specific вЂ” ask if unsure).

**Pre-commit vs CI parity** вЂ” verify every check that runs in CI also runs locally via pre-commit hooks. If CI catches something that pre-commit doesn't flag, either add a pre-commit hook or document the gap (and accept that CI will catch it).

**SPDX/licensing audit** вЂ” verify every new or modified source file has an SPDX header matching the repo's LICENSE file. If LICENSE is missing, flag it. If multiple licenses exist, document coverage per directory.

### 5c. Improve skills used during the session

Identify which `.skills/<name>/README.md` were loaded during the analyzed session. For each:

- Did the session reveal a gap or improvement in the skill's workflow?
- Does the skill reference tooling patterns that changed during the session?
- Should a "Lessons Learned" section or updated step be added?

If yes, update the skill README immediately as part of the retrospective commit.

### 6. Suggest improvements

Present findings in a structured table:

| Change | Trigger | Root gap | Fix |
| ------------------------- | ------------- | ------------------- | -------------------- |
| `doc/XXX.md` | User request | Missing template | Added В§0.7 checklist |
| `.pre-commit-config.yaml` | Retro finding | No formatting guard | Added mdformat hook |

Include concrete file paths and exact changes needed.

### 7. Store lessons

Append a structured retrospective entry to the target document identified in В§5a.
**Every classified gap must have a corresponding retrospective entry** вЂ” even if the fix was already applied directly (code changes, doc updates, config changes). The entry records why the gap existed, not just what was done about it.

If no existing heading matches, create a new one: `### Retrospective вЂ” <title>` in `doc/GIT_FLOW.md` В§7 or `doc/DEVELOPMENT_PROCESS.md`; add to the mistake journal table in `.tooling.md`:

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

If yes, append an entry to the `## Self-improvement log` section at the bottom of this file. This creates a feedback loop: retrospectives improve themselves.

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
1. The retro itself violated process rules — created standalone `doc/RETROSPECTIVE_*.md` instead of appending to `GIT_FLOW.md` §9. The retro had no self-check for rule compliance.

**Fix**: Added two new questions to step 8: "Did I load any skills?" and "Did the retrospective itself violate any process rules?" This creates a feedback loop for the retro process itself.

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

- `git` вЂ” to inspect commit history
- Read access to `doc/GIT_FLOW.md` вЂ” to check В§7 previous retros
- Read access to `doc/DEVELOPMENT_PROCESS.md` вЂ” to check previous retros
- Read access to `.tooling.md` вЂ” to check mistake journal
