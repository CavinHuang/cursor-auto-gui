#!/usr/bin/env python
"""
Cursor Pro 打包脚本
"""
import os
import sys
import platform
import shutil
import subprocess
import time
from pathlib import Path

# 项目根目录
ROOT_DIR = Path(__file__).parent.parent.absolute()

# 环境变量名
ENV_VARS = {
    'SKIP_ADMIN': 'CURSOR_PRO_SKIP_ADMIN',
    'RESTARTED': 'CURSOR_PRO_RESTARTED',
    'LOG_FILE': 'CURSOR_PRO_LOG_FILE'
}

def ensure_dir(directory):
    """确保目录存在"""
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory

def clean_build_dir():
    """清理构建目录"""
    build_dir = os.path.join(ROOT_DIR, 'build')
    dist_dir = os.path.join(ROOT_DIR, 'dist')

    if os.path.exists(build_dir):
        print(f"清理构建目录: {build_dir}")
        shutil.rmtree(build_dir)

    if os.path.exists(dist_dir):
        print(f"清理分发目录: {dist_dir}")
        shutil.rmtree(dist_dir)

def check_dependencies():
    """检查构建所需的依赖项"""
    missing_deps = []

    # 检查 PyInstaller
    try:
        subprocess.run(['pyinstaller', '--version'], check=True, stdout=subprocess.PIPE)
        print("✓ PyInstaller 已安装")
    except (subprocess.SubprocessError, FileNotFoundError):
        missing_deps.append("PyInstaller")
        print("✗ PyInstaller 未安装")

    # 检查 PySide6
    try:
        import importlib
        importlib.import_module('PySide6')
        print("✓ PySide6 已安装")
    except ImportError:
        missing_deps.append("PySide6")
        print("✗ PySide6 未安装")

    # 验证项目文件
    required_files = [
        'launcher.py',
        'main.py',
        'CursorPro.spec',
        os.path.join('resources', 'icons')
    ]

    for file_path in required_files:
        full_path = os.path.join(ROOT_DIR, file_path)
        if os.path.exists(full_path):
            print(f"✓ 已找到 {file_path}")
        else:
            print(f"✗ 未找到 {file_path}")
            if file_path != 'CursorPro.spec':  # .spec 文件是可选的
                missing_deps.append(file_path)

    return missing_deps

