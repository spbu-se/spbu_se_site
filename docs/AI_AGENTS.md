# AI Tooling Configuration

<!-- encoding: utf-8 -->

AI-agent-specific knowledge: tool permissions, quirks, workarounds, and typical issues.
Does not cover: process workflow (see `docs/DEVELOPMENT_PROCESS.md`), commands (see `AGENTS.md`), skills (see `CLAUDE.md`).

## Permission Recommendation

Recommended permissions (example for OpenCode — adapt to your tool):

```jsonc
{
  "permission": {
    "read": "allow",
    "edit": "ask",
    "glob": "allow",
    "grep": "allow",
    "bash": {
      "*": "ask",
      "pytest*": "allow",
      "ruff*": "allow",
      "python src/flask_se*": "allow",
      "pip install*": "allow",
      "ls*": "allow",
      "mkdir*": "allow"
    },
    "todowrite": "allow",
    "webfetch": "allow",
    "question": "allow",
    "skill": "allow",
    "lsp": "allow"
  }
}
```

## Tool Quirks

### Glob tool doesn't descend into dot-prefixed directories

When the glob tool's `path` parameter points to a parent directory, patterns like `.skills/**/*.md` return **no results**. The tool must point directly into the dot directory:

```jsonc
// WRONG — returns nothing:
// glob(path=".", pattern=".skills/**/*.md")

// CORRECT — finds all 11 skill files:
// glob(path=".skills", pattern="**/*.md")
```

This applies to the opencode glob tool on all platforms. Other AI tools (Claude Code, Cursor) may have different behavior — their glob implementations are independent.
