# Source-Launcher Distribution + Font Bump Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the PyInstaller `.exe` distribution with a run-from-source shortcut workflow that sidesteps Bitdefender heuristic AV quarantines, and bump small label fonts in `ui/theme.py` for readability.

**Architecture:** No code logic changes. The HUD remains a customtkinter desktop app. We add `run.vbs` (silent launcher invoking `pythonw.exe main.py`) and `setup.ps1` (one-time bootstrap that creates the venv, installs deps, and generates Desktop + Start-Menu shortcuts pointing at `run.vbs`). Font constants in `ui/theme.py` are bumped: size 8 → 10, size 9 → 11. The PyInstaller build path is deprecated but not deleted.

**Tech Stack:** Python 3.10+, customtkinter, Windows-native VBScript + PowerShell, existing pytest test suite.

---

## File Structure

| File | Status | Responsibility |
|---|---|---|
| `run.vbs` | Create | Silent launcher; resolves project dir from script path; invokes `venv\Scripts\pythonw.exe main.py`; shows messagebox if venv missing |
| `setup.ps1` | Create | First-time bootstrap: detects Python, creates venv, `pip install -r requirements.txt`, generates Desktop + Start Menu shortcuts |
| `ui/theme.py` | Modify | Bump font sizes 8→10 and 9→11 on four constants |
| `build.py` | Modify | Add deprecation docstring at top |
| `CLAUDE.md` | Modify | Replace Commands and Distribution sections |
| `calculator.py`, `settings.py`, `main.py`, `ui/display.py`, `ui/inputs.py`, `ui/settings_dialog.py`, `tests/*` | Untouched | No logic changes |

Branch: `feature/source-launcher-font-bump` (already created and contains the design spec commit).

---

## Task 1: Bump font sizes in `ui/theme.py`

**Files:**
- Modify: `C:/Claude/CHALLENGE_CALC/ui/theme.py:38,39,46,47`
- Verify: `tests/` (full suite must still pass)

**Rationale:** Smallest, lowest-risk change. Verifies the test suite still runs and the HUD launches before we touch distribution mechanics. Fonts are centralised — single file, four lines.

- [ ] **Step 1: Apply the four font-size edits**

Edit `ui/theme.py` lines 38, 39, 46, 47. Final state of those four lines:

```python
FONT_LABEL = (FONT_UI, 11)
FONT_LABEL_BOLD = (FONT_UI, 11, "bold")
```

```python
FONT_STAT_LABEL = (FONT_UI, 10)
FONT_SECTION = (FONT_UI, 11, "bold")
```

All other font constants (`FONT_TITLE`, `FONT_BALANCE`, `FONT_RISK`, `FONT_RISK_LABEL`, `FONT_TP_INPUT`, `FONT_STATUS`, `FONT_STAT_VALUE`) remain unchanged.

- [ ] **Step 2: Run the test suite**

Run from project root with venv activated:
```bash
python -m pytest tests/ -v
```
Expected: all tests pass. Tests cover `calculator.py` formulas, not fonts; this confirms we haven't accidentally broken imports.

- [ ] **Step 3: Manual visual check**

Run from project root with venv activated:
```bash
python main.py
```
Expected behaviours:
- HUD launches.
- On both tabs, the small `R:R` / `Vol` / `%` labels next to the entry boxes are visibly larger (10pt) than before (8pt).
- The `BAL`, `T1`, `T2`, `Trades to Pass` headers are visibly larger (11pt) than before (9pt).
- No text clipping; window remains compact (~300×380).
- Settings dialog opens; `ACCOUNT SETTINGS` heading and field labels render cleanly without truncation.

If any clipping appears, increase the affected widget's `width=` parameter minimally (e.g., `width=50` → `width=58`) in `ui/inputs.py` or `ui/settings_dialog.py`. No theme overhaul.

- [ ] **Step 4: Commit**

