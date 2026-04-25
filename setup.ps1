# Golden Bullet - first-time setup (Python + venv + deps only).
# Run with:
#   powershell -ExecutionPolicy Bypass -File setup.ps1
#
# Idempotent: safe to re-run. Shortcut creation is delegated to
# install_shortcuts.vbs to keep this PowerShell script minimal and
# friendly to antivirus heuristics.

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition

Write-Host "Golden Bullet setup" -ForegroundColor Cyan
Write-Host "Project root: $projectRoot"
Write-Host ""

# 1. Detect Python
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "ERROR: Python not found on PATH." -ForegroundColor Red
    Write-Host "Install Python 3.10+ from https://www.python.org/downloads/"
    Write-Host "Tick 'Add Python to PATH' during install, then re-run this script."
    exit 1
}
Write-Host "Found Python: $($python.Source)"

# 2. Create venv if missing
$venvPath = Join-Path $projectRoot "venv"
if (-not (Test-Path $venvPath)) {
    Write-Host "Creating virtual environment..."
    & python -m venv $venvPath
    if ($LASTEXITCODE -ne 0) { throw "venv creation failed (exit $LASTEXITCODE)" }
} else {
    Write-Host "Virtual environment already exists, skipping creation."
}

# 3. Install / update dependencies
# Use `python -m pip` rather than pip.exe directly so pip can upgrade itself
# without hitting Windows' "file in use" lock on its own executable.
$venvPython = Join-Path $venvPath "Scripts\python.exe"
$requirements = Join-Path $projectRoot "requirements.txt"

Write-Host "Upgrading pip..."
& $venvPython -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw "pip self-upgrade failed (exit $LASTEXITCODE)" }

Write-Host "Installing requirements..."
& $venvPython -m pip install -r $requirements
if ($LASTEXITCODE -ne 0) { throw "pip install failed (exit $LASTEXITCODE)" }

# 4. Hand off to VBS helper for shortcut creation
$vbsHelper = Join-Path $projectRoot "install_shortcuts.vbs"
if (Test-Path $vbsHelper) {
    Write-Host "Creating shortcuts via install_shortcuts.vbs..."
    & wscript.exe $vbsHelper
} else {
    Write-Host "install_shortcuts.vbs not found - skipping shortcut creation." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Setup complete." -ForegroundColor Green
Write-Host "Launch via the Desktop shortcut or Start Menu > Golden Bullet."
Write-Host "If no shortcut was created, right-click run.vbs -> Send to -> Desktop (create shortcut)."
