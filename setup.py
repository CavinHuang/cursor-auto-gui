from setuptools import setup, find_packages
import os

# 读取requirements.txt获取依赖列表
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name="cursor-auto-gui",
    version="0.1",
    packages=find_packages(),
    install_requires=requirements,
    python_requires=">=3.6",
    scripts=['launcher.py'],  # 添加launcher.py作为脚本
    # 包含其他文件
    data_files=[
        ('', ['launcher.py', 'main.py']),
        ('config', [os.path.join('config', f) for f in os.listdir('config') if os.path.isfile(os.path.join('config', f))]),
        ('resources', [os.path.join('resources', f) for f in os.listdir('resources') if os.path.isfile(os.path.join('resources', f))])
    ],
    # 配置PyInstaller打包信息
    options={
        'build_exe': {
            'includes': ['launcher'],
            'include_files': ['launcher.py'],
        },
        'bdist_mac': {
            'custom_info_plist': 'resources/Info.plist',
        },
        'bdist_dmg': {
            'applications_shortcut': True,
        },
    },
    entry_points={
        'console_scripts': [
            'cursorpro=launcher:main',
        ],
    },
)