# skill-for-skills

<!-- encoding: utf-8 -->

Maintain every skill in sync with the canonical docs, enforce all skills architecture principles, and keep itself consistent. Does not create new skills — may propose with verified proof per extraction triggers in `docs/AI_AGENTS.md` §Skills.

## When to load

- After any doc restructuring that could affect skills
- On request from user or from `merge-gate`
- When a new skill was created or an existing skill was modified

## Workflow

### Phase 1 — Self-check

Verify skill-for-skills itself follows every principle before auditing others:

| Principle | Check | If violated |
|-----------|-------|-------------|
| Registered in Skills directory | Exists in `docs/AI_AGENTS.md` §Skills directory table | Fix first |
| Registered in `CLAUDE.md` | Has row in skill table | Fix first |
| Stubs exist | `.claude/skills/skill-for-skills/SKILL.md`, `.agents/` | Create stubs |
| No new knowledge | Every statement derivable from `docs/AI_AGENTS.md` §Skills or other canonical docs | Add missing info to docs before removing from skill |
| No `.skills/` refs in process docs | `grep -rn \.skills/skill-for-skills docs/` returns nothing | Remove |
| Self-maintains | If phase 1 finds gaps, fix docs/skill before phase 2 | Iterate until self-check passes |

### Phase 2 — Audit each skill

For each skill in the Skills directory table, run:

#### 2.1 Registration audit

- Exists in `docs/AI_AGENTS.md` §Skills directory table?
- Exists in `CLAUDE.md` skill table with load condition?
- Stubs exist: `.claude/skills/<name>/SKILL.md` and `.agents/skills/<name>/SKILL.md`?
- Canonical source `.skills/<name>/README.md` exists?

#### 2.2 Boundaries audit

```
grep -rn "\.skills/<name>/" docs/ --include "*.md"
```

Any matches in process docs (DEVELOPMENT_PROCESS, DOCS, GIT_FLOW, TESTING, REPO_REVIEW) violate the Boundaries principle — report for delegation to `docs/AI_AGENTS.md`.

#### 2.3 Derivability audit

For each section/step in the skill, check the corresponding canonical doc (from the Source of truth table in `docs/AI_AGENTS.md` §Skills):

- If a step exists in the skill but not in any canonical doc → it is new knowledge. Report: add to the canonical doc.
- Exception: skills marked "Canonical For" their workflow in the directory table may define procedure without doc backup.

#### 2.4 Source of truth compliance

- Skill reads only its listed docs from the Source of truth table?
- Skill writes only its listed docs?
- If reading/writing unlisted docs, flag for source-of-truth table update.

#### 2.5 Maintenance check

- Has the canonical doc changed since the skill was last audited? (`git log --oneline <doc>` since skill's last commit)
- If doc added new rules or sections, does the skill need updating?

### Phase 3 — Report

```
## Skill Audit Results

### Self-check: PASS / FAIL

### Auto-fixed

| Skill | Finding | Action |
|-------|---------|--------|
| test-writer | Missing .claude stub | Created from template |
| ... | ... | ... |

### Reported (requires action)

| Skill | Principle | Issue | Fix |
|-------|-----------|-------|-----|
| code-audit | Boundaries | Referenced in docs/DEVELOPMENT_PROCESS.md §4.5 | Must move ref to AI_AGENTS.md |
| ... | ... | ... | ... |

### Skills in good standing: <N>

### Proposals (new skill warranted?)

If recurring gaps across multiple skills fit an extraction trigger, propose:
- Trigger met: <size signal / complexity / efficiency>
- Evidence: <specific examples from audit>
```

### Phase 4 — Self-heal

If any self-check failed, fix the skill or docs before finishing. This ensures no principle is unchecked ever.

## Auto-fix rules

| Finding | Auto-fix? | Method |
|---------|-----------|--------|
| Missing `.claude/skills/<name>/SKILL.md` | Yes | Create template from skill's aim header |
| Missing `.agents/skills/<name>/SKILL.md` | Yes | Same template |
| Missing from `docs/AI_AGENTS.md` §Skills directory table | Yes | Add row from skill README scope/covers |
| Missing from `CLAUDE.md` skill table | Yes | Add row from skill's "When to load" |
| Stale stub path | Yes | Fix to match canonical `.skills/<name>/README.md` |
| Process doc `.skills/` ref | No | Report — needs human judgment |
| Skill info not in doc | No | Report — propose doc update |
| Doc changed, skill stale | No | Report — flag for review |
| Canonical file missing | No | Report — directory entry stale |

All non-auto-fix items must be reported in retrospective. The retrospective must run a skill-update pass after code review and after docs update.

## Dependencies

- Read access to `docs/AI_AGENTS.md` §Skills (all subsections)
- Read access to `CLAUDE.md` (skill table)
- Read access to `docs/DOCS.md` §8.1 (integrity checks)
- Read access to all `.skills/<name>/README.md` files
- Read access to `git log` (to check doc change dates)
