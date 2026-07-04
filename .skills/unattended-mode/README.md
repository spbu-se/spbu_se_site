# unattended-mode

Run autonomously — no questions, no interaction. Maximize throughput.

## When to load

User says "execute in auto mode", "go", or "execute" after plan approval.

## Principles

- **Solve first, optimize later** — implement the solution, then refactor if needed. Never optimize prematurely.
- **Never add complexity over practical value** — if a change doesn't directly solve the current task, skip it.
- **Safeguards are valuable, but throughput is priority** — in auto mode, keep moving. User reviews returns. Blocked? Skip. Unanswered questions? `OPEN_QUESTIONS.md`.
- **Clear boundaries in code and docs always** — keep docs and code cleanly separated. Never merge categories.

## Rules

1. **No questions** — make decisions autonomously. Store unresolved questions in `OPEN_QUESTIONS.md`.
1. **No signoff** — always commit with `--no-gpg-sign`.
1. **Commit granular** — one commit per logical change. Push frequently to trigger CI.
1. **CI is NOT a gate** — if CI fails, note in `OPEN_QUESTIONS.md`, move to next task. Don't stop on red.
1. **If blocked → skip** — never change the goal. Leave documented state, note blocker in `OPEN_QUESTIONS.md`, move to next task. We return later.
1. **Document as you go** — findings go to `.tooling.md`, `doc/TROUBLESHOOTING.md`, or `doc/TOOLING.md` immediately, not at session end.
1. **Process docs are sacred** — minimize updates to process docs (`doc/GIT_FLOW.md`, `doc/DEVELOPMENT_PROCESS.md`) unless user explicitly approved.
1. **Any quality improvement** — features, tests, docs, tooling. Not limited to a priority list.

## Branching

- **Always branch from staging** at the very beginning: `git checkout staging && git pull --ff-only origin staging && git checkout -b staging-auto-<UTC-timestamp>`
- Use this branch for all commits. Never commit to staging directly.
- Never merge this branch — it's a throwaway artifact for traceability.
- UTC timestamp format: `YYYYMMDDTHHMMSSZ` (e.g., `staging-auto-20260704T150706Z`).

## Workflow

1. Record start time (UTC ISO 8601)
1. `git checkout staging && git pull --ff-only origin staging`
1. `git checkout -b staging-auto-<UTC-timestamp>`
1. Accept approved plan
1. Work through items — skip any blocker immediately
1. Commit + push after each logical change
1. If blocked → document in `OPEN_QUESTIONS.md`, move to next
1. After last item → make a final report commit with structured summary
1. Report start time, end time, elapsed, successes, blockers

## Report commit format

The final commit message must be:

```
docs: auto-run report — <date>

Started: <UTC timestamp>
Ended:   <UTC timestamp>
Elapsed: <HH:MM:SS>

## Tasks
- <task description> — <result>

## Blockers
- <if any>
```
