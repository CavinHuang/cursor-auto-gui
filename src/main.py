import sys
import platform
from PySide6.QtWidgets import QApplication, QMessageBox
from src.gui.main_window import MainWindow
from src.logic.utils.admin_helper import is_admin, restart_as_admin
from src.logic.log.log_manager import logger, LogLevel

def main():
    """程序主函数"""
    print("=== 程序启动 ===")
    app = QApplication(sys.argv)

    # 记录基本系统信息
    current_platform = platform.system()
    print(f"当前操作系统: {current_platform}")

    # 检查管理员权限
    has_admin = is_admin()
    print(f"当前程序是否有管理员权限: {has_admin}")

    # 如果没有管理员权限，自动请求
    if not has_admin:
        print("检测到无管理员权限，正在自动请求...")

        # 创建并显示对话框，自动请求管理员权限
        msg_box = QMessageBox()
        msg_box.setWindowTitle("需要管理员权限")
        msg_box.setText(f"Cursor Pro 需要管理员权限才能正常运行所有功能。\n当前操作系统: {current_platform}")
        msg_box.setInformativeText("是否以管理员身份重新启动程序？")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.Yes)  # 设置默认按钮为"是"

        # 显示对话框并获取用户选择
        result = msg_box.exec()

        if result == QMessageBox.Yes:
            print("用户同意授予管理员权限，正在重启程序...")
            # 以管理员权限重启程序
            success = restart_as_admin()
            print(f"重启程序请求结果: {'成功' if success else '失败'}")

            if success:
                # 显示成功消息
                success_msg = QMessageBox()
                success_msg.setWindowTitle("重启中")
                success_msg.setText("程序即将以管理员权限重新启动，请稍候...")
                success_msg.exec()

                # 退出当前实例
                return 0
            else:
                # 显示错误消息
                error_msg = QMessageBox()
                error_msg.setWindowTitle("权限请求失败")
                error_msg.setText(f"无法以管理员权限重启程序。\n在 {current_platform} 平台上请求权限失败。")
                error_msg.setInformativeText("程序将以普通权限继续运行，部分功能可能受限。")
                error_msg.setIcon(QMessageBox.Critical)
                error_msg.exec()

    print("正在启动主窗口...")
    # 创建并显示主窗口
    window = MainWindow()
    window.show()

    # 记录启动信息
    logger.log(f"Cursor Pro 应用程序已启动，操作系统: {current_platform}", LogLevel.INFO)
    logger.log(f"管理员权限状态: {'已获取' if is_admin() else '未获取'}", LogLevel.INFO)

    return app.exec()

if __name__ == "__main__":
    sys.exit(main())