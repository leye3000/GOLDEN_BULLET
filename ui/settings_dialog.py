"""Settings dialog — modal popup for set-once challenge fields."""

import customtkinter as ctk
from ui import theme as T


class SettingsDialog(ctk.CTkToplevel):
    def __init__(self, master, current_settings, on_save=None):
        super().__init__(master)
        self.title("Account Settings")
        self.geometry("280x340")
        self.configure(fg_color=T.BG)
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        self._on_save = on_save
        self._settings = dict(current_settings)
        self._entries = {}

        self._build_ui()
        self.after(100, self.focus_force)

    def _build_ui(self):
        header = ctk.CTkLabel(self, text="ACCOUNT SETTINGS", font=T.FONT_SECTION,
                              text_color=T.TEXT_SECONDARY)
        header.pack(anchor="w", padx=T.PAD_SECTION, pady=(T.PAD_SECTION, T.PAD_INNER))

        fields = [
            ("Starting Balance", "starting_bal", self._settings["starting_bal"], False),
            ("Profit Target %", "profit_target_pct", self._settings["profit_target_pct"] * 100, True),
            ("Max Drawdown %", "max_dd_pct", self._settings["max_dd_pct"] * 100, True),
            ("Max Daily Loss %", "daily_loss_pct", self._settings["daily_loss_pct"] * 100, True),
        ]

        for label_text, key, display_val, is_pct in fields:
            row = ctk.CTkFrame(self, fg_color="transparent")
            row.pack(fill="x", padx=T.PAD_SECTION, pady=3)

            ctk.CTkLabel(row, text=label_text, font=T.FONT_LABEL,
                         text_color=T.TEXT_SECONDARY).pack(side="left")

            entry = ctk.CTkEntry(row, font=T.FONT_TP_INPUT, width=90,
                                 fg_color=T.INPUT_BG, border_color=T.BORDER,
                                 text_color=T.TEXT_PRIMARY, justify="right",
                                 border_width=1, corner_radius=T.INPUT_RADIUS)
            entry.pack(side="right")
            fmt = f"{display_val:.1f}" if is_pct else f"{display_val:,.0f}"
            entry.insert(0, fmt)
            self._entries[key] = (entry, is_pct)

        # Challenge Phase dropdown
        phase_row = ctk.CTkFrame(self, fg_color="transparent")
        phase_row.pack(fill="x", padx=T.PAD_SECTION, pady=3)
        ctk.CTkLabel(phase_row, text="Challenge Phase", font=T.FONT_LABEL,
                     text_color=T.TEXT_SECONDARY).pack(side="left")
        self.phase_menu = ctk.CTkOptionMenu(
            phase_row, values=["Phase 1", "Phase 2", "Funded"],
            font=T.FONT_TP_INPUT, width=100,
            fg_color=T.INPUT_BG, button_color=T.ACCENT,
            button_hover_color=T.ACCENT_SUBTLE,
            text_color=T.TEXT_PRIMARY)
        self.phase_menu.set(self._settings.get("phase", "Phase 1"))
        self.phase_menu.pack(side="right")

        # Warning label for starting balance change
        self.warning = ctk.CTkLabel(self, text="", font=T.FONT_STAT_LABEL,
                                    text_color=T.WARNING, wraplength=250)
        self.warning.pack(padx=T.PAD_SECTION, pady=(2, 0))

        # Save button
        save_btn = ctk.CTkButton(self, text="Save", font=T.FONT_LABEL_BOLD,
                                 fg_color=T.ACCENT, hover_color=T.ACCENT_SUBTLE,
                                 text_color=T.TEXT_PRIMARY, corner_radius=T.RADIUS,
                                 command=self._save)
        save_btn.pack(pady=T.PAD_SECTION)

    def _save(self):
        new_settings = {}
        for key, (entry, is_pct) in self._entries.items():
            try:
                raw = entry.get().replace(",", "").strip()
                val = float(raw)
                if is_pct:
                    val = val / 100.0
                new_settings[key] = val
            except ValueError:
                return

        old_starting = self._settings.get("starting_bal", 50_000)
        if new_settings.get("starting_bal") != old_starting:
            self.warning.configure(
                text="Changing Starting Balance will reset your target and DD anchor")
            self._settings["starting_bal"] = new_settings["starting_bal"]

        self._settings.update(new_settings)
        self._settings["phase"] = self.phase_menu.get()

        if self._on_save:
            self._on_save(self._settings)
        self.destroy()
