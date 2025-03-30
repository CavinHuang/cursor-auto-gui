import os
import sys
import shutil
import subprocess
import tempfile
import winreg
import ctypes
from pathlib import Path
import urllib.request

def build_windows():
    # 确保在项目根目录
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)

    # 清理之前的构建
    if os.path.exists('build'):
        shutil.rmtree('build')
    if os.path.exists('dist'):
        shutil.rmtree('dist')

    # 设置版本信息
    version = "3.0.0"

    # 安装依赖
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pywin32'])  # 用于创建安装程序
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])

    # 检查并下载必要的资源
    ensure_resources_exist()

    # 检查NSIS是否已安装
    nsis_path = detect_nsis_path()
    if not nsis_path:
        print("NSIS未安装，请安装NSIS以创建安装程序: https://nsis.sourceforge.io/Download")
        print("或者从这里下载: https://nsis.sourceforge.io/Download")
        sys.exit(1)
    else:
        print(f"已检测到NSIS安装路径: {nsis_path}")

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
            '--add-data=resources;resources',  # Windows使用分号作为分隔符
            '--add-binary=install.py;.',  # 添加安装脚本
            '--add-binary=launcher.py;.',  # 添加启动器脚本
            '--icon=resources/icon.ico',  # 添加图标
            '--version-file=version_info.txt',  # 添加版本信息
            'main.py'
        ])

    # 创建Windows版本信息文件
    create_version_info_file(version)

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
            '--add-data=resources;resources',  # Windows使用分号作为分隔符
            '--add-binary=install.py;.',  # 添加安装脚本
            '--add-binary=launcher.py;.',  # 添加启动器脚本
            '--icon=resources/icon.ico',  # 添加图标
            '--version-file=version_info.txt',  # 添加版本信息
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

    # 创建安装程序
    create_windows_installer(nsis_path, version)

    # 创建便携版ZIP
    create_portable_version(version)

    print('Windows build completed successfully!')
    print('安装包已创建:')
    print(f'1. 安装程序: dist/CursorPro_Setup_{version}.exe')
    print(f'2. 便携版: dist/CursorPro_Portable_{version}.zip')

def detect_nsis_path():
    """检测NSIS的安装路径"""
    try:
        # 尝试从注册表读取NSIS安装路径
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\NSIS") as key:
            nsis_path = winreg.QueryValueEx(key, "")[0]
            makensis_path = os.path.join(nsis_path, "makensis.exe")
            if os.path.exists(makensis_path):
                return makensis_path
    except:
        pass

    # 尝试常见的安装路径
    common_paths = [
        r"C:\Program Files\NSIS\makensis.exe",
        r"C:\Program Files (x86)\NSIS\makensis.exe",
    ]

    for path in common_paths:
        if os.path.exists(path):
            return path

    # 检查PATH环境变量
    for path in os.environ["PATH"].split(os.pathsep):
        potential_path = os.path.join(path, "makensis.exe")
        if os.path.exists(potential_path):
            return potential_path

    return None

def ensure_resources_exist():
    """确保资源文件存在"""
    # 创建资源目录
    resources_dir = os.path.join(os.getcwd(), "resources")
    os.makedirs(resources_dir, exist_ok=True)

    # 确保图标文件存在
    icon_file = os.path.join(resources_dir, "icon.ico")
    if not os.path.exists(icon_file):
        print("未找到图标文件，创建默认图标...")
        # 尝试从网络下载一个默认图标
        try:
            icon_url = "https://raw.githubusercontent.com/cavinHuang/cursor-auto-gui/main/resources/icon.ico"
            urllib.request.urlretrieve(icon_url, icon_file)
            print("成功下载默认图标")
        except Exception as e:
            print(f"下载图标失败: {e}，将创建空图标文件")
            # 如果下载失败，创建一个空文件
            with open(icon_file, 'wb') as f:
                f.write(b'')

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

