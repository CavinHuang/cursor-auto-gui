import os
import sys
import shutil
import subprocess
import plistlib
import tempfile
import platform

def build_macos_intel():
    # 确保在项目根目录
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)

    # 安全清理之前的构建
    safe_clean_directories(['build', 'dist'])

    # 安装依赖
    subprocess.check_call(['arch', '-x86_64', sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])

    # 检查并移除可能与PyInstaller冲突的pathlib包
    try:
        # 先检查是否是anaconda环境
        is_conda = os.path.exists(os.path.join(os.path.dirname(sys.executable), 'conda'))
        if is_conda:
            print("检测到Anaconda环境，检查pathlib包...")
            # 检查是否安装了pathlib
            result = subprocess.run(['arch', '-x86_64', sys.executable, '-m', 'pip', 'list'], capture_output=True, text=True)
            if "pathlib " in result.stdout:  # 注意空格，避免匹配pathlib2等包
                print("发现过时的pathlib包，正在移除...")
                subprocess.check_call([os.path.join(os.path.dirname(sys.executable), 'conda'), 'remove', '--yes', 'pathlib'])
    except Exception as e:
        print(f"检查pathlib时出错: {e}")
        print("继续执行，但可能会遇到PyInstaller兼容性问题")

    # 安装PyInstaller和其他依赖
    subprocess.check_call(['arch', '-x86_64', sys.executable, '-m', 'pip', 'install', 'pyinstaller>=5.9.0'])
    subprocess.check_call(['arch', '-x86_64', sys.executable, '-m', 'pip', 'install', 'dmgbuild'])  # 用于创建DMG包
    subprocess.check_call(['arch', '-x86_64', sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])

    # 设置环境变量以确保构建Intel版本
    os.environ['ARCHFLAGS'] = '-arch x86_64'

    # 创建 entitlements 文件
    entitlements_path = os.path.join(project_root, 'entitlements.plist')
    with open(entitlements_path, 'w') as f:
        f.write('''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>com.apple.security.cs.allow-unsigned-executable-memory</key>
    <true/>
    <key>com.apple.security.cs.allow-jit</key>
    <true/>
    <key>com.apple.security.cs.disable-library-validation</key>
    <true/>
    <key>com.apple.security.automation.apple-events</key>
    <true/>
</dict>
</plist>''')

    # 检查spec文件是否存在，如果不存在则创建一个
    spec_file = os.path.join(project_root, 'CursorPro.spec')
    if not os.path.exists(spec_file):
        print("未找到spec文件，创建新的spec文件...")
        # 首先创建基本的spec文件
        subprocess.check_call([
            'arch', '-x86_64', sys.executable, '-m', 'PyInstaller',
            '--name=CursorPro',
            '--windowed',
            '--noconfirm',
            '--clean',
            '--noupx',
            '--add-data=resources:resources',
            '--add-binary=install.py:.',  # 添加安装脚本
            '--add-binary=launcher.py:.',  # 添加启动器脚本
            '--icon=resources/icon.icns',  # 添加图标
            'main.py'
        ])

    # 确保图标文件存在
    icon_file = os.path.join('resources', 'icon.icns')
    if not os.path.exists(icon_file):
        create_default_icon(icon_file)

    # 运行PyInstaller
    if os.path.exists('CursorPro.spec'):
        subprocess.check_call(['arch', '-x86_64', sys.executable, '-m', 'PyInstaller', 'CursorPro.spec'])
    else:
        # 如果spec文件仍然不存在，直接使用main.py
        print("警告: 未找到spec文件，使用main.py直接进行打包")
        subprocess.check_call([
            'arch', '-x86_64', sys.executable, '-m', 'PyInstaller',
            '--name=CursorPro',
            '--windowed',
            '--noconfirm',
            '--clean',
            '--noupx',
            '--add-data=resources:resources',
            '--add-binary=install.py:.',  # 添加安装脚本
            '--add-binary=launcher.py:.',  # 添加启动器脚本
            '--icon=resources/icon.icns',  # 添加图标
            'main.py'
        ])

    # 确保输出目录存在
    if not os.path.exists('dist/CursorPro.app'):
        print("警告: 打包后未找到应用程序，检查output目录")
        # 列出dist目录内容
        if os.path.exists('dist'):
            print("dist目录内容:")
            for item in os.listdir('dist'):
                print(f"  - {item}")
        return

    # 设置权限
    os.chmod('dist/CursorPro.app/Contents/MacOS/CursorPro', 0o755)

    # 为所有脚本和二进制文件设置可执行权限
    for root, dirs, files in os.walk('dist/CursorPro.app'):
        for file in files:
            file_path = os.path.join(root, file)
            # 只对可能需要执行权限的文件设置
            if file.endswith(('.sh', '.py', '.so', '.dylib')) or '.' not in file:
                os.chmod(file_path, 0o755)

    # 添加 Info.plist 设置
    info_plist_path = 'dist/CursorPro.app/Contents/Info.plist'
    if os.path.exists(info_plist_path):
        # 使用plistlib读取和修改plist文件，更加可靠
        try:
            with open(info_plist_path, 'rb') as fp:
                plist = plistlib.load(fp)

            # 添加或更新必要的键
            plist['LSUIElement'] = True
            plist['CFBundleDisplayName'] = 'Cursor Pro'
            plist['CFBundleIdentifier'] = 'com.cursor.pro'
            plist['CFBundleShortVersionString'] = '3.0.0'
            plist['CFBundleVersion'] = '3.0.0'
            plist['NSHighResolutionCapable'] = True
            plist['LSApplicationCategoryType'] = 'public.app-category.utilities'

            # 写回修改后的plist
            with open(info_plist_path, 'wb') as fp:
                plistlib.dump(plist, fp)

            print("成功更新Info.plist文件")
        except Exception as e:
            print(f"更新Info.plist时出错: {e}")
            # 回退到旧方法
            with open(info_plist_path, 'r+') as f:
                content = f.read()
                if '<key>LSUIElement</key>' not in content:
                    insert_pos = content.rfind('</dict>')
                    if insert_pos > 0:
                        new_content = content[:insert_pos]
                        new_content += '  <key>LSUIElement</key>\n  <true/>\n'
                        new_content += content[insert_pos:]
                        f.seek(0)
                        f.write(new_content)
                        f.truncate()

    # 创建安装脚本
    create_macos_installer()

    # 创建DMG文件
    create_macos_dmg()

    # 执行 ad-hoc 签名
    subprocess.check_call(['codesign', '--force', '--deep', '--sign', '-',
                         '--entitlements', entitlements_path,
                         '--options', 'runtime',
                         'dist/CursorPro.app'])

    print('MacOS Intel build completed successfully!')
    print('安装包已准备就绪:')
    print('1. PKG格式: dist/CursorPro_Installer_Intel.pkg')
    print('2. DMG格式: dist/CursorPro_Intel.dmg')

