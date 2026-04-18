"""Golden Bullet Risk Calculator — pure formula logic.

All functions are pure Python with zero UI dependencies.
Formulas match Golden Bullet Risk Calculator V1.1.xlsx cell-for-cell.
"""


# ---------------------------------------------------------------------------
# Derived Values
# ---------------------------------------------------------------------------

def calc_target(starting_bal, profit_target_pct):
    return starting_bal * (1 + profit_target_pct)


def calc_to_target(target, current_bal):
    return target - current_bal


def calc_dd_remaining(current_bal, starting_bal, max_dd_pct):
    return current_bal - (starting_bal * (1 - max_dd_pct))


def calc_drawdown_pct(starting_bal, current_bal):
    if starting_bal == 0:
        return 0.0
    return max(0.0, (starting_bal - current_bal) / starting_bal)


def calc_daily_cap(current_bal, daily_loss_pct):
    return current_bal * daily_loss_pct


def calc_win_mult(tp1_rr, tp1_vol, tp2_rr, tp2_vol):
    return (tp1_rr * tp1_vol) + (tp2_rr * tp2_vol)


# ---------------------------------------------------------------------------
# Risk % — core formula (Excel cell H9)
# ---------------------------------------------------------------------------

def calc_risk_pct(current_bal, starting_bal, max_dd_pct, win_mult,
                  trades_to_pass, to_target, daily_loss_pct, dd_remaining):
    if current_bal <= starting_bal * (1 - max_dd_pct):
        return 0.0

    if win_mult == 0:
        return None

    component_1 = to_target / (current_bal * win_mult * trades_to_pass)
    component_2 = daily_loss_pct - 0.005
    component_3 = (dd_remaining / current_bal) - 0.005

    result = min(component_1, component_2, component_3)
    return max(0.0, result)


# ---------------------------------------------------------------------------
# Risk $ (Excel cell L9)
# ---------------------------------------------------------------------------

def calc_risk_usd(current_bal, risk_pct):
    if risk_pct is None:
        return None
    return current_bal * risk_pct


# ---------------------------------------------------------------------------
# Status Message (Excel cell G10 — exact priority order)
# ---------------------------------------------------------------------------

def calc_status(current_bal, starting_bal, max_dd_pct, win_mult,
                risk_pct, daily_loss_pct, dd_remaining):
    if current_bal <= starting_bal * (1 - max_dd_pct):
        return ("ACCOUNT FAILED \u2014 MAX DD BREACHED", "red")

    if win_mult == 0:
        return ("Configure TP Settings", "amber")

    if risk_pct is None:
        return ("\u2014", "neutral")

    if risk_pct >= daily_loss_pct - 0.005:
        return ("AT DAILY LIMIT", "red")

    if risk_pct >= (dd_remaining / current_bal) - 0.005:
        return ("AT DD LIMIT", "red")

    if risk_pct >= daily_loss_pct * 0.8:
        return ("Near Daily Limit", "amber")

    if starting_bal > 0 and (starting_bal - current_bal) / starting_bal >= max_dd_pct * 0.8:
        return ("Near Max DD", "amber")

    return ("Safe to trade", "green")


# ---------------------------------------------------------------------------
# Conditional Formatting (from Excel conditional formatting rules)
# ---------------------------------------------------------------------------

def dd_pct_colour(drawdown_pct):
    """Drawdown % is red when > 0 (Excel: H6>0 → red bold)."""
    return "danger" if drawdown_pct > 0 else "normal"


def dd_remaining_colour(dd_remaining, starting_bal, max_dd_pct):
    """DD Remaining turns red when < 50% of max DD buffer (Excel: L5 < C5*C9*0.5)."""
    threshold = starting_bal * max_dd_pct * 0.5
    return "danger" if dd_remaining < threshold else "normal"


# ---------------------------------------------------------------------------
# Full Recalculation — convenience wrapper
# ---------------------------------------------------------------------------

def recalculate(starting_bal, current_bal, profit_target_pct, max_dd_pct,
                daily_loss_pct, trades_to_pass, tp1_rr, tp1_vol, tp2_rr, tp2_vol):
    target = calc_target(starting_bal, profit_target_pct)
    to_target = calc_to_target(target, current_bal)
    dd_remaining = calc_dd_remaining(current_bal, starting_bal, max_dd_pct)
    drawdown_pct = calc_drawdown_pct(starting_bal, current_bal)
    daily_cap = calc_daily_cap(current_bal, daily_loss_pct)
    win_mult = calc_win_mult(tp1_rr, tp1_vol, tp2_rr, tp2_vol)

    risk_pct = calc_risk_pct(current_bal, starting_bal, max_dd_pct, win_mult,
                             trades_to_pass, to_target, daily_loss_pct, dd_remaining)
    risk_usd = calc_risk_usd(current_bal, risk_pct)

    status_msg, status_colour = calc_status(
        current_bal, starting_bal, max_dd_pct, win_mult,
        risk_pct, daily_loss_pct, dd_remaining)

    dd_pct_style = dd_pct_colour(drawdown_pct)
    dd_rem_style = dd_remaining_colour(dd_remaining, starting_bal, max_dd_pct)

    return {
        "target": target,
        "to_target": to_target,
        "dd_remaining": dd_remaining,
        "drawdown_pct": drawdown_pct,
        "daily_cap": daily_cap,
        "win_mult": win_mult,
        "risk_pct": risk_pct,
        "risk_usd": risk_usd,
        "status_msg": status_msg,
        "status_colour": status_colour,
        "dd_pct_style": dd_pct_style,
        "dd_rem_style": dd_rem_style,
    }
