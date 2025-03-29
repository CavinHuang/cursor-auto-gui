import os
import sys
import shutil
import subprocess
import tempfile
import json
import datetime

def build_linux():
    # 确保在项目根目录
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)

    # 获取版本信息
    version = "3.0.0"

    # 清理之前的构建
    if os.path.exists('build'):
        shutil.rmtree('build')
    if os.path.exists('dist'):
        shutil.rmtree('dist')

    # 安装依赖
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])

    # 检查Linux平台特定的工具
    required_tools = check_required_tools()

    # 确保资源存在
    ensure_resources_exist()

    # 安装依赖项
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])

    # 检查spec文件是否存在，如果不存在则创建一个
    spec_file = os.path.join(project_root, 'CursorPro.spec')
    if not os.path.exists(spec_file):
        print("未找到spec文件，创建新的spec文件...")
        # 首先创建基本的spec文件
        subprocess.check_call([
            sys.executable, '-m', 'PyInstaller',
            '--name=CursorPro',
            '--windowed',
            '--noconfirm',
            '--clean',
            '--noupx',
            '--add-data=resources:resources',
            '--add-binary=install.py:.',  # 添加安装脚本
            '--add-binary=launcher.py:.',  # 添加启动器脚本
            '--icon=resources/icon.png',  # 添加图标
            'main.py'
        ])

    # 运行PyInstaller
    if os.path.exists('CursorPro.spec'):
        subprocess.check_call([sys.executable, '-m', 'PyInstaller', 'CursorPro.spec'])
    else:
        # 如果spec文件仍然不存在，直接使用main.py
        print("警告: 未找到spec文件，使用main.py直接进行打包")
        subprocess.check_call([
            sys.executable, '-m', 'PyInstaller',
            '--name=CursorPro',
            '--windowed',
            '--noconfirm',
            '--clean',
            '--noupx',
            '--add-data=resources:resources',
            '--add-binary=install.py:.',  # 添加安装脚本
            '--add-binary=launcher.py:.',  # 添加启动器脚本
            '--icon=resources/icon.png',  # 添加图标
            'main.py'
        ])

    # 确保输出目录存在
    if not os.path.exists('dist/CursorPro'):
        print("警告: 打包后未找到应用程序，检查output目录")
        # 列出dist目录内容
        if os.path.exists('dist'):
            print("dist目录内容:")
            for item in os.listdir('dist'):
                print(f"  - {item}")
        return

    # 创建安装包
    deb_path = create_deb_package(version) if 'dpkg-deb' in required_tools else None
    rpm_path = create_rpm_package(version) if 'rpmbuild' in required_tools else None
    appimage_path = create_appimage(version) if 'appimagetool' in required_tools else None

    # 创建便携版
    tarball_path = create_portable_tarball(version)

    # 创建自动更新metainfo
    create_update_info(version, deb_path, rpm_path, appimage_path, tarball_path)

    print('Linux build completed successfully!')
    print('安装包已创建：')
    if deb_path:
        print(f'1. DEB格式: {deb_path}')
    if rpm_path:
        print(f'2. RPM格式: {rpm_path}')
    if appimage_path:
        print(f'3. AppImage格式: {appimage_path}')
    print(f'4. 便携版: {tarball_path}')
    print('5. 更新元数据: dist/update_info.json')

