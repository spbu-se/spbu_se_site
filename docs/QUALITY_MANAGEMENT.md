# Quality Management

<!-- encoding: utf-8 -->

Quality philosophy, motivation, and policy for the SE Site project. Connects every quality practice to the Supreme Directives: never hurt the user, never hurt the product.

Covers: quality philosophy, quality tiers motivation, agent recommendation protocol reasoning, CI discipline motivation, quality management artifacts catalog. Does not cover: tool-specific options and configs — see `docs/TOOLING.md`, agent instructions — see `docs/AI_AGENTS.md`, testing discipline — see `docs/TESTING.md`, individual bug tracking — see `docs/CODE_ISSUES.md`.

## 1. Quality Philosophy

### Tools are used excessively for code quality

If a quality gap exists, the first question is always: **"Is there a tool that can prevent this?"** A tool may exist that catches the pattern earlier, cheaper, or more reliably than a manual check. Suggest it proactively — do not wait for a 3rd recurrence to escalate from documentation to tooling.

Some tools must be used. The agent suggests, the user chooses. The agent's job is to know the tool landscape, recognize when a gap has a tool-based fix, and propose it with cost and alternatives. The user decides whether the tool's benefit justifies its overhead.

### Connection to doctrine

Quality management traces directly to the two Supreme Directives (`docs/DEVELOPMENT_PROCESS.md` §Process Identity):

- **Supreme I — Never hurt the user**: Bugs reach users through untested code, unvalidated inputs, unchecked types, unresolved vulnerabilities. Every quality practice below exists to intercept these before they ship.
- **Supreme II — Never hurt the product**: Test debt, type debt, security debt, complexity debt — each erodes the product's long-term health. Quality practices are investments against this erosion.

## 2. Quality Tiers

Four tiers, from local convenience to production gate:

| Tier | What | Gate type | Execution time | Authority |
|------|------|-----------|----------------|-----------|
| Pre-commit | Formatters, auto-fix | Polish, skip allowed | ~1s | None — convenience |
| Pre-push | Format check, type check | Early feedback | ~33s | Informational — CI overrides |
| CI | Full test suite, format, types | Authority | ~3min | Source of truth |
| Offline review | Complexity, dead code, security | Deep analysis | Variable | Advisory — user decides |

### Motivation

**Pre-commit as polish**: Formatting noise distracts code review from logic. Auto-fix catches it at the last possible moment before commit. If the hook fails, the user can `--no-verify` — formatting is not a quality gate, it's convenience.

**Pre-push as early feedback**: A format or type error caught at push time costs ~33s. The same error caught by CI costs ~3min plus a full round-trip. The fail-fast chain ensures format failure aborts before type check — no wasted time. Pre-push is a courtesy to the developer, not an authority.

**CI as authority**: The test suite decides whether code ships. Pre-commit and pre-push are fallible — CI is not. Every check that matters must be in CI. Checks in pre-push that are not in CI are advisory only.

**Offline review for depth**: Static analysis (complexity, dead code, dependency audit) and manual review (architecture, design) are too slow or too judgment-dependent for CI. They run before L tasks, before refactoring, or on user request.

## 3. Agent Recommendation Protocol

The agent must suggest tools proactively, not reactively. When a gap is identified at any layer:

1. Ask: **"Can a tool prevent this from happening at all?"**
1. If yes, propose it immediately in this format:
   - **What problem** it solves (specific bug class, missing validation, type hole)
   - **Where** it would run (CI / pre-commit / pre-push / offline review)
   - **Cost** (execution time, dependencies, maintenance burden)
   - **Alternative** — a simpler solution that doesn't require a new tool
1. The user decides whether to adopt. No tool is added without approval.

The exact proposal template and instructions for the agent live in `docs/AI_AGENTS.md` §Tool recommendation proposals.

**Why proactive?** Waiting for a gap to recur 3 times before escalating to tooling (the escalation ladder in `docs/RETROSPECTIVES.md`) is wasteful. The first occurrence is enough to ask "does a tool exist for this?" If it does, suggest it. The ladder is for structural enforcement (pre-commit hooks, CI checks) — not for tool discovery.

## 4. CI Discipline

CI runs tests asynchronously. Deliberate delay between push and result is a feature, not a bug — it lets the developer continue working while the machine validates.

| Principle | Motivation |
|-----------|------------|
| S tasks skip CI check | Lowest risk — formatting-only or single-file changes. Checking CI would add latency without proportional safety. |
| M tasks start CI async | Moderate risk — push, start CI, continue working. Check CI on return. If red, merge fix into current work. Don't stop for it. |
| **S → ... → M** row must end green | A row of S tasks followed by an M means the M closes the row. The row is not finished until CI is green. |
| L tasks require green CI | Highest risk — starting a large task on red CI means the first commits will be fixup, not progress. Fix first, then build. |
| Handoff requires green CI | Session end with red CI leaves the next developer with unknown state. Green means "safe to continue." |
| Whoosh rerun once | Known intermittent race — `EmptyIndexError` or `FileNotFoundError` on `whooshee/`. Rerun clears false positives. If fails twice, it's a real failure. |

The exact trigger table with actions lives in `docs/AI_AGENTS.md` §CI discipline.

## 5. Quality Management Artifacts

Standard techniques for systematic quality management, each with a dedicated artifact:

| Artifact | What it tracks | Why it exists |
|----------|---------------|---------------|
| `docs/CODE_ISSUES.md` | Known production bugs, prioritized by severity | Systematic issue tracking prevents silent regression. Status lifecycle (OPEN → FIXED → verified) ensures nothing is dropped. |
| `docs/RETROSPECTIVES.md` | Process gaps, pattern recurrences, escalation history | Learning from mistakes is the only way to improve process. Pattern recurrence detection with escalation ladder prevents stagnation. |
| `docs/TESTING.md` | Testing discipline, coverage targets, xfail policy | Tests are the primary quality signal. Explicit policy for what to test, what to skip, and what to expect to fail. |
| `docs/TOOLING.md` §Quality Tool Catalog | All quality tools, exact configs, adoption status | Registry of available tools. Prevents "which tool for this job?" debates. User reviews and approves additions. |

## 6. See also

- `docs/AI_AGENTS.md` — Agent instructions for CI discipline and tool proposals
- `docs/TOOLING.md` §Quality Tool Catalog — exact tool configurations
- `docs/TESTING.md` — Testing discipline and coverage targets
- `docs/CODE_ISSUES.md` — Bug inventory
- `docs/DEVELOPMENT_PROCESS.md` — Project doctrine and process identity
- `AGENTS.md` — Pre-flight checklist and environment quirks
