# MCP Servers & Agent Tooling Policy

<!-- encoding: utf-8 -->

Selection, security, and token policy for Model Context Protocol (MCP) servers and the CLI+skills alternative used by this project's AI agents.

Covers: the CLI/scripts-vs-MCP decision, the adopted/recommended/evaluate/avoid catalog with rationale, security and token-economy rules, and the configuration stance. Does not cover: general per-tool CLI mechanics — see `docs/TOOLING.md`; development process — see `docs/DEVELOPMENT_PROCESS.md`; the tool-proposal format — see `docs/AI_AGENTS.md` §Tool recommendation proposals.

## 1. Why This Exists

This project is AI-assisted and mostly non-interactive, so agent tooling must not silently expand the attack surface or the context budget. Three principles decide every adoption:

1. **Security first** — an MCP server is third-party code running with the agent's credentials and network access. Least privilege, read-only by default, minimal scopes, no secrets in committed config.
1. **Token-economy-safe** — MCP tool schemas load into context on every turn. CLI invocations cost nothing until called; **CLI + skills** (progressive disclosure) is the default lane.
1. **Simple local setup** — prefer tools that work from the shell (`uv`, `npx`, `gh`) with no daemon; keep configuration user-global and out of the repo.

**Default lane (user decision 2026-09-10):** browser/UI verification uses **`playwright-cli` + skills**; Playwright **MCP** is reserved for exploratory/stateful loops. See `docs/AI_AGENTS.md` §UI verification.

## 2. Decision Framework — CLI/scripts vs CLI+skills vs MCP

The cheapest tool that does the job deterministically wins. MCP carries a persistent context and trust cost, so it must earn its place.

| Need | Use | Why |
|------|-----|-----|
| Deterministic, repeatable, CI-schedulable (tests, lint, build, DB queries, deploy) | Repo script or CLI (`pytest`, `ruff`, `gh`, `sqlite3`, `uv`, `npm run build`) | Zero schema cost; runs in CI; reviewed in-repo |
| A good CLI exists and the agent can learn it from a skill | CLI + `.skills/` wrapper | No persistent schema cost; progressive disclosure |
| Interactive, stateful, iterative session (browser DOM/network, traces, container forensics) | MCP | Session state across many small steps outweighs token cost |
| Complex remote API with auth/pagination that changes often (GitHub, Sentry, Context7) | MCP | Centralizes OAuth, pagination, and a typed schema |
| Occasional one-off | CLI | MCP schema cost is not amortized |

**Token economy.** MCP cost ≈ (tools × schema tokens) on every turn, plus verbose structured responses. CLI cost ≈ the command plus bounded output, only when invoked. Mitigations: scope toolsets, gate tools per agent, disable unused patterns (e.g. `"github_*": false`), and pin versions.

**Durable win.** Use MCP to *discover* an interactive flow, then codify it into a script, skill, or test. The script is what persists.

**Never MCP:** anything that must run in CI, and anything a single well-scoped shell command already does.

## 3. Catalog

Trust criteria, in order: vendor-backed or well-maintained? minimal scopes / read-only possible? real project need? token cost justified?

### 3.1 Adopted

| Tool | Lane | Why | How |
|------|------|-----|-----|
| **Playwright CLI** (`@playwright/cli`) | **Default browser verification** | Token-efficient, skill-based, sessions, console/network/tracing; no page data forced into context | `npm install -g @playwright/cli@latest` then `playwright-cli install --skills`; named sessions via `-s=`, headless by default (`--headed` to watch) |
| **Playwright MCP** (`@playwright/mcp`) | Optional exploratory | Persistent state, rich introspection, self-healing/iterative loops | `npx @playwright/mcp@latest`; reserve for sessions where continuous browser context beats the token cost |

Browser artifacts (`.playwright-cli/`, `.playwright-mcp/`) are generated files — keep them out of the tree (see §5).

### 3.2 Recommended (Tier 1)

| Tool | What / why | How (scope it) |
|------|-----------|----------------|
| **Context7** | Up-to-date library/API documentation during implementation; avoids hallucinated APIs | Prefer CLI+skills: `npx ctx7 setup --opencode`; remote endpoint `https://mcp.context7.com/mcp`. Read-only |
| **GitHub MCP** | PR/issue/CI/Dependabot/security triage — auth + pagination handled | Remote `https://api.githubcopilot.com/mcp/` with `oauth:false` + `Authorization: Bearer {env:GITHUB_PERSONAL_ACCESS_TOKEN}`; scope toolsets via the `X-MCP-Toolsets` header; gate with `"tools": {"github_*": false}` and re-enable per agent. **High token cost** — never enable unscoped |
| **Semgrep MCP** | Ad-hoc security scan of a working-tree diff | `uvx semgrep-mcp` or `ghcr.io/semgrep/mcp`; the server now lives in `semgrep/semgrep`. Read-only analysis |

