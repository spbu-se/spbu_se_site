# unattended-mode

Run autonomously — no questions, no interaction. Maximize throughput.

## When to load

User says "execute in auto mode", "go", or "execute" after plan approval.

## Rules

1. **No questions** — make decisions autonomously. Store unresolved questions in `OPEN_QUESTIONS.md`.
2. **No signoff** — commit with `--no-gpg-sign` to staging. Only merge commits to `current` need signoff (see `doc/GIT_FLOW.md` §4).
3. **Commit granular** — one commit per logical change. Push frequently to trigger CI.
4. **CI is NOT a gate** — if CI fails, note in `OPEN_QUESTIONS.md`, move to next task. Don't stop on red.
5. **If blocked → skip** — never change the goal. Leave documented state in a `wip/` branch, push, note blocker in `OPEN_QUESTIONS.md`, move to next task. We return later.
6. **Document as you go** — findings go to `.tooling.md`, `doc/TROUBLESHOOTING.md`, or `doc/TOOLING.md` immediately, not at session end.
7. **Process docs are sacred** — minimize updates to process docs (`doc/GIT_FLOW.md`, `doc/DEVELOPMENT_PROCESS.md`) unless user explicitly approved.
8. **Any quality improvement** — features, tests, docs, tooling. Not limited to a priority list.

## WIP branch protocol

Before pushing any `wip/` branch:
- All findings and blockers go to `OPEN_QUESTIONS.md` (or appropriate doc file)
- If no proper doc file exists → fallback to `OPEN_QUESTIONS.md`
- This preserves state and reasoning even if the branch is never revisited

## Workflow

1. Accept approved plan
2. Work through items — skip any blocker immediately
3. Commit + push after each logical change
4. If blocked → `wip/` branch, push, document in `OPEN_QUESTIONS.md`, move to next
5. After last item → report summary with list of blockers and what was achieved