def build_mac():
    """构建 macOS 应用程序"""
    print("开始构建 macOS 应用程序...")

    # 确保资源目录中包含App图标
    resources_dir = os.path.join(ROOT_DIR, 'resources')
    icons_dir = os.path.join(resources_dir, 'icons')
    ensure_dir(icons_dir)

    # 创建Info.plist文件，设置需要管理员权限
    info_plist_path = os.path.join(resources_dir, 'Info.plist')
    if not os.path.exists(info_plist_path):
        with open(info_plist_path, 'w') as f:
            f.write('''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleIdentifier</key>
    <string>com.cursorpro.app</string>
    <key>CFBundleName</key>
    <string>CursorPro</string>
    <key>CFBundleDisplayName</key>
    <string>Cursor Pro</string>
    <key>CFBundleExecutable</key>
    <string>CursorPro</string>
    <key>CFBundleIconFile</key>
    <string>app_icon.icns</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>NSRequiresAquaSystemAppearance</key>
    <false/>
    <key>LSEnvironment</key>
    <dict>
        <key>MallocNanoZone</key>
        <string>0</string>
    </dict>
</dict>
</plist>
''')
        print(f"已创建 Info.plist: {info_plist_path}")

    # 使用spec文件进行打包
    spec_file = os.path.join(ROOT_DIR, 'CursorPro.spec')

    if not os.path.exists(spec_file):
        print(f"错误: spec文件不存在: {spec_file}")
        print("正在使用命令行参数代替...")

        # 使用原来的命令行方式打包
        # 构建图标路径，确保使用有效的路径
        icon_path = ''
        if os.path.exists(os.path.join(ROOT_DIR, 'resources/icons/app_icon.icns')):
            icon_path = os.path.join(ROOT_DIR, 'resources/icons/app_icon.icns')

        # 使用PyInstaller打包
        cmd = [
            'pyinstaller',
            '--name=CursorPro',
            '--windowed',
            '--onefile',  # 打包为单一文件
            '--clean',    # 清理临时文件
        ]

        # 仅在存在图标文件时添加icon参数
        if icon_path:
            cmd.append(f'--icon={icon_path}')

        # 添加其他必要参数
        cmd.extend([
            '--add-data=resources:resources',
            '--add-data=config:config',
            '--add-data=launcher.py:.',
            '--add-data=main.py:.',
            '--add-data=version:.',
            '--hidden-import=PySide6.QtSvg',
            '--hidden-import=PySide6.QtXml',
            '--hidden-import=PySide6.QtCore',
            '--hidden-import=PySide6.QtGui',
            '--hidden-import=PySide6.QtWidgets',
            '--hidden-import=PySide6.QtCharts',
            '--hidden-import=PySide6.QtNetwork',
            '--hidden-import=hashlib',
            '--hidden-import=json',
            '--hidden-import=imaplib',
            '--hidden-import=email',
            '--hidden-import=smtplib',
            '--hidden-import=email.message',
            '--hidden-import=email.parser',
            '--hidden-import=email.policy',
            '--hidden-import=email.utils',
            '--hidden-import=email.mime.text',
            '--hidden-import=email.mime.multipart',
            '--hidden-import=src',
            '--hidden-import=src.main',
            '--hidden-import=src.gui',
            '--hidden-import=src.gui.main_window',
            '--hidden-import=src.logic',
            '--hidden-import=src.logic.utils.admin_helper',
            '--hidden-import=src.logic.log.log_manager',
            '--hidden-import=src.logic.cursor_pro.keep_alive',
            '--hidden-import=src.logic.cursor_pro.get_email_code',
            os.path.join(ROOT_DIR, 'launcher.py')  # 提供完整的脚本路径
        ])
    else:
        # 使用spec文件打包
        cmd = [
            'pyinstaller',
            '--clean',    # 清理临时文件
            spec_file     # 使用spec文件
        ]

    # 打印命令以便调试
    print("执行命令:")
    print(" ".join(cmd))

    # 执行打包命令
    start_time = time.time()
    result = subprocess.run(cmd, cwd=ROOT_DIR)
    end_time = time.time()

    if result.returncode != 0:
        print(f"错误: PyInstaller 命令失败，返回码: {result.returncode}")
        return False

    # 复制一些额外文件
    dist_dir = os.path.join(ROOT_DIR, 'dist', 'CursorPro.app')
    if os.path.exists(dist_dir):
        # 复制Info.plist
        dest_plist = os.path.join(dist_dir, 'Contents', 'Info.plist')
        shutil.copy2(info_plist_path, dest_plist)
        print(f"已复制Info.plist: {dest_plist}")

        # 验证可执行文件
        macos_dir = os.path.join(dist_dir, 'Contents', 'MacOS')
        exe_path = os.path.join(macos_dir, 'CursorPro')
        if os.path.exists(exe_path) and os.access(exe_path, os.X_OK):
            print(f"✓ 可执行文件已创建并具有执行权限: {exe_path}")
        else:
            print(f"✗ 可执行文件不存在或没有执行权限: {exe_path}")
            if os.path.exists(exe_path):
                os.chmod(exe_path, 0o755)
                print(f"已添加执行权限到: {exe_path}")

    print(f"macOS应用程序构建完成! 用时: {int(end_time - start_time)}秒")
    return True