def create_version_info_file(version):
    """创建Windows版本信息文件"""
    version_info_path = os.path.join(os.getcwd(), "version_info.txt")
    with open(version_info_path, 'w') as f:
        f.write(f"""# UTF-8
#
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms646997.aspx
VSVersionInfo(
  ffi=FixedFileInfo(
    # filevers and prodvers should be always a tuple with four items: (1, 2, 3, 4)
    # Set not needed items to zero 0.
    filevers=({version.replace('.', ', ')}, 0),
    prodvers=({version.replace('.', ', ')}, 0),
    # Contains a bitmask that specifies the valid bits 'flags'r
    mask=0x3f,
    # Contains a bitmask that specifies the Boolean attributes of the file.
    flags=0x0,
    # The operating system for which this file was designed.
    # 0x4 - NT and there is no need to change it.
    OS=0x40004,
    # The general type of file.
    # 0x1 - the file is an application.
    fileType=0x1,
    # The function of the file.
    # 0x0 - the function is not defined for this fileType
    subtype=0x0,
    # Creation date and time stamp.
    date=(0, 0)
    ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'080404b0',
        [StringStruct(u'CompanyName', u'Cursor Pro Team'),
        StringStruct(u'FileDescription', u'Cursor Pro工具'),
        StringStruct(u'FileVersion', u'{version}'),
        StringStruct(u'InternalName', u'CursorPro'),
        StringStruct(u'LegalCopyright', u'© 2023-2024 Cursor Pro Team. 保留所有权利。'),
        StringStruct(u'OriginalFilename', u'CursorPro.exe'),
        StringStruct(u'ProductName', u'Cursor Pro'),
        StringStruct(u'ProductVersion', u'{version}')])
      ]),
    VarFileInfo([VarStruct(u'Translation', [2052, 1200])])
  ]
)""")

    print(f"已创建版本信息文件: {version_info_path}")
    return version_info_path

def create_portable_version(version):
    """创建便携版ZIP包"""
    try:
        import zipfile

        # 创建ZIP文件
        zip_path = f'dist/CursorPro_Portable_{version}.zip'
        print(f"正在创建便携版ZIP包: {zip_path}")

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # 添加所有文件
            for root, dirs, files in os.walk('dist/CursorPro'):
                for file in files:
                    file_path = os.path.join(root, file)
                    # 计算相对路径
                    arcname = os.path.join('CursorPro', os.path.relpath(file_path, 'dist/CursorPro'))
                    zipf.write(file_path, arcname)

            # 添加便携版启动器脚本
            portable_launcher = 'portable_launcher.bat'
            with open(portable_launcher, 'w') as f:
                f.write('@echo off\necho 正在启动Cursor Pro...\n.\\CursorPro\\CursorPro.exe\n')
            zipf.write(portable_launcher, 'CursorPro启动器.bat')
            os.remove(portable_launcher)

        print(f"便携版ZIP包创建成功: {zip_path}")
    except Exception as e:
        print(f"创建便携版失败: {e}")

