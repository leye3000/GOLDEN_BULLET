# Source-launcher distribution + font bump

**Date:** 2026-04-25
**Status:** Draft, pending review

## Context

Golden Bullet v1.0 ships as a PyInstaller-built `.exe`. Bitdefender on the primary
machine repeatedly quarantines the binary — most recently a Windows update triggered
Bitdefender to delete all build artefacts. Source files in git are intact. The
PyInstaller bootstrapper architecture (unpacking bytecode at runtime) triggers
heuristic AV detection regardless of code signing, temp-dir tricks, or version-pinning;
this is structural, not fixable through PyInstaller config.

A secondary issue: input-area font sizes feel small during active trading.

## Goals

1. Eliminate AV-quarantine risk permanently for the primary use case.
2. Preserve the floating always-on-top desktop HUD form factor — no browser, no UI
   rewrite.
3. Improve readability of HUD labels without breaking the compact layout.
4. Recovery should be `git restore`, not "rebuild and re-add Bitdefender exclusions."

## Non-Goals

- Distribution to other people / fresh machines without Python installed. Personal
  use only. (Future VPS use is the same workflow on a machine the user controls — no
  separate distribution channel needed.)
- Code signing, EV certificates, switching packagers (Nuitka, Tauri, etc.).
- UI rewrite, theme overhaul, behavioural changes to the calculator.

## Approach

Replace the compiled-binary distribution model with **run-from-source via a Windows
shortcut**. The HUD is still a native customtkinter window; the only change is how it
launches. `pythonw.exe` (signed by the Python Software Foundation) runs the existing
`main.py` directly, eliminating the PyInstaller bootstrapper that AV heuristics flag.

A one-time `setup.ps1` provisions the venv, installs dependencies, and creates a
desktop / Start Menu shortcut. Day-to-day use is double-click the shortcut (or pin to
taskbar) — visually identical to the prior `.exe` workflow.

## Scope

### 1. Launcher and shortcut

**New files at project root:**

- **`run.vbs`** — silent VBS launcher. Resolves the project directory dynamically
  from the script's own path, then invokes `venv\Scripts\pythonw.exe main.py`.
  `pythonw.exe` runs windowless — no console flash. The shortcut therefore works
  regardless of where the project folder lives. If the venv is missing (e.g., user
  cloned the repo but hasn't run `setup.ps1` yet), shows a single message box
  instructing the user to run `setup.ps1` first, then exits cleanly. No silent
  failure path.

- **`setup.ps1`** — first-time bootstrap PowerShell script:
  1. Detect Python on PATH; abort with a clear remediation message if missing.
  2. Create `venv\` if missing (`python -m venv venv`).
  3. `pip install -r requirements.txt` into the venv.
  4. Generate `GoldenBullet.lnk` shortcut on Desktop and in Start Menu (user
     Programs folder) targeting `run.vbs`, with `icon.ico` and "Golden Bullet" as
     the display name.
  5. Print a success message instructing the user to pin to taskbar manually if
     desired.
  6. Header comment documents the one-line `Set-ExecutionPolicy -Scope Process
     Bypass` workaround in case execution policy blocks the script.

**Behaviour:** double-clicking the shortcut launches the HUD identically to the prior
`.exe`. No console window, no AV interaction at any step.

### 2. Deprecate (don't delete) the `.exe` build path

- Add a deprecation docstring to the top of `build.py` explaining the AV problem and
  pointing at `run.vbs` / `setup.ps1` as the supported launch method.
- `GoldenBulletCalc.spec` and the `release/` directory: leave in place untouched.
- Rationale: preserves the option for an emergency portable build, but signals it is
  no longer the supported path.

### 3. Update project docs

- `CLAUDE.md` Commands section — replace the `python build.py` block with:
  - First-time: `powershell -ExecutionPolicy Bypass -File setup.ps1`
  - Daily use: double-click `GoldenBullet.lnk` (or pin to taskbar)
- `CLAUDE.md` Distribution section — replace GitHub-Releases language with a
  personal-use, run-from-source note. The "download .exe on any Windows machine"
  flow is no longer supported.

### 4. Font bump (`ui/theme.py`)

Preserves the existing visual hierarchy: heading-style fonts remain larger than
label-style fonts. All affected constants live in a single file.

| Constant          | Before | After | Used by                                                         |
|-------------------|--------|-------|-----------------------------------------------------------------|
| `FONT_STAT_LABEL` | 8      | 10    | `R:R`, `Vol`, `%`, `DD`, `DD Left`, `Daily Cap` micro-labels    |
| `FONT_LABEL`      | 9      | 11    | Settings-dialog field labels                                    |
| `FONT_LABEL_BOLD` | 9      | 11    | `BAL`, `T1`, `T2`, `Trades to Pass` headers, Save button        |
| `FONT_SECTION`    | 9      | 11    | `ACCOUNT SETTINGS` header in settings dialog                    |

Unchanged: `FONT_TITLE` (12), `FONT_BALANCE` (16), `FONT_RISK` (18), `FONT_RISK_LABEL`
(10), `FONT_TP_INPUT` (11), `FONT_STATUS` (10), `FONT_STAT_VALUE` (11).

### 5. Layout verification

The bump is roughly +22% on the affected labels. After the change, visual check:

- HUD does not clip text on either tab.
- The compact floating window remains compact (no major footprint expansion).
- Settings dialog widgets still fit without truncation.

If clipping appears, adjust `width=` parameters on the affected widgets minimally to
accommodate. No theme overhaul.

## Architecture Impact

- `calculator.py`, `settings.py`, `main.py`, `ui/display.py`, `ui/inputs.py`,
  `ui/settings_dialog.py`, and `tests/` are not modified.
- Excel-as-source-of-truth for formulas is unaffected.
- Test suite (`python -m pytest tests/ -v`) continues to pass unchanged.

## Risks and Mitigations

| Risk                                          | Mitigation                                                                                |
|-----------------------------------------------|-------------------------------------------------------------------------------------------|
| Font bump causes layout clipping              | Step 5 visual check; adjust widget `width=` minimally if needed.                          |
| PowerShell execution policy blocks `setup.ps1`| Header comment documents `-ExecutionPolicy Bypass` invocation.                            |
| Python not on PATH                            | `setup.ps1` detects and prints clear remediation.                                         |
| Bitdefender flags `pythonw.exe` itself        | Vanishingly rare — `pythonw.exe` is signed by Python Software Foundation, widely trusted. |
| Future VPS deployment                         | Same workflow: `git clone`, `setup.ps1`, shortcut. No separate path needed.               |

## Success Criteria

1. Double-clicking `GoldenBullet.lnk` from Desktop launches the HUD with no console
   flash and no AV prompt.
2. No `.exe` is produced, kept, or expected during normal use.
3. `ui/theme.py` contains no font sizes 8 or 9; size-8 entries are now 10, size-9
   entries are now 11.
4. HUD layout remains readable and compact after the bump on both tabs.
5. All existing tests pass unchanged.
