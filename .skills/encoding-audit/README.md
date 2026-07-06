# encoding-audit

Detect and fix non-UTF-8 encoding in source files on Windows. PowerShell encoding trap, detection scripts, git recovery workflow, encoding declaration templates.

Reusable across any Windows dev environment with Python or markdown files that contain non-ASCII text (Cyrillic, Chinese, accented Latin, em-dashes, etc.).

Does NOT cover project-specific encoding declaration policy (see that project's `docs/DEVELOPMENT_PROCESS.md`). Does NOT cover configuration formats (TOML, YAML, JSON) that don't support inline encoding declarations.

## When to load

- When `mdformat` or `ruff` reports `UnicodeDecodeError`
- When text output shows `�` or garbled characters instead of expected non-ASCII text
- When `git diff` shows hunks of garbled bytes in previously clean files
- After any bulk file edit on Windows that may have used PowerShell `Set-Content` or `Out-File`
- When setting up a new Windows dev environment for a project with non-ASCII text

## Root cause

PowerShell's `Set-Content` and `Out-File` cmdlets default to the system's active ANSI code page (Windows-1252 on en-US Windows), NOT UTF-8. This corrupts any file containing non-ASCII bytes when the file is expected to be UTF-8.

```powershell
# ❌ WRONG — writes Windows-1252
Set-Content -Path file.md -Value $content

# ❌ WRONG — also Windows-1252
$content > file.md

# ✅ CORRECT — writes UTF-8 without BOM
[System.IO.File]::WriteAllText($path, $content, [System.Text.UTF8Encoding]::new($false))

# ✅ CORRECT — reads UTF-8
[System.IO.File]::ReadAllText($path, [System.Text.Encoding]::UTF8)

# ✅ CORRECT — writes bytes as UTF-8
[System.IO.File]::WriteAllBytes($path, [System.Text.Encoding]::UTF8.GetBytes($content))
```

## Detection

### Find files with invalid UTF-8 bytes

```powershell
Get-ChildItem -Recurse -Include "*.py","*.md" -Exclude "*node_modules*","*.venv*" | ForEach-Object {
    try { $null = [System.Text.UTF8Encoding]::UTF8.GetString([System.IO.File]::ReadAllBytes($_.FullName)) }
    catch { Write-Host $_.FullName }
}
```

### Find specific invalid bytes (0x80-0xBF continuation bytes outside multi-byte sequence)

```powershell
$badBytes = @(0x80..0xBF)
Get-ChildItem -Recurse -Include "*.py","*.md" -Exclude "*node_modules*","*.venv*" | ForEach-Object {
    $bytes = [System.IO.File]::ReadAllBytes($_.FullName)
    for ($i=0; $i -lt $bytes.Count; $i++) {
        if ($badBytes -contains $bytes[$i]) { Write-Host "$($_.FullName): bad byte at $i" }
    }
}
```

## Fix workflow

### 1. Find the committed clean version

```bash
git log --all --oneline -- <file>      # list commits touching this file
# Or search for when valid UTF-8 text existed:
git log --all --oneline -S "<known-good-text>" -- <file>
```

### 2. Restore from clean commit (binary-safe)

```python
import subprocess
result = subprocess.run(['git', 'show', '<clean-sha>:<file>'], capture_output=True)
with open('<file>', 'wb') as f:
    f.write(result.stdout)
```

### 3. Re-apply encoding declaration (Python, not PowerShell)

```python
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()
if not content.startswith('# -*- coding'):
    with open(path, 'w', encoding='utf-8', newline='\r\n') as f:
        f.write('# -*- coding: utf-8 -*-' + '\n')
        f.write(content)
```

### 4. Verify

```bash
uv run python -c "exec(open('path.py', encoding='utf-8').read()); print('OK')"
uv run mdformat path.md --check
```

## Encoding declaration templates

### Python (`.py`)

```
# -*- coding: utf-8 -*-
```

Insert as line 1, before any other comment or code.

### Markdown (`.md`)

```html
<!-- encoding: utf-8 -->
```

Insert as line 2 (after the H1 `# Title`), before any content.

For files without an H1 title (e.g., vendor stubs starting with `___` separators), insert on line 1.

### Verification

```bash
Get-ChildItem -Recurse -Include "*.py" | Select-String -Pattern "^# -\*- coding: utf-8 -\*-" | Measure-Object | Select-Object Count
Get-ChildItem -Recurse -Include "*.md" | Select-String -Pattern "encoding: utf-8" | Measure-Object | Select-Object Count
```

## git recovery safety net

If the working tree is corrupted and the committed version is also corrupted (because corrupted bytes were committed), restore from the last known-clean commit:

```bash
git checkout <clean-sha> -- <file>
```

Then re-apply any intentional changes that happened BETWEEN the clean commit and now, but using the encoding-safe write method (see §Root cause).

To find clean commits by scanning for valid bytes:

```python
import subprocess
commits = ['sha1', 'sha2', ...]
for sha in commits:
    r = subprocess.run(['git', 'show', f'{sha}:path.py'], capture_output=True)
    has_valid = b'<known-utf8-bytes>' in r.stdout
    print(f'{sha}: valid={has_valid}')
```

## Related PowerShell pitfalls

### `uv export` stderr contamination

`uv export` prints progress to stderr (`uv : Resolved 115 packages in 3ms`). Shell redirections that merge stderr into stdout (`2>&1`) or use `$(...)` interpolation can embed this garbage into `requirements.txt`.

```powershell
# ❌ WRONG — stderr bleeds into file
uv export --no-dev --no-hashes > requirements.txt

# ❌ WRONG — $(...) flattens multi-line into single line
[System.IO.File]::WriteAllText("reqs.txt", $(uv export --no-dev --no-hashes), ...)

# ✅ CORRECT — use Python to capture stdout cleanly
uv run python -c "import subprocess; r=subprocess.run(['uv','export','--no-dev','--no-hashes'],capture_output=True,text=True); r.check_returncode(); open('requirements.txt','w',encoding='utf-8',newline='\n').write(r.stdout)"
```

### CI `mdformat --check .` traverses vendored `.venv/` and `node_modules/`

On CI (Ubuntu), `mdformat --check .` traverses into `.venv/Lib/site-packages/*.md` and `.opencode/node_modules/*.md` which contain non-UTF-8 vendored files. Always use explicit paths in CI workflows:

```yaml
- run: mdformat --check docs/ AGENTS.md CLAUDE.md README.md TODO.md .skills/ .opencode/commands/ .claude/ .agents/
```
