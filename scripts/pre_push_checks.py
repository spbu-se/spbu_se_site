"""Cross-platform pre-push gate (.pre-commit-config.yaml `pre-push-fast-checks`).

Runs the same ordered checks on Linux and PowerShell/Windows. One script (not
separate hooks) because pre-commit continues after a failing always_run hook —
this keeps the explicit fail-fast chain that the former `powershell -Command
"…; if ($?) { … }"` entry provided.
"""

from __future__ import annotations

import subprocess
import sys

CHECKS: list[tuple[str, list[str]]] = [
    (
        "mdformat --check (docs + instruction files)",
        [
            "uv",
            "run",
            "mdformat",
            "--check",
            "docs/",
            "AGENTS.md",
            "CLAUDE.md",
            "README.md",
            "TODO.md",
            ".skills/",
            ".opencode/commands/",
            ".claude/",
            ".agents/",
        ],
    ),
    ("ruff format --check", ["uv", "run", "ruff", "format", "--check", "src/", "tests/"]),
    ("ruff check", ["uv", "run", "ruff", "check", "src/", "tests/"]),
    (
        "pylint similarities",
        ["uv", "run", "pylint", "--disable=all", "--enable=similarities", "src/", "tests/"],
    ),
    (
        "vulture dead-code",
        ["uv", "run", "vulture", "src/", "--min-confidence", "100", "--ignore-names", "is_created"],
    ),
    (
        "asset-pipeline guard",
        ["uv", "run", "pytest", "tests/test_asset_pipeline.py", "--no-cov", "--tb=short"],
    ),
]


def main() -> int:
    for name, cmd in CHECKS:
        print(f"[pre-push] {name}")
        result = subprocess.run(cmd, check=False)
        if result.returncode != 0:
            print(f"[pre-push] FAILED: {name} (exit {result.returncode})", file=sys.stderr)
            return result.returncode
    print("[pre-push] all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
