#!/usr/bin/env python3
"""Check that recommended project tools are available.

Run at session start (or manually) to verify the tools this project's
opencode.jsonc expects are actually usable.  Prints any missing tool
with the command needed to install/configure it.

Recommended tools (from se-site/opencode.jsonc):
  - marksman LSP       — markdown navigation, [[wiki-link]] resolution
  - ty LSP (built-in) — Python analysis (OpenCode builtin, no install)
  - playwright MCP     — browser automation, screenshots, visual QA
  - mcp-markdown MCP   — semantic doc access (sections, headings, code blocks)

Usage:
  uv run python scripts/check_project_tools.py

Exit code: 0 = all present, 1 = one or more missing (still OK to proceed).
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_ROOT / "opencode.jsonc"

CHECK_RESULTS: list[str] = []


def ok(label: str, detail: str = "") -> None:
    CHECK_RESULTS.append(f"  ✅  {label}" + (f"  ({detail})" if detail else ""))


def missing(label: str, hint: str) -> None:
    CHECK_RESULTS.append(f"  ❌  {label}\n      → {hint}")


def check_binary(name: str, hint: str) -> bool:
    if shutil.which(name):
        ok(name, f"found at {shutil.which(name)}")
        return True
    missing(name, hint)
    return False


def check_npx_package(pkg: str, hint: str) -> bool:
    """Check if an npx-available package resolves (does not install it)."""
    try:
        result = subprocess.run(
            ["npx", "--yes", "--no-install", pkg, "--version"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if result.returncode == 0:
            ok(pkg, result.stdout.strip()[:60])
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    missing(pkg, hint)
    return False


def main() -> int:
    print(f"── Tool check for {PROJECT_ROOT.name} ──────────────────────────────")

    # 1. marksman LSP
    print("\n[LSP] marksman (markdown navigation, go-to-def, [[wiki-links]])")
    check_binary("marksman", "Install: see https://github.com/artempyanykh/marksman")

    # 2. ty LSP (built-in OpenCode)
    print("\n[LSP] ty (Python analysis, built-in OpenCode LSP)")
    print("      • ty is built into OpenCode — no manual install needed.")
    print("      • Verify it's enabled in your opencode.jsonc or project-level config.")
    ok("ty", "built-in, enabled in se-site/opencode.jsonc")

    # 3. Playwright MCP
    print("\n[MCP] playwright (browser automation, screenshots, QA)")
    # The MCP server is run by OpenCode's MCP framework via npx.
    # Check that the underlying browsers are installed.
    pw_ok = check_npx_package(
        "@playwright/mcp",
        "MCP not available locally. The project opencode.jsonc enables it via npx — "
        "OpenCode will auto-install on first run.",
    )
    if pw_ok:
        # Check if browsers are cached (playwright installs them to ~/.cache/ms-playwright)
        browsers = subprocess.run(
            ["npx", "playwright", "install", "--dry-run"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if "already installed" in browsers.stdout.lower():
            ok("playwright browsers", "cached locally")
        else:
            print("      ⚠  Playwright browsers not cached — will install on first `navigate` call.")

    # 4. mcp-server-markdown MCP
    print("\n[MCP] mcp-server-markdown (semantic doc access)")
    check_npx_package(
        "mcp-server-markdown",
        "MCP not available locally. Auto-installed by OpenCode via npx on first run.",
    )

    # 5. Project config file presence
    print("\n[config] se-site/opencode.jsonc")
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            cfg = json.load(f)
        mcp_keys = list(cfg.get("mcp", {}).keys())
        lsp_keys = list(cfg.get("lsp", {}).keys())
        ok("opencode.jsonc", f"MCPs: {mcp_keys}, LSPs: {lsp_keys}")
    else:
        missing("opencode.jsonc", "Project-level config not found — check the repo root")

    # ── Summary ──────────────────────────────────────────────────────────
    print("\n────────────────────────────────────────────────────────────────")
    missing_count = sum(1 for r in CHECK_RESULTS if r.startswith("  ❌"))
    for r in CHECK_RESULTS:
        print(r)

    if missing_count:
        print(f"\n⚠  {missing_count} tool(s) missing — the project will still work, but these")
        print("   tools improve navigation, QA, and doc access.")
        return 1

    print("\n✅  All recommended tools are available.")
    return 0


if __name__ == "__main__":
    sys.exit(main())