def create_windows_installer(nsis_path, version):
    """创建Windows安装程序"""
    print("正在创建Windows安装程序...")

    # 创建NSIS脚本
    nsis_script = os.path.join(tempfile.gettempdir(), 'cursor_installer.nsi')

    with open(nsis_script, 'w', encoding='utf-8') as f:
        f.write(f"""
; Cursor Pro安装脚本
Unicode true
SetCompressor /SOLID lzma

!define APPNAME "Cursor Pro"
!define COMPANYNAME "Cursor Pro Team"
!define DESCRIPTION "Cursor Pro工具"
!define VERSIONMAJOR {version.split('.')[0]}
!define VERSIONMINOR {version.split('.')[1]}
!define VERSIONBUILD {version.split('.')[2]}
!define VERSION "{version}"

!define HELPURL "https://github.com/cavinHuang/cursor-auto-gui"
!define UPDATEURL "https://github.com/cavinHuang/cursor-auto-gui"
!define ABOUTURL "https://github.com/cavinHuang/cursor-auto-gui"

; 包含必要的库
!include LogicLib.nsh
!include MUI2.nsh
!include FileFunc.nsh
!include UAC.nsh

; Modern UI定义
!define MUI_ABORTWARNING
!define MUI_ICON "resources\\icon.ico"
!define MUI_UNICON "resources\\icon.ico"

; MUI界面定制
!define MUI_WELCOMEFINISHPAGE_BITMAP "resources\\installer-side.bmp"
!define MUI_UNWELCOMEFINISHPAGE_BITMAP "resources\\installer-side.bmp"
!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_BITMAP "resources\\installer-header.bmp"
!define MUI_HEADERIMAGE_RIGHT

; 安装程序属性设置
Name "${{APPNAME}} v${{VERSION}}"
OutFile "dist\\CursorPro_Setup_${{VERSION}}.exe"
InstallDir "$PROGRAMFILES\\${{APPNAME}}"
InstallDirRegKey HKLM "Software\\${{APPNAME}}" "Install_Dir"

; 请求管理员权限
RequestExecutionLevel admin

; 安装界面设置
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!define MUI_FINISHPAGE_RUN "$INSTDIR\\CursorPro.exe"
!define MUI_FINISHPAGE_RUN_TEXT "启动 Cursor Pro"
!insertmacro MUI_PAGE_FINISH

; 卸载界面设置
!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; 语言设置
!insertmacro MUI_LANGUAGE "SimpChinese"

; 安装部分
Section "安装"
    SetOutPath $INSTDIR
    SetOverwrite on

    ; 显示安装进度
    DetailPrint "正在复制程序文件..."

    ; 复制主程序文件
    File /r "dist\\CursorPro\\*.*"

    ; 创建启动器脚本
    FileOpen $0 "$INSTDIR\\启动Cursor Pro.bat" w
    FileWrite $0 "@echo off$\\r$\\n"
    FileWrite $0 "echo 正在启动Cursor Pro...$\\r$\\n"
    FileWrite $0 "start \"\" \"$INSTDIR\\CursorPro.exe\"$\\r$\\n"
    FileClose $0

    DetailPrint "创建快捷方式..."

    ; 创建快捷方式
    CreateDirectory "$SMPROGRAMS\\${{APPNAME}}"
    CreateShortcut "$SMPROGRAMS\\${{APPNAME}}\\${{APPNAME}}.lnk" "$INSTDIR\\CursorPro.exe"
    CreateShortcut "$SMPROGRAMS\\${{APPNAME}}\\卸载 ${{APPNAME}}.lnk" "$INSTDIR\\uninstall.exe"
    CreateShortcut "$DESKTOP\\${{APPNAME}}.lnk" "$INSTDIR\\CursorPro.exe"

    DetailPrint "注册应用程序信息..."

    ; 写入卸载信息
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "DisplayName" "${{APPNAME}} ${{VERSION}}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "UninstallString" "$\\"$INSTDIR\\uninstall.exe$\\""
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "DisplayIcon" "$INSTDIR\\CursorPro.exe"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "Publisher" "${{COMPANYNAME}}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "HelpLink" "${{HELPURL}}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "URLUpdateInfo" "${{UPDATEURL}}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "URLInfoAbout" "${{ABOUTURL}}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "DisplayVersion" "${{VERSION}}"
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "VersionMajor" ${{VERSIONMAJOR}}
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "VersionMinor" ${{VERSIONMINOR}}
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "NoModify" 1
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "NoRepair" 1

    ; 获取安装大小
    ${{GetSize}} "$INSTDIR" "/S=0K" $0 $1 $2
    IntFmt $0 "0x%08X" $0
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "EstimatedSize" "$0"

    DetailPrint "创建卸载程序..."

    ; 创建卸载程序
    WriteUninstaller "$INSTDIR\\uninstall.exe"

    DetailPrint "安装完成！"
SectionEnd

; 卸载部分
Section "Uninstall"
    ; 显示卸载进度
    DetailPrint "正在删除程序文件..."

    ; 删除程序文件和目录
    Delete "$INSTDIR\\启动Cursor Pro.bat"
    RMDir /r "$INSTDIR\\*.*"
    RMDir "$INSTDIR"

    DetailPrint "正在删除快捷方式..."

    ; 删除快捷方式
    Delete "$SMPROGRAMS\\${{APPNAME}}\\${{APPNAME}}.lnk"
    Delete "$SMPROGRAMS\\${{APPNAME}}\\卸载 ${{APPNAME}}.lnk"
    RMDir "$SMPROGRAMS\\${{APPNAME}}"
    Delete "$DESKTOP\\${{APPNAME}}.lnk"

    DetailPrint "正在清理注册表..."

    ; 删除注册表项
    DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}"
    DeleteRegKey HKLM "Software\\${{APPNAME}}"

    DetailPrint "卸载完成！"
SectionEnd

; 安装前检查函数
Function .onInit
    ; 设置安装程序详细信息
    BrandingText "${{APPNAME}} ${{VERSION}} 安装程序"

    ; 检查是否已经安装
    ReadRegStr $R0 HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "UninstallString"
    StrCmp $R0 "" done

    ; 程序已安装，询问是否卸载旧版本
    MessageBox MB_OKCANCEL|MB_ICONINFORMATION \
    "${{APPNAME}}已经安装在您的系统上。$\\n$\\n点击'确定'移除旧版本或者'取消'取消安装。" \
    IDOK uninst
    Abort

    ; 运行卸载程序
    uninst:
        ClearErrors
        ExecWait '$R0 _?=$INSTDIR'
    done:
FunctionEnd
        """)

    # 确保安装程序图像文件存在
    ensure_installer_images()

    # 运行NSIS创建安装程序
    try:
        subprocess.check_call([nsis_path, nsis_script])
        print(f"Windows安装程序创建成功！")
    except subprocess.SubprocessError as e:
        print(f"创建安装程序失败: {e}")
        sys.exit(1)

