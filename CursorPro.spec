# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from pathlib import Path

# 定义项目根目录（使用当前工作目录）
ROOT_DIR = os.path.abspath(os.getcwd())
print(f"项目根目录: {ROOT_DIR}")

# 检查各种资源目录是否存在，确保打包前所有必要文件都准备好
resources_dir = os.path.join(ROOT_DIR, 'resources')
config_dir = os.path.join(ROOT_DIR, 'config')
src_dir = os.path.join(ROOT_DIR, 'src')
icons_dir = os.path.join(resources_dir, 'icons')
version_path = os.path.join(ROOT_DIR, 'version')

# 确保必要的目录存在
for dir_path in [resources_dir, config_dir, src_dir, icons_dir]:
    if not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)
        print(f"创建目录: {dir_path}")

# 检查必要的文件
launcher_path = os.path.join(ROOT_DIR, 'launcher.py')
main_path = os.path.join(ROOT_DIR, 'main.py')

# 根据不同平台选择不同的图标格式
if sys.platform == 'darwin':  # macOS
    icon_path = os.path.join(resources_dir, 'icons', 'app_icon.icns')
    icon_name = 'app_icon.icns'
elif sys.platform == 'win32':  # Windows
    icon_path = os.path.join(resources_dir, 'icons', 'app_icon.ico')
    icon_name = 'app_icon.ico'
else:  # Linux或其他平台
    icon_path = os.path.join(resources_dir, 'icons', 'app_icon.png')
    icon_name = 'app_icon.png'

# 检查图标文件是否存在
if not os.path.exists(icon_path):
    print(f"警告: 平台 {sys.platform} 对应的图标文件不存在 - {icon_path}")
    # 尝试查找其他格式的图标作为备用
    for alt_ext in ['icns', 'ico', 'png']:
        alt_path = os.path.join(resources_dir, 'icons', f'app_icon.{alt_ext}')
        if os.path.exists(alt_path):
            print(f"找到替代图标: {alt_path}")
            icon_path = alt_path
            break

if not os.path.exists(launcher_path):
    print(f"警告: 启动器文件不存在 - {launcher_path}")
if not os.path.exists(main_path):
    print(f"警告: 主程序文件不存在 - {main_path}")

a = Analysis(
    [launcher_path],  # 使用变量替代硬编码路径
    pathex=[ROOT_DIR],  # 添加项目根目录到搜索路径
    binaries=[],
    datas=[
        (resources_dir, 'resources'),
        (config_dir, 'config'),
        (launcher_path, '.'),
        (main_path, '.'),
        (src_dir, 'src'),
        (version_path, '.')
    ],
    hiddenimports=[
        # PySide6相关模块
        'PySide6.QtSvg',
        'PySide6.QtXml',
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'PySide6.QtCharts',  # 图表模块
        'PySide6.QtNetwork', # 网络模块

        # 标准库模块
        'hashlib',
        'json',
        'logging',
        'logging.handlers',  # 添加日志处理器模块
        'datetime',
        'tempfile',
        'platform',
        'traceback',
        'subprocess',
        'time',
        'os',
        'sys',
        'pathlib',
        'poplib',
        'enum',  # 添加枚举模块，用于LogLevel

        # 缺失的依赖模块
        'DrissionPage',
        '_scproxy',

        # 数据处理相关模块
        'openpyxl',
        'openpyxl.worksheet',
        'openpyxl.worksheet._reader',
        'openpyxl.workbook',
        'openpyxl.styles',
        'openpyxl.cell',
        'openpyxl.utils',
        'DataRecorder',
        'DataRecorder.base',
        'DataRecorder.byte_recorder',
        'DataRecorder.setter',

        # 网络和HTTP相关模块
        'urllib',
        'urllib.request',
        'urllib.parse',
        'urllib.error',
        'http',
        'http.client',
        'http.cookiejar',
        'http.cookies',
        'requests',
        'requests.adapters',
        'requests.auth',
        'requests.cookies',
        'requests.exceptions',
        'requests.hooks',
        'requests.models',
        'requests.packages',
        'requests.structures',
        'requests.utils',

        # 邮件相关模块
        'imaplib',
        'email',
        'smtplib',
        'email.message',
        'email.parser',
        'email.policy',
        'email.utils',
        'email.mime.text',
        'email.mime.multipart',

        # 项目模块
        'src',
        'src.main',
        'src.gui',
        'src.gui.main_window',
        'src.gui.widgets',
        'src.gui.widgets.icons',
        'src.gui.pages',
        'src.gui.pages.about',
        'src.logic',
        'src.logic.utils.admin_helper',
        'src.logic.log',
        'src.logic.log.log_manager',
        'src.logic.cursor_pro.keep_alive',
        'src.logic.cursor_pro.get_email_code',
        'src.utils',
        'src.utils.browser_utils',

        # 其他可能用到的模块
        'threading',
        'queue',
        'socket',
        'ssl',
        'json',
        'base64',
        're',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['PyQt5', 'PyQt6', 'PySide2', 'tkinter'],  # 排除不需要的GUI库
    noarchive=False,
    optimize=0,  # 保留原始代码，方便调试
)

# 收集资源文件
extra_binaries = []
extra_datas = []

# 检查并添加一些特定平台的资源文件
if sys.platform == 'darwin':  # macOS
    # 检查并添加macOS特定资源
    pass
elif sys.platform == 'win32':  # Windows
    # 检查并添加Windows特定资源
    pass
elif sys.platform.startswith('linux'):  # Linux
    # 检查并添加Linux特定资源
    pass

# 添加额外的二进制文件和数据文件
if extra_binaries:
    a.binaries.extend(extra_binaries)
if extra_datas:
    a.datas.extend(extra_datas)

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
    console=False,  # GUI应用，无控制台
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=[icon_path],  # 使用变量替代硬编码路径
)

# macOS特定配置
if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name='CursorPro.app',
        icon=icon_path,
        bundle_identifier='com.cursorpro.app',  # 添加唯一的bundle标识符
        info_plist={
            'CFBundleShortVersionString': '1.0.0',  # 添加版本信息
            'CFBundleVersion': '1.0.0',
            'NSHighResolutionCapable': True,        # 支持高分辨率显示
            'NSRequiresAquaSystemAppearance': False, # 支持黑暗模式
            'LSEnvironment': {'MallocNanoZone': '0'},
        },
    )
