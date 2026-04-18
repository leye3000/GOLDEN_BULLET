"""Tests for calculator.py — verified against Golden Bullet Risk Calculator V1.1.xlsx."""

import pytest
from calculator import (
    calc_target, calc_to_target, calc_dd_remaining, calc_drawdown_pct,
    calc_daily_cap, calc_win_mult, calc_risk_pct, calc_risk_usd,
    calc_status, dd_pct_colour, dd_remaining_colour, recalculate,
)


# ---------------------------------------------------------------------------
# Excel Reference Case
# Starting=50000, Current=48000, Target=8%, DD=10%, Daily=4%, Trades=1
# TP1: 0 R:R / 0%, TP2: 4 R:R / 100%
# ---------------------------------------------------------------------------

class TestExcelReferenceCase:
    def setup_method(self):
        self.starting = 50_000
        self.current = 48_000
        self.profit_target = 0.08
        self.max_dd = 0.10
        self.daily_loss = 0.04
        self.trades = 1
        self.tp1_rr, self.tp1_vol = 0.0, 0.0
        self.tp2_rr, self.tp2_vol = 4.0, 1.0

    def test_target(self):
        assert calc_target(self.starting, self.profit_target) == 54_000

    def test_to_target(self):
        assert calc_to_target(54_000, self.current) == 6_000

    def test_dd_remaining(self):
        assert calc_dd_remaining(self.current, self.starting, self.max_dd) == 3_000

    def test_drawdown_pct(self):
        assert calc_drawdown_pct(self.starting, self.current) == pytest.approx(0.04)

    def test_daily_cap(self):
        assert calc_daily_cap(self.current, self.daily_loss) == 1_920

    def test_win_mult(self):
        assert calc_win_mult(self.tp1_rr, self.tp1_vol, self.tp2_rr, self.tp2_vol) == 4.0

    def test_risk_pct(self):
        win_mult = 4.0
        to_target = 6_000
        dd_remaining = 3_000
        result = calc_risk_pct(self.current, self.starting, self.max_dd, win_mult,
                               self.trades, to_target, self.daily_loss, dd_remaining)
        # min(6000/(48000*4*1), 0.035, 3000/48000-0.005) = min(0.03125, 0.035, 0.0575)
        assert result == pytest.approx(0.03125)

    def test_risk_usd(self):
        assert calc_risk_usd(self.current, 0.03125) == pytest.approx(1_500.0)

    def test_status_safe(self):
        msg, colour = calc_status(self.current, self.starting, self.max_dd, 4.0,
                                  0.03125, self.daily_loss, 3_000)
        assert msg == "Safe to trade"
        assert colour == "green"

    def test_full_recalculate(self):
        r = recalculate(self.starting, self.current, self.profit_target,
                        self.max_dd, self.daily_loss, self.trades,
                        self.tp1_rr, self.tp1_vol, self.tp2_rr, self.tp2_vol)
        assert r["target"] == 54_000
        assert r["to_target"] == 6_000
        assert r["dd_remaining"] == 3_000
        assert r["drawdown_pct"] == pytest.approx(0.04)
        assert r["daily_cap"] == 1_920
        assert r["win_mult"] == 4.0
        assert r["risk_pct"] == pytest.approx(0.03125)
        assert r["risk_usd"] == pytest.approx(1_500.0)
        assert r["status_msg"] == "Safe to trade"
        assert r["status_colour"] == "green"


# ---------------------------------------------------------------------------
# Edge Cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_account_blown(self):
        # current_bal <= starting * (1 - max_dd) → 45000 <= 50000*0.9 = 45000
        risk = calc_risk_pct(45_000, 50_000, 0.10, 4.0, 1, 9_000, 0.04, 0)
        assert risk == 0.0

    def test_account_blown_status(self):
        msg, colour = calc_status(45_000, 50_000, 0.10, 4.0, 0.0, 0.04, 0)
        assert "ACCOUNT FAILED" in msg
        assert colour == "red"

    def test_no_tp_configured(self):
        risk = calc_risk_pct(48_000, 50_000, 0.10, 0, 1, 6_000, 0.04, 3_000)
        assert risk is None

    def test_no_tp_status(self):
        msg, colour = calc_status(48_000, 50_000, 0.10, 0, None, 0.04, 3_000)
        assert msg == "Configure TP Settings"
        assert colour == "amber"

    def test_balance_at_target(self):
        # to_target = 0, so component_1 = 0
        risk = calc_risk_pct(54_000, 50_000, 0.10, 4.0, 1, 0, 0.04, 9_000)
        assert risk == 0.0

    def test_negative_risk_clamped(self):
        # balance beyond target → to_target negative → result clamped to 0
        risk = calc_risk_pct(56_000, 50_000, 0.10, 4.0, 1, -2_000, 0.04, 11_000)
        assert risk == 0.0

    def test_risk_usd_none_when_no_tp(self):
        assert calc_risk_usd(48_000, None) is None


# ---------------------------------------------------------------------------
# Status Priority Chain
# ---------------------------------------------------------------------------

class TestStatusPriority:
    def test_at_daily_limit(self):
        # risk_pct >= daily_loss - 0.005 = 0.035
        msg, colour = calc_status(48_000, 50_000, 0.10, 4.0, 0.035, 0.04, 3_000)
        assert msg == "AT DAILY LIMIT"
        assert colour == "red"

    def test_at_dd_limit(self):
        # dd_remaining/current - 0.005 is close to risk_pct
        # dd_remaining = 500, current = 48000 → threshold = 500/48000-0.005 ≈ 0.00542
        msg, colour = calc_status(48_000, 50_000, 0.10, 4.0, 0.006, 0.04, 500)
        assert msg == "AT DD LIMIT"
        assert colour == "red"

    def test_near_daily_limit(self):
        # risk_pct >= daily_loss * 0.8 = 0.032
        msg, colour = calc_status(48_000, 50_000, 0.10, 4.0, 0.033, 0.04, 3_000)
        assert msg == "Near Daily Limit"
        assert colour == "amber"

    def test_near_max_dd(self):
        # (starting - current) / starting >= max_dd * 0.8
        # (50000 - 45800) / 50000 = 0.084 >= 0.08
        msg, colour = calc_status(45_800, 50_000, 0.10, 4.0, 0.01, 0.04, 800)
        assert msg == "Near Max DD"
        assert colour == "amber"

    def test_safe(self):
        msg, colour = calc_status(49_000, 50_000, 0.10, 4.0, 0.02, 0.04, 4_000)
        assert msg == "Safe to trade"
        assert colour == "green"


# ---------------------------------------------------------------------------
# Conditional Formatting
# ---------------------------------------------------------------------------

class TestConditionalFormatting:
    def test_dd_pct_red_when_positive(self):
        assert dd_pct_colour(0.04) == "danger"

    def test_dd_pct_normal_when_zero(self):
        assert dd_pct_colour(0.0) == "normal"

    def test_dd_remaining_red_when_critical(self):
        # threshold = 50000 * 0.10 * 0.5 = 2500, dd_remaining = 2000 < 2500
        assert dd_remaining_colour(2_000, 50_000, 0.10) == "danger"

    def test_dd_remaining_normal_when_healthy(self):
        # threshold = 2500, dd_remaining = 3000 >= 2500
        assert dd_remaining_colour(3_000, 50_000, 0.10) == "normal"

    def test_dd_remaining_exactly_at_threshold(self):
        # threshold = 2500, dd_remaining = 2500 — not less than, so normal
        assert dd_remaining_colour(2_500, 50_000, 0.10) == "normal"
