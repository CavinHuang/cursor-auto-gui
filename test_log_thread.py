import sys
sys.path.append('src')

from PySide6.QtWidgets import QApplication, QTextEdit
from PySide6.QtCore import QThread
from src.logic.log.log_manager import logger, LogLevel
import time

class TestThread(QThread):
    """测试工作线程，用于测试日志线程安全性"""

    def run(self):
        """线程运行函数"""
        for i in range(10):
            logger.log(f'工作线程日志测试 {i}', LogLevel.INFO)
            time.sleep(0.5)

def main():
    """主函数"""
    app = QApplication([])

    # 创建文本编辑器并显示
    text_edit = QTextEdit()
    text_edit.setWindowTitle("日志线程安全测试")
    text_edit.resize(600, 400)
    text_edit.show()

    # 设置日志管理器
    logger.set_gui_logger(text_edit)

    # 主线程日志
    logger.log("主线程开始记录日志", LogLevel.INFO)

    # 创建并启动工作线程
    thread = TestThread()
    thread.start()

    # 继续在主线程记录日志
    for i in range(5):
        logger.log(f"主线程日志 {i}", LogLevel.INFO)
        time.sleep(1)

    # 运行应用程序事件循环
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())