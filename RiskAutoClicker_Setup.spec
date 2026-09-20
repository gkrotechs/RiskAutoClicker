# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['installer/installer_main.py'],
    pathex=[],
    binaries=[],
    datas=[('installer/installer_frontend', 'installer_frontend'), ('dist/RiskAutoClicker.exe', '.'), ('C:/Users/gkro/Documents/Projects/ClearAutoClicker/app.ico', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='RiskAutoClicker_Setup',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['C:/Users/gkro/Documents/Projects/ClearAutoClicker/app.ico'],
)
