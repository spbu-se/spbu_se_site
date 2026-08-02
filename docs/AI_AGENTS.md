# AI Agent Configuration & Output Conventions

<!-- encoding: utf-8 -->

Covers: AI-agent-specific knowledge: tool permissions, quirks, workarounds, typical issues, output format conventions for all agent-generated reports, summaries, and responses, skills architecture (creation, usage, maintenance), and skills catalog with vendor stubs and commands.
Does not cover: process workflow (see `docs/DEVELOPMENT_PROCESS.md`), commands (see `AGENTS.md`).

## Permission Recommendation

Recommended permissions (example for OpenCode — adapt to your tool):

```jsonc
{
  "permission": {
    "read": "allow",
    "edit": "ask",
    "glob": "allow",
    "grep": "allow",
    "bash": {
      "*": "ask",
      "pytest*": "allow",
      "ruff*": "allow",
      "python src/flask_se*": "allow",
      "pip install*": "allow",
      "ls*": "allow",
      "mkdir*": "allow"
    },
    "todowrite": "allow",
    "webfetch": "allow",
    "question": "allow",
    "skill": "allow",
    "lsp": "allow"
  }
}
```

## Tool Quirks

### Glob tool doesn't descend into dot-prefixed directories

When the glob tool's `path` parameter points to a parent directory, patterns like `.skills/**/*.md` return **no results**. The tool must point directly into the dot directory:

```jsonc
// WRONG — returns nothing:
// glob(path=".", pattern=".skills/**/*.md")

// CORRECT — finds all 11 skill files:
// glob(path=".skills", pattern="**/*.md")
```

This applies to the opencode glob tool on all platforms. Other AI tools (Claude Code, Cursor) may have different behavior — their glob implementations are independent.

## Output Format

### Compliance rules

Agent output (summaries, reports, responses, wrap-ups) follows these rules:

1. **Exact match** — If a format is prescribed for the exact situation, the agent MUST use it verbatim.
1. **Similar situation** — If a format exists for a similar (not exact) situation, the agent SHOULD follow it but MAY adapt with justification.
1. **No precedent** — If no similar format is documented, the agent MAY propose a reasonable format.

### Timing for auto-mode runs

Every auto-mode batch summary MUST include a timing line:

```
**Timing: estimated as <rough time estimated in planning phase>, but <DD:HH:MM> wall clock elapsed**
```

### Batch run summary (TODO.md)

Use for auto-mode session wrap-ups:

```
## Batch run <YYYY-MM-DD> — session <N> (<scope>)
**Timing: estimated as <planning estimate>, but <DD:HH:MM>**

- <item 1>
- <item 2>
...

### Process violations

Every `--no-verify`, `git commit --no-verify`, `git push --no-verify`, or manual
override of any hook MUST be listed here with the rationale. If none, state
"None".

### CI overhead

If the session pushed to staging, count pushes and CI round-trips. Flag any that
could have been avoided by a local pre-push check:

| Push | Trigger | Avoidable? | Reason |
|------|---------|-----------|--------|
| 1 | Initial basedpyright migration | No | First push |
| 2 | Fix CI exit code | Yes | Could have tested basedpyright locally |
| ... | ... | ... | ... |
```

### Status updates (interactive mode)

For progress reports during a session, follow the same structure: lead with timing, then bullet items. Less formal — omit the TODO.md heading wrapper.

### PR description (squash-merge)

Use for `gh pr create` descriptions on feature branches merged via `gh pr merge --squash` (see `docs/GIT_FLOW.md §2.1`).

**Issue linkage:** if the PR fixes or closes GitHub issues, say so directly with `Closes #<n>` / `Fixes #<n>` in the body (one per line). GitHub then links the issues to the PR and auto-closes them on merge. Issues only partially addressed should use `References #<n>`.

