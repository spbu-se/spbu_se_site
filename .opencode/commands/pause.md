<!-- encoding: utf-8 -->

______________________________________________________________________

## description: Graceful exit — save session state and unfinished plan

Save session state to `.unfinished.plan.md`:

1. Check `git status --short` for dirty/uncommitted files and current branch
1. Write `.unfinished.plan.md` with:
   - Date/time, focus task summary
   - Current branch, last commit hash
   - Dirty/untracked files
   - Completed steps
   - Remaining actions
   - Undocumented decisions made during session
   - Next steps to resume
1. If on a feature branch with unfinished code and context switch is needed:
   a. `git add -A && git commit -m "wip: <summary>"`
   b. Create `_UNFINISHED.md` with richer context (why partial, design rationale, next steps)
   c. `git add _UNFINISHED.md && git commit -m "docs: save _UNFINISHED.md with context"`
1. Output compaction summary to user: what was done, what remains
