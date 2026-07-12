______________________________________________________________________

## name: readme-generator description: Generate a polished project-specific README. Load when user says "generate readme", "update readme", "improve readme", "create readme". Works for Web, CLI, and Library projects.

# readme-generator

<!-- encoding: utf-8 -->

Generates a project-specific README by probing the repository structure. Works for Web apps, CLI tools, and Python/Node/Rust libraries.

## Workflow

### 0. Licensing rules (agent must follow strictly)

1. **Never modify LICENSE** — the LICENSE file in the repo root is final. Do not edit, replace, or delete.
1. **Missing LICENSE?** — do NOT create one. Ask the user to add one. Mention every pushed file needs a license.
1. **Present LICENSE?** — that is THE license. Extract its SPDX identifier. Use it on every new file.
1. **Multiple licenses?** — document in README. Keep a note for yourself.
1. **SPDX on every file** — every source file (`.py`, `.js`, `.rs`, `.ts`, etc.) you create or edit must get an SPDX header matching the repo's license:
   - MIT: `# SPDX-License-Identifier: MIT`
   - Apache-2.0: `# SPDX-License-Identifier: Apache-2.0`
   - GPL-3.0: `# SPDX-License-Identifier: GPL-3.0-or-later`
1. **Auto-attribute** — all content developed for the project inherits the project's license. No additional copyright notice beyond the SPDX header.

### 1. Probe the project

Use `uv run python -c` for cross-platform probing (works on Windows, Linux, macOS):

```bash
uv run python -c "
import json, os, re, subprocess, sys
from pathlib import Path

root = Path('.')

# --- Repo identity ---
try:
    r = subprocess.run(['git', 'remote', 'get-url', 'origin'], capture_output=True, text=True)
    remote = r.stdout.strip()
    m = re.search(r'[:\/]([^\/]+\/[^\/\.]+?)(\.git)?$', remote)
    owner_repo = m.group(1) if m else ''
    owner, repo = owner_repo.split('/', 1) if '/' in owner_repo else ('', '')
except Exception:
    owner, repo = '', root.name

info = {'owner': owner, 'repo': repo}

# --- Project type ---
if (root / 'pyproject.toml').exists():
    text = (root / 'pyproject.toml').read_text(encoding='utf-8')
    has_wsgi = bool(re.search(r'(flask|django|fastapi|starlette|bottle|tornado)', text, re.I))
    has_cli = bool(re.search(r'console_scripts|scripts', text))
    has_app_file = any((root / 'src' / f).exists() for f in ['flask_se.py', 'app.py', 'manage.py', 'wsgi.py'])
    if has_wsgi or has_app_file:
        info['type'] = 'web'
    elif has_cli:
        info['type'] = 'cli'
    else:
        info['type'] = 'library'
elif (root / 'package.json').exists():
    info['type'] = 'node'
elif (root / 'Cargo.toml').exists():
    info['type'] = 'rust'
else:
    info['type'] = 'unknown'

# --- Metadata ---
if (root / 'pyproject.toml').exists():
    text = (root / 'pyproject.toml').read_text(encoding='utf-8')
    for key in ['name', 'version', 'description', 'requires-python']:
        m = re.search(f'^{key} = \"(.+)\"', text, re.M)
        info[key] = m.group(1) if m else ''
    m = re.search(r'^license = \"(.+)\"', text, re.M)
    info['license_pyproject'] = m.group(1) if m else ''

if (root / '.python-version').exists():
    info['dev_python'] = (root / '.python-version').read_text(encoding='utf-8').strip()

# --- License from file ---
if (root / 'LICENSE').exists():
    header = (root / 'LICENSE').read_text(encoding='utf-8', errors='replace')[:300]
    m = re.search(r'(MIT|Apache|GPL|BSD|MPL)', header, re.I)
    info['license'] = m.group(1) if m else 'custom'
elif info.get('license_pyproject'):
    info['license'] = info['license_pyproject']
else:
    info['license'] = ''

# --- CI workflows ---
wf_dir = root / '.github' / 'workflows'
if wf_dir.exists():
    wfs = [f.stem for f in wf_dir.glob('*.yml')]
    ci = [w for w in wfs if re.search(r'ci|test', w, re.I)]
    info['ci_workflow'] = ci[0] if ci else (wfs[0] if wfs else '')
    info['all_workflows'] = wfs
else:
    info['ci_workflow'] = ''

# --- Config files ---
configs = []
for p in root.rglob('*'):
    if p.suffix in ('.conf',) or p.name.startswith('.env'):
        configs.append(str(p.relative_to(root)))
info['config_files'] = sorted(configs)[:10]

# --- Docker ---
info['has_docker'] = (root / 'Dockerfile').exists()
info['has_dockercompose'] = (root / 'docker-compose.yml').exists()

# --- Docs ---
info['docs'] = sorted([str(f.relative_to(root)) for f in (root / 'doc').glob('*.md')]) if (root / 'doc').exists() else []

# --- CLI entry points ---
if info.get('type') == 'cli' and (root / 'pyproject.toml').exists():
    text = (root / 'pyproject.toml').read_text(encoding='utf-8')
    eps = re.findall(r'\"(.+)=(.+)\"', text[text.find('console_scripts'):]) if 'console_scripts' in text else []
    info['cli_commands'] = [e[0].strip() for e in eps]

# --- Test command ---
if (root / 'pyproject.toml').exists():
    info['test_cmd'] = 'pytest'
elif (root / 'package.json').exists():
    info['test_cmd'] = 'npm test'
elif (root / 'Cargo.toml').exists():
    info['test_cmd'] = 'cargo test'
else:
    info['test_cmd'] = ''

# --- Output ---
print(json.dumps(info, indent=2))
"
```

