# merge-gate

<!-- encoding: utf-8 -->

> **Last updated**: 2026-09-18 — Rewrote Phase 3/4 from two-branch staging→current model to single-branch feature→current via PR model (GIT_FLOW.md changed).

Pre-merge workflow: audit doc health, audit code quality, compact context, verify CI, and merge with proper commit discipline. Collects all findings first, outputs a summary, then executes.
Not a replacement for process docs — reads them, follows their rules.

## When to load

- End of auto-mode batch session (after audit skills)
- Before manual feature branch merge via PR to current
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
- Check CI status on the target branch

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

### Phase 3 — Execute (feature → current via PR)

Only after phase 2 is acknowledged or no blocking issues remain:

1. **Create a PR** (if not already open):
   ```bash
   gh pr create --base current --head <branch> --title "<type>: <summary>"
   ```
1. **Wait for CI green**:
   ```bash
   gh pr checks <number> --watch
   ```
   If CI fails, fix on branch, push, retry.
1. **Squash-merge** (GitHub-signed, auto-verified):
   ```bash
   gh pr merge <number> --squash --delete-branch
   ```
1. **Clean up**: delete local feature branch
1. **Post-merge deploy verification**: confirm the deploy landed — the latest
   deployment on the upstream repo must point at the merged SHA with
   `state == success`.
1. **Output merge summary**: commit hash, files changed, merge result

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