```bash
git -C C:/Claude/CHALLENGE_CALC add ui/theme.py
# Also add ui/inputs.py or ui/settings_dialog.py only if Step 3 required width tweaks.
git -C C:/Claude/CHALLENGE_CALC commit -m "Bump small fonts in theme: size 8 -> 10, size 9 -> 11"
```

---

## Task 2: Create `run.vbs` silent launcher

**Files:**
- Create: `C:/Claude/CHALLENGE_CALC/run.vbs`

**Rationale:** Standalone artefact with no dependencies on other new files. We can manually verify it before building `setup.ps1` on top of it.

- [ ] **Step 1: Create `run.vbs` at project root**

Write this exact content:

```vbs
' Golden Bullet - silent launcher.
' Resolves the project directory from this script's location, then launches
' main.py via pythonw.exe (windowless, no console flash). If the venv has
' not been created yet, shows a messagebox pointing the user at setup.ps1.

Option Explicit

Dim fso, shell, scriptDir, pythonw, mainPy
Set fso = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")

scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
pythonw = scriptDir & "\venv\Scripts\pythonw.exe"
mainPy = scriptDir & "\main.py"

If Not fso.FileExists(pythonw) Then
    MsgBox "Virtual environment not found." & vbCrLf & vbCrLf & _
           "Please run setup.ps1 first to install dependencies." & vbCrLf & vbCrLf & _
           "From PowerShell in this folder, run:" & vbCrLf & _
           "  powershell -ExecutionPolicy Bypass -File setup.ps1", _
           vbExclamation, "Golden Bullet"
    WScript.Quit 1
End If

shell.CurrentDirectory = scriptDir
shell.Run """" & pythonw & """ """ & mainPy & """", 0, False
```

- [ ] **Step 2: Manual launch test**