def check_required_tools():
    """检查Linux环境中必要的工具"""
    required_tools = {}

    # 检查dpkg-deb (DEB打包)
    try:
        subprocess.check_call(['which', 'dpkg-deb'],
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)
        required_tools['dpkg-deb'] = True
        print("✓ 已检测到dpkg-deb，将创建DEB包")
    except (subprocess.SubprocessError, FileNotFoundError):
        required_tools['dpkg-deb'] = False
        print("✗ 未检测到dpkg-deb，跳过创建DEB包")

    # 检查rpmbuild (RPM打包)
    try:
        subprocess.check_call(['which', 'rpmbuild'],
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)
        required_tools['rpmbuild'] = True
        print("✓ 已检测到rpmbuild，将创建RPM包")
    except (subprocess.SubprocessError, FileNotFoundError):
        required_tools['rpmbuild'] = False
        print("✗ 未检测到rpmbuild，跳过创建RPM包")

    # 检查appimagetool (AppImage打包)
    try:
        subprocess.check_call(['which', 'appimagetool'],
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)
        required_tools['appimagetool'] = True
        print("✓ 已检测到appimagetool，将创建AppImage包")
    except (subprocess.SubprocessError, FileNotFoundError):
        # 尝试下载AppImageTool
        try:
            print("正在尝试下载AppImageTool...")
            appimage_tool_url = "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"
            appimage_tool_path = os.path.join(tempfile.gettempdir(), "appimagetool")

            # 下载AppImageTool
            subprocess.check_call(["wget", appimage_tool_url, "-O", appimage_tool_path])
            os.chmod(appimage_tool_path, 0o755)

            # 测试AppImageTool
            subprocess.check_call([appimage_tool_path, "--version"],
                                 stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL)

            # 设置环境变量
            os.environ['PATH'] = os.environ['PATH'] + os.pathsep + tempfile.gettempdir()

            required_tools['appimagetool'] = True
            print("✓ 已下载并配置appimagetool，将创建AppImage包")
        except:
            required_tools['appimagetool'] = False
            print("✗ 无法下载或使用appimagetool，跳过创建AppImage包")

    return required_tools

def ensure_resources_exist():
    """确保资源文件存在"""
    # 创建资源目录
    resources_dir = os.path.join(os.getcwd(), "resources")
    os.makedirs(resources_dir, exist_ok=True)

    # 确保图标文件存在
    icon_file = os.path.join(resources_dir, "icon.png")
    if not os.path.exists(icon_file):
        print("未找到图标文件，创建默认图标...")
        # 尝试创建简单的PNG图标
        try:
            from PIL import Image, ImageDraw

            # 创建128x128的PNG图标
            img = Image.new('RGBA', (128, 128), color=(65, 205, 82, 255))
            draw = ImageDraw.Draw(img)

            # 添加一个简单的"C"字母
            draw.rectangle([(10, 10), (118, 118)], outline=(255, 255, 255, 255), width=3)
            draw.text((45, 45), "CP", fill=(255, 255, 255, 255))

            img.save(icon_file, 'PNG')
            print(f"创建PNG图标成功: {icon_file}")
        except:
            # 如果PIL不可用，创建一个空文件
            with open(icon_file, 'wb') as f:
                f.write(b'')
            print(f"创建空图标文件: {icon_file}")

    # 确保许可证文件存在
    license_path = os.path.join(os.getcwd(), "LICENSE")
    if not os.path.exists(license_path):
        print("未找到许可证文件，创建默认许可证...")
        with open(license_path, 'w') as f:
            f.write("""MIT License

Copyright (c) 2023-2024 Cursor Pro Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
""")

def create_portable_tarball(version):
    """创建便携版的tar.gz压缩包"""
    print("创建便携版tar.gz压缩包...")

    tarball_path = f'dist/CursorPro_Linux_Portable_{version}.tar.gz'

    # 创建启动脚本
    os.makedirs('dist/portable/CursorPro', exist_ok=True)
    with open('dist/portable/start_cursorpro.sh', 'w') as f:
        f.write("""#!/bin/bash
# Cursor Pro 启动脚本
echo "正在启动 Cursor Pro..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/CursorPro"
./CursorPro "$@"
""")

    # 设置脚本可执行权限
    os.chmod('dist/portable/start_cursorpro.sh', 0o755)

    # 复制程序目录
    for item in os.listdir('dist/CursorPro'):
        src = os.path.join('dist/CursorPro', item)
        dst = os.path.join('dist/portable/CursorPro', item)
        if os.path.isdir(src):
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)

    # 创建压缩包
    subprocess.check_call(['tar', 'czf', tarball_path, '-C', 'dist/portable', '.'])

    # 清理临时目录
    shutil.rmtree('dist/portable')

    print(f"便携版压缩包创建成功: {tarball_path}")
    return tarball_path

