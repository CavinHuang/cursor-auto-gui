import os
import sys
import shutil
import subprocess

def build_macos_intel():
    # 确保在项目根目录
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)

    # 清理之前的构建
    if os.path.exists('build'):
        shutil.rmtree('build')
    if os.path.exists('dist'):
        shutil.rmtree('dist')

    # 安装依赖
    subprocess.check_call(['arch', '-x86_64', sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])
    subprocess.check_call(['arch', '-x86_64', sys.executable, '-m', 'pip', 'install', 'pyinstaller'])
    subprocess.check_call(['arch', '-x86_64', sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])

    # 设置环境变量以确保构建Intel版本
    os.environ['ARCHFLAGS'] = '-arch x86_64'

    # 运行PyInstaller
    subprocess.check_call(['arch', '-x86_64', sys.executable, '-m', 'PyInstaller', 'CursorKeepAlive.spec'])

    print('MacOS Intel build completed successfully!')

if __name__ == '__main__':
    build_macos_intel()