"""Compact face input widgets — TP settings, Trades to Pass."""

import customtkinter as ctk
from ui import theme as T


class TPInputRow(ctk.CTkFrame):
    def __init__(self, master, label, default_rr, default_vol_pct, on_change=None):
        super().__init__(master, fg_color="transparent")
        self._on_change = on_change
        self._last_rr = str(default_rr)
        self._last_vol = str(int(default_vol_pct * 100))

        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(3, weight=1)

        ctk.CTkLabel(self, text=label, font=T.FONT_LABEL_BOLD, width=30,
                     text_color=T.TEXT_SECONDARY).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(self, text="R:R", font=T.FONT_STAT_LABEL,
                     text_color=T.TEXT_MUTED).grid(row=0, column=1, sticky="e", padx=(4, 2))

        self.rr_entry = ctk.CTkEntry(self, font=T.FONT_TP_INPUT, width=50,
                                     fg_color=T.INPUT_BG, border_color=T.BORDER,
                                     text_color=T.TEXT_PRIMARY, justify="right",
                                     border_width=1, corner_radius=T.INPUT_RADIUS)
        self.rr_entry.grid(row=0, column=2, padx=(0, 8))
        self.rr_entry.insert(0, self._last_rr)
        self.rr_entry.bind("<Return>", self._handle_rr)
        self.rr_entry.bind("<FocusOut>", self._handle_rr)

        ctk.CTkLabel(self, text="Vol", font=T.FONT_STAT_LABEL,
                     text_color=T.TEXT_MUTED).grid(row=0, column=3, sticky="e", padx=(0, 2))

        self.vol_entry = ctk.CTkEntry(self, font=T.FONT_TP_INPUT, width=50,
                                      fg_color=T.INPUT_BG, border_color=T.BORDER,
                                      text_color=T.TEXT_PRIMARY, justify="right",
                                      border_width=1, corner_radius=T.INPUT_RADIUS)
        self.vol_entry.grid(row=0, column=4)
        self.vol_entry.insert(0, self._last_vol)
        self.vol_entry.bind("<Return>", self._handle_vol)
        self.vol_entry.bind("<FocusOut>", self._handle_vol)

        ctk.CTkLabel(self, text="%", font=T.FONT_STAT_LABEL,
                     text_color=T.TEXT_MUTED).grid(row=0, column=5, padx=(1, 0))

    def _handle_rr(self, event=None):
        try:
            val = float(self.rr_entry.get().strip())
            self._last_rr = str(val)
        except ValueError:
            self.rr_entry.delete(0, "end")
            self.rr_entry.insert(0, self._last_rr)
            return
        if self._on_change:
            self._on_change()

    def _handle_vol(self, event=None):
        try:
            val = float(self.vol_entry.get().strip())
            self._last_vol = str(int(val)) if val == int(val) else str(val)
        except ValueError:
            self.vol_entry.delete(0, "end")
            self.vol_entry.insert(0, self._last_vol)
            return
        if self._on_change:
            self._on_change()

    def get_rr(self):
        try:
            return float(self.rr_entry.get().strip())
        except ValueError:
            return float(self._last_rr)

    def get_vol(self):
        try:
            return float(self.vol_entry.get().strip()) / 100.0
        except ValueError:
            return float(self._last_vol) / 100.0

    def set_values(self, rr, vol_decimal):
        self._last_rr = str(rr)
        vol_pct = int(vol_decimal * 100)
        self._last_vol = str(vol_pct)
        self.rr_entry.delete(0, "end")
        self.rr_entry.insert(0, self._last_rr)
        self.vol_entry.delete(0, "end")
        self.vol_entry.insert(0, self._last_vol)


class TradesToPassInput(ctk.CTkFrame):
    def __init__(self, master, default=1, on_change=None):
        super().__init__(master, fg_color="transparent")
        self._on_change = on_change
        self._last_valid = str(default)

        ctk.CTkLabel(self, text="Trades to Pass", font=T.FONT_LABEL_BOLD,
                     text_color=T.TEXT_SECONDARY).pack(side="left")

        self.entry = ctk.CTkEntry(self, font=T.FONT_TP_INPUT, width=50,
                                  fg_color=T.INPUT_BG, border_color=T.BORDER,
                                  text_color=T.TEXT_PRIMARY, justify="right",
                                  border_width=1, corner_radius=T.INPUT_RADIUS)
        self.entry.pack(side="right")
        self.entry.insert(0, self._last_valid)
        self.entry.bind("<Return>", self._handle_change)
        self.entry.bind("<FocusOut>", self._handle_change)

    def _handle_change(self, event=None):
        try:
            val = int(self.entry.get().strip())
            val = max(1, val)
            self._last_valid = str(val)
            self.entry.delete(0, "end")
            self.entry.insert(0, self._last_valid)
        except ValueError:
            self.entry.delete(0, "end")
            self.entry.insert(0, self._last_valid)
            return
        if self._on_change:
            self._on_change()

    def get_value(self):
        try:
            return max(1, int(self.entry.get().strip()))
        except ValueError:
            return int(self._last_valid)

    def set_value(self, val):
        self._last_valid = str(max(1, val))
        self.entry.delete(0, "end")
        self.entry.insert(0, self._last_valid)


class VolWarning(ctk.CTkLabel):
    def __init__(self, master):
        super().__init__(master, text="", font=T.FONT_STAT_LABEL,
                         text_color=T.WARNING)

    def check(self, tp1_vol, tp2_vol):
        if tp1_vol + tp2_vol > 1.0:
            self.configure(text="TP volumes exceed 100%")
        else:
            self.configure(text="")
