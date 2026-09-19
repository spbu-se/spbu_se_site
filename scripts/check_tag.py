# -*- coding: utf-8 -*-
"""Pre-tag gate: verify tag is on upstream/current HEAD, signed, and email
matches signer.

Exit 0 if all checks pass, 1 otherwise (blocking).
"""

from __future__ import annotations

import subprocess
import sys


def _run(cmd: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([cmd, *args], capture_output=True, text=True, check=False)


def main() -> int:
    errors: list[str] = []

    # 1. Tag name must be provided
    tag = (sys.argv[1] if len(sys.argv) > 1 else "").strip()
    if not tag:
        errors.append("Usage: python scripts/check_tag.py <tagname>")
        errors.append("Example: python scripts/check_tag.py v2026.09.18")
        print("\n".join(errors), file=sys.stderr)
        return 1

    # 2. Fetch upstream current to get the latest
    _run("git", "fetch", "upstream", "current")
    current = _run("git", "rev-parse", "upstream/current")
    if current.returncode != 0:
        errors.append("Cannot resolve upstream/current — fetch may have failed")
        print("\n".join(errors), file=sys.stderr)
        return 1
    current_sha = current.stdout.strip()

    # 3. Verify current HEAD is the target
    local_head = _run("git", "rev-parse", "HEAD")
    head_sha = local_head.stdout.strip() if local_head.returncode == 0 else ""
    if head_sha != current_sha:
        errors.append(
            f"Tag would be at HEAD ({head_sha[:10]}) but "
            f"upstream/current is at ({current_sha[:10]})"
        )
        errors.append("  Run: git checkout upstream/current && git tag -s <tagname>")

    # 4. Check gpg.format
    gpg_fmt = _run("git", "config", "--global", "gpg.format")
    fmt = gpg_fmt.stdout.strip() if gpg_fmt.returncode == 0 else "gpg"
    if fmt != "gpg":
        errors.append(f"gpg.format is '{fmt}', not 'gpg' — tag may not verify on GitHub")
        errors.append("  Fix: git config --global gpg.format gpg")

    # 5. Check signing key exists
    key = _run("git", "config", "--global", "user.signingkey")
    if key.returncode != 0 or not key.stdout.strip():
        errors.append("user.signingkey is not set")
        errors.append("  Fix: git config --global user.signingkey <key-id>")

    # 6. Check git user.email matches GPG key email
    email = _run("git", "config", "user.email")
    git_email = email.stdout.strip() if email.returncode == 0 else ""
    if not git_email:
        email2 = _run("git", "config", "--global", "user.email")
        git_email = email2.stdout.strip() if email2.returncode == 0 else ""
    if git_email:
        key_list = _run(
            "gpg", "--list-keys", "--with-colons", "--keyid-format=long"
        )
        if key_list.returncode == 0:
            # Check if any UID matches git_email
            import re
            uid_emails = re.findall(r"uid[^:]*:[^:]*:[^:]*:[^:]*:[^:]*:[^:]*:[^:]*:[^:]*:[^:]*:([^:]+@[^:]+)", key_list.stdout)
            if uid_emails and git_email not in uid_emails:
                errors.append(
                    f"git user.email ({git_email}) does not match any GPG key email"
                )
                errors.append(f"  Key emails: {', '.join(uid_emails[:5])}")
                errors.append("  Fix: git config user.email <email-on-key>")

    if errors:
        print("[pre-tag] FAILED:", file=sys.stderr)
        for e in errors:
            print(f"  {e}", file=sys.stderr)
        return 1

    print("[pre-tag] all checks passed — ready to tag")
    return 0


if __name__ == "__main__":
    sys.exit(main())