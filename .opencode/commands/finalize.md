<!-- encoding: utf-8 -->

______________________________________________________________________

## description: Finalize staging — run the gate and merge to main if approved

Follow `doc/GIT_FLOW.md` §2 step 11 — Propose finalization:

1. Check CI status on staging branch
1. Show `git log --oneline main..staging`
1. Await explicit user approval
1. If approved, run the full staging→main gate:
   retrospective analysis, docs sync, §2.7 checklist, backward compat
1. If CI on staging is green after the gate:
   `git checkout main && git merge --ff-only staging`
1. If CI fails on main after merge → stop, don't push, fix in a branch
