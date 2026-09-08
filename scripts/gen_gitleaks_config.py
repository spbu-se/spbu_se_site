"""Render .gitleaks.toml from scripts/privacy_gate_config.json (SSOT).

Run `uv run python scripts/gen_gitleaks_config.py` to regenerate after editing
the JSON; run with `--check` to assert the committed file is byte-identical
(wired into the pre-push gate). Never hand-edit .gitleaks.toml.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "scripts" / "privacy_gate_config.json"
OUT = ROOT / ".gitleaks.toml"

_TEMPLATE = """title = "se-site gitleaks config (generated from scripts/privacy_gate_config.json)"

[extend]
useDefault = true

# Allowlist paths are derived from the SSOT scan-scope. Minified artifacts and
# vendored libraries are excluded here (their sources are scanned); thesis is
# public content by decision. Per-finding exceptions use inline `gitleaks:allow`
# comments in code — keep this list directory-level only.
[allowlist]
paths = [
{paths}
]
regexes = [
]
"""


def _regex(path: str) -> str:
    return path.replace(".", r"\.").replace("/", r"\/")


def render() -> str:
    with CONFIG.open(encoding="utf-8") as fh:
        cfg = json.load(fh)
    scope = cfg["scope"]
    prefixes = scope["exclude_path_prefixes"] + scope["vendored_prefixes"]
    entries = [_regex(p) for p in prefixes]
    entries += [_regex(f) for f in scope["theme_main_files"]]
    entries += ["(?i).*" + _regex(s) + "$" for s in scope["minified_suffixes"]]
    paths = "".join(f"  {e!r},\n" for e in entries)
    return _TEMPLATE.format(paths=paths)


def main() -> int:
    text = render()
    if "--check" in sys.argv:
        if OUT.exists() and OUT.read_text(encoding="utf-8") == text:
            print("[gitleaks-config] .gitleaks.toml is up to date")
            return 0
        print(
            "[gitleaks-config] FAILED: .gitleaks.toml is stale — run "
            "`uv run python scripts/gen_gitleaks_config.py`",
            file=sys.stderr,
        )
        return 1
    OUT.write_text(text, encoding="utf-8")
    print(f"[gitleaks-config] wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
