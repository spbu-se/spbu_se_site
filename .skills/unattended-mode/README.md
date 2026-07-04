# unattended-mode

Run autonomously — no questions, no signoff, fix CI first.

## When to load

User says "execute in auto mode", "go", or "execute" after plan approval.

## Rules

1. **No questions** — make decisions autonomously. Store unresolved questions in `OPEN_QUESTIONS.md`.
2. **No signoff** — commit with `--no-gpg-sign` to staging. Only merge commits to `current` need signoff (see `doc/GIT_FLOW.md` §4).
3. **Commit granular** — one commit per logical change. Push frequently to trigger CI.
4. **CI is the gate** — if CI fails, stop and fix before new work. `gh run list --branch staging --limit 1 --json status,conclusion` to check.
5. **Plan adherence** — follow the prioritized list. If blocked, skip to next item, note the blocker in `OPEN_QUESTIONS.md`.
6. **Document as you go** — findings go to `.tooling.md`, `doc/TROUBLESHOOTING.md`, or `doc/TOOLING.md` immediately, not at session end.
7. **Process docs are sacred** — minimize updates to process docs (`doc/GIT_FLOW.md`, `doc/DEVELOPMENT_PROCESS.md`) unless user explicitly approved.

## Workflow

1. Accept approved plan
2. Work through items in priority order
3. Commit + push after each logical change
4. Check CI after each push
5. If CI red → fix before next commit
6. If blocked → skip, note in `OPEN_QUESTIONS.md`
7. After last item → report summary
