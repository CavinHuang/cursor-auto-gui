# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['launcher.py'],
    pathex=[],
    binaries=[
        ('main.py', '.'),
        ('bootstrap.py', '.'),  # 确保bootstrap.py被作为二进制文件包含
    ],
    datas=[
        ('resources', 'resources'),
        ('src', 'src'),  # 确保包含src目录
    ],
    hiddenimports=[
        'src.main',
        'src.gui.main_window',
        'src.logic.utils.admin_helper',
        'src.logic.log.log_manager',
        'PySide6.QtWidgets',
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtNetwork',
        'PySide6.QtSvg',
        'PySide6.QtDBus',
        'platform',
        'subprocess',
        'sys',
        'os',
        'time',
        'traceback',
    ],
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
    [],
    exclude_binaries=True,
    name='CursorPro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='CursorPro',
)
app = BUNDLE(
    coll,
    name='CursorPro.app',
    icon=None,
    bundle_identifier='com.cursor.pro',
)
