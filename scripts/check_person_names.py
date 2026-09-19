# -*- coding: utf-8 -*-
"""Pre-push gate: reject published docs containing GitHub @usernames, emails,
or ``Contributors`` headers. Use placeholder roles instead.

Called from ``pre_push_checks.py`` as ``uv run python scripts/check_person_names.py``.
"""

from __future__ import annotations

import re
import subprocess
import sys

# Files in scope — only published docs (private tooling/notes excluded)
SCOPE_GLOB = ("docs/", "README.md", "AGENTS.md", "CLAUDE.md", "TODO.md")

# Patterns that indicate a real person reference
PERSON_PATTERNS: list[tuple[str, str]] = [
    (r"^Contributors", "Contributors header — use placeholder roles"),
    (r"<[^>]+@[^>]+>", "Email in angle brackets"),
    (r"@[\w-]+", "GitHub @username"),
]


def _git_staged_changed_md() -> list[str]:
    """Return staged/changed .md files within scope."""
    try:
        raw = subprocess.check_output(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=AM"],
            text=True,
        )
    except subprocess.CalledProcessError:
        raw = ""
    files = raw.splitlines()
    # Also include unstaged tracked .md files in scope
    try:
        raw2 = subprocess.check_output(
            ["git", "diff", "--name-only", "--diff-filter=AM"], text=True
        )
    except subprocess.CalledProcessError:
        raw2 = ""
    files.extend(raw2.splitlines())
    # Deduplicate and filter
    return sorted(
        {
            f
            for f in files
            if f.endswith(".md")
            and any(f.startswith(prefix) for prefix in SCOPE_GLOB)
        }
    )


def main() -> int:
    files = _git_staged_changed_md()
    if not files:
        return 0

    errors: list[str] = []
    for path in files:
        try:
            with open(path, encoding="utf-8") as fh:
                for lineno, line in enumerate(fh, 1):
                    for pattern, label in PERSON_PATTERNS:
                        if re.search(pattern, line):
                            errors.append(
                                f"{path}:{lineno}: {label}: {line.strip()[:80]}"
                            )
        except FileNotFoundError:
            continue

    if errors:
        print("[pre-push] PERSON NAMES IN PUBLISHED DOCS (blocking):", file=sys.stderr)
        for err in errors:
            print(f"  {err}", file=sys.stderr)
        print(
            "\nUse placeholder roles instead: 'the user', 'site admin', 'ops team'.",
            file=sys.stderr,
        )
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())