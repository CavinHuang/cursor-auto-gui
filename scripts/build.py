#!/usr/bin/env python
"""
Cursor Pro 打包脚本
"""
import os
import sys
import platform
import shutil
import subprocess
from pathlib import Path

# 项目根目录
ROOT_DIR = Path(__file__).parent.parent.absolute()

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
        '--hidden-import=PySide6.QtSvg',
        '--hidden-import=PySide6.QtXml',
        '--hidden-import=hashlib',
        '--hidden-import=json',
        '--hidden-import=src',       # 确保src模块被导入
        '--hidden-import=src.main',  # 确保src.main模块被导入
        os.path.join(ROOT_DIR, 'launcher.py')  # 提供完整的脚本路径
    ])

    # 打印命令以便调试
    print("执行命令:")
    print(" ".join(cmd))

    # 执行打包命令
    subprocess.run(cmd, cwd=ROOT_DIR)

    # 复制一些额外文件
    dist_dir = os.path.join(ROOT_DIR, 'dist', 'CursorPro.app')
    if os.path.exists(dist_dir):
        # 复制Info.plist
        dest_plist = os.path.join(dist_dir, 'Contents', 'Info.plist')
        shutil.copy2(info_plist_path, dest_plist)
        print(f"已复制Info.plist: {dest_plist}")

    print("macOS应用程序构建完成!")

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
        '--hidden-import=PySide6.QtSvg',
        '--hidden-import=PySide6.QtXml',
        '--hidden-import=hashlib',
        '--hidden-import=json',
        '--hidden-import=src',       # 确保src模块被导入
        '--hidden-import=src.main',  # 确保src.main模块被导入
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
    subprocess.run(cmd, cwd=ROOT_DIR)

    # 检查打包结果
    dist_dir = os.path.join(ROOT_DIR, 'dist')
    if os.path.exists(dist_dir):
        exe_file = os.path.join(dist_dir, 'CursorPro.exe')
        if os.path.exists(exe_file):
            print(f"已成功创建可执行文件: {exe_file}")
        else:
            print("警告: 可执行文件未创建成功")

    print("Windows应用程序构建完成!")

def build_linux():
    """构建Linux应用程序"""
    print("开始构建Linux应用程序...")

    # 确保资源目录中包含App图标
    resources_dir = os.path.join(ROOT_DIR, 'resources')
    icons_dir = os.path.join(resources_dir, 'icons')
    ensure_dir(icons_dir)

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
        '--hidden-import=hashlib',
        '--hidden-import=json',
        '--hidden-import=src',       # 确保src模块被导入
        '--hidden-import=src.main',  # 确保src.main模块被导入
        os.path.join(ROOT_DIR, 'launcher.py')  # 提供完整的脚本路径
    ])

    # 打印命令以便调试
    print("执行命令:")
    print(" ".join(cmd))

    # 执行打包命令
    subprocess.run(cmd, cwd=ROOT_DIR)

    # 检查打包结果
    dist_dir = os.path.join(ROOT_DIR, 'dist')
    if os.path.exists(dist_dir):
        exe_file = os.path.join(dist_dir, 'CursorPro')
        if os.path.exists(exe_file):
            print(f"已成功创建可执行文件: {exe_file}")
            # 确保可执行权限
            os.chmod(exe_file, 0o755)
        else:
            print("警告: 可执行文件未创建成功")

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

    print("Linux应用程序构建完成!")

def main():
    """主函数"""
    # 清理旧的构建文件
    clean_build_dir()

    # 确保必要的目录存在
    ensure_dir(os.path.join(ROOT_DIR, 'resources'))
    ensure_dir(os.path.join(ROOT_DIR, 'resources', 'icons'))
    ensure_dir(os.path.join(ROOT_DIR, 'config'))

    # 检查必要文件是否存在
    if not os.path.exists(os.path.join(ROOT_DIR, 'launcher.py')):
        print("错误: launcher.py 不存在，无法构建应用程序")
        return 1

    if not os.path.exists(os.path.join(ROOT_DIR, 'main.py')):
        print("错误: main.py 不存在，无法构建应用程序")
        return 1

    # 检查是否安装了PyInstaller
    try:
        subprocess.run(['pyinstaller', '--version'], check=True, stdout=subprocess.PIPE)
    except (subprocess.SubprocessError, FileNotFoundError):
        print("错误: PyInstaller 未安装或不可用")
        print("请使用命令安装: pip install pyinstaller")
        return 1

    # 根据当前操作系统选择打包方式
    system = platform.system()
    if system == 'Darwin':
        build_mac()
    elif system == 'Windows':
        build_windows()
    elif system == 'Linux':
        build_linux()
    else:
        print(f"不支持的操作系统: {system}")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())