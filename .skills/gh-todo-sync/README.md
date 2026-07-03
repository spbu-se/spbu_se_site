# gh-todo-sync

Sync TODO.md from GitHub issues and PRs, and check GHA CI status for failures.

## Workflow

### 1. GHA Status Check

```bash
gh run list --status failure --limit 10 --json headBranch,workflowName,conclusion,createdAt,displayTitle
```

### 2. Fetch Issues and PRs

```bash
gh issue list --state open --json number,title,labels --limit 50
gh pr list --state open --json number,title,headRefName,baseRefName --limit 50
```

### 3. Map to TODO.md Structure

| Issue label | TODO.md section |
| ------------- | ----------------------- |
| `backlog` | Backlog — numbered item |
| `enhancement` | Backlog — numbered item |
| `icebox` | Icebox — bullet point |
| `bug` | Backlog — "BUG:" prefix |
| `ci` | Backlog — first item |

### 4. Report Result

```
CI: ✓ no failures | ✗ <N> failure(s)
Issues: <N> open
PRs: <N> open
TODO.md: <N> backlog, <M> icebox
```