def build_windows():
    """构建Windows应用程序"""
    print("开始构建Windows应用程序...")

    # 确保资源目录中包含App图标
    resources_dir = os.path.join(ROOT_DIR, 'resources')
    icons_dir = os.path.join(resources_dir, 'icons')
    ensure_dir(icons_dir)

    # 创建UAC清单文件
    manifest_path = os.path.join(resources_dir, 'uac_manifest.xml')
    if not os.path.exists(manifest_path):
        with open(manifest_path, 'w') as f:
            f.write('''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
  <trustInfo xmlns="urn:schemas-microsoft-com:asm.v3">
    <security>
      <requestedPrivileges>
        <requestedExecutionLevel level="requireAdministrator" uiAccess="false"/>
      </requestedPrivileges>
    </security>
  </trustInfo>
</assembly>
''')
        print(f"已创建UAC清单文件: {manifest_path}")

    # 使用spec文件进行打包
    spec_file = os.path.join(ROOT_DIR, 'CursorPro.spec')

    if os.path.exists(spec_file):
        # 使用spec文件打包
        cmd = [
            'pyinstaller',
            '--clean',    # 清理临时文件
            spec_file     # 使用spec文件
        ]

        # 打印命令以便调试
        print("执行命令:")
        print(" ".join(cmd))

        # 执行打包命令
        start_time = time.time()
        result = subprocess.run(cmd, cwd=ROOT_DIR)
        end_time = time.time()

        if result.returncode != 0:
            print(f"错误: PyInstaller 命令失败，返回码: {result.returncode}")
            return False
    else:
        # 构建图标路径，确保使用有效的路径
        icon_path = ''
        if os.path.exists(os.path.join(ROOT_DIR, 'resources/icons/app_icon.ico')):
            icon_path = os.path.join(ROOT_DIR, 'resources/icons/app_icon.ico')

        # 使用PyInstaller打包
        cmd = [
            'pyinstaller',
            '--name=CursorPro',
            '--windowed',
            '--onefile',  # 打包为单一文件
            '--clean',    # 清理临时文件
        ]

        # 仅在存在图标文件时添加icon参数
        if icon_path:
            cmd.append(f'--icon={icon_path}')

        # 添加其他必要参数
        cmd.extend([
            '--add-data=resources;resources',
            '--add-data=config;config',
            '--add-data=launcher.py;.',
            '--add-data=main.py;.',
            '--add-data=version;.',
            '--hidden-import=PySide6.QtSvg',
            '--hidden-import=PySide6.QtXml',
            '--hidden-import=PySide6.QtCore',
            '--hidden-import=PySide6.QtGui',
            '--hidden-import=PySide6.QtWidgets',
            '--hidden-import=PySide6.QtCharts',
            '--hidden-import=PySide6.QtNetwork',
            '--hidden-import=hashlib',
            '--hidden-import=json',
            '--hidden-import=imaplib',
            '--hidden-import=email',
            '--hidden-import=smtplib',
            '--hidden-import=email.message',
            '--hidden-import=email.parser',
            '--hidden-import=email.policy',
            '--hidden-import=email.utils',
            '--hidden-import=email.mime.text',
            '--hidden-import=email.mime.multipart',
            '--hidden-import=src',
            '--hidden-import=src.main',
            '--hidden-import=src.gui',
            '--hidden-import=src.gui.main_window',
            '--hidden-import=src.logic',
            '--hidden-import=src.logic.utils.admin_helper',
            '--hidden-import=src.logic.log.log_manager',
            '--hidden-import=src.logic.cursor_pro.keep_alive',
            '--hidden-import=src.logic.cursor_pro.get_email_code',
            '--uac-admin',  # 请求管理员权限
        ])

        # 添加清单文件
        if os.path.exists(manifest_path):
            cmd.append(f'--manifest={manifest_path}')

        # 添加入口点脚本
        cmd.append(os.path.join(ROOT_DIR, 'launcher.py'))

        # 打印命令以便调试
        print("执行命令:")
        print(" ".join(cmd))

        # 执行打包命令
        start_time = time.time()
        result = subprocess.run(cmd, cwd=ROOT_DIR)
        end_time = time.time()

        if result.returncode != 0:
            print(f"错误: PyInstaller 命令失败，返回码: {result.returncode}")
            return False

    # 检查打包结果
    dist_dir = os.path.join(ROOT_DIR, 'dist')
    if os.path.exists(dist_dir):
        exe_file = os.path.join(dist_dir, 'CursorPro.exe')
        if os.path.exists(exe_file):
            print(f"✓ 已成功创建可执行文件: {exe_file}")
        else:
            print("✗ 警告: 可执行文件未创建成功")
            return False

    print(f"Windows应用程序构建完成! 用时: {int(end_time - start_time)}秒")
    return True