Double-click `run.vbs` in Windows Explorer (project already has a venv from Task 1's verification step).

Expected:
- HUD window appears within ~1 second.
- No console window flashes.
- No AV prompt or quarantine notification.

- [ ] **Step 3: Manual missing-venv test**

Temporarily rename the venv to confirm the error path:

```bash
mv C:/Claude/CHALLENGE_CALC/venv C:/Claude/CHALLENGE_CALC/_venv_backup
```

Double-click `run.vbs`. Expected: a single MessageBox titled "Golden Bullet" with the text "Virtual environment not found... Please run setup.ps1 first..." Click OK to dismiss.

Restore the venv:

```bash
mv C:/Claude/CHALLENGE_CALC/_venv_backup C:/Claude/CHALLENGE_CALC/venv
```

Re-test launch (Step 2) to confirm restoration.

- [ ] **Step 4: Commit**

```bash
git -C C:/Claude/CHALLENGE_CALC add run.vbs
git -C C:/Claude/CHALLENGE_CALC commit -m "Add run.vbs silent launcher"
```

---

## Task 3: Create `setup.ps1` bootstrap

**Files:**
- Create: `C:/Claude/CHALLENGE_CALC/setup.ps1`
- Depends on: `run.vbs` and `icon.ico` already at project root

**Rationale:** `setup.ps1` builds on `run.vbs` (the shortcuts target it). One-time-use script for Lee's machine and any future VPS deployment.

- [ ] **Step 1: Create `setup.ps1` at project root**

Write this exact content:

```powershell
# Golden Bullet - first-time setup.
# Run with:
#   powershell -ExecutionPolicy Bypass -File setup.ps1
#
# Idempotent: safe to re-run. Creates venv if missing, installs/updates
# dependencies, and (re)creates Desktop + Start Menu shortcuts.

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition

Write-Host "Golden Bullet setup" -ForegroundColor Cyan
Write-Host "Project root: $projectRoot"
Write-Host ""

# ---------------------------------------------------------------------------
# 1. Detect Python
# ---------------------------------------------------------------------------
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "ERROR: Python not found on PATH." -ForegroundColor Red
    Write-Host "Install Python 3.10+ from https://www.python.org/downloads/"
    Write-Host "Make sure to tick 'Add Python to PATH' during install, then re-run this script."
    exit 1
}
Write-Host "Found Python: $($python.Source)"

# ---------------------------------------------------------------------------
# 2. Create venv if missing
# ---------------------------------------------------------------------------
$venvPath = Join-Path $projectRoot "venv"
if (-not (Test-Path $venvPath)) {
    Write-Host "Creating virtual environment..."
    & python -m venv $venvPath
    if ($LASTEXITCODE -ne 0) { throw "venv creation failed (exit $LASTEXITCODE)" }
} else {
    Write-Host "Virtual environment already exists, skipping creation."
}

# ---------------------------------------------------------------------------
# 3. Install / update dependencies
# ---------------------------------------------------------------------------
$pip = Join-Path $venvPath "Scripts\pip.exe"
$requirements = Join-Path $projectRoot "requirements.txt"

Write-Host "Upgrading pip..."
& $pip install --upgrade pip --quiet
if ($LASTEXITCODE -ne 0) { throw "pip self-upgrade failed (exit $LASTEXITCODE)" }

Write-Host "Installing requirements..."
& $pip install -r $requirements --quiet
if ($LASTEXITCODE -ne 0) { throw "pip install failed (exit $LASTEXITCODE)" }

# ---------------------------------------------------------------------------
# 4. Create shortcuts (Desktop + Start Menu)
# ---------------------------------------------------------------------------
$runVbs = Join-Path $projectRoot "run.vbs"
$iconPath = Join-Path $projectRoot "icon.ico"

if (-not (Test-Path $runVbs)) { throw "run.vbs not found at $runVbs - cannot create shortcut" }
if (-not (Test-Path $iconPath)) { throw "icon.ico not found at $iconPath - cannot create shortcut" }

function New-GoldenBulletShortcut {
    param([string]$Path)
    $wshShell = New-Object -ComObject WScript.Shell
    $shortcut = $wshShell.CreateShortcut($Path)
    $shortcut.TargetPath = "wscript.exe"
    $shortcut.Arguments = "`"$runVbs`""
    $shortcut.IconLocation = $iconPath
    $shortcut.WorkingDirectory = $projectRoot
    $shortcut.Description = "Golden Bullet Risk Calculator"
    $shortcut.Save()
    Write-Host "  Created: $Path"
}

$desktopShortcut = Join-Path ([Environment]::GetFolderPath("Desktop")) "GoldenBullet.lnk"
$startMenuDir = Join-Path ([Environment]::GetFolderPath("Programs")) "Golden Bullet"
$startMenuShortcut = Join-Path $startMenuDir "GoldenBullet.lnk"

if (-not (Test-Path $startMenuDir)) {
    New-Item -ItemType Directory -Path $startMenuDir | Out-Null
}

Write-Host "Creating shortcuts..."
New-GoldenBulletShortcut -Path $desktopShortcut
New-GoldenBulletShortcut -Path $startMenuShortcut

