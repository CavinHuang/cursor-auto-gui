import sys
import platform
from PySide6.QtWidgets import QApplication
from src.gui.main_window import MainWindow
from src.logic.utils.admin_helper import is_admin
from src.logic.log.log_manager import logger, LogLevel

def main():
    """应用程序主函数"""
    print("=== 应用程序初始化开始 ===")
    app = QApplication(sys.argv)

    # 记录基本系统信息
    current_platform = platform.system()
    print(f"当前操作系统: {current_platform}")

    # 检查并记录权限状态（仅用于日志，不再请求权限）
    has_admin = is_admin()
    print(f"当前程序是否有管理员权限: {has_admin}")
    admin_status = "已获取管理员权限" if has_admin else "未获取管理员权限"

    print("正在创建主窗口...")
    # 创建并显示主窗口
    window = MainWindow()
    window.show()

    # 记录启动信息
    logger.log(f"Cursor Pro v3.0.0 启动成功", LogLevel.INFO)
    logger.log(f"操作系统: {current_platform}", LogLevel.INFO)
    logger.log(f"管理员权限状态: {admin_status}", LogLevel.INFO)

    print("=== 应用程序初始化完成 ===")
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())