# gh-todo-sync

<!-- encoding: utf-8 -->

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
| `backlog` | Backlog вЂ” numbered item |
| `enhancement` | Backlog вЂ” numbered item |
| `icebox` | Icebox вЂ” bullet point |
| `bug` | Backlog вЂ” "BUG:" prefix |
| `ci` | Backlog вЂ” first item |

### 4. Report Result

```
CI: вњ“ no failures | вњ— <N> failure(s)
Issues: <N> open
PRs: <N> open
TODO.md: <N> backlog, <M> icebox
```
