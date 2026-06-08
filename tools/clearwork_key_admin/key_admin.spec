# -*- mode: python ; coding: utf-8 -*-
# ClearWork Key Admin — portable build
# Запускати: pyinstaller key_admin.spec

from pathlib import Path

project_root = Path(SPECPATH)
repo_root = project_root.parents[1]
src_root = repo_root / "src"

a = Analysis(
    [str(project_root / "main.py")],
    pathex=[str(src_root), str(project_root)],
    binaries=[],
    datas=[],
    hiddenimports=[
        "resolve_key_admin_root",
        "ui.main_window",
        "services.ensure_registry_schema",
        "services.generate_setup_key_for_customer",
        "services.insert_key_issue_record",
        "services.list_key_issue_records",
        "osah.domain.services.setup_key.build_setup_key_document",
        "osah.domain.services.setup_key.build_setup_key_payload",
        "osah.domain.services.setup_key.canonical_setup_key_payload_bytes",
        "osah.domain.services.setup_key.setup_key_paste_token",
        "osah.domain.services.setup_key.verify_setup_key_document",
        "cryptography",
        "PySide6.QtCore",
        "PySide6.QtGui",
        "PySide6.QtWidgets",
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
    a.binaries,
    a.datas,
    [],
    name="ClearWorkKeyAdmin",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
