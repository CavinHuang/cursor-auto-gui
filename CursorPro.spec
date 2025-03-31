# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['/Users/cavinhuang/workspace/projects/cursor-auto-gui/launcher.py'],
    pathex=[],
    binaries=[],
    datas=[('resources', 'resources'), ('config', 'config'), ('launcher.py', '.'), ('main.py', '.')],
    hiddenimports=['PySide6.QtSvg', 'PySide6.QtXml', 'hashlib', 'json', 'src', 'src.main'],
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
    name='CursorPro',
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
    icon=['/Users/cavinhuang/workspace/projects/cursor-auto-gui/resources/icons/app_icon.icns'],
)
app = BUNDLE(
    exe,
    name='CursorPro.app',
    icon='/Users/cavinhuang/workspace/projects/cursor-auto-gui/resources/icons/app_icon.icns',
    bundle_identifier=None,
)
