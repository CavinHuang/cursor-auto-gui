#!/usr/bin/env python
"""
Cursor Pro 安装脚本
设置正确的文件权限并安装依赖
"""

import os
import sys
import platform
import subprocess

def main():
    """主函数"""
    print("=== Cursor Pro 安装程序 ===")

    # 获取当前目录
    current_dir = os.getcwd()
    print(f"当前目录: {current_dir}")

    # 确保launcher.py和main.py有执行权限
    files_to_chmod = ["launcher.py", "main.py"]
    for file in files_to_chmod:
        file_path = os.path.join(current_dir, file)
        if os.path.exists(file_path):
            try:
                # 为文件添加执行权限
                os.chmod(file_path, 0o755)
                print(f"已为 {file} 添加执行权限")
            except Exception as e:
                print(f"为 {file} 添加执行权限时出错: {e}")
        else:
            print(f"警告: {file} 不存在")

    # 检查python依赖
    try:
        print("正在检查依赖...")
        import PySide6
        print("PySide6已安装")
    except ImportError:
        print("PySide6未安装，正在安装...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "PySide6"], check=True)
            print("PySide6安装成功")
        except Exception as e:
            print(f"PySide6安装失败: {e}")

    print("=== 安装完成 ===")
    print("您现在可以通过以下命令启动程序:")
    print("  python launcher.py")

    return 0

if __name__ == "__main__":
    sys.exit(main())