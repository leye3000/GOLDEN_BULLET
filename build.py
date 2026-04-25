"""DEPRECATED - PyInstaller build is no longer the supported distribution path.

PyInstaller-built .exe files are repeatedly quarantined by Bitdefender on the
primary machine. The bootstrapper architecture (unpacking bytecode at runtime)
triggers heuristic AV detection regardless of code signing or temp-dir tricks.

Supported launch path: run.vbs + GoldenBullet.lnk shortcut, set up via setup.ps1.
See CLAUDE.md for current run instructions.

This file is retained only for emergency portable builds where Python cannot be
installed on the target machine. Expect AV interference.

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
