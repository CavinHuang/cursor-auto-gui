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
from PySide6.QtWidgets import QApplication, QMessageBox
from src.logic.utils.admin_helper import is_admin, restart_as_admin

def launch_app():
    """在确认有管理员权限后，启动主应用程序"""
    print("=== 启动主应用程序 ===")

    # 使用子进程启动主程序
    try:
        # 使用完整路径构建命令，确保在当前目录执行
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
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数，检查权限并在需要时请求"""
    print("=== 权限启动器启动 ===")
    app = QApplication(sys.argv)

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
            error_msg.setText(f"无法获取管理员权限。")
            error_msg.setInformativeText("程序将退出。")
            error_msg.setIcon(QMessageBox.Critical)
            error_msg.exec()
            return 1

if __name__ == "__main__":
    sys.exit(main())