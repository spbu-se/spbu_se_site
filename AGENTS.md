# SE Site

<!-- encoding: utf-8 -->

Сайт кафедры системного программирования СПбГУ.
`docs/DEVELOPMENT_PROCESS.md` for full workflow. `docs/GIT_FLOW.md` for branching.
`docs/TESTING.md` for testing strategy.

Available skills: `docs/AI_AGENTS.md` lists all `.skills/<name>/` workflows.
Read the matching `.skills/<name>/README.md` manually before starting a task — the `skill` tool does not surface project skills.

Every line must answer: "Would an agent likely miss this without help?" If not, cut it.
CLAUDE.md defers to this file. This file defers to `docs/`.

## Pre-flight checklist

- `git fetch --prune origin upstream`
- Create a branch BEFORE any work: `git checkout -b <prefix>/<short-desc> upstream/current`
  Prefixes: feat/, fix/, refactor/, docs/, test/, chore/, ci/
  (see `docs/GIT_FLOW.md` §1.1). Never commit directly to `current`.
- Verify current branch is NOT `current`: `git branch --show-current`
- Check `upstream/current` CI — `gh run list --repo spbu-se/spbu_se_site --branch current --limit 1 --json conclusion` — if red, stop and fix first
- **Read the skill README for this task** — identify which task/skill matches (e.g., `retrospective-analysis`, `test-writer`, `merge-gate`) and read `.skills/<name>/README.md` before starting. Confirm by stating which skill READMEs were read.
- Before using `2>&1`, flatten ErrorRecords with `| ForEach-Object { "$_" }` or suppress stderr with `2>($null)` — see `docs/TOOLING.md` §PowerShell
- Before writing piped/chained commands, read `docs/TOOLING.md` §PowerShell
- Before editing any doc, re-read its first 5 lines (scope/aim header). Verify your changes match that scope. If existing content doesn't match, flag it.
- After any command that produces error output or non-zero exit, ask: "Was this expected?" If unexpected, stop and investigate.
- **Timeout recovery**: if a command times out, READ the partial output — calc ETA from progress rate → retry ONCE with right timeout. See `docs/AI_AGENT_EXPERIENCE.md` for the failure pattern.
- Before merge: verify CI shows test results, not just lint results — inspect the CI run log to confirm pytest actually ran, not just basedpyright
- Before merging a pushed feature branch: CI won't trigger on the branch. Create a PR first, wait for CI green, then squash-merge via `gh pr merge --squash --delete-branch`
- Before merging any dependabot PR: verify its head is a descendant of the base branch (`git diff --stat upstream/current..<head>` must show only the intended files — GH PR metadata is cached and can underreport the real delta). Dep bumps that feed the asset pipeline (`esbuild`, `terser`, `purgecss`) must also regenerate the committed min outputs (`npm run build`). Repair recipe: `docs/TOOLING.md` §Dependabot PR repair; CI gate: `.github/workflows/dependabot-gate.yml`
- **Multi-PR sessions**: branch each PR from `upstream/current` — never from a sibling PR's branch (stacking + squash-merge rewrites hashes → merge conflicts). Only stack on a real code dependency and rebase dependents onto `upstream/current` after each merge. Each PR carries only its own retro; never drop merged retros when resolving conflicts. Parallel PRs that append to the same docs (`RETROSPECTIVES.md`, `PERFORMANCE.md`) conflict at the shared tail — merge sequentially and resolve by keeping all entries. See `docs/GIT_FLOW.md §8.5`.
- Before merge: verify TODO.md has no completed items that belong in commit messages instead
- Before deleting any branch (local or remote): prove it is merged via `gh pr list --repo <owner>/<repo> --state merged --json number,headRefName` — squash-merged branches are never ancestors of `staging`/`current`, so `git branch --merged` and `-d` can't detect them; forced `-D` is justified only by merged-PR evidence. See `docs/AI_AGENT_EXPERIENCE.md`.
- **Session retrospective is mandatory before any PR** — run `.skills/retrospective-analysis` and append the entry to `docs/RETROSPECTIVES.md` before opening the PR. If a PR was opened without it, add the retro as the last commit and update the PR description. See `docs/DEVELOPMENT_PROCESS.md` §0.7.
- Before any session summary or handoff: scan `docs/AI_AGENTS.md` §Output Format for the prescribed format — comply with timing, state, and section structure
- When running tests: default to `--tb=long` for full diagnostics on first run. Only use `-q` for the final green confirmation when zero failures are expected. Never truncate a diagnostic run's output (`Select-Object -Last/-First`, `head`/`tail`) — let the full log be captured and search the captured file instead. See `docs/TESTING.md` §3a.
- Proactively use `git-history_git_wrapup_instructions` at session start (orientation snapshot), mid-session (checkpoint against acceptance criteria), and pre-merge (readiness gate) — not just at the end. See `docs/DEVELOPMENT_PROCESS.md` §0.7 (Session lifecycle — wrap-up protocol).
- Before staging templates/HTML or Python: run the auto-fix hooks on ALL files first (`pre-commit run djlint --all-files` for templates, `uv run ruff format src/` for Python) — these hooks reformat more than the staged set and abort with "Stashed changes conflicted with hook auto-fixes" if staged edits differ. See `docs/AI_AGENT_EXPERIENCE.md` §djLint / §ruff-format.
- If a template change introduces a **new CSS class**, regenerate the purged/minified assets (`npm run build`) or the CI `assets` drift job fails — do it AFTER rebasing onto merged `current`, never before (single-line min file conflicts on squash-merge). See `docs/TOOLING.md` §Purged/minified assets.
- Verify the active branch before committing — `git branch --show-current` must be the intended feature branch, never `current`/`staging`. If work was committed to the wrong branch, recover via `git cherry-pick -n` + `git commit --no-gpg-sign` (see `.tooling.md` §cherry-pick).
- Before creating any PR: include `Closes #<n>` / `References #<n>` per fixed/referenced issue in the body (one per line). See `docs/AI_AGENTS.md` §PR description.
- Always learn, never forget — encode patterns before session ends

