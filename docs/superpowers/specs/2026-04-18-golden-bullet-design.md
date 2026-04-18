# Golden Bullet Risk Calculator — Design Spec

**Project:** GOLDEN_BULLET
**Date:** 2026-04-18
**Source of truth:** `Golden Bullet Risk Calculator V1.1.xlsx`
**Delivery:** Single `.exe` for Windows, always-on-top, compact trading HUD

---

## 1. Purpose

Standalone desktop risk calculator for prop firm challenge trading. The trader inputs account parameters once (via settings), then updates Current Balance, TP settings, and Trades to Pass between trades to get instantly recalculated risk sizing. The app floats over charts as a compact heads-up display.

---

## 2. Tech Stack

| Layer | Choice |
|---|---|
| Language | Python 3.11+ |
| UI framework | customtkinter |
| Persistence | JSON file in `%APPDATA%\GoldenBulletCalc\settings.json` |
| Distribution | PyInstaller `--onefile --windowed` |
| Always-on-top | `window.attributes('-topmost', True)` |

Dependencies: `customtkinter`, `pyinstaller` (build only).

---

## 3. UI Layout

### 3.1 Compact Face (~300px wide x ~360px tall)

This is the primary trading view — always visible, floating over charts.

```
┌──────────────────────────────────┐
│ Golden Bullet       [📌] [⚙]    │  ← Title bar
├──────────────────────────────────┤
│  BALANCE        $ 48,000.00  [__]│  ← Editable, large font
├──────────────────────────────────┤
│  DD: 4.00%   DD Left $3,000     │  ← DD% red when >0
│  Daily Cap  $1,920              │    DD Left red when critical
├──────────────────────────────────┤
│  TP1   R:R [0.0]   Vol [  0%]   │
│  TP2   R:R [4.0]   Vol [100%]   │
│  Trades to Pass    [ 1 ]        │
├──────────────────────────────────┤
│  ┌────────────────────────────┐  │
│  │  RISK  3.13%    $1,500.00  │  │  ← Accent-bordered output
│  └────────────────────────────┘  │
│  ✓ Safe to trade                 │  ← Colour-coded status banner
└──────────────────────────────────┘
```

### 3.2 Compact Face Elements

**Inputs (editable, always visible):**
- Current Balance — large font, most prominent field
- TP1 R:R / Vol%
- TP2 R:R / Vol%
- Trades to Pass

**Outputs (display-only, always visible):**
- Drawdown % — red bold text when > 0 (from Excel conditional formatting)
- DD Remaining — turns red when < 50% of max DD buffer remaining
- Daily Cap $
- Risk % / Risk $ — in highlighted accent box
- Status banner — colour-coded (green/amber/red)

**Controls:**
- Pin button (📌) — toggles always-on-top (default: on)
- Gear button (⚙) — opens settings dialog

### 3.3 Settings Dialog

Opened via gear icon. Modal/toplevel window for set-once-per-challenge fields:

- Starting Balance (default: 50,000)
- Challenge Phase (dropdown: Phase 1, Phase 2, Funded)
- Profit Target % (default: 8)
- Max Drawdown % (default: 10)
- Max Daily Loss % (default: 4)

On save: persists to JSON, triggers full recalculate, closes dialog.

---

## 4. Input Fields

| Field | Variable | Type | Default | Location |
|---|---|---|---|---|
| Starting Balance | `starting_bal` | float | 50000 | Settings dialog |
| Current Balance | `current_bal` | float | 50000 | Compact face |
| Challenge Phase | `phase` | string | "Phase 1" | Settings dialog |
| Profit Target % | `profit_target_pct` | float | 0.08 | Settings dialog |
| Max Drawdown % | `max_dd_pct` | float | 0.10 | Settings dialog |
| Max Daily Loss % | `daily_loss_pct` | float | 0.04 | Settings dialog |
| Trades to Pass | `trades_to_pass` | int | 1 | Compact face |
| TP1 R:R | `tp1_rr` | float | 0.0 | Compact face |
| TP1 Volume % | `tp1_vol` | float | 0.0 | Compact face |
| TP2 R:R | `tp2_rr` | float | 4.0 | Compact face |
| TP2 Volume % | `tp2_vol` | float | 1.0 | Compact face |

Percentage fields: user types `8`, stored as `0.08`, displayed as `8.00%`.

---

## 5. Computed Outputs — Exact Formulas

All outputs recalculate on every input change. These formulas match the Excel source of truth cell-for-cell.

### 5.1 Derived Values

