<!-- encoding: utf-8 -->

______________________________________________________________________

## description: Finalize — run the gate and merge to current via PR squash-merge

Follow `docs/GIT_FLOW.md` §2.1 — Feature → current:

1. Show `git log --oneline upstream/current..HEAD`
1. Await explicit user approval
1. If approved, run the full gate:
   retrospective analysis (see `docs/RETROSPECTIVES.md`), code review checklist (`docs/DEVELOPMENT_PROCESS.md` §4.5), backward compat
1. Create PR: `gh pr create --base current --head <branch> --title "<summary>"`
1. Wait for CI green: `gh pr checks <number> --watch`
1. Merge: `gh pr merge <number> --squash --delete-branch`