def create_deb_package(version):
    """创建DEB安装包"""
    print("创建DEB安装包...")

    # 创建临时目录结构
    temp_dir = tempfile.mkdtemp()

    # 1. 创建DEB包
    deb_dir = os.path.join(temp_dir, 'deb')
    deb_content_dir = os.path.join(deb_dir, 'DEBIAN')
    os.makedirs(deb_content_dir, exist_ok=True)

    # 创建应用程序目录
    app_dir = os.path.join(deb_dir, 'opt', 'cursorpro')
    os.makedirs(app_dir, exist_ok=True)

    # 复制应用程序文件
    dist_dir = os.path.join('dist', 'CursorPro')
    if os.path.exists(dist_dir):
        for item in os.listdir(dist_dir):
            s = os.path.join(dist_dir, item)
            d = os.path.join(app_dir, item)
            if os.path.isdir(s):
                shutil.copytree(s, d)
            else:
                shutil.copy2(s, d)

    # 为主程序设置可执行权限
    main_program = os.path.join(app_dir, 'CursorPro')
    if os.path.exists(main_program):
        os.chmod(main_program, 0o755)

    # 创建桌面菜单项
    desktop_dir = os.path.join(deb_dir, 'usr', 'share', 'applications')
    os.makedirs(desktop_dir, exist_ok=True)

    with open(os.path.join(desktop_dir, 'cursorpro.desktop'), 'w') as f:
        f.write(f"""[Desktop Entry]
Version={version}
Type=Application
Name=Cursor Pro
Comment=Cursor Pro工具
Exec=/opt/cursorpro/CursorPro
Icon=/opt/cursorpro/resources/icon.png
Terminal=false
Categories=Utility;Development;
Keywords=cursor;development;utility;
StartupNotify=true
StartupWMClass=CursorPro
""")

    # 创建图标目录
    icon_dir = os.path.join(deb_dir, 'usr', 'share', 'icons', 'hicolor', '128x128', 'apps')
    os.makedirs(icon_dir, exist_ok=True)

    # 复制图标
    icon_src = os.path.join('resources', 'icon.png')
    shutil.copy2(icon_src, os.path.join(icon_dir, 'cursorpro.png'))

    # 确保resources目录存在于app目录中
    app_resources_dir = os.path.join(app_dir, 'resources')
    os.makedirs(app_resources_dir, exist_ok=True)
    shutil.copy2(icon_src, os.path.join(app_resources_dir, 'icon.png'))

    # 创建二进制链接目录
    bin_dir = os.path.join(deb_dir, 'usr', 'bin')
    os.makedirs(bin_dir, exist_ok=True)

    # 创建启动器脚本
    with open(os.path.join(bin_dir, 'cursorpro'), 'w') as f:
        f.write("""#!/bin/sh
/opt/cursorpro/CursorPro "$@"
""")

    os.chmod(os.path.join(bin_dir, 'cursorpro'), 0o755)

    # 创建control文件
    with open(os.path.join(deb_content_dir, 'control'), 'w') as f:
        f.write(f"""Package: cursor-pro
Version: {version}
Section: utils
Priority: optional
Architecture: amd64
Depends: python3 (>= 3.6), libgtk-3-0, libnotify4
Maintainer: Cursor Pro Team <support@cursorpro.com>
Homepage: https://github.com/cavinHuang/cursor-auto-gui
Description: Cursor Pro工具
 一个用于Cursor的辅助工具，自动化各种任务。
 .
 Cursor Pro提供了一套丰富的功能，帮助用户更高效地使用Cursor。
""")

    # 创建postinst脚本
    with open(os.path.join(deb_content_dir, 'postinst'), 'w') as f:
        f.write("""#!/bin/sh
# 设置权限
chmod -R 755 /opt/cursorpro
chmod 755 /usr/bin/cursorpro
chmod 644 /usr/share/applications/cursorpro.desktop
chmod 644 /usr/share/icons/hicolor/128x128/apps/cursorpro.png

# 更新图标缓存
if [ -x "$(command -v gtk-update-icon-cache)" ]; then
    gtk-update-icon-cache --force --quiet /usr/share/icons/hicolor
fi

# 更新桌面数据库
if [ -x "$(command -v update-desktop-database)" ]; then
    update-desktop-database -q /usr/share/applications
fi

# 注册MIME类型
if [ -x "$(command -v xdg-mime)" ]; then
    xdg-mime default cursorpro.desktop x-scheme-handler/cursorpro
fi

exit 0
""")

    # 创建prerm脚本 (卸载前执行)
    with open(os.path.join(deb_content_dir, 'prerm'), 'w') as f:
        f.write("""#!/bin/sh
# 停止可能正在运行的应用
if [ -x "$(command -v pkill)" ]; then
    pkill -f "CursorPro" || true
fi
exit 0
""")

    # 设置脚本可执行权限
    os.chmod(os.path.join(deb_content_dir, 'postinst'), 0o755)
    os.chmod(os.path.join(deb_content_dir, 'prerm'), 0o755)

    # 创建DEB包
    deb_output = f'dist/cursor-pro_{version}_amd64.deb'
    subprocess.check_call(['dpkg-deb', '--build', deb_dir, deb_output])

    # 清理临时目录
    shutil.rmtree(temp_dir)

    print(f"DEB包已创建: {deb_output}")
    return deb_output