def ensure_installer_images():
    """确保安装程序所需的图像文件存在"""
    resources_dir = os.path.join(os.getcwd(), "resources")

    # 安装程序侧边栏图像
    sidebar_image = os.path.join(resources_dir, "installer-side.bmp")
    if not os.path.exists(sidebar_image):
        print("创建安装程序侧边栏图像...")
        create_dummy_bmp(sidebar_image, 164, 314)

    # 安装程序头部图像
    header_image = os.path.join(resources_dir, "installer-header.bmp")
    if not os.path.exists(header_image):
        print("创建安装程序头部图像...")
        create_dummy_bmp(header_image, 150, 57)

def create_dummy_bmp(filepath, width, height):
    """创建一个简单的BMP图像文件"""
    try:
        from PIL import Image, ImageDraw

        # 创建一个新图像
        img = Image.new('RGB', (width, height), color=(240, 240, 240))
        draw = ImageDraw.Draw(img)

        # 添加一些简单的图案
        draw.rectangle([(0, 0), (width-1, height-1)], outline=(200, 200, 200))
        draw.text((width//2-30, height//2-10), "Cursor Pro", fill=(100, 100, 100))

        # 保存为BMP
        img.save(filepath, 'BMP')
        print(f"创建图像文件成功: {filepath}")
    except Exception as e:
        print(f"创建图像文件失败: {e}")
        # 如果PIL不可用，创建一个最小的BMP文件
        with open(filepath, 'wb') as f:
            # BMP 文件头 (14字节)
            f.write(b'BM')  # 标识 (2字节)
            f.write((54 + width * height * 3).to_bytes(4, byteorder='little'))  # 文件大小 (4字节)
            f.write(b'\x00\x00\x00\x00')  # 保留 (4字节)
            f.write((54).to_bytes(4, byteorder='little'))  # 数据偏移 (4字节)

            # DIB 头 (40字节)
            f.write((40).to_bytes(4, byteorder='little'))  # DIB头大小 (4字节)
            f.write(width.to_bytes(4, byteorder='little'))  # 宽度 (4字节)
            f.write(height.to_bytes(4, byteorder='little'))  # 高度 (4字节)
            f.write((1).to_bytes(2, byteorder='little'))  # 色彩平面数 (2字节)
            f.write((24).to_bytes(2, byteorder='little'))  # 每像素位数 (2字节)
            f.write(b'\x00\x00\x00\x00')  # 压缩方式 (4字节)
            f.write((width * height * 3).to_bytes(4, byteorder='little'))  # 图像数据大小 (4字节)
            f.write(b'\x00\x00\x00\x00')  # 水平分辨率 (4字节)
            f.write(b'\x00\x00\x00\x00')  # 垂直分辨率 (4字节)
            f.write(b'\x00\x00\x00\x00')  # 调色板颜色数 (4字节)
            f.write(b'\x00\x00\x00\x00')  # 重要颜色数 (4字节)

            # 写入最简单的图像数据 (全白)
            for y in range(height):
                for x in range(width):
                    f.write(b'\xff\xff\xff')  # 白色像素 (BGR)

                # BMP行需要4字节对齐，添加必要的填充
                padding = (4 - ((width * 3) % 4)) % 4
                f.write(b'\x00' * padding)

if __name__ == '__main__':
    build_windows()