# ---------------------------------------------------------------------------
# Done
# ---------------------------------------------------------------------------
Write-Host ""
Write-Host "Setup complete." -ForegroundColor Green
Write-Host "Launch via the Desktop shortcut or Start Menu > Golden Bullet."
Write-Host "Tip: launch once, then right-click the taskbar icon and pick 'Pin to taskbar'."
```

- [ ] **Step 2: Run the bootstrap to verify idempotence**

The venv already exists from prior development. The script should detect that and skip recreation, but still re-install requirements and re-create shortcuts.

```bash
powershell -ExecutionPolicy Bypass -File C:/Claude/CHALLENGE_CALC/setup.ps1
```

Expected output (in order):
- "Found Python: ..."
- "Virtual environment already exists, skipping creation."
- "Upgrading pip..."
- "Installing requirements..."
- "Creating shortcuts..."
- "  Created: ...\Desktop\Golden Bullet.lnk"
- "  Created: ...\Programs\Golden Bullet\Golden Bullet.lnk"
- "Setup complete." in green

Expected exit code: 0.

- [ ] **Step 3: Verify shortcut launches the HUD**

Double-click `Golden Bullet.lnk` on the Desktop.

Expected:
- HUD window appears.
- No console flash.
- No AV prompt.
- Taskbar icon shows the Golden Bullet icon (not generic VBScript icon).

- [ ] **Step 4: Verify Start Menu entry**

Press Windows key, type "Golden Bullet". The app should appear as a search result. Launch it from there. Expected: same behaviour as Desktop launch.

- [ ] **Step 5: Commit**

```bash
git -C C:/Claude/CHALLENGE_CALC add setup.ps1
git -C C:/Claude/CHALLENGE_CALC commit -m "Add setup.ps1 first-time bootstrap with shortcut creation"
```

---

## Task 4: Deprecate `build.py`

**Files:**
- Modify: `C:/Claude/CHALLENGE_CALC/build.py:1-6`

**Rationale:** Don't delete — preserve the option for emergency portable builds — but signal clearly that this is no longer the supported path.

- [ ] **Step 1: Replace the existing module docstring**

Replace lines 1-6 of `build.py` (the existing `"""Build script — compiles GoldenBulletCalc.exe via PyInstaller. ... """` block) with:

```python
"""DEPRECATED - PyInstaller build is no longer the supported distribution path.

PyInstaller-built .exe files are repeatedly quarantined by Bitdefender on the
primary machine. The bootstrapper architecture (unpacking bytecode at runtime)
triggers heuristic AV detection regardless of code signing or temp-dir tricks.

Supported launch path: run.vbs + GoldenBullet.lnk shortcut, set up via setup.ps1.
See CLAUDE.md for current run instructions.

This file is retained only for emergency portable builds where Python cannot be
installed on the target machine. Expect AV interference.

Run from project root with venv activated:
    python build.py
"""
```

The rest of the file (the imports and `PyInstaller.__main__.run([...])` call) remains unchanged.

- [ ] **Step 2: Confirm `build.py` still parses**

```bash
python -c "import ast; ast.parse(open('C:/Claude/CHALLENGE_CALC/build.py').read()); print('OK')"
```
Expected: prints `OK`. (We don't actually run the build — we just verify the file is still syntactically valid Python.)

- [ ] **Step 3: Commit**

```bash
git -C C:/Claude/CHALLENGE_CALC add build.py
git -C C:/Claude/CHALLENGE_CALC commit -m "Deprecate build.py - source-launcher is now the supported path"
```

---

## Task 5: Update `CLAUDE.md`

**Files:**
- Modify: `C:/Claude/CHALLENGE_CALC/CLAUDE.md:20-39`

**Rationale:** Future-Claude reads `CLAUDE.md` first. The `python build.py` block and Distribution section are now misleading.

- [ ] **Step 1: Replace the Commands section**

Find this block in `CLAUDE.md` (lines 20-32):

````markdown
## Commands

```bash
# Run the app
python main.py

# Run tests
python -m pytest tests/ -v

# Build standalone .exe
python build.py
# Output: release/GoldenBulletCalc.exe
```
````

Replace it with:

````markdown
## Commands

```bash
# First-time setup (creates venv, installs deps, creates Desktop + Start Menu shortcuts)
powershell -ExecutionPolicy Bypass -File setup.ps1

# Daily use
# Double-click "Golden Bullet" shortcut on Desktop, or press Windows key and search.
# (run.vbs launches main.py via pythonw.exe with no console window.)

# Run from CLI (development)
python main.py

