"""Persistence layer — load/save JSON to %APPDATA%\\GoldenBulletCalc\\settings.json."""

import json
import os

DEFAULTS = {
    "starting_bal": 50_000.0,
    "current_bal": 50_000.0,
    "phase": "Phase 1",
    "profit_target_pct": 0.08,
    "max_dd_pct": 0.10,
    "daily_loss_pct": 0.04,
    "trades_to_pass": 1,
    "tp1_rr": 0.0,
    "tp1_vol": 0.0,
    "tp2_rr": 4.0,
    "tp2_vol": 1.0,
    "always_on_top": True,
    "window_x": None,
    "window_y": None,
}

_APP_DIR = os.path.join(os.environ.get("APPDATA", "."), "GoldenBulletCalc")
_SETTINGS_PATH = os.path.join(_APP_DIR, "settings.json")


def load_settings():
    try:
        with open(_SETTINGS_PATH, "r") as f:
            data = json.load(f)
        merged = {**DEFAULTS, **data}
        return merged
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return dict(DEFAULTS)


def save_settings(settings):
    os.makedirs(_APP_DIR, exist_ok=True)
    with open(_SETTINGS_PATH, "w") as f:
        json.dump(settings, f, indent=2)