```python
target        = starting_bal * (1 + profit_target_pct)
to_target     = target - current_bal
dd_remaining  = current_bal - (starting_bal * (1 - max_dd_pct))
drawdown_pct  = max(0, (starting_bal - current_bal) / starting_bal)
daily_cap_usd = current_bal * daily_loss_pct
win_mult      = (tp1_rr * tp1_vol) + (tp2_rr * tp2_vol)
```

### 5.2 Risk % (core formula — from Excel cell H9)

```python
def calc_risk_pct(current_bal, starting_bal, max_dd_pct, win_mult,
                  trades_to_pass, to_target, daily_loss_pct, dd_remaining):
    # Guard: account blown
    if current_bal <= starting_bal * (1 - max_dd_pct):
        return 0.0

    # Guard: TP not configured
    if win_mult == 0:
        return None  # display "—"

    component_1 = to_target / (current_bal * win_mult * trades_to_pass)
    component_2 = daily_loss_pct - 0.005
    component_3 = (dd_remaining / current_bal) - 0.005

    return min(component_1, component_2, component_3)
```

### 5.3 Risk $

```python
risk_usd = current_bal * risk_pct   # only if risk_pct is not None
```

### 5.4 Status Message (from Excel cell G10 — exact priority order)

```python
def calc_status(current_bal, starting_bal, max_dd_pct, win_mult,
                risk_pct, daily_loss_pct, dd_remaining):
    if current_bal <= starting_bal * (1 - max_dd_pct):
        return ("ACCOUNT FAILED — MAX DD BREACHED", "red")

    if win_mult == 0:
        return ("Configure TP Settings", "amber")

    if risk_pct is None or risk_pct == "":
        return ("—", "neutral")

    if risk_pct >= daily_loss_pct - 0.005:
        return ("AT DAILY LIMIT", "red")

    if risk_pct >= (dd_remaining / current_bal) - 0.005:
        return ("AT DD LIMIT", "red")

    if risk_pct >= daily_loss_pct * 0.8:
        return ("Near Daily Limit", "amber")

    if (starting_bal - current_bal) / starting_bal >= max_dd_pct * 0.8:
        return ("Near Max DD", "amber")

    return ("Safe to trade", "green")
```

---

## 6. Conditional Formatting (from Excel)

These rules are extracted directly from the spreadsheet's conditional formatting:

| Element | Condition | Style |
|---------|-----------|-------|
| Drawdown % | > 0% | Red text (`#C0392B`), bold |
| DD Remaining | < 50% of max DD buffer (`dd_remaining < starting_bal * max_dd_pct * 0.5`) | Red text, dark background |
| Risk % / Risk $ | Always | Bold, large font, accent-bordered box |
| Status banner | "Safe" | Green bg (`#149E61`), white text |
| Status banner | "Near..." warnings | Amber bg (`#D08700`), dark text |
| Status banner | "AT LIMIT" / "FAILED" | Red bg (`#C0392B`), white text |

---

## 7. Visual Theme — Kraken-Inspired Dark Mode

### Colour Palette

| Role | Hex | Usage |
|------|-----|-------|
| Background | `#101114` | Window background |
| Surface | `#1A1B21` | Panel backgrounds, input containers |
| Input Field | `#242530` | Text input backgrounds |
| Accent | `#7132F5` | Risk output box border, active states |
| Accent Subtle | `rgba(113,50,245,0.16)` | Highlight fills |
| Text Primary | `#FFFFFF` | Values, outputs |
| Text Secondary | `#9497A9` | Labels |
| Text Muted | `#686B82` | Hints, disabled |
| Success | `#149E61` | Safe to trade |
| Warning | `#D08700` | Near-limit warnings |
| Danger | `#C0392B` | DD%, failed, at-limit |
| Risk Box BG | `#2A2520` | Warm-tinted risk output background |
| Border | `rgba(148,151,169,0.12)` | Subtle dividers |

### Typography

| Element | Font | Size | Weight |
|---------|------|------|--------|
| Title bar | Segoe UI | 12px | 600 |
| Labels | Segoe UI | 9px | 400 |
| Section headers | Segoe UI | 9px | 600 |
| Balance input | Consolas | 16px | 700 |
| Risk output | Consolas | 18px | 700 |
| TP inputs | Consolas | 11px | 500 |
| Status banner | Segoe UI | 10px | 700 |

### Styling Details

- Corner radius: 6px on cards/panels, 4px on inputs
- Borders: 1px `rgba(148,151,169,0.12)`
- Risk output box: 3px left border in `#7132F5`, `#2A2520` background
- Spacing: 8px gutters, 12px section padding
- Pin/gear icons: `#9497A9` default, `#7132F5` when active
- Numbers: right-aligned, Consolas throughout
- Currency: `$` (hardcoded, no selector)

