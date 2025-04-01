import sys
import platform
import getpass
import subprocess
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
    platform_version = platform.version()
    os_info = f"{current_platform} {platform_version}"
    print(f"当前操作系统: {current_platform}")

    # 获取当前用户
    current_user = getpass.getuser()

    # 获取版本号 (假设为常量）
    version = "3.0.0"  # 实际项目中应该从配置文件读取

    # 检查并记录权限状态
    has_admin = is_admin()
    print(f"当前程序是否有管理员权限: {has_admin}")
    admin_status = "已获取管理员权限" if has_admin else "未获取管理员权限"

    # 记录启动信息 - 在创建GUI前先记录重要信息
    logger.log(f"Cursor Pro v{version} 启动中...", LogLevel.INFO)
    logger.log(f"操作系统: {os_info}", LogLevel.INFO)
    logger.log(f"当前用户: {current_user}", LogLevel.INFO)
    admin_log_message = f"✅ 当前程序已拥有管理员权限，可以正常执行所有功能" if has_admin else "❌ 当前程序无管理员权限，部分功能可能受限"
    logger.log(admin_log_message, LogLevel.INFO)

    # 主题检测
    try:
        theme_detection_method = "defaults 命令"
        if current_platform == 'Darwin':
            # 使用macOS的defaults命令获取当前主题设置
            result = subprocess.run(
                ['defaults', 'read', '-g', 'AppleInterfaceStyle'],
                capture_output=True, text=True, check=False
            )
            theme_result = "深色" if result.returncode == 0 and "Dark" in result.stdout else "浅色"
        else:
            theme_detection_method = "不支持的平台"
            theme_result = "未知"

        logger.log(f"主题检测方法: {theme_detection_method}", LogLevel.INFO)
        logger.log(f"检测结果: {theme_result}", LogLevel.INFO)
    except Exception as e:
        logger.log(f"主题检测失败: {e}", LogLevel.WARNING)

    logger.log("已从配置文件加载设置", LogLevel.INFO)

    print("正在创建主窗口...")
    # 创建并显示主窗口
    window = MainWindow()
    window.show()

    # 记录启动成功信息
    logger.log(f"Cursor Pro v{version} 启动成功", LogLevel.INFO)
    logger.log(f"操作系统: {current_platform}", LogLevel.INFO)
    logger.log(f"管理员权限状态: {admin_status}", LogLevel.INFO)

    print("=== 应用程序初始化完成 ===")
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())