# Run tests
python -m pytest tests/ -v
```
````

- [ ] **Step 2: Replace the Distribution section**

Find this block in `CLAUDE.md` (lines 34-39):

````markdown
## Distribution

The compiled `.exe` is attached to GitHub Releases. Download on any Windows machine:
```bash
gh release download --repo leye3000/GOLDEN_BULLET --pattern "*.exe"
```
````

Replace it with:

````markdown
## Distribution

Personal-use, run-from-source. There is no compiled binary in the supported path —
PyInstaller `.exe` builds were repeatedly quarantined by Bitdefender heuristics, so
distribution is now: `git clone` → `setup.ps1` → launch via shortcut. The same flow
works for VPS deployment.

`build.py` and `release/` remain in the repo as a deprecated emergency-portable
fallback (see `build.py` docstring). Not for routine use.
````

- [ ] **Step 3: Commit**

```bash
git -C C:/Claude/CHALLENGE_CALC add CLAUDE.md
git -C C:/Claude/CHALLENGE_CALC commit -m "Update CLAUDE.md: source-launcher is the canonical run path"
```

---

## Task 6: Final end-to-end verification

**Files:** None — verification only.

**Rationale:** Confirm the full first-time-user flow works on a clean state, mirroring what would happen on a fresh `git clone` (or after a Bitdefender event nuked the venv).

- [ ] **Step 1: Simulate a fresh clone — remove venv and shortcuts**

```bash
rm -rf C:/Claude/CHALLENGE_CALC/venv
```

Manually delete the existing Desktop shortcut "GoldenBullet.lnk" and the Start-Menu folder `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Golden Bullet\`. (Easier via File Explorer than command line.)

- [ ] **Step 2: Run the full bootstrap**

```bash
powershell -ExecutionPolicy Bypass -File C:/Claude/CHALLENGE_CALC/setup.ps1
```

Expected: completes successfully with green "Setup complete." message. Time: under 2 minutes (mostly pip install).

- [ ] **Step 3: Run the test suite via the new venv**

```bash
C:/Claude/CHALLENGE_CALC/venv/Scripts/python.exe -m pytest C:/Claude/CHALLENGE_CALC/tests/ -v
```
Expected: all tests pass.

- [ ] **Step 4: Launch via Desktop shortcut**

Double-click "Golden Bullet" on the Desktop. Expected: HUD launches, no console flash, no AV prompt, font sizes are visibly bumped on both tabs.

- [ ] **Step 5: Test the missing-venv error path one final time**

Close the HUD. Rename the venv:

```bash
mv C:/Claude/CHALLENGE_CALC/venv C:/Claude/CHALLENGE_CALC/_venv_backup
```

Double-click the Desktop shortcut. Expected: MessageBox appears with the "Virtual environment not found" message. Click OK.

Restore:
```bash
mv C:/Claude/CHALLENGE_CALC/_venv_backup C:/Claude/CHALLENGE_CALC/venv
```

- [ ] **Step 6: Confirm no AV interaction**

Open Bitdefender's "Notifications" / "History" panel. Confirm no Golden Bullet entries appear from any of the steps above.

- [ ] **Step 7: Final commit (if any width tweaks were captured during Task 1 Step 3)**

If Task 1 Step 3 surfaced layout issues that were patched, those should already be committed there. If you spot any further issues during this end-to-end pass, fix and commit:

```bash
git -C C:/Claude/CHALLENGE_CALC status
# stage any layout fixes
git -C C:/Claude/CHALLENGE_CALC commit -m "Fix layout clipping after font bump"
```

If `git status` is clean, no commit needed.

- [ ] **Step 8: Summary**

Confirm all of the following are true:
- `run.vbs`, `setup.ps1` exist at project root.
- Desktop shortcut "GoldenBullet.lnk" launches the HUD silently.
- Start Menu entry "Golden Bullet" launches the HUD silently.
- `ui/theme.py` contains no font sizes 8 or 9.
- `build.py` first line begins with `"""DEPRECATED`.
- `CLAUDE.md` Commands section references `setup.ps1` and the shortcut, not `python build.py`.
- All tests pass.
- No Bitdefender quarantine events.

Branch `feature/source-launcher-font-bump` is ready for merge to `master`.