---

## 8. Architecture

### Project Structure

```
GoldenBulletCalc/
├── main.py              # Entry point — window init, event loop
├── calculator.py        # Pure logic — all formulas, no UI dependencies
├── settings.py          # Load/save JSON to %APPDATA%
├── ui/
│   ├── theme.py         # Kraken dark palette, fonts, spacing constants
│   ├── display.py       # Output widgets (risk box, status banner, stats)
│   ├── inputs.py        # Compact face inputs (balance, TP, trades)
│   └── settings_dialog.py  # Settings popup (starting bal, phase, targets)
├── icon.ico
└── requirements.txt
```

### Separation of Concerns

`calculator.py` is pure Python with zero UI imports. Every formula is a function that takes inputs and returns outputs. This enables:
- Unit testing against the Excel reference values
- UI as a thin rendering layer only
- Swapping the UI framework without touching logic

### Data Flow

```
User edits input (Balance / TP / Trades)
    │
    ▼
UI callback (FocusOut / Return / variable trace)
    │
    ▼
calculator.py receives all current values
    │
    ├─► calc derived values (target, to_target, dd_remaining, etc.)
    ├─► calc_risk_pct() → risk_pct
    ├─► calc_risk_usd() → risk_usd
    └─► calc_status() → (message, colour)
    │
    ▼
UI updates all display widgets + conditional formatting
    │
    ▼
settings.py persists full state to JSON
```

---

## 9. Persistence

Auto-save on every input change to `%APPDATA%\GoldenBulletCalc\settings.json`.

```json
{
  "starting_bal": 50000,
  "current_bal": 48000,
  "phase": "Phase 2",
  "profit_target_pct": 0.08,
  "max_dd_pct": 0.10,
  "daily_loss_pct": 0.04,
  "trades_to_pass": 1,
  "tp1_rr": 0.0,
  "tp1_vol": 0.0,
  "tp2_rr": 4.0,
  "tp2_vol": 1.0,
  "always_on_top": true,
  "window_x": null,
  "window_y": null
}
```

On startup: load settings if file exists, else use defaults. Restore window position and always-on-top state.

On corrupt/missing file: fall back to defaults silently.

---

## 10. Input Validation

| Field | Rule | On invalid |
|-------|------|-----------|
| All numeric fields | Reject non-numeric on FocusOut | Revert to last valid value |
| Percentage fields | Accept plain number (8 → 0.08) | Revert |
| Starting Balance | Warn on mid-session change | Tooltip: "This will reset your target and DD anchor" |
| Trades to Pass | Integer, min 1 | Clamp to 1 |
| TP Vol% fields | Must sum to ≤ 100% | Inline amber warning |

---

## 11. Edge Cases

| Scenario | Behaviour |
|----------|-----------|
| Balance at or below DD floor | Risk = 0%, "ACCOUNT FAILED" red banner |
| No TP configured (win_mult = 0) | Risk = "—", "Configure TP Settings" amber |
| risk_pct negative (balance > target) | Clamp to 0% |
| trades_to_pass = 0 | Blocked — minimum 1 |
| Balance exactly at target | to_target = 0, risk = 0% |
| Settings file missing/corrupt | Fall back to defaults |

---

## 12. Build & Distribution

### Development
```bash
python main.py
```

### Compile to .exe
```bash
pyinstaller --onefile --windowed --name "GoldenBulletCalc" --icon=icon.ico main.py
```

Output: `dist/GoldenBulletCalc.exe` — no installer needed, user copies and runs.

Include `icon.ico` (16x16, 32x32, 48x48 sizes) in project root.

---

## 13. Verification

Test case to verify parity with Excel (default inputs):

- Starting Balance: 50,000
- Current Balance: 48,000
- Profit Target: 8%
- Max DD: 10%
- Max Daily Loss: 4%
- Trades to Pass: 1
- TP1: 0 R:R / 0%
- TP2: 4 R:R / 100%

**Expected:**
- target = 54,000
- to_target = 6,000
- dd_remaining = 3,000
- drawdown_pct = 4.00%
- daily_cap = $1,920
- win_mult = 4.0
- Risk % = min(6000/(48000×4×1), 0.035, 3000/48000−0.005) = min(0.03125, 0.035, 0.0575) = **3.125%**
- Risk $ = **$1,500.00**
- Status = **Safe to trade** (green)