def safe_clean_directories(directories):
    """安全清理目录，处理macOS上的权限问题"""
    for directory in directories:
        if os.path.exists(directory):
            print(f"清理 {directory} 目录...")
            try:
                # 先尝试修复权限
                if platform.system() == 'Darwin':  # macOS
                    try:
                        # 使用sudo尝试修改权限（如果有管理员权限）
                        subprocess.run(['sudo', 'chmod', '-R', '777', directory],
                                    check=False,
                                    stderr=subprocess.DEVNULL,
                                    stdout=subprocess.DEVNULL)
                    except:
                        pass

                    # 使用普通权限修改
                    subprocess.run(['chmod', '-R', '777', directory],
                                 check=False,
                                 stderr=subprocess.DEVNULL,
                                 stdout=subprocess.DEVNULL)

                    # 特别处理CodeResources文件
                    code_resources = os.path.join(directory, 'CursorPro.app/Contents/_CodeSignature/CodeResources')
                    if os.path.exists(code_resources):
                        os.chmod(code_resources, 0o777)

                # 尝试直接删除
                shutil.rmtree(directory)
                print(f"已删除 {directory} 目录")
            except PermissionError as e:
                print(f"无法删除 {directory} 目录，尝试强制删除: {e}")
                try:
                    # 如果是macOS，尝试使用rm -rf命令
                    if platform.system() == 'Darwin':
                        result = subprocess.run(['rm', '-rf', directory], check=False)
                        if result.returncode == 0:
                            print(f"使用命令行强制删除 {directory} 成功")
                        else:
                            print(f"警告: 无法删除 {directory} 目录，可能需要手动删除")
                    else:
                        # 在其他系统上，再次尝试用Python删除
                        # 遍历目录并逐个改变文件权限
                        for root, dirs, files in os.walk(directory, topdown=False):
                            for name in files:
                                try:
                                    os.chmod(os.path.join(root, name), 0o777)
                                except:
                                    pass
                            for name in dirs:
                                try:
                                    os.chmod(os.path.join(root, name), 0o777)
                                except:
                                    pass

                        # 再次尝试删除
                        shutil.rmtree(directory, ignore_errors=True)
                        print(f"已尝试强制删除 {directory} 目录")
                except Exception as e2:
                    print(f"警告: 即使强制删除也无法移除 {directory} 目录: {e2}")
                    print(f"可能需要手动删除 {directory} 目录后再运行此脚本")
            except Exception as e:
                print(f"清理 {directory} 目录时出现未知错误: {e}")
                print(f"可能需要手动删除 {directory} 目录后再运行此脚本")

