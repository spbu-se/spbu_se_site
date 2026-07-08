# js-bundle-analysis

<!-- encoding: utf-8 -->

Extract API contracts, data models, validation rules, and architectural patterns from JS bundles.

## Four-Phase Workflow

### Phase 1: Structural Map

- Identify module structure (Vite/Webpack chunks, entry points)
- Note activation conditions (route patterns, auth guards)
- List SPA routes and their component mappings
- Record storage keys, base URLs, and API basenames

### Phase 2: Surface Scan

- List all API endpoints found in bundles
- Note external URLs, upload constraints, auth requirements
- Identify WebSocket connections and event channels
- Record form validation rules (regex patterns, field limits)

### Phase 3: Deep Dive

- Per-endpoint: extract calling functions, payload shapes, transformations
- Per-model: extract field types, validation rules, default values
- Trace React effects and data flow patterns
- Document enum values and their mappings

### Phase 4: Verification

- Cross-reference extracted schemas against real API traces (curl)
- Validate models against actual responses
- Flag discrepancies between bundle and observed behavior
- Record findings in `docs/` (e.g., `docs/PROJECT_DOCS.md`)

## Tools

- **Prettier / dprint** — format minified JS for readability
- **ripgrep** — search for endpoint patterns (`api/`, `/v1/`, `fetch(`, `axios.`)
- **curl** — verify extracted endpoints against live API
- **Manual analysis** — trace React component tree and data flow

## Rules

- Never modify originals — work on copies in `private/`
- No prod traffic without permission
- Cross-reference with `docs/ARCHITECTURE.md` before recording decisions