```
## Summary

<One-paragraph high-level description of what changed and why>

Closes #<issue-number>
Closes #<issue-number>

**Timing: estimated as <planning estimate>, but <wall clock> wall clock elapsed**
<optional one-line context>

### Changes

**<Category header, bolded>**:
- <item 1>
- <item 2>

**<Category header, bolded>**:
- ...

### <Section header if needed (e.g. "Testing")>

- <N> tests pass, <M> failures
- CI: <list of green checks>
```

## Communication with user

If "why" is not obvious or could be ambiguous given the user's known decisions, ask before proceeding.

## Skills

### Definition

A skill (`.skills/<name>/README.md`) is the "how" to a doc's "what". Docs define policy and goals. Skills define the executable workflow — step-by-step instructions for an AI agent to achieve the goal.

### Boundaries

Process docs (DEVELOPMENT_PROCESS, DOCS, GIT_FLOW, TESTING, REPO_REVIEW, etc.) never reference skills or `.skills/` paths directly. They may reference `docs/AI_AGENTS.md` if they need to delegate an AI-agent-specific concern.

All skill-related knowledge lives in this section:

- **Catalog**: which skills exist, their scope, what they are canonical for
- **Architecture**: definition, delegation chain, source of truth
- **Extraction triggers**: when a new skill is warranted
- **Creating a skill**: the 8-step checklist
- **Lifecycle**: how skills evolve and split
- **Maintenance**: how to update skills without losing knowledge
- **Commands**: tool-specific automation workflows (`.opencode/commands/`)

CLAUDE.md is the agent entry point for "which skill to load when" — it lists skills with load conditions. Skills are derivable from docs; no skill contains knowledge that cannot be found in a canonical doc (except skills cataloged as canonical for their workflow in the Skills directory below).

### Efficiency modes

Every skill may define a light (quick/fast) workflow alongside the default full workflow.

- **Full** is the default — run when unsure, run after doc restructuring, run on user request
- **Light** is a reduced subset — for routine/auto-mode calls where full analysis would be disproportional
- If a light run misses something, it is **not a fault** if a higher-level workflow (merge-gate, full retro) runs the full version later as a guardrail
- The light/full split for each skill is documented in its "## When to load" section

Rebalancing between light and full is a cost-optimization decision. The default is full. A light mode may be added when:

1. **Evidence** — the full workflow has been run N times without finding significant issues in the skipped sections
1. **Safety** — a guardrail exists at a higher level (merge-gate, full retro, user review) that catches anything the light mode would miss
1. **No harm** — the light mode skipping a check cannot hurt users or the product. If there is any doubt, keep full.

The retrospective-analysis skill (§10) reviews whether splits are still appropriate after each full run.

### Delegation chain

```
CLAUDE.md → AGENTS.md → docs/ → .skills/<name>/README.md
```

Each layer delegates down, never copies up. Skill stubs (`.claude/skills/`, `.agents/skills/`) are thin `SKILL.md` wrappers pointing to the canonical `.skills/<name>/README.md` — never author skill content in stubs.

### Source of truth

| Concern | Lives in | Skill reads/writes |
|---------|----------|-------------------|
| Process policy | `docs/DEVELOPMENT_PROCESS.md`, `docs/GIT_FLOW.md`, `docs/TESTING.md` | `retrospective-analysis` |
| Doc conventions | `docs/DOCS.md` | `docs-audit` |
| Bug inventory | `docs/CODE_ISSUES.md` | `code-audit` (reads, appends) |
| Repo checklist | `docs/REPO_REVIEW.md` | `repo-review` (reads) |
| Task backlog | `TODO.md` | All audit skills (feed items) |
| Merge discipline | `docs/GIT_FLOW.md` §2, `docs/DEVELOPMENT_PROCESS.md` §0.8 | `merge-gate` (reads, writes staging branch, TODO.md) |
| Process gap history | `docs/RETROSPECTIVES.md` | `retrospective-analysis` (appends) |

Skills reference docs. Docs never reference skills — a doc must make sense without the skill.

### Extraction triggers

A new skill is warranted when:

1. **Section size signal** — a doc section has 8+ rows or grew 50%+ since creation → it has accumulated concerns, time to split
1. **Process step complexity** — a process step is complex enough that an agent would benefit from a guided walkthrough (e.g., `code-audit` with 9 sections across code, CI, and security)
1. **Agent efficiency** — a step is repeated across multiple sessions and skipping it would cause real harm (e.g., merge gate, doc audit)

When splitting, take a full inventory first — map all content that belongs to the split concern, then batch-extract in one operation.

### Creating a new skill

Checklist:

1. Which doc defines the "what" (policy/goal)?
1. What steps does the agent need to follow?
1. Which existing docs does the skill read or write?
1. Create the workflow in `.skills/<name>/README.md`
1. Create thin stubs: `.claude/skills/<name>/SKILL.md`, `.agents/skills/<name>/SKILL.md`
1. Register in `CLAUDE.md` skill table
1. Register in `docs/DOCS.md` §Skills directory
1. Process gap history → `docs/RETROSPECTIVES.md`, never inline in the skill

### Skill lifecycle

```
Accumulate concerns in a section → reach size/complexity threshold →
run concern audit (does every item still share the original purpose?) →
split by boundary → create dedicated skill → keep both lean
```

### Maintenance

Skills add no new knowledge — everything in a skill is derived from docs and reorganized for agent efficiency.

When updating a skill, any useful info removed from the skill must first exist in the corresponding canonical doc. If it does not, add it to the doc before removing from the skill.

**Exception**: skills cataloged as canonical for their workflow (per the Skills directory below) are the source of truth for that procedure — no doc migration needed.

### Skills directory

| File | Scope | Covers | Canonical For |
|------|-------|--------|---------------|
| `.skills/retrospective-analysis/README.md` | Analysis | Process gap identification and classification | Retrospective workflow |
| `.skills/docs-audit/README.md` | Docs | Doc health checks: freshness, cross-refs, scope, encoding, SPDX | Doc audit workflow |
| `.skills/code-audit/README.md` | Code | Code quality and security audit: secrets, redirects, deprecations, crash safety, file safety, test health, bug inventory, repo review | Code audit workflow |
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
| `.skills/merge-gate/README.md` | Merge | Pre-merge workflow: audit, compact, verify CI, merge with discipline | Merge gate workflow |
| `.skills/skill-for-skills/README.md` | Meta | Enforce skills principles, maintain skills in sync with docs, self-maintain | Skill audit workflow |

### Vendor skill stubs (.opencode/skills/, .claude/skills/, .agents/skills/)

Each stub (`SKILL.md`) points to the canonical source in `.skills/<name>/README.md`. These are thin wrappers for tool-specific loading — never author skill content here.

### Commands (.opencode/commands/)

| File | Purpose |
|------|---------|
| `pause.md` | Graceful exit — save session state |
| `finalize.md` | Run staging→current gate and merge |

## CI discipline

Quality management policy (`docs/QUALITY_MANAGEMENT.md` §4) defines why:
CI runs `pytest` asynchronously. Pre-push does not run tests — that's CI's job.

| Trigger | Action |
|---------|--------|
| After **S** task | Push, ignore CI. No check needed. |
| After **M** task | Push → start CI → move to next task. Check CI when you return. |
| M CI fails | Merge fix into current open task. Don't stop current work. |
| **S → ... → M** row | CI must be green after the M that closes the row. |
| Before **L** task | CI must be green. Fix any prior M's CI before starting L. |
| Before **handoff / session end** | CI must be green. |

## Tool recommendation proposals

When the agent identifies a quality gap, propose a tool (see `docs/QUALITY_MANAGEMENT.md` §3 for the philosophy).

Proposal format:

1. **What problem** — the specific bug class, missing validation, type hole, or quality gap
1. **Where** — CI (blocking or advisory), pre-commit, pre-push, or offline review
1. **Cost** — execution time, dependencies, maintenance burden
1. **Alternative** — a simpler approach without a new tool

The user decides whether to adopt. No tool is added without approval.