### 3.3 Evaluate (Tier 2)

| Tool | Why it might help | Caveat |
|------|-------------------|--------|
| **Chrome DevTools MCP** | Perf/network/console traces for SEO and Core Web Vitals work | Google-maintained; **sends usage statistics/CrUX data by default** — run with statistics disabled if adopted |
| **Podman MCP** (`manusa/podman-mcp-server`) | Interactive container forensics (inspect logs/processes/networks, debug a failed container) | Community (Go, Apache-2.0), supports Podman + Docker; CLI remains the tool for build/run. Use a rootless socket, minimal scope |
| **Docker MCP Gateway** (`docker/mcp-gateway`) | A *safe runtime* for third-party MCP servers: container isolation, secrets management, OAuth, per-profile tool allowlists | Requires Docker Desktop 4.59+ (CE/WSL2 needs `DOCKER_MCP_IN_CONTAINER=1`); does not apply to Podman-only setups |
| **Sentry MCP** | Error/issue/trace triage **if Sentry is adopted** | Remote `https://mcp.sentry.dev/mcp`, OAuth; some tools need an LLM provider key; broad token scopes. Not used by this project today |
| **SQLite MCP** | Read-only DB exploration | No vendor-backed server (official reference is archived). Prefer `sqlite3` or a repo script; the DB is SQLite+FTS5 |
| **grep.app** (Vercel) | Search public code for usage examples | Optional; `rg` over local vendored packages is usually enough |

### 3.4 Not Recommended — and Why

| Tool | Why not |
|------|---------|
| Official reference **filesystem / git / fetch** servers | Duplicate built-in agent tools; extra process, token cost, and trust surface for no gain |
| **`git-history` / `git_commit` MCP** | Observed unusable here (rejects the workspace path; commit calls time out through pre-commit hooks). Use `git` via the shell — see `docs/AI_AGENT_EXPERIENCE.md` |
| **memory / sequential-thinking** | No project need; would grow the context budget without a durable artifact |
| **PostgreSQL / Redis** MCP | Not in this stack |
| **pytest / ruff** MCP | No credible vendor-backed server; pytest and ruff are deterministic, CI-schedulable CLI tools — MCP adds cost with no benefit |

## 4. Security & Token Rules

**Why:** an MCP server runs arbitrary third-party code with the agent's privileges; a misconfigured one can leak secrets or act unexpectedly.

- **Least privilege** — read-only first; add write tools only when a workflow needs them.
- **Scope toolsets** — register only the tools/workflows you use; disable the rest per agent.
- **No secrets in the repo** — never commit MCP config or tokens. Use user-global config and `{env:VAR_NAME}` interpolation.
- **Pin versions** for adopted servers. `@latest` is acceptable only while evaluating.
- **Prefer local / self-hosted / containerized** servers for anything touching internal data.
- **No MCP in CI** — MCP is interactive-only; CI uses scripts and CLIs.
- **Codify after discovery** — turn a one-off MCP flow into a test or script so it survives without the server.

## 5. Configuration Stance

- **Agent-agnostic snippets, not committed configs.** Document how to configure a server; the developer applies it to their own agent. In-repo, agent-agnostic MCP config is **deferred** until a concrete shared need appears (user decision 2026-09-10).
- **OpenCode specifics** (adapt to your tool): MCP servers live under the `mcp` key; each entry needs `"type": "local"` or `"type": "remote"`; a local `command` is a single array (executable + args); the env key is `environment` (not `env`); set `"oauth": false` when passing a PAT in an `Authorization` header.
- **Generated artifacts** belong in `.tmp/` (gitignored): `.playwright-cli/`, `.playwright-mcp/`. `.local_development.db` is the MCP database exception documented in `docs/DOCS.md` §3.2a.

## 6. Process — Adding or Changing an MCP

Use the proposal format in `docs/AI_AGENTS.md` §Tool recommendation proposals (problem → where → cost → simpler alternative). An MCP is adopted only with user approval, then recorded here; if it changes agent behavior at a decision point, add a retrieval cue in `AGENTS.md`. Maintain: re-check toolset scope and version pins when a server is updated.

## 7. Related

- `docs/AI_AGENTS.md` — AI-agent tool permissions, quirks, skills, and the tool-proposal format.
- `docs/TOOLING.md` — cross-platform CLI mechanics (`uv`, `pytest`, `gh`, PowerShell).
- `docs/AI_AGENT_EXPERIENCE.md` — observed MCP/tooling failures and fallbacks.
- `docs/QUALITY_MANAGEMENT.md` — why quality gates and tool discipline exist.
