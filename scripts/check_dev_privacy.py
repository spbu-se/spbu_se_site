"""Developer-host privacy gate: dev-artifact filename blocklist + local-path scan.

Consumes scripts/privacy_gate_config.json (SSOT). Invoked from pre-commit with
the staged file list and from the pre-push gate with --all (full tracked tree).

Checks:
1. Filename blocklist — config/credential/database/mail/env/log classes that
   must never be tracked (force-add net beyond .gitignore); *.example allowed.
2. Local absolute paths with a developer username (/home/<user>, /Users/<user>,
   C:\\Users\\<user>) in text content — excluding deploy/container paths and the
   browser `C:\\fakepath\\` idiom.
3. Content scan skips thesis (public by decision), vendored libraries, and
   minified build artifacts (their sources are scanned).
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "scripts" / "privacy_gate_config.json"


def load_config() -> dict:
    with CONFIG.open(encoding="utf-8") as fh:
        return json.load(fh)


def _tracked_files() -> list[str]:
    out = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, check=True, capture_output=True)  # noqa: S607  git via PATH, cross-platform
    return [p for p in out.stdout.decode("utf-8").split("\0") if p]


def _content_skip(name: str, cfg: dict) -> bool:
    scope = cfg["scope"]
    if any(name.startswith(p) for p in scope["exclude_path_prefixes"]):
        return True
    if any(name.startswith(p) for p in scope["vendored_prefixes"]):
        return True
    low = name.lower()
    return any(low.endswith(s) for s in scope["minified_suffixes"])


def _is_binary(path: Path) -> bool:
    with path.open("rb") as fh:
        return b"\x00" in fh.read(8192)


def _filename_violation(name: str, cfg: dict) -> str | None:
    low = name.lower()
    arts = cfg["artifacts"]
    if any(low.endswith(s) for s in arts["allow_suffixes"]):
        return None
    if any(low.endswith(ext) for ext in arts["blocked_extensions"]):
        return f"blocked extension (dev artifact class): {name}"
    frags = "|".join(re.escape(f) for f in arts["blocked_name_fragments"])
    if re.search(rf"(?:^|[_.-])(?:{frags})s?(?:[_.-]|$)", low):
        return f"blocked name fragment (credential/backup class): {name}"
    return None


def _path_violation(name: str, cfg: dict) -> list[str]:
    if _content_skip(name, cfg):
        return []
    path = ROOT / name
    if not path.is_file() or _is_binary(path):
        return []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    dp = cfg["dev_paths"]
    idioms = re.compile("|".join(re.escape(i) for i in dp["allowed_idioms"]))
    text = idioms.sub("", text)
    hits: list[str] = []
    for pat in dp["flag_patterns"]:
        for m in re.finditer(pat, text):
            raw = m.group(0)
            if any(raw.startswith(p) for p in dp["allowed_path_prefixes"]):
                continue
            user_part = raw.rsplit("/", 1)[-1] if "/" in raw else raw.split("\\\\")[-1]
            if user_part in dp["allowed_user_components"]:
                continue
            line = text.count("\n", 0, m.start()) + 1
            hits.append(f"{name}:{line}: local path {raw!r}")
    return hits


def main() -> int:
    cfg = load_config()
    if "--all" in sys.argv:
        files = _tracked_files()
        label = "full tracked tree"
    else:
        files = [a for a in sys.argv[1:] if not a.startswith("--")]
        label = f"{len(files)} staged file(s)"
    findings: list[str] = []
    for name in files:
        if not _content_skip(name, cfg):
            v = _filename_violation(name, cfg)
            if v:
                findings.append(v)
        findings.extend(_path_violation(name, cfg))
    if findings:
        print(f"[dev-privacy] FAILED ({label}):", file=sys.stderr)
        for f in findings:
            print(f"  - {f}", file=sys.stderr)
        return 1
    print(f"[dev-privacy] ok ({label})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
