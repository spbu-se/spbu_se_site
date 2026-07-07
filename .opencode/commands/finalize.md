<!-- encoding: utf-8 -->

______________________________________________________________________

## description: Finalize staging — run the gate and merge to current if approved

Follow `docs/GIT_FLOW.md` §2.2 — Staging → current:

1. Check CI status on staging branch
1. Show `git log --oneline current..staging`
1. Await explicit user approval
1. If approved, run the full staging→current gate:
   retrospective analysis (see `docs/RETROSPECTIVES.md`), code review checklist (`docs/DEVELOPMENT_PROCESS.md` §4.5), backward compat
1. If CI on staging is green after the gate:
   `git checkout current && git merge --ff-only staging`
1. If CI fails on current after merge → stop, don't push, fix in a branch
