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
# Run the app
python main.py

# Run tests
python -m pytest tests/ -v

# Build standalone .exe
python build.py
# Output: release/GoldenBulletCalc.exe
```

## Distribution

The compiled `.exe` is attached to GitHub Releases. Download on any Windows machine:
```bash
gh release download --repo leye3000/GOLDEN_BULLET --pattern "*.exe"
```