def create_rpm_package(version):
    """创建RPM安装包"""
    print("创建RPM安装包...")

    # 创建临时目录结构
    temp_dir = tempfile.mkdtemp()

    try:
        # 创建RPM构建目录结构
        rpm_build_dir = os.path.join(temp_dir, 'rpm_build')
        os.makedirs(rpm_build_dir, exist_ok=True)

        for subdir in ['BUILD', 'RPMS', 'SOURCES', 'SPECS', 'SRPMS']:
            os.makedirs(os.path.join(rpm_build_dir, subdir), exist_ok=True)

        # 创建压缩源代码
        source_dir = os.path.join(rpm_build_dir, 'SOURCES')
        app_tarball = os.path.join(source_dir, f'cursorpro-{version}.tar.gz')

        # 创建临时目录用于打包
        tar_temp_dir = os.path.join(temp_dir, f'cursorpro-{version}')
        os.makedirs(tar_temp_dir, exist_ok=True)

        # 复制应用程序文件到临时目录
        dist_dir = os.path.join('dist', 'CursorPro')
        if os.path.exists(dist_dir):
            for item in os.listdir(dist_dir):
                s = os.path.join(dist_dir, item)
                d = os.path.join(tar_temp_dir, item)
                if os.path.isdir(s):
                    shutil.copytree(s, d)
                else:
                    shutil.copy2(s, d)

        # 创建desktop文件
        with open(os.path.join(tar_temp_dir, 'cursorpro.desktop'), 'w') as f:
            f.write(f"""[Desktop Entry]
Version={version}
Type=Application
Name=Cursor Pro
Comment=Cursor Pro工具
Exec=/opt/cursorpro/CursorPro
Icon=/opt/cursorpro/resources/icon.png
Terminal=false
Categories=Utility;Development;
Keywords=cursor;development;utility;
StartupNotify=true
StartupWMClass=CursorPro
""")

        # 确保resources目录存在
        resources_dir = os.path.join(tar_temp_dir, 'resources')
        os.makedirs(resources_dir, exist_ok=True)

        # 复制图标
        icon_src = os.path.join('resources', 'icon.png')
        shutil.copy2(icon_src, os.path.join(resources_dir, 'icon.png'))

        # 创建tar.gz包
        subprocess.check_call(['tar', 'czf', app_tarball, '-C', os.path.dirname(tar_temp_dir), f'cursorpro-{version}'])

        # 创建spec文件
        spec_file = os.path.join(rpm_build_dir, 'SPECS', 'cursorpro.spec')
        with open(spec_file, 'w') as f:
            f.write(f"""Name:           cursor-pro
Version:        {version}
Release:        1%{{?dist}}
Summary:        Cursor Pro工具

License:        MIT
URL:            https://github.com/cavinHuang/cursor-auto-gui
Source0:        cursorpro-{version}.tar.gz

BuildArch:      x86_64
Requires:       python3 >= 3.6, gtk3, libnotify

%description
一个用于Cursor的辅助工具，自动化各种任务。
Cursor Pro提供了一套丰富的功能，帮助用户更高效地使用Cursor。

%prep
%setup -q -n cursorpro-{version}

%install
mkdir -p %{{buildroot}}/opt/cursorpro
mkdir -p %{{buildroot}}/usr/bin
mkdir -p %{{buildroot}}/usr/share/applications
mkdir -p %{{buildroot}}/usr/share/icons/hicolor/128x128/apps

cp -r * %{{buildroot}}/opt/cursorpro/
install -m 644 cursorpro.desktop %{{buildroot}}/usr/share/applications/
install -m 644 resources/icon.png %{{buildroot}}/usr/share/icons/hicolor/128x128/apps/cursorpro.png

# 创建启动脚本
cat > %{{buildroot}}/usr/bin/cursorpro << EOF
#!/bin/sh
/opt/cursorpro/CursorPro "\\$@"
EOF
chmod 755 %{{buildroot}}/usr/bin/cursorpro

%files
%license LICENSE
%{{_bindir}}/cursorpro
%{{_datadir}}/applications/cursorpro.desktop
%{{_datadir}}/icons/hicolor/128x128/apps/cursorpro.png
/opt/cursorpro

%post
# 更新图标缓存
if [ -x "$(command -v gtk-update-icon-cache)" ]; then
    gtk-update-icon-cache --force --quiet %{{_datadir}}/icons/hicolor
fi
# 更新桌面数据库
if [ -x "$(command -v update-desktop-database)" ]; then
    update-desktop-database -q %{{_datadir}}/applications
fi
# 注册MIME类型
if [ -x "$(command -v xdg-mime)" ]; then
    xdg-mime default cursorpro.desktop x-scheme-handler/cursorpro
fi

%preun
# 停止可能正在运行的应用
if [ "$1" = 0 ] && [ -x "$(command -v pkill)" ]; then
    pkill -f "CursorPro" || :
fi

%changelog
* {datetime.datetime.now().strftime('%a %b %d %Y')} Cursor Pro Team <support@cursorpro.com> - {version}-1
- 初始版本
""")

        # 构建RPM包
        subprocess.check_call(['rpmbuild', '--define', f"_topdir {rpm_build_dir}", '-ba', spec_file])

        # 复制RPM包到dist目录
        rpm_output = os.path.join(rpm_build_dir, 'RPMS', 'x86_64', f'cursor-pro-{version}-1.x86_64.rpm')
        rpm_dest = os.path.join('dist', f'cursor-pro-{version}-1.x86_64.rpm')
        shutil.copy2(rpm_output, rpm_dest)

        print(f"RPM包已创建: {rpm_dest}")
        return rpm_dest

    except Exception as e:
        print(f"创建RPM包时出错: {e}")
        return None

    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir)

