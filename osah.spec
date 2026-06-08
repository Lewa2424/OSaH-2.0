# -*- mode: python ; coding: utf-8 -*-
# ClearWork — PyInstaller build specification
# Запускати: pyinstaller osah.spec

import sys
from pathlib import Path

project_root = Path(SPECPATH)
src_root = project_root / "src"

a = Analysis(
    [str(project_root / "main.py")],
    pathex=[str(src_root)],
    binaries=[],
    datas=[
        # Включаємо теми та шрифти (якщо є)
        (str(src_root / "osah" / "ui" / "qt" / "design"), "osah/ui/qt/design"),
        # Включаємо іконки та інші статичні UI-ресурси
        (str(src_root / "osah" / "ui" / "qt" / "assets"), "osah/ui/qt/assets"),
        (str(src_root / "osah" / "infrastructure" / "config" / "setup_key_public_key.pem"), "osah/infrastructure/config"),
    ],
    hiddenimports=[
        "osah",
        "osah.main",
        "osah.domain",
        "osah.application",
        "osah.infrastructure",
        "osah.ui",
        "osah.ui.qt",
        "osah.ui.qt.screens",
        "PySide6.QtCore",
        "PySide6.QtGui",
        "PySide6.QtWidgets",
        "PySide6.QtSvg",
        "PySide6.QtSvgWidgets",
        "sqlite3",
        "tomllib",
        "urllib.request",
        "xml.etree.ElementTree",
        "email.mime.text",
        "email.mime.multipart",
        "smtplib",
        "cryptography",
        "docx",
        "osah.version",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "pytest",
        "unittest",
        "tkinter",
        "matplotlib",
        "numpy",
        "PIL",
    ],
    noarchive=False,
    optimize=1,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="ClearWork",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,           # Без чорного вікна терміналу
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(src_root / "osah" / "ui" / "qt" / "assets" / "icons" / "clearwork.ico"),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="ClearWork",
)
