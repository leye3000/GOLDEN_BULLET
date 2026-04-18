"""Golden Bullet Risk Calculator — entry point."""

import customtkinter as ctk
from calculator import recalculate
from settings import load_settings, save_settings
from ui import theme as T
from ui.display import BalanceDisplay, StatsRow, RiskBox, StatusBanner
from ui.inputs import TPInputRow, TradesToPassInput, VolWarning
from ui.settings_dialog import SettingsDialog


class GoldenBulletApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.settings = load_settings()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.title("Golden Bullet")
        self.geometry(f"{T.WINDOW_WIDTH}x{T.WINDOW_HEIGHT}")
        self.minsize(280, 340)
        self.configure(fg_color=T.BG)

        if self.settings.get("always_on_top", True):
            self.attributes("-topmost", True)
        self._pinned = self.settings.get("always_on_top", True)

        wx = self.settings.get("window_x")
        wy = self.settings.get("window_y")
        if wx is not None and wy is not None:
            self.geometry(f"+{wx}+{wy}")

        self._build_ui()
        self._load_values()
        self._recalculate()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self):
        # --- Title Bar ---
        title_bar = ctk.CTkFrame(self, fg_color=T.SURFACE, corner_radius=0, height=36)
        title_bar.pack(fill="x")
        title_bar.pack_propagate(False)

        ctk.CTkLabel(title_bar, text="Golden Bullet", font=T.FONT_TITLE,
                     text_color=T.TEXT_PRIMARY).pack(side="left", padx=T.PAD_SECTION)

        gear_btn = ctk.CTkButton(title_bar, text="\u2699", width=30, height=28,
                                 font=(T.FONT_UI, 14), fg_color="transparent",
                                 hover_color=T.INPUT_BG, text_color=T.TEXT_SECONDARY,
                                 command=self._open_settings)
        gear_btn.pack(side="right", padx=(0, 4))

        self._pin_btn = ctk.CTkButton(title_bar, text="\ud83d\udccc", width=30, height=28,
                                      font=(T.FONT_UI, 12), fg_color="transparent",
                                      hover_color=T.INPUT_BG,
                                      text_color=T.ACCENT if self._pinned else T.TEXT_MUTED,
                                      command=self._toggle_pin)
        self._pin_btn.pack(side="right")

        # --- Balance ---
        self.balance_display = BalanceDisplay(self, on_change=self._recalculate)
        self.balance_display.pack(fill="x", padx=T.PAD_GUTTER, pady=(T.PAD_GUTTER, 0))

        # --- Separator ---
        ctk.CTkFrame(self, fg_color=T.BORDER, height=1).pack(fill="x", padx=T.PAD_SECTION,
                                                              pady=T.PAD_GUTTER)

        # --- Stats Row ---
        self.stats_row = StatsRow(self)
        self.stats_row.pack(fill="x")

        # --- Separator ---
        ctk.CTkFrame(self, fg_color=T.BORDER, height=1).pack(fill="x", padx=T.PAD_SECTION,
                                                              pady=(0, T.PAD_GUTTER))

        # --- TP Inputs ---
        tp_frame = ctk.CTkFrame(self, fg_color="transparent")
        tp_frame.pack(fill="x", padx=T.PAD_SECTION)

        self.tp1 = TPInputRow(tp_frame, "TP1", 0.0, 0.0, on_change=self._recalculate)
        self.tp1.pack(fill="x", pady=2)

        self.tp2 = TPInputRow(tp_frame, "TP2", 4.0, 1.0, on_change=self._recalculate)
        self.tp2.pack(fill="x", pady=2)

        self.vol_warning = VolWarning(tp_frame)
        self.vol_warning.pack(anchor="w")

        self.trades_input = TradesToPassInput(tp_frame, default=1,
                                             on_change=self._recalculate)
        self.trades_input.pack(fill="x", pady=(4, 0))

        # --- Separator ---
        ctk.CTkFrame(self, fg_color=T.BORDER, height=1).pack(fill="x", padx=T.PAD_SECTION,
                                                              pady=T.PAD_GUTTER)

        # --- Risk Box ---
        self.risk_box = RiskBox(self)
        self.risk_box.pack(fill="x", padx=T.PAD_GUTTER)

        # --- Status Banner ---
        self.status_banner = StatusBanner(self)
        self.status_banner.pack(fill="x", padx=T.PAD_GUTTER, pady=(T.PAD_GUTTER, T.PAD_GUTTER))

    def _load_values(self):
        s = self.settings
        self.balance_display.set_value(s["current_bal"])
        self.tp1.set_values(s["tp1_rr"], s["tp1_vol"])
        self.tp2.set_values(s["tp2_rr"], s["tp2_vol"])
        self.trades_input.set_value(s["trades_to_pass"])

    def _recalculate(self):
        s = self.settings

        current_bal = self.balance_display.get_value()
        if current_bal is None:
            return

        tp1_rr = self.tp1.get_rr()
        tp1_vol = self.tp1.get_vol()
        tp2_rr = self.tp2.get_rr()
        tp2_vol = self.tp2.get_vol()
        trades = self.trades_input.get_value()

        self.vol_warning.check(tp1_vol, tp2_vol)

        result = recalculate(
            starting_bal=s["starting_bal"],
            current_bal=current_bal,
            profit_target_pct=s["profit_target_pct"],
            max_dd_pct=s["max_dd_pct"],
            daily_loss_pct=s["daily_loss_pct"],
            trades_to_pass=trades,
            tp1_rr=tp1_rr, tp1_vol=tp1_vol,
            tp2_rr=tp2_rr, tp2_vol=tp2_vol,
        )

        self.stats_row.update_values(
            result["drawdown_pct"], result["dd_remaining"],
            result["daily_cap"], result["dd_pct_style"], result["dd_rem_style"])
        self.risk_box.update_values(result["risk_pct"], result["risk_usd"])
        self.status_banner.update_status(result["status_msg"], result["status_colour"])

        s["current_bal"] = current_bal
        s["tp1_rr"] = tp1_rr
        s["tp1_vol"] = tp1_vol
        s["tp2_rr"] = tp2_rr
        s["tp2_vol"] = tp2_vol
        s["trades_to_pass"] = trades
        save_settings(s)

    def _toggle_pin(self):
        self._pinned = not self._pinned
        self.attributes("-topmost", self._pinned)
        self._pin_btn.configure(text_color=T.ACCENT if self._pinned else T.TEXT_MUTED)
        self.settings["always_on_top"] = self._pinned
        save_settings(self.settings)

    def _open_settings(self):
        SettingsDialog(self, self.settings, on_save=self._on_settings_save)

    def _on_settings_save(self, new_settings):
        self.settings.update(new_settings)
        save_settings(self.settings)
        self._recalculate()

    def _on_close(self):
        try:
            self.settings["window_x"] = self.winfo_x()
            self.settings["window_y"] = self.winfo_y()
            save_settings(self.settings)
        except Exception:
            pass
        self.destroy()


if __name__ == "__main__":
    app = GoldenBulletApp()
    app.mainloop()