def create_appimage(version):
    """创建AppImage包"""
    print("创建AppImage包...")

    try:
        # 创建AppDir
        appdir = os.path.join('dist', 'AppDir')
        if os.path.exists(appdir):
            shutil.rmtree(appdir)
        os.makedirs(appdir, exist_ok=True)

        # 复制应用程序文件
        dist_dir = os.path.join('dist', 'CursorPro')
        if os.path.exists(dist_dir):
            for item in os.listdir(dist_dir):
                s = os.path.join(dist_dir, item)
                d = os.path.join(appdir, 'usr', 'bin', item)
                os.makedirs(os.path.dirname(d), exist_ok=True)
                if os.path.isdir(s):
                    shutil.copytree(s, d)
                else:
                    shutil.copy2(s, d)

        # 创建.desktop文件
        os.makedirs(os.path.join(appdir, 'usr', 'share', 'applications'), exist_ok=True)
        with open(os.path.join(appdir, 'usr', 'share', 'applications', 'cursorpro.desktop'), 'w') as f:
            f.write(f"""[Desktop Entry]
Version={version}
Type=Application
Name=Cursor Pro
Comment=Cursor Pro工具
Exec=CursorPro
Icon=cursorpro
Terminal=false
Categories=Utility;Development;
Keywords=cursor;development;utility;
StartupNotify=true
StartupWMClass=CursorPro
X-AppImage-Name=Cursor Pro
X-AppImage-Version={version}
X-AppImage-Arch=x86_64
""")

        # 创建AppRun脚本
        with open(os.path.join(appdir, 'AppRun'), 'w') as f:
            f.write("""#!/bin/sh
# AppRun脚本 - 为AppImage设置环境并启动应用程序
HERE="$(dirname "$(readlink -f "${0}")")"
export PATH="${HERE}/usr/bin:${PATH}"
export LD_LIBRARY_PATH="${HERE}/usr/lib:${LD_LIBRARY_PATH}"
export XDG_DATA_DIRS="${HERE}/usr/share:${XDG_DATA_DIRS}"
export PYTHONPATH="${HERE}/usr/bin:${PYTHONPATH}"
export PYTHONHOME="${HERE}/usr"

# 启动程序
"${HERE}/usr/bin/CursorPro" "$@"
""")

        # 设置AppRun可执行权限
        os.chmod(os.path.join(appdir, 'AppRun'), 0o755)

        # 复制图标
        os.makedirs(os.path.join(appdir, 'usr', 'share', 'icons', 'hicolor', '128x128', 'apps'), exist_ok=True)
        icon_src = os.path.join('resources', 'icon.png')
        shutil.copy2(icon_src, os.path.join(appdir, 'usr', 'share', 'icons', 'hicolor', '128x128', 'apps', 'cursorpro.png'))

        # 复制到应用根目录作为AppImage图标
        shutil.copy2(icon_src, os.path.join(appdir, 'cursorpro.png'))

        # 创建update.zsync文件 (用于AppImage自动更新)
        with open(os.path.join(appdir, 'usr', 'bin', '.update-info'), 'w') as f:
            f.write(f"""[AppImageUpdate]
update_information=gh-releases-zsync|cavinHuang|cursor-auto-gui|latest|CursorPro-*-x86_64.AppImage.zsync
""")

        # 创建AppImage
        appimage_output = f'dist/CursorPro-{version}-x86_64.AppImage'

        # 检查appimagetool路径
        if os.path.exists('/usr/local/bin/appimagetool'):
            appimagetool_path = '/usr/local/bin/appimagetool'
        elif os.path.exists('/usr/bin/appimagetool'):
            appimagetool_path = '/usr/bin/appimagetool'
        else:
            appimagetool_path = 'appimagetool'

        # 运行appimagetool
        subprocess.check_call([
            appimagetool_path,
            '-n',  # 不更新AppImage
            '--comp=xz',  # 使用xz压缩
            appdir,
            appimage_output
        ])

        print(f"AppImage已创建: {appimage_output}")
        return appimage_output

    except Exception as e:
        print(f"创建AppImage失败: {e}")
        return None

