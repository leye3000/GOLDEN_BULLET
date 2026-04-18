"""Output display widgets — risk box, status banner, stats row, balance."""

import customtkinter as ctk
from ui import theme as T


class BalanceDisplay(ctk.CTkFrame):
    def __init__(self, master, on_change=None):
        super().__init__(master, fg_color=T.SURFACE, corner_radius=T.RADIUS)
        self._on_change = on_change
        self._last_valid = "50,000.00"

        label = ctk.CTkLabel(self, text="BALANCE", font=T.FONT_LABEL_BOLD,
                             text_color=T.TEXT_SECONDARY)
        label.pack(anchor="w", padx=T.PAD_SECTION, pady=(T.PAD_INNER, 0))

        input_frame = ctk.CTkFrame(self, fg_color="transparent")
        input_frame.pack(fill="x", padx=T.PAD_SECTION, pady=(2, T.PAD_INNER))

        dollar = ctk.CTkLabel(input_frame, text="$", font=T.FONT_BALANCE,
                              text_color=T.TEXT_PRIMARY)
        dollar.pack(side="left")

        self.entry = ctk.CTkEntry(input_frame, font=T.FONT_BALANCE,
                                  fg_color=T.INPUT_BG, border_color=T.BORDER,
                                  text_color=T.TEXT_PRIMARY, justify="right",
                                  border_width=1, corner_radius=T.INPUT_RADIUS)
        self.entry.pack(side="left", fill="x", expand=True, padx=(4, 0))
        self.entry.bind("<Return>", self._handle_change)
        self.entry.bind("<FocusOut>", self._handle_change)

    def set_value(self, value):
        self._last_valid = f"{value:,.2f}"
        self.entry.delete(0, "end")
        self.entry.insert(0, self._last_valid)

    def get_value(self):
        try:
            raw = self.entry.get().replace(",", "").strip()
            return float(raw)
        except ValueError:
            return None

    def _handle_change(self, event=None):
        val = self.get_value()
        if val is None:
            self.entry.delete(0, "end")
            self.entry.insert(0, self._last_valid)
        else:
            self._last_valid = f"{val:,.2f}"
            self.entry.delete(0, "end")
            self.entry.insert(0, self._last_valid)
            if self._on_change:
                self._on_change()


class StatsRow(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        row1 = ctk.CTkFrame(self, fg_color="transparent")
        row1.pack(fill="x", padx=T.PAD_SECTION, pady=(T.PAD_INNER, 2))
        row1.grid_columnconfigure(0, weight=1)
        row1.grid_columnconfigure(1, weight=1)

        dd_frame = ctk.CTkFrame(row1, fg_color="transparent")
        dd_frame.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(dd_frame, text="DD ", font=T.FONT_STAT_LABEL,
                     text_color=T.TEXT_SECONDARY).pack(side="left")
        self.dd_pct_label = ctk.CTkLabel(dd_frame, text="0.00%",
                                         font=T.FONT_STAT_VALUE, text_color=T.TEXT_PRIMARY)
        self.dd_pct_label.pack(side="left")

        dd_left_frame = ctk.CTkFrame(row1, fg_color="transparent")
        dd_left_frame.grid(row=0, column=1, sticky="e")
        ctk.CTkLabel(dd_left_frame, text="DD Left ", font=T.FONT_STAT_LABEL,
                     text_color=T.TEXT_SECONDARY).pack(side="left")
        self.dd_left_label = ctk.CTkLabel(dd_left_frame, text="$0",
                                          font=T.FONT_STAT_VALUE, text_color=T.TEXT_PRIMARY)
        self.dd_left_label.pack(side="left")

        row2 = ctk.CTkFrame(self, fg_color="transparent")
        row2.pack(fill="x", padx=T.PAD_SECTION, pady=(0, T.PAD_INNER))

        ctk.CTkLabel(row2, text="Daily Cap ", font=T.FONT_STAT_LABEL,
                     text_color=T.TEXT_SECONDARY).pack(side="left")
        self.daily_cap_label = ctk.CTkLabel(row2, text="$0",
                                            font=T.FONT_STAT_VALUE, text_color=T.TEXT_PRIMARY)
        self.daily_cap_label.pack(side="left")

    def update_values(self, drawdown_pct, dd_remaining, daily_cap, dd_pct_style, dd_rem_style):
        dd_colour = T.DANGER if dd_pct_style == "danger" else T.TEXT_PRIMARY
        self.dd_pct_label.configure(text=f"{drawdown_pct:.2%}", text_color=dd_colour)

        rem_colour = T.DANGER if dd_rem_style == "danger" else T.TEXT_PRIMARY
        self.dd_left_label.configure(text=f"${dd_remaining:,.0f}", text_color=rem_colour)

        self.daily_cap_label.configure(text=f"${daily_cap:,.0f}")


class RiskBox(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=T.RISK_BOX_BG, corner_radius=T.RADIUS,
                         border_width=0)

        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(fill="x", padx=T.PAD_SECTION, pady=T.PAD_INNER)

        accent_bar = ctk.CTkFrame(self, fg_color=T.ACCENT, width=3,
                                  corner_radius=0)
        accent_bar.place(x=0, y=0, relheight=1.0)

        left = ctk.CTkFrame(inner, fg_color="transparent")
        left.pack(side="left", expand=True)
        ctk.CTkLabel(left, text="RISK", font=T.FONT_RISK_LABEL,
                     text_color=T.TEXT_SECONDARY).pack(anchor="w")
        self.risk_pct_label = ctk.CTkLabel(left, text="--", font=T.FONT_RISK,
                                           text_color=T.TEXT_PRIMARY)
        self.risk_pct_label.pack(anchor="w")

        right = ctk.CTkFrame(inner, fg_color="transparent")
        right.pack(side="right")
        ctk.CTkLabel(right, text="", font=T.FONT_RISK_LABEL,
                     text_color=T.TEXT_SECONDARY).pack(anchor="e")
        self.risk_usd_label = ctk.CTkLabel(right, text="--", font=T.FONT_RISK,
                                           text_color=T.TEXT_PRIMARY)
        self.risk_usd_label.pack(anchor="e")

    def update_values(self, risk_pct, risk_usd):
        if risk_pct is None:
            self.risk_pct_label.configure(text="\u2014")
            self.risk_usd_label.configure(text="\u2014")
        else:
            self.risk_pct_label.configure(text=f"{risk_pct:.2%}")
            self.risk_usd_label.configure(text=f"${risk_usd:,.2f}")


class StatusBanner(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=T.RADIUS, height=32)
        self.label = ctk.CTkLabel(self, text="", font=T.FONT_STATUS)
        self.label.pack(expand=True, fill="both", padx=T.PAD_INNER, pady=4)

    def update_status(self, message, colour):
        colours = T.STATUS_COLOURS.get(colour, T.STATUS_COLOURS["neutral"])
        self.configure(fg_color=colours["bg"])
        self.label.configure(text=message, text_color=colours["fg"])
