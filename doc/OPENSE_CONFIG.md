# AI Tooling Configuration

AI tooling configuration, agents, commands, skills, and workflow for the SE Site project.

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

## Custom Commands

| Command | Description |
|---|---|
| `test` | `pytest` |
| `format` | `ruff format src/` on all dirs |
| `commit` | Autoformat -> test -> git add -> commit |
| `merge` | Ask user, squash-merge into staging, then staging -> current |
| `build` | `python src/flask_se.py build` for static site |

## Agent Skills

Skills are auto-registered in `.skills/<name>/README.md`. Available skills:

| Skill | When to load |
|---|---|
| `test-writer` | Writing hermetic pytest tests — load before coding |
| `retrospective-analysis` | Analyzing process gaps after merges or sessions |

## Agent Workflow

1. **Plan** -> analyze, apply priority ladder, present to user
1. User approves or redirects
1. Branch (see `doc/GIT_FLOW.md`)
1. **Doc first** -> commit docs before code
1. **Implement** -> write tests first (TDD), implement until tests pass, auto-commit iteratively
1. **Plan** -> final review
1. Verify on `staging` branch
1. Merge `staging` -> `current`
1. Fail -> `git branch -D`, Succeed -> squash-merge + delete branch
