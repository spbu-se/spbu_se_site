# merge-gate

<!-- encoding: utf-8 -->

Pre-merge workflow: audit doc health, audit code quality, compact context, verify CI, and merge with proper commit discipline. Collects all findings first, outputs a summary, then executes.
Not a replacement for process docs — reads them, follows their rules.

## When to load

- End of auto-mode batch session (after audit skills)
- Before manual feature branch merge to staging
- On user command "finalize session"

## Workflow

### Phase 1 — Collect

Run each step in sequence, collecting findings without stopping. Do not fix mid-audit — collect everything first.

#### 1.1 Load and run `docs-audit`

Walk through `.skills/docs-audit/README.md` §1-6. Collect findings in a temporary accumulator.

#### 1.2 Load and run `code-audit`

Walk through `.skills/code-audit/README.md` §1-9. Append findings to the same accumulator.

#### 1.3 Context compaction

Follow `docs/DEVELOPMENT_PROCESS.md` §0.6 (Workflow Discipline → Context compaction):

1. Update `docs/DESIGN_DECISIONS.md` with new choices
1. Update `TODO.md` — remove completed items (move to Resolved), reorder backlog
1. Run AI instructions drift check (see `docs/DOCS.md §5.3`)
1. Audit cross-references: scan every `.md` file under `docs/` and `.skills/` for hardcoded step numbers. Replace with section-title references.
1. If session involved doc restructuring or touched 3+ `.md` files, prepare to propose retrospective

#### 1.4 Pre-merge checks

- `uv.lock` in sync with `pyproject.toml` (`uv lock --check`) — regenerate if stale
- Run commit checklist: `mdformat`, `ruff`, `basedpyright`, `pytest -n 2`
- **Verify the session retrospective was run** — every PR must include a
  `docs/RETROSPECTIVES.md` entry (see `docs/DEVELOPMENT_PROCESS.md §0.7`). If the
  PR was opened without one, run `.skills/retrospective-analysis`, add the entry
  as the last commit, and update the PR description.
- Check `origin/staging` CI status

### Phase 2 — Report

Output a summary of all findings:

```
## Merge Gate Report

### Auto-fixed
| Finding | Action |
|---------|--------|
| TODO.md: test opt item still in Planned | Moved to Resolved |
| README.md test count stale | Updated to 1105 |

### Declined (with reason)
| Finding | Reason |
|---------|--------|
| Stale cross-ref in AGENTS.md to .tooling.md | Section no longer exists — manual fix required |

### New issues
| Finding | Severity | Action |
|---------|----------|--------|
| Bare `except:` in flask_se_practice.py:442 | Harm | Reported to CODE_ISSUES.md |

### Audit summary
- docs-audit: <N> issues
- code-audit: <N> issues
- Context compaction: <N> updates
- Pre-merge checks: <pass/fail>
```

For each finding, indicate:

- **Auto-fixed** — was corrected automatically
- **Declined** — was detected but skipped, with reason why (not a fault if reasonable)

The user may ask to expand any section for details.

### Phase 3 — Execute (staging gate)

Only after phase 2 is acknowledged or no blocking issues remain:

1. **Squash-merge** (no GPG — auto branches are throwaway):
   ```bash
   git checkout staging
   git merge --squash <branch>
   git commit -m "<type>: <summary>"
   git push origin staging
   ```
1. **Clean up**: delete local and remote feature branch
1. **Output merge summary**: commit hash, files changed, merge result

### Phase 4 — Execute (current gate — future)

For staging → current merges (after staging gate is validated):

1. Same phase 1-3 as above
1. Ensure `uv lock --check` passes (lock ↔ pyproject parity)
1. **Fast-forward merge** with GPG signoff:
   ```bash
   git checkout current
   git merge --ff-only staging
   git tag -a v<version> -m "<version>"
   git push origin current --tags
   ```
1. **Clean up**: delete merged local branches, list stale remote branches
1. **Update `docs/RETROSPECTIVES.md`** if retro occurred

### Auto-fix rules

| Pattern | Auto-fix? | Method |
|---------|-----------|--------|
| Stale TODO items (completed in Planned) | Yes | Move to Resolved section |
| Stale metrics (test count, coverage %) | Yes | Update from `pytest`/`coverage` output |
| Stale cross-refs (section moved or renamed) | Report only | Risk of wrong target — suggest fix |
| Expired guardrails ("do X until Y") | Report only | Requires human judgment |
| New bug/security findings | Report only | Append to CODE_ISSUES.md, flag for review |

If uncertain: skip, include in report as `⚠️ Skipped: <reason>`. Not a fault if reasonable.

## Dependencies

- Read access to `.skills/docs-audit/README.md`
- Read access to `.skills/code-audit/README.md`
- Read access to `docs/GIT_FLOW.md` §2 (merge strategy)
- Read access to `docs/DEVELOPMENT_PROCESS.md` §0.6 (Context compaction)
- Read access to `docs/DOCS.md` §5.3 (AI drift check)
- Read/write access to `TODO.md`, `docs/ARCHITECTURE.md`
- Git access to merge and push