def create_update_info(version, deb_path, rpm_path, appimage_path, tarball_path):
    """创建更新元数据"""
    print("创建更新元数据...")

    update_info = {
        "version": version,
        "release_date": datetime.datetime.now().isoformat(),
        "changelog": [
            "初始版本发布"
        ],
        "downloads": {
            "linux": {
                "portable": {
                    "url": f"https://github.com/cavinHuang/cursor-auto-gui/releases/download/v{version}/CursorPro_Linux_Portable_{version}.tar.gz",
                    "size": os.path.getsize(tarball_path) if tarball_path and os.path.exists(tarball_path) else 0
                }
            }
        }
    }

    # 添加DEB包信息（如果存在）
    if deb_path and os.path.exists(deb_path):
        update_info["downloads"]["linux"]["deb"] = {
            "url": f"https://github.com/cavinHuang/cursor-auto-gui/releases/download/v{version}/cursor-pro_{version}_amd64.deb",
            "size": os.path.getsize(deb_path)
        }

    # 添加RPM包信息（如果存在）
    if rpm_path and os.path.exists(rpm_path):
        update_info["downloads"]["linux"]["rpm"] = {
            "url": f"https://github.com/cavinHuang/cursor-auto-gui/releases/download/v{version}/cursor-pro-{version}-1.x86_64.rpm",
            "size": os.path.getsize(rpm_path)
        }

    # 添加AppImage包信息（如果存在）
    if appimage_path and os.path.exists(appimage_path):
        update_info["downloads"]["linux"]["appimage"] = {
            "url": f"https://github.com/cavinHuang/cursor-auto-gui/releases/download/v{version}/CursorPro-{version}-x86_64.AppImage",
            "size": os.path.getsize(appimage_path),
            "update_info": f"gh-releases-zsync|cavinHuang|cursor-auto-gui|latest|CursorPro-*-x86_64.AppImage.zsync"
        }

    # 写入更新信息文件
    update_info_path = 'dist/update_info.json'
    with open(update_info_path, 'w', encoding='utf-8') as f:
        json.dump(update_info, f, ensure_ascii=False, indent=2)

    print(f"更新元数据已创建: {update_info_path}")

if __name__ == '__main__':
    build_linux()