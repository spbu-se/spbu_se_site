"""Cross-platform pre-push gate (.pre-commit-config.yaml `pre-push-fast-checks`).

Runs the same ordered checks on Linux and PowerShell/Windows. One script (not
separate hooks) because pre-commit continues after a failing always_run hook —
this keeps the explicit fail-fast chain that the former `powershell -Command
"…; if ($?) { … }"` entry provided.

The asset-pipeline step runs pytest with `-n 0` because spawning xdist workers
fails (OOM / bootstrap EOFError) on memory-constrained Windows machines under
the default worker count.
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
        "gitleaks config drift (SSOT)",
        ["uv", "run", "python", "scripts/gen_gitleaks_config.py", "--check"],
    ),
    (
        "dev-privacy full-tree (artifacts + local paths)",
        ["uv", "run", "python", "scripts/check_dev_privacy.py", "--all"],
    ),
    (
        "asset-pipeline guard",
        [
            "uv",
            "run",
            "pytest",
            "tests/test_asset_pipeline.py",
            "--no-cov",
            "--tb=short",
            "-n",
            "0",
        ],
    ),
    (
        "person-names in published docs",
        ["uv", "run", "python", "scripts/check_person_names.py"],
    ),
    (
        "merge conflict markers",
        [
            "uv",
            "run",
            "bash",
            "-c",
            r'grep -rn "^<<<<<<< .*\|^=======\$\|^>>>>>>> .*" src/ tests/ scripts/ --include="*.py" --include="*.sh" --include="*.yml" --include="*.yaml" --include="*.html" --include="*.css" --include="*.js" 2>/dev/null; rc=$?; [ $rc -ge 2 ] && exit 0; [ $rc -eq 0 ] && exit 1; exit 0',
        ],
    ),
]


def warn_hardcoded_section_refs() -> None:
    """Warning-only: hardcoded §N refs in docs/ (too many existing to fail)."""
    import re
    from pathlib import Path

    pattern = re.compile(r"§\d+(\.\d+)?")
    hits: list[str] = []
    for path in sorted(Path("docs").glob("*.md")):
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if pattern.search(line):
                hits.append(f"{path}:{lineno}: {line.strip()}")
    if hits:
        print(f"[pre-push] WARNING: {len(hits)} hardcoded §N refs in docs/ (non-blocking)")
        for hit in hits[:10]:
            print(f"  {hit}")


def main() -> int:
    for name, cmd in CHECKS:
        print(f"[pre-push] {name}")
        result = subprocess.run(cmd, check=False)
        if result.returncode != 0:
            print(f"[pre-push] FAILED: {name} (exit {result.returncode})", file=sys.stderr)
            return result.returncode
    warn_hardcoded_section_refs()
    print("[pre-push] all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
