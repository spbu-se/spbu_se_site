# Session Root-Cause Analysis — 2026-09-18

## Mistakes and wrong decisions

| # | Incident | Root cause | Process gap | Severity |
|---|----------|------------|-------------|----------|
| 1 | Committed `.omo/` boulder refs to AGENTS.md + DEVELOPMENT_PROCESS.md | Didn't check that process docs serve all devs, not just OMO users | No "audience check" in pre-flight | HIGH |
| 2 | upload.py converted to LFS pointer by encoding-sweep commit | Modified LFS-tracked file without understanding LFS mechanics | No "LFS-aware file edit" guardrail | MEDIUM |
| 3 | Checked prod URL instead of staging URL | Didn't read docs/TOOLING.md §Staging environment | No "read docs before action" check in tooling | MEDIUM |
| 4 | SSH-signed tag instead of GPG-signed | User's `git config gpg.format = ssh` silently overrides `git tag -s`; no pre-tag check | No pre-tag signing-format guardrail | **BLOCKING** |
| 5 | Release checklist not run before tagging | No automated pre-tag gate — checklist is manual, easy to skip | No automated gate linking tagging to checklist completion | HIGH |
| 6 | Post-deploy smoke test not performed after 5 CD runs | No automated health check in CD workflow (added in PR #330 as a fix for this) | No post-deploy verification step | HIGH |
| 7 | Release draft attached to `untagged-*` instead of existing tag | Didn't verify tag SHA matches current HEAD before creating draft | No "verify tag position" step in release procedure | LOW |
| 8 | `app.logger` in boot-time code | Not idiomatic Python logging — should have used `logging.getLogger(__name__)` | No lint rule for `app.logger` outside request context | LOW |
| 9 | Skipped retro before some PRs | Rushed through PR chain — each PR should have its own retro | Retro requirement not enforced (manual AGENTS.md check only) | MEDIUM |
| 10 | Committed to `current` (branch violation) | Didn't verify `git branch --show-current` before committing | Branch-protection AGENTS.md check skipped | HIGH |

## Recurring patterns

| Pattern | Occurrences | Escalation |
|---------|-------------|------------|
| Process doc exists but was not followed | 5 (tagging, checkout, pre-push, retro, staging check) | Layer 2: CI gate or pre-hook |
| Tool config vs docs mismatch | 2 (gpg.format, staging URL) | Layer 1: pre-flight checklist |
| LFS file corruption | 2 (upload.py in docs-drift-review, upload.py in encoding hook) | Layer 2: LFS guardrail in pre-commit |
| Skipped verification step | 3 (staging after deploy, signing before tag, checklist before tag) | Layer 1: add to pre-flight + Layer 2: CI gate |

## Proposed improvements

### Layer 1 — Pre-flight checklist (AGENTS.md)
- [ ] Add "Verify gpg.format is GPG" step before tagging (already done in PR #329)
- [ ] Add "Verify staging deploy after CD" step (already done in PR #330)
- [ ] Add "Read docs/TOOLING.md §Staging URL before inspecting staging" step
- [ ] Add "Check if file is LFS-tracked before editing" step

### Layer 2 — Automated gates
- [ ] Pre-tag CI check: verify tag signing format is GPG (not SSH, not lightweight) — `git config --get gpg.format` must be `gpg` or unset
- [ ] Post-deploy CI check: polling loop for /staging/ health (added in PR #330)
- [ ] Pre-commit LFS guardrail: `git lfs ls-files` on staged files, warn if modifying LFS-tracked content
- [ ] Pre-push branch-name check: reject commits with `git branch --show-current = current`

### Layer 3 — Docs updates
- [ ] AGENTS.md pre-flight: reorder critical checks to top (branch verification, retro, pre-push gate)
- [ ] DEVELOPMENT_PROCESS.md: add "verify signing format" to release process
- [ ] RELEASE_CHECKLIST.md: B11 already fixed to accept GPG or SSH; add "verify tag SHA matches upstream/current HEAD"

### Scripts
- [ ] `scripts/pre-tag-check.sh`: verifies gpg.format, signingkey, checklist completion, tag position
- [ ] `scripts/verify-deploy.sh`: curl polling loop against /staging/ (mirror of the CD workflow step)