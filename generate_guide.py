"""Generate the VPS setup guide PDF."""

from fpdf import FPDF


class GuidePDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(113, 50, 245)
        self.cell(0, 8, "GOLDEN BULLET", align="R")
        self.ln(12)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

    def section_title(self, title):
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(16, 17, 20)
        self.cell(0, 10, title)
        self.ln(12)

    def sub_title(self, title):
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(50, 50, 50)
        self.cell(0, 8, title)
        self.ln(10)

    def body_text(self, text):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(60, 60, 60)
        self.multi_cell(0, 6, text)
        self.ln(2)

    def code_block(self, text):
        self.set_font("Courier", "", 9)
        self.set_fill_color(36, 37, 48)
        self.set_text_color(255, 255, 255)
        x = self.get_x()
        y = self.get_y()
        lines = text.strip().split("\n")
        block_h = len(lines) * 6 + 8
        self.rect(x, y, self.w - 2 * self.l_margin, block_h, "F")
        self.set_y(y + 4)
        for line in lines:
            self.cell(0, 6, "  " + line)
            self.ln(6)
        self.ln(6)

    def bullet(self, text):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(60, 60, 60)
        x = self.get_x()
        self.cell(6, 6, "-")
        self.multi_cell(0, 6, text)
        self.ln(1)

    def numbered(self, num, text):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(113, 50, 245)
        self.cell(8, 6, f"{num}.")
        self.set_font("Helvetica", "", 10)
        self.set_text_color(60, 60, 60)
        self.multi_cell(0, 6, text)
        self.ln(1)


pdf = GuidePDF()
pdf.set_auto_page_break(auto=True, margin=20)
pdf.add_page()

# Title
pdf.set_font("Helvetica", "B", 22)
pdf.set_text_color(16, 17, 20)
pdf.cell(0, 12, "Golden Bullet Risk Calculator")
pdf.ln(10)
pdf.set_font("Helvetica", "", 12)
pdf.set_text_color(100, 100, 100)
pdf.cell(0, 8, "VPS Installation Guide")
pdf.ln(16)

# Overview
pdf.section_title("Overview")
pdf.body_text(
    "Golden Bullet is a standalone Windows desktop application for calculating "
    "risk sizing during prop firm trading challenges. It runs as a compact "
    "always-on-top HUD that floats over your charts."
)
pdf.body_text(
    "The compiled .exe requires no Python installation and no dependencies. "
    "Download it, run it, and it works."
)

# Prerequisites
pdf.section_title("Prerequisites")
pdf.bullet("Windows VPS with desktop access (RDP)")
pdf.bullet("Internet connection (for initial download only)")
pdf.bullet("GitHub CLI (gh) installed -OR -a web browser")
pdf.ln(2)

# Method 1
pdf.section_title("Method 1: Download via GitHub CLI")
pdf.body_text("If the GitHub CLI (gh) is installed and authenticated on your VPS:")
pdf.ln(2)

pdf.numbered(1, "Open a terminal (Command Prompt, PowerShell, or Git Bash)")
pdf.ln(1)
pdf.numbered(2, "Navigate to where you want the app to live:")
pdf.code_block("cd C:\\Tools")
pdf.numbered(3, "Download the latest release:")
pdf.code_block("gh release download v1.0.0 --repo leye3000/GOLDEN_BULLET --pattern \"*.exe\"")
pdf.numbered(4, "Run the app:")
pdf.code_block("GoldenBulletCalc.exe")
pdf.body_text("That's it. The app will launch and float on top of your other windows.")

# Method 2
pdf.section_title("Method 2: Download via Web Browser")
pdf.numbered(1, "Open a browser on the VPS and go to:")
pdf.code_block("https://github.com/leye3000/GOLDEN_BULLET/releases/tag/v1.0.0")
pdf.numbered(2, 'Under "Assets", click GoldenBulletCalc.exe to download it.')
pdf.numbered(3, "Move the file to a permanent location (e.g. C:\\Tools\\).")
pdf.numbered(4, "Double-click to run.")

# Method 3
pdf.add_page()
pdf.section_title("Method 3: Build from Source")
pdf.body_text(
    "If you prefer to build the .exe yourself, or need to modify the code:"
)
pdf.ln(2)
pdf.numbered(1, "Install Python 3.11+ on the VPS")
pdf.numbered(2, "Clone the repository:")
pdf.code_block(
    "git clone https://github.com/leye3000/GOLDEN_BULLET.git\n"
    "cd GOLDEN_BULLET"
)
pdf.numbered(3, "Create a virtual environment and install dependencies:")
pdf.code_block(
    "python -m venv venv\n"
    "venv\\Scripts\\activate\n"
    "pip install customtkinter pyinstaller"
)
pdf.numbered(4, "Build the .exe:")
pdf.code_block("python build.py")
pdf.numbered(5, "The compiled app will be in the release/ folder:")
pdf.code_block("release\\GoldenBulletCalc.exe")

# First Run
pdf.section_title("First Run & Configuration")
pdf.body_text("On first launch, the app uses these defaults:")
pdf.bullet("Starting Balance: $50,000")
pdf.bullet("Profit Target: 8%")
pdf.bullet("Max Drawdown: 10%")
pdf.bullet("Max Daily Loss: 4%")
pdf.bullet("TP2: 4.0 R:R at 100% volume")
pdf.ln(2)
pdf.body_text(
    'Click the gear icon to open Account Settings and configure '
    "these values for your specific challenge. Settings are saved "
    "automatically and persist between sessions."
)
pdf.body_text(
    "Settings are stored at: %APPDATA%\\GoldenBulletCalc\\settings.json"
)

# Antivirus Note
pdf.section_title("Antivirus Note")
pdf.body_text(
    "PyInstaller-built .exe files are sometimes flagged by antivirus software "
    "(false positive). If the app is blocked or quarantined:"
)
pdf.bullet("Add GoldenBulletCalc.exe to your antivirus exclusion list")
pdf.bullet("Or add the folder containing the .exe as an excluded path")
pdf.body_text(
    "This is a known issue with PyInstaller and does not indicate any "
    "security risk. The source code is fully available in the repository."
)

# Updating
pdf.section_title("Updating to a New Version")
pdf.body_text("When a new release is published:")
pdf.code_block(
    "gh release download --repo leye3000/GOLDEN_BULLET --pattern \"*.exe\" --clobber"
)
pdf.body_text(
    "The --clobber flag overwrites the existing .exe. Your settings are "
    "preserved (stored separately in %APPDATA%)."
)

pdf.output("Golden_Bullet_VPS_Setup_Guide.pdf")
print("PDF generated: Golden_Bullet_VPS_Setup_Guide.pdf")