## Live metrics

Always query live, never hardcode:

| Metric | Command | Duration |
|--------|---------|----------|
| Test count + xfails | `pytest --tb=no -q` | ~7 min |
| Coverage | `pytest --cov=src --cov-report=term-missing` | ~8 min |
| CI status | `gh run list --repo spbu-se/spbu_se_site --branch current --limit 1 --json conclusion` | ~2s |
| pyright ignores | `basedpyright src/` | ~30s |

See `docs/QUALITY_MANAGEMENT.md §6` for interpretation thresholds.

## Quality gates

Three tiers of quality, from local convenience to production gate. Full mechanics in `docs/DEVELOPMENT_PROCESS.md §0.6`; tier rationale in `docs/QUALITY_MANAGEMENT.md §2`.

- **Pre-commit** (fast, ~1s, changed files only): runs on `git commit`, auto-fixes formatting. Not a quality gate — local commits can be imperfect; `git commit --no-verify` is acceptable if a hook genuinely blocks you for a non-formatting reason.
- **Pre-push** (strict, all files, fail-fast): runs on `git push`. Checks in order: requirements format → actionlint → `uv lock --check` → format + lint (mdformat, ruff format `--check`, ruff check on `src/ tests/`, via PowerShell) → basedpyright. Failure at any step aborts. This is the real local quality gate.
- **CI** (async, ~10min): pytest runs on CI, not pre-push. See `docs/AI_AGENTS.md` §CI discipline for when to check.

**Windows-only pre-push step**: the format+lint step's entry is `powershell -Command "..."` — on Linux it fails with `Executable 'powershell' not found`. Run the equivalent checks manually:

```bash
uv run mdformat --check docs/ AGENTS.md CLAUDE.md README.md TODO.md .skills/ .opencode/commands/ .claude/ .agents/
uv run ruff format --check src/ tests/
uv run ruff check src/ tests/
```