def build_linux():
    """构建Linux应用程序"""
    print("开始构建Linux应用程序...")

    # 确保资源目录中包含App图标
    resources_dir = os.path.join(ROOT_DIR, 'resources')
    icons_dir = os.path.join(resources_dir, 'icons')
    ensure_dir(icons_dir)

    # 使用spec文件进行打包
    spec_file = os.path.join(ROOT_DIR, 'CursorPro.spec')

    if os.path.exists(spec_file):
        # 使用spec文件打包
        cmd = [
            'pyinstaller',
            '--clean',    # 清理临时文件
            spec_file     # 使用spec文件
        ]

        # 打印命令以便调试
        print("执行命令:")
        print(" ".join(cmd))

        # 执行打包命令
        start_time = time.time()
        result = subprocess.run(cmd, cwd=ROOT_DIR)
        end_time = time.time()

        if result.returncode != 0:
            print(f"错误: PyInstaller 命令失败，返回码: {result.returncode}")
            return False
    else:
        # 构建图标路径，确保使用有效的路径
        icon_path = ''
        if os.path.exists(os.path.join(ROOT_DIR, 'resources/icons/app_icon.png')):
            icon_path = os.path.join(ROOT_DIR, 'resources/icons/app_icon.png')

        # 使用PyInstaller打包
        cmd = [
            'pyinstaller',
            '--name=CursorPro',
            '--windowed',
            '--onefile',  # 打包为单一文件
            '--clean',    # 清理临时文件
        ]

        # 仅在存在图标文件时添加icon参数
        if icon_path:
            cmd.append(f'--icon={icon_path}')

        # 添加其他必要参数
        cmd.extend([
            '--add-data=resources:resources',
            '--add-data=config:config',
            '--add-data=launcher.py:.',
            '--add-data=main.py:.',
            '--hidden-import=PySide6.QtSvg',
            '--hidden-import=PySide6.QtXml',
            '--hidden-import=PySide6.QtCore',
            '--hidden-import=PySide6.QtGui',
            '--hidden-import=PySide6.QtWidgets',
            '--hidden-import=PySide6.QtCharts',
            '--hidden-import=PySide6.QtNetwork',
            '--hidden-import=hashlib',
            '--hidden-import=json',
            '--hidden-import=imaplib',
            '--hidden-import=email',
            '--hidden-import=smtplib',
            '--hidden-import=email.message',
            '--hidden-import=email.parser',
            '--hidden-import=email.policy',
            '--hidden-import=email.utils',
            '--hidden-import=email.mime.text',
            '--hidden-import=email.mime.multipart',
            '--hidden-import=src',
            '--hidden-import=src.main',
            '--hidden-import=src.gui',
            '--hidden-import=src.gui.main_window',
            '--hidden-import=src.logic',
            '--hidden-import=src.logic.utils.admin_helper',
            '--hidden-import=src.logic.log.log_manager',
            '--hidden-import=src.logic.cursor_pro.keep_alive',
            '--hidden-import=src.logic.cursor_pro.get_email_code',
            os.path.join(ROOT_DIR, 'launcher.py')  # 提供完整的脚本路径
        ])

        # 打印命令以便调试
        print("执行命令:")
        print(" ".join(cmd))

        # 执行打包命令
        start_time = time.time()
        result = subprocess.run(cmd, cwd=ROOT_DIR)
        end_time = time.time()

        if result.returncode != 0:
            print(f"错误: PyInstaller 命令失败，返回码: {result.returncode}")
            return False

    # 检查打包结果
    dist_dir = os.path.join(ROOT_DIR, 'dist')
    if os.path.exists(dist_dir):
        exe_file = os.path.join(dist_dir, 'CursorPro')
        if os.path.exists(exe_file):
            print(f"✓ 已成功创建可执行文件: {exe_file}")
            # 确保可执行权限
            os.chmod(exe_file, 0o755)
        else:
            print("✗ 警告: 可执行文件未创建成功")
            return False

    # 创建桌面文件，添加需要管理员权限的标记
    desktop_file_path = os.path.join(ROOT_DIR, 'dist', 'CursorPro.desktop')
    with open(desktop_file_path, 'w') as f:
        f.write('''[Desktop Entry]
Name=Cursor Pro
Comment=Cursor Pro Application
Exec=pkexec %k
Icon=cursorpro
Terminal=false
Type=Application
Categories=Utility;
''')
    print(f"已创建桌面文件: {desktop_file_path}")

    print(f"Linux应用程序构建完成! 用时: {int(end_time - start_time)}秒")
    return True

def main():
    """主函数"""
    # 显示欢迎信息
    print("=" * 50)
    print("Cursor Pro 应用程序构建工具")
    print("=" * 50)
    print(f"操作系统: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version.split()[0]}")
    print(f"项目目录: {ROOT_DIR}")
    print("-" * 50)

    # 检查依赖项
    print("正在检查依赖项...")
    missing_deps = check_dependencies()
    if missing_deps:
        print("\n缺少必要的依赖项:")
        for dep in missing_deps:
            print(f"  - {dep}")

        if "PyInstaller" in missing_deps:
            print("\n请使用以下命令安装PyInstaller:")
            print("  pip install pyinstaller")

        if "PySide6" in missing_deps:
            print("\n请使用以下命令安装PySide6:")
            print("  pip install PySide6")

        if any(dep not in ["PyInstaller", "PySide6"] for dep in missing_deps):
            print("\n请确保以下项目文件存在:")
            print("  - launcher.py")
            print("  - main.py")
            print("  - resources/icons/")

        print("\n修复这些问题后再次运行构建脚本。")
        return 1

    # 清理旧的构建文件
    print("\n正在清理旧的构建文件...")
    clean_build_dir()

    # 确保必要的目录存在
    ensure_dir(os.path.join(ROOT_DIR, 'resources'))
    ensure_dir(os.path.join(ROOT_DIR, 'resources', 'icons'))
    ensure_dir(os.path.join(ROOT_DIR, 'config'))

    # 根据当前操作系统选择打包方式
    system = platform.system()
    build_success = False

    try:
        print("\n" + "=" * 50)
        if system == 'Darwin':
            build_success = build_mac()
        elif system == 'Windows':
            build_success = build_windows()
        elif system == 'Linux':
            build_success = build_linux()
        else:
            print(f"不支持的操作系统: {system}")
            return 1
    except Exception as e:
        print(f"构建过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return 1

    if build_success:
        print("\n" + "=" * 50)
        print("✅ 构建成功完成!")
        print(f"应用程序可在以下位置找到: {os.path.join(ROOT_DIR, 'dist')}")
        print("=" * 50)
        return 0
    else:
        print("\n" + "=" * 50)
        print("❌ 构建失败!")
        print("请检查上面的错误信息，修复问题后重新构建。")
        print("=" * 50)
        return 1

if __name__ == "__main__":
    sys.exit(main())