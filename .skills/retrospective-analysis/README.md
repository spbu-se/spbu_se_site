# retrospective-analysis

Analyze a session or merge to identify process gaps, classify root causes, and suggest improvements.

## When to load

- After every merge to main (see `doc/GIT_FLOW.md` §2 — Merge staging → main)
- At session end, during context compaction (see `doc/GIT_FLOW.md` §2 — Context Compaction)
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

| Question | If yes → |
| ---------------------------------------------- | -------------------------------------------------------- |
| Was this planned (pro-active)? | No fix needed — record as completed work |
| Was this re-active (fixing something missing)? | **Classify the gap** (next step) |
| Was this a user request? | Record as completed work |
| Could this rule have been automated? | It was left at doc-only — **classify as missing config** |

### 3. Classify the gap

| Gap type | Root cause | Fix action | Also check skill? |
| ---------------------- | ------------------------------------------ | ---------------------------------------------------- | ------------------------------- |
| **Missing convention** | No rule described how to do this | Add rule to `doc/DEVELOPMENT_PROCESS.md` | Could this be a `.skills/` workflow? |
| **Missing template** | No template existed for this artifact type | Add template or checklist (e.g., §0.7) | Could this be a skill README? |
| **Missing config** | Toolchain didn't catch this | Add linter, pre-commit hook, CI step | No — tool config, not skill |
| **Human error** | Process was documented but not followed | Add guardrail or automation | Could a skill have prevented this? |
| **Pattern recurrence** | Same gap appeared in a previous retro | Previous fix was insufficient — revisit and escalate | Was the skill updated last time? |

### 4. Check for pattern recurrence

Scan previous retrospective entries in the relevant target document (see §5a). If this gap or a similar one was already fixed, the fix was incomplete — propose a stronger solution.

### 5. Classify target document

Determine where the retrospective belongs based on the gap's or change's area:

| Gap category | Target document |
| ----------------------------------------------------------------- | ------------------------------------------- |
| Git flow, branching, commits, staging, guardrails, hotfixes | `doc/GIT_FLOW.md` §7 |
| Planning, TDD, testing, types, release, dependencies, conventions | `doc/DEVELOPMENT_PROCESS.md` |
| Tooling, environment, PowerShell, local config, platform quirks | `.tooling-environment.md` (mistake journal) |

If gaps span multiple categories, split across documents. Each document is scoped to its own area — never duplicate a retrospective across docs.

### 5b. Audit doc health

Scan the session's changed docs for three signal patterns:

| Pattern | How to detect | Action |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------- |
| **Config duplication** | Rule is described in doc AND enforced by `.pre-commit-config.yaml`, `.github/workflows/ci.yml`, `.gitignore`, `pyproject.toml`, or `dprint.json` | Remove from doc. Cross-reference the config file. |
| **Cross-doc duplication** | Same rule appears in 2+ docs (e.g., `AGENTS.md` + `GIT_FLOW.md`) | Keep in one canonical doc. Replace others with cross-reference (`See X.md §Y`). |
| **Self-evident rule** | Rule describes standard git/developer practice (e.g., "never commit to main", "stash before branching") | Delete. If the rule was added because someone violated it, keep as a retrospective entry instead. |

Signal strength: high-confidence finds are config-duplicates (the config IS the truth). Low-confidence are self-evident rules (may be project-specific — ask if unsure).

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
| `doc/XXX.md` | User request | Missing template | Added §0.7 checklist |
| `.pre-commit-config.yaml` | Retro finding | No formatting guard | Added mdformat hook |

Include concrete file paths and exact changes needed.

### 7. Store lessons

Append a structured retrospective entry to the target document identified in §5a under the appropriate heading (`### Retrospective — <title>` in `doc/GIT_FLOW.md` §7 or `doc/DEVELOPMENT_PROCESS.md`; add to the mistake journal table in `.tooling-environment.md`):

```markdown
### Retrospective — <title>

<Brief description of what happened>

**What went wrong**: <root cause analysis>
**Root cause**: <gap type>
**Fix**: <what was done to prevent recurrence>
```

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

## Dependencies

- `git` — to inspect commit history
- Read access to `doc/GIT_FLOW.md` — to check §7 previous retros
- Read access to `doc/DEVELOPMENT_PROCESS.md` — to check previous retros
- Read access to `.tooling-environment.md` — to check mistake journal