Before every `git push`, verify locally: `uv run pre-commit run --all-files --hook-stage pre-push` and fix any failures.

**Never use `git push --no-verify`** unless the user gives a direct, unbiased instruction.
An unbiased instruction states the goal without suggesting the method. Every `--no-verify` must be logged in the retrospective as a process violation.

### Merge to `current`

PRs are squash-merged into `current` via `gh pr merge --admin --squash`. Never push directly to `current`.
CI must be green before merging (see `docs/AI_AGENTS.md` §CI discipline).

### First-time setup

```powershell
uv run pre-commit install --install-hooks --hook-type pre-commit --hook-type pre-push
```

## Testing quirks

- **FTS5 search index in session DB template** — `_seeded_db_path` (seeded) session fixture builds the DB once; FTS5 index lives inside the DB file, so per-test `shutil.copy2` copies it (~ms). No separate index management (Whoosh was replaced by SQLite FTS5 in PR #11).
- **Application factory** — `create_app(config_overrides, start_scheduler)` in `flask_se.py`; module-level `app = create_app()` singleton preserved for wsgi/scripts/tests. `config_overrides` builds test instances without import-time patching.
- **scrypt unsupported on Python 3.13** — conftest.py mocks `check_password_hash` at module level
- **APScheduler gated off in tests** — conftest sets `SE_START_SCHEDULER=0` before importing `flask_se` (replaces the old `scheduler.shutdown()`). Production leaves it unset → jobs run.
- **Login bypass fixture** — `logged_client` injects `session["_user_id"]` instead of POST login (avoids scrypt)

## Environment quirks

- **Main branch**: `current` (not `main`)
- **Config files** (never committed): `flask_se_secret.conf`, `flask_se_mail.conf`, `flask_se_practice_yandex_secret.conf`, `flask_se_vk_secret.conf`, `flask_se_thesis.conf`
- **requirements.txt staleness** — CI runs `pip install -r` on every push. Must match `uv.lock`. Always regenerate before pushing
- **Line endings** — `.gitattributes` normalizes all text to LF (`* text=auto eol=lf`), so checkouts are LF on Windows too; mdformat behaves identically locally and in CI
- **GPG keylocker** — if `git config commit.gpgsign` is true, use `git commit --no-gpg-sign` on all branches (only `current` gets signed commits)
- **Config-secret path vs contents** — secrets live in config files, and the code reads their **contents** via `flask_se_config.read_secret_from_file()`. Never treat a config file's *path* as the secret (that was CVE-class bug: `SECRET_KEY` was a path string → forgeable sessions). CSRF is globally enforced (`CSRFProtect`): any new POST form must include `{{ csrf_token() }}`, and new state-changing actions must be POST, not GET
- **Generated/temp files** — all scratch and generated files must live in `.tmp/` (gitignored): session notes, log captures, route-map dumps, release-note drafts. Never leave them at the repo root. See `docs/DOCS.md` §3.

## Process improvement

- **Root-cause analysis** — when something goes wrong, fix the root cause, not the symptom (a surface fix repeats). Trace past the surface error to one of: **missing hook** (no trigger/checklist exists — add one), **missing in docs** (knowledge wasn't recorded — write it down), **forgot to search** (add a "check docs" step), **ignored error signal** (tool produced `fatal:` but execution continued — add an "On tool error" hook).
- **Gaps escalate** — 1st occurrence: document (canonical doc); 2nd: automate (CI check or pre-commit hook); 3rd+: tool config (linter rule, structural guard).
- **Safe updates** (when removing/changing documented content) — (1) would removing this change agent behavior? if yes, keep it; (2) is the claim provably wrong? only then delete/correct — verify against executable sources (config, workflow, code); (3) does it enforce a docs/structure contract? keep structural-convention rules even when the wording looks generic. Rationale must never be deleted — relocate it, don't drop it.
