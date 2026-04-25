"""Kraken-inspired dark mode theme constants."""


# ---------------------------------------------------------------------------
# Colour Palette
# ---------------------------------------------------------------------------

BG = "#101114"
SURFACE = "#1A1B21"
INPUT_BG = "#242530"
ACCENT = "#7132F5"
ACCENT_SUBTLE = "#1E1730"
TEXT_PRIMARY = "#FFFFFF"
TEXT_SECONDARY = "#9497A9"
TEXT_MUTED = "#686B82"
SUCCESS = "#149E61"
WARNING = "#D08700"
DANGER = "#C0392B"
RISK_BOX_BG = "#2A2520"
BORDER = "#2A2B33"

STATUS_COLOURS = {
    "green": {"bg": SUCCESS, "fg": TEXT_PRIMARY},
    "amber": {"bg": WARNING, "fg": "#1A1A1A"},
    "red": {"bg": DANGER, "fg": TEXT_PRIMARY},
    "neutral": {"bg": SURFACE, "fg": TEXT_SECONDARY},
}


# ---------------------------------------------------------------------------
# Typography
# ---------------------------------------------------------------------------

FONT_UI = "Segoe UI"
FONT_MONO = "Consolas"

FONT_TITLE = (FONT_UI, 12, "bold")
FONT_LABEL = (FONT_UI, 11)
FONT_LABEL_BOLD = (FONT_UI, 11, "bold")
FONT_BALANCE = (FONT_MONO, 16, "bold")
FONT_RISK = (FONT_MONO, 18, "bold")
FONT_RISK_LABEL = (FONT_UI, 10, "bold")
FONT_TP_INPUT = (FONT_MONO, 11)
FONT_STATUS = (FONT_UI, 10, "bold")
FONT_STAT_VALUE = (FONT_MONO, 11, "bold")
FONT_STAT_LABEL = (FONT_UI, 10)
FONT_SECTION = (FONT_UI, 11, "bold")


# ---------------------------------------------------------------------------
# Spacing & Layout
# ---------------------------------------------------------------------------

RADIUS = 6
INPUT_RADIUS = 4
PAD_SECTION = 12
PAD_INNER = 8
PAD_GUTTER = 8
WINDOW_WIDTH = 300
WINDOW_HEIGHT = 380
