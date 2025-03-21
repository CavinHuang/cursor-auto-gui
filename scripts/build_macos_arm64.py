import os
import sys
import shutil
import subprocess

def build_macos_arm64():
    # 确保在项目根目录
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)

    # 清理之前的构建
    if os.path.exists('build'):
        shutil.rmtree('build')
    if os.path.exists('dist'):
        shutil.rmtree('dist')

    # 安装依赖
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller>=5.9.0'])  # 确保使用最新的 PyInstaller
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])

    # 设置环境变量以确保构建ARM64版本
    os.environ['ARCHFLAGS'] = '-arch arm64'

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

    # 运行PyInstaller
    subprocess.check_call([sys.executable, '-m', 'PyInstaller', 'CursorKeepAlive.spec'])

    # 确保包含设置权限的步骤
    os.chmod('dist/CursorPro.app/Contents/MacOS/CursorPro', 0o755)

    # 为所有脚本和二进制文件设置可执行权限
    for root, dirs, files in os.walk('dist/CursorPro.app'):
        for file in files:
            file_path = os.path.join(root, file)
            # 只对可能需要执行权限的文件设置
            if file.endswith(('.sh', '.py', '.so', '.dylib')) or '.' not in file:
                os.chmod(file_path, 0o755)

    # 添加 Info.plist 设置以避免隔离
    info_plist_path = 'dist/CursorPro.app/Contents/Info.plist'
    if os.path.exists(info_plist_path):
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

    # 执行 ad-hoc 签名
    subprocess.check_call(['codesign', '--force', '--deep', '--sign', '-',
                          '--entitlements', entitlements_path,
                          '--options', 'runtime',
                          'dist/CursorPro.app'])

    print('MacOS ARM64 build completed successfully!')

if __name__ == '__main__':
    build_macos_arm64()