def create_default_icon(icon_path):
    """创建默认图标文件"""
    os.makedirs(os.path.dirname(icon_path), exist_ok=True)

    # 检查是否有png图标可以转换
    png_icon = os.path.join(os.path.dirname(icon_path), 'icon.png')
    if os.path.exists(png_icon):
        try:
            # 尝试使用sips转换
            subprocess.check_call(['sips', '-s', 'format', 'icns', png_icon, '--out', icon_path])
            print(f"已使用sips将PNG图标转换为ICNS格式: {icon_path}")
            return
        except Exception as e:
            print(f"无法使用sips转换图标: {e}")

    # 创建一个空文件作为占位符
    with open(icon_path, 'wb') as f:
        f.write(b'')
    print(f"创建了空图标文件: {icon_path}")

def create_macos_installer():
    """创建macOS PKG安装包"""
    print("创建macOS PKG安装包...")

    # 创建安装脚本目录
    installer_dir = 'dist/installer'
    if os.path.exists(installer_dir):
        shutil.rmtree(installer_dir)
    os.makedirs(installer_dir)

    # 创建postinstall脚本
    scripts_dir = os.path.join(installer_dir, 'scripts')
    os.makedirs(scripts_dir)

    postinstall_path = os.path.join(scripts_dir, 'postinstall')
    with open(postinstall_path, 'w') as f:
        f.write('''#!/bin/bash
# 设置应用程序权限
chmod -R 755 "/Applications/CursorPro.app"

# 创建快捷方式到应用程序目录
mkdir -p "/usr/local/bin"
ln -sf "/Applications/CursorPro.app/Contents/MacOS/CursorPro" "/usr/local/bin/cursorpro"

# 注册文件类型关联
/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister -f "/Applications/CursorPro.app"

# 刷新图标缓存
touch "/Applications/CursorPro.app"
touch "/Applications"

echo "CursorPro安装完成！"
exit 0
''')

    # 设置脚本可执行权限
    os.chmod(postinstall_path, 0o755)

    # 复制应用到临时目录
    app_temp_dir = os.path.join(installer_dir, 'app')
    os.makedirs(app_temp_dir)
    shutil.copytree('dist/CursorPro.app', os.path.join(app_temp_dir, 'CursorPro.app'))

    # 使用pkgbuild创建安装包
    subprocess.check_call([
        'pkgbuild',
        '--root', app_temp_dir,
        '--install-location', '/Applications',
        '--scripts', scripts_dir,
        '--identifier', 'com.cursor.pro',
        '--version', '3.0.0',
        'dist/CursorPro_Installer_Intel.pkg'
    ])

    print("macOS PKG安装包创建成功!")

def create_macos_dmg():
    """创建macOS DMG安装包"""
    print("创建macOS DMG安装包...")

    try:
        # 检查dmgbuild是否已安装
        subprocess.check_call(['arch', '-x86_64', sys.executable, '-m', 'dmgbuild', '--help'],
                              stdout=subprocess.DEVNULL,
                              stderr=subprocess.DEVNULL)

        # 创建DMG配置文件
        dmg_settings = os.path.join(tempfile.gettempdir(), 'dmg_settings.py')
        with open(dmg_settings, 'w') as f:
            f.write('''
# DMG配置文件

# 卷名将显示在左侧边栏
volume_name = 'Cursor Pro 3.0.0'

# 在DMG上显示的图标的大小
icon_size = 80

# 背景图片路径（如果存在）
# background = 'background.png'

# 图标在DMG中的位置
icon_locations = {
    'CursorPro.app': (120, 120),
    'Applications': (380, 120)
}

# 窗口大小和位置
window_rect = ((100, 100), (500, 300))

# 文件要包含在DMG中
files = [ 'dist/CursorPro.app' ]

# 符号链接到Applications文件夹
symlinks = { 'Applications': '/Applications' }

# 是否隐藏扩展名
hide_extension = { 'CursorPro.app': True }

# DMG格式
format = 'UDBZ'  # 压缩格式
''')

        # 使用dmgbuild创建DMG
        subprocess.check_call([
            'arch', '-x86_64', sys.executable, '-m', 'dmgbuild',
            '-s', dmg_settings,
            'Cursor Pro',
            'dist/CursorPro_Intel.dmg'
        ])

        print("macOS DMG安装包创建成功!")

    except Exception as e:
        print(f"创建DMG失败: {e}")
        print("请确保已安装dmgbuild库: pip install dmgbuild")

if __name__ == '__main__':
    build_macos_intel()