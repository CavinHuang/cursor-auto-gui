#!/usr/bin/env python
"""
Cursor Pro 权限启动器
负责检查管理员权限，无需弹窗提示直接请求系统授权
整个流程中不会显示任何应用程序自己的对话框，只会显示系统的授权对话框
- 已有权限：直接启动主程序
- 无权限：直接弹出系统授权对话框
- 授权成功：自动启动主程序
- 授权失败：显示一个错误消息并退出
"""

import sys
import os
import platform
import subprocess
import time
import traceback
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt
from src.logic.utils.admin_helper import is_admin, restart_as_admin

def is_frozen():
    """检查当前是否在打包环境中运行"""
    return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')

def get_app_path():
    """获取应用程序的路径，适用于开发环境和打包环境"""
    if is_frozen():
        # 打包环境，返回应用包的路径
        if platform.system() == 'Darwin':  # macOS
            # 向上查找直到找到.app目录
            app_path = os.path.abspath(sys.executable)
            while not app_path.endswith('.app') and app_path != '/':
                app_path = os.path.dirname(app_path)

            if app_path == '/':
                print("警告: 无法找到.app包路径，使用当前目录")
                return os.getcwd()

            return app_path
        else:
            # Windows或Linux
            return os.path.dirname(sys.executable)
    else:
        # 开发环境，返回当前工作目录
        return os.getcwd()

def find_executable(app_path):
    """查找可执行文件的路径，适用于macOS环境"""
    if platform.system() == 'Darwin':
        # 首先检查默认位置
        default_exe = os.path.join(app_path, "Contents/MacOS/CursorPro")
        if os.path.exists(default_exe) and os.access(default_exe, os.X_OK):
            return default_exe

        # 如果默认可执行文件不存在，搜索MacOS目录下的所有可执行文件
        macos_dir = os.path.join(app_path, "Contents/MacOS")
        if os.path.exists(macos_dir):
            print(f"搜索可执行文件: {macos_dir}")
            for file in os.listdir(macos_dir):
                exe_path = os.path.join(macos_dir, file)
                if os.path.isfile(exe_path) and os.access(exe_path, os.X_OK):
                    print(f"找到可执行文件: {exe_path}")
                    return exe_path

        print(f"警告: 在 {app_path} 中未找到可执行文件")

    # 对于非macOS或找不到可执行文件的情况，返回None
    return None

def launch_app():
    """在确认有管理员权限后，启动主应用程序"""
    print("=== 启动主应用程序 ===")

    # 使用子进程启动主程序
    try:
        # 检查是否在打包环境中
        if is_frozen():
            # 打包环境
            if platform.system() == 'Darwin':  # macOS
                app_path = get_app_path()
                exe_path = find_executable(app_path)

                if not exe_path:
                    raise RuntimeError(f"在 {app_path} 中未找到可执行文件")

                print(f"使用可执行文件: {exe_path}")
                args = [exe_path, "--skip-admin-check"]
            else:
                # Windows或Linux
                exe_path = sys.executable
                args = [exe_path, "--skip-admin-check"]
        else:
            # 开发环境
            current_dir = os.getcwd()
            args = [sys.executable, os.path.join(current_dir, "main.py"), "--skip-admin-check"]

        print(f"执行命令: {' '.join(args)}")

        # 使用subprocess.Popen启动进程，并等待它完成
        process = subprocess.Popen(args)

        # 等待一小段时间确保程序启动
        time.sleep(1)

        # 检查进程是否成功启动
        if process.poll() is None:  # None表示进程仍在运行
            print("主程序成功启动")
            return True
        else:
            print(f"主程序启动失败，返回码: {process.returncode}")
            return False
    except Exception as e:
        print(f"启动主程序失败: {e}")
        traceback.print_exc()
        return False

def main():
    """主函数，检查权限并在需要时请求"""
    print("=== 权限启动器启动 ===")
    print(f"Python版本: {sys.version}")
    print(f"运行路径: {sys.executable}")
    print(f"当前工作目录: {os.getcwd()}")
    print(f"命令行参数: {sys.argv}")
    print(f"是否打包环境: {is_frozen()}")

    app = QApplication(sys.argv)

    # 显示自定义图标，即使处于打包环境中
    app_icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "icon.png")
    if os.path.exists(app_icon_path):
        from PySide6.QtGui import QIcon
        app.setWindowIcon(QIcon(app_icon_path))

    # 如果是从管理员模式重启，直接启动应用程序
    if "--restart-as-admin" in sys.argv:
        print("检测到管理员权限重启标志")
        # 再次检查权限，确认确实获得了管理员权限
        has_admin = is_admin()
        if has_admin:
            print("确认已获得管理员权限，无弹窗启动应用程序")
            # 直接启动，不显示任何错误弹窗
            launch_app()
            return 0
        else:
            print("警告：权限请求可能未成功，但仍尝试启动应用程序")
            # 尝试启动应用，无论成功与否都不显示弹窗
            launch_app()
            return 0

    # 如果命令行中包含--skip-admin-check参数，则跳过权限检查
    if "--skip-admin-check" in sys.argv:
        print("跳过管理员权限检查")
        return 0

    # 检查是否已经有管理员权限
    has_admin = is_admin()
    current_platform = platform.system()
    print(f"当前操作系统: {current_platform}")
    print(f"当前是否有管理员权限: {has_admin}")

    if has_admin:
        print("已拥有管理员权限，直接启动应用程序")
        # 直接启动，忽略启动结果
        launch_app()
        return 0
    else:
        print("需要请求管理员权限，直接进行系统授权")

        try:
            # 检查打包环境下的应用程序路径
            if is_frozen() and platform.system() == 'Darwin':
                app_path = get_app_path()
                print(f"应用程序路径: {app_path}")

                # 列出MacOS目录内容
                macos_dir = os.path.join(app_path, "Contents/MacOS")
                if os.path.exists(macos_dir):
                    print(f"MacOS目录内容:")
                    for item in os.listdir(macos_dir):
                        file_path = os.path.join(macos_dir, item)
                        is_executable = os.access(file_path, os.X_OK)
                        print(f"  {item} {'(可执行)' if is_executable else ''}")

            # 直接请求管理员权限，不显示询问对话框
            success = restart_as_admin()
            print(f"请求管理员权限结果: {'成功' if success else '失败'}")

            if success:
                # 成功请求了权限，直接退出当前进程，管理员权限的进程会自动启动
                print("权限请求成功，程序将以管理员权限重新启动")
                return 0
            else:
                # 请求失败，显示错误消息
                error_msg = QMessageBox()
                error_msg.setWindowTitle("权限请求失败")
                error_msg.setText("无法获取管理员权限。")
                error_msg.setInformativeText("程序将退出。")
                error_msg.setIcon(QMessageBox.Critical)
                error_msg.exec()
                return 1
        except Exception as e:
            # 捕获任何异常，显示给用户
            error_msg = QMessageBox()
            error_msg.setWindowTitle("发生错误")
            error_msg.setText("请求管理员权限时出现错误。")
            error_msg.setDetailedText(f"错误详情: {str(e)}\n\n{traceback.format_exc()}")
            error_msg.setIcon(QMessageBox.Critical)
            error_msg.exec()
            return 1

if __name__ == "__main__":
    sys.exit(main())