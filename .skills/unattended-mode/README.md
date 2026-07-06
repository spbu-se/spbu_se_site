# unattended-mode

<!-- encoding: utf-8 -->

Run autonomously вЂ” no questions, no interaction. Maximize throughput.

## When to load

User says "execute in auto mode", "go", or "execute" after plan approval.

## Principles

- **Solve first, optimize later** вЂ” implement the solution, then refactor if needed. Never optimize prematurely.
- **Never add complexity over practical value** вЂ” if a change doesn't directly solve the current task, skip it.
- **Try hard before declaring blocked** вЂ” attempt at least 3 distinct approaches before declaring a blocker. Each approach must be real code written and executed. Commit each attempt. Only then document with error evidence and move on.
- **Clear boundaries in code and docs always** вЂ” keep docs and code cleanly separated. Never merge categories.

## Rules

1. **No questions** вЂ” make decisions autonomously. Store unresolved questions in `OPEN_QUESTIONS.md`.
1. **No signoff** вЂ” always commit with `--no-gpg-sign`.
1. **Commit granular** вЂ” one commit per logical change. Push frequently to trigger CI.
1. **CI is NOT a gate** вЂ” if CI fails, note in `OPEN_QUESTIONS.md`, move to next task. Don't stop on red.
1. **If blocked в†’ try 3 approaches first** вЂ” a "blocker" means you attempted at least 3 distinct approaches, each with real code committed, and each failed with a specific error. Only after 3 failed approaches: document the blocker with full error output in `OPEN_QUESTIONS.md`, skip, move to next task.
1. **Re-check target every 5 commits** вЂ” after every 5 commits on the auto branch, compare current metric(s) against the plan's goal(s). If the gap is >15% of the target, continue. If the gap is \<15%, evaluate whether to push through or conclude. For non-numeric goals, ask: "am I closer to the goal than 5 commits ago?" If no, pivot. This applies to ALL auto runs, not just coverage targets.
1. **Verify CI after push** вЂ” after each push, run `gh run list --branch <branch> --limit 1 --json conclusion` and confirm green before proceeding. If red, fix immediately вЂ” do not continue with new work while CI is broken.
1. **Document as you go** вЂ” findings go to `.tooling.md`, `doc/TROUBLESHOOTING.md`, or `doc/TOOLING.md` immediately, not at session end.
1. **Process docs are sacred** вЂ” minimize updates to process docs (`doc/GIT_FLOW.md`, `doc/DEVELOPMENT_PROCESS.md`) unless user explicitly approved.
1. **Any quality improvement** вЂ” features, tests, docs, tooling. Not limited to a priority list.
1. **Plan completion is mandatory** вЂ” do not stop before every task in the approved plan has been attempted with 3 approaches each. The final report must contain evidence for every uncompleted task.

## Branching

- **Always branch from staging** at the very beginning: `git checkout staging && git pull --ff-only origin staging && git checkout -b staging-auto-<UTC-timestamp>`
- Use this branch for all commits. Never commit to staging directly.
- `staging-auto-*` branches are **scratch space** вЂ” commit freely, no garbage rules. CI runs automatically via `ci-staging.yml` (trigger `staging-auto-*`).
- These branches are **never merged raw**. Later, the user squash-merges to staging with clean, feature-grouped commits.
- In non-auto (interactive) mode, merges to staging require GPG signoff.
- UTC timestamp format: `YYYYMMDDTHHMMSSZ` (e.g., `staging-auto-20260704T150706Z`).

## Workflow

1. Record start time (UTC ISO 8601)
1. `git checkout staging && git pull --ff-only origin staging`
1. `uv run pre-commit install --install-hooks` вЂ” ensure hooks are active before any commits
1. `git checkout -b staging-auto-<UTC-timestamp>`
1. Accept approved plan
1. Work through items. For each item:
   - Write tests / code
   - Run, check coverage delta
   - If it fails: try a different approach. Repeat up to 3 times.
   - After 3 failed approaches: commit the attempt, document blocker with error output, move to next item.
1. Commit + push after each logical change (including failed attempts)
1. After every 5th commit: pause, re-check target (Rule 6), document progress in OPEN_QUESTIONS.md.
1. After each push: verify CI is green (Rule 7). If red, fix immediately before new work.
1. After last item в†’ run retrospective, commit lessons to staging-auto branch
1. Make final report commit with structured summary including evidence for every task
1. Report start time, end time, elapsed, results, blockers with error output

## Report commit format

The final commit message must be:

```
docs: auto-run report вЂ” <date>

Started: <UTC timestamp>
Ended:   <UTC timestamp>
Elapsed: <HH:MM:SS>

## Tasks
- <task description> вЂ” <result>

## Blockers (with evidence)
- <task>: Attempt 1: <what was tried and error>
- <task>: Attempt 2: <what was tried and error>
- <task>: Attempt 3: <what was tried and error>

## Open Questions
<full contents of OPEN_QUESTIONS.md here>
```
