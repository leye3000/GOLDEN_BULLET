"""Build script — compiles GoldenBulletCalc.exe via PyInstaller.

Patches around Windows Defender interference with PE timestamp/checksum writes.
Run from project root with venv activated:
    python build.py
"""

import PyInstaller.utils.win32.winutils as winutils
winutils.set_exe_build_timestamp = lambda *a, **k: None
winutils.update_exe_pe_checksum = lambda *a, **k: None

import PyInstaller.__main__

PyInstaller.__main__.run([
    "--onefile", "--windowed",
    "--name", "GoldenBulletCalc",
    "--icon", "icon.ico",
    "--distpath", "release",
    "--clean",
    "main.py",
])
