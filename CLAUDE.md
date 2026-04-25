# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

**GOLDEN_BULLET** — Prop Firm Challenge Risk Calculator

Calculates position sizing, risk parameters, and drawdown limits for prop firm trading challenges. Helps traders stay within challenge rules (max daily loss, max total drawdown, profit targets) while optimizing position sizes.

## Architecture

- `calculator.py` — pure formula logic, zero UI imports, testable independently against Excel reference
- `settings.py` — JSON persistence to `%APPDATA%\GoldenBulletCalc\settings.json`
- `ui/` — customtkinter widgets (theme, display, inputs, settings dialog)
- `main.py` — window init, wires UI to calculator, handles lifecycle

Formulas must match `Golden Bullet Risk Calculator V1.1.xlsx` cell-for-cell. The Excel file is the source of truth.

## Commands

```bash
# First-time setup (creates venv, installs deps, creates Desktop + Start Menu shortcuts)
powershell -ExecutionPolicy Bypass -File setup.ps1

# Daily use
# Double-click "GoldenBullet" shortcut on Desktop, or press Windows key and search.
# (run.vbs launches main.py via pythonw.exe with no console window.)

# Run from CLI (development)
python main.py

# Run tests
python -m pytest tests/ -v
```

## Distribution

Personal-use, run-from-source. There is no compiled binary in the supported path —
PyInstaller `.exe` builds were repeatedly quarantined by Bitdefender heuristics, so
distribution is now: `git clone` → `setup.ps1` → launch via shortcut. The same flow
works for VPS deployment.

`build.py` and `release/` remain in the repo as a deprecated emergency-portable
fallback (see `build.py` docstring). Not for routine use.