Parse the JSON output from the Python probe into variables:

```
owner=<from probe>
repo=<from probe>
type=<web|cli|library|node|rust>
name=<project name>
version=<version>
description=<description>
python_req=<requires-python>
dev_python=<dev python version>
license_identifier=<SPDX identifier>
ci_workflow=<first CI workflow name>
config_files=<list of config files>
has_docker=<bool>
has_dockercompose=<bool>
docs=<list of doc paths>
cli_commands=<list of CLI entry points>
test_cmd=<test command>
```

SPDX identifier mapping:

| LICENSE content | SPDX header |
|---|---|
| MIT | `# SPDX-License-Identifier: MIT` |
| Apache | `# SPDX-License-Identifier: Apache-2.0` |
| GPL | `# SPDX-License-Identifier: GPL-3.0-or-later` |
| BSD | `# SPDX-License-Identifier: BSD-3-Clause` |
| MPL | `# SPDX-License-Identifier: MPL-2.0` |
| other | `# SPDX-License-Identifier: <as-detected>` |

### 2. Build sections by project type

| LICENSE content | SPDX header |
|---|---|
| MIT | `# SPDX-License-Identifier: MIT` |
| Apache | `# SPDX-License-Identifier: Apache-2.0` |
| GPL | `# SPDX-License-Identifier: GPL-3.0-or-later` |
| BSD | `# SPDX-License-Identifier: BSD-3-Clause` |
| MPL | `# SPDX-License-Identifier: MPL-2.0` |
| other | `# SPDX-License-Identifier: <as-detected>` |

### 2. Build sections by project type

| Section | Web | CLI | Library | Always |
|---------|-----|-----|---------|-------|
| Title + description | ✓ | ✓ | ✓ | ✓ |
| Badges | ✓ | ✓ | ✓ | ✓ |
| Screenshot (placeholder) | ✓ | — | — | |
| Prerequisites | ✓ | ✓ | ✓ | ✓ |
| Quick start | ✓ | ✓ | ✓ | ✓ |
| Configuration | ✓ | ✓ | ✓ | |
| Commands / Routes | ✓ | ✓ | — | |
| Usage examples | ✓ | ✓ | ✓ | |
| Deployment | ✓ | — | — | |
| Project structure | ✓ | ✓ | ✓ | ✓ |
| Documentation links | ✓ | ✓ | ✓ | ✓ |
| Contributing | ✓ | ✓ | ✓ | ✓ |
| Troubleshooting | ✓ | ✓ | ✓ | ✓ |
| License | ✓ | ✓ | ✓ | ✓ |

### 3. Generate markdown

Build the README from probed data. Common section templates:

**Badges:**

```markdown
[![CI](https://github.com/{owner}/{repo}/actions/workflows/{ci_workflow}.yml/badge.svg)](https://github.com/{owner}/{repo}/actions)
[![Python](https://img.shields.io/badge/python-{version}-blue)](.python-version)
[![License](https://img.shields.io/badge/license-{license}-green)](LICENSE)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
```

**Quick start (pip):**

```bash
python -m venv venv
# Windows: venv\Scripts\activate
source venv/bin/activate
pip install -r requirements.txt
```

**Quick start (uv):**

```bash
uv sync
```

**Configuration:**
List actual `.conf` and `.env.example` files found. Reference each.

**Documentation:**
Link to each detected `docs/*.md` file with its purpose from the first line.

### 4. Format and present

Run `mdformat` on the generated content. Present to user in a code block. **Do NOT overwrite README.md** — wait for explicit user approval.

## Notes

- Repo-agnostic: badges use the detected remote from `git remote get-url origin`
- Preserve existing README — show diff if overwriting
- If CI workflow not found, omit CI badge
- Troubleshooting — check `docs/TOOLING.md` and `docs/AI_AGENT_EXPERIENCE.md` for common errors and debugging trails
- **SPDX on every push**: any new file you create or edit gets an SPDX header matching the repo's license. If no SPDX scheme exists in the repo, use `# SPDX-License-Identifier: <license>` for `.py` files, `// SPDX-License-Identifier: <license>` for `.js`/`.rs`/`.ts` files.
- **Missing SPDX in repo**: if existing files lack SPDX headers, suggest adding them in a future task. Do NOT add them without user approval (bulk SPDX addition is a deliberate change, not a formatting fix).
