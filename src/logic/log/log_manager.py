import logging
from enum import Enum, auto
from PySide6.QtWidgets import QTextEdit
import datetime

class LogLevel(Enum):
    """日志级别枚举类"""
    DEBUG = auto()
    INFO = auto()
    WARNING = auto()
    ERROR = auto()
    CRITICAL = auto()

class LogManager:
    """日志管理类，用于集中管理应用程序的日志输出"""

    def __init__(self):
        """初始化日志管理器"""
        self.logger = logging.getLogger("CursorPro")
        self.logger.setLevel(logging.DEBUG)

        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)

        # 设置日志格式
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)

        # 添加处理器
        self.logger.addHandler(console_handler)

        # GUI日志输出对象
        self.gui_logger = None

    def set_gui_logger(self, text_edit):
        """设置GUI日志输出对象"""
        if isinstance(text_edit, QTextEdit):
            self.gui_logger = text_edit

    def log(self, message, level=LogLevel.INFO):
        """记录日志"""
        if level == LogLevel.DEBUG:
            self.logger.debug(message)
        elif level == LogLevel.INFO:
            self.logger.info(message)
        elif level == LogLevel.WARNING:
            self.logger.warning(message)
        elif level == LogLevel.ERROR:
            self.logger.error(message)
        elif level == LogLevel.CRITICAL:
            self.logger.critical(message)

        # 如果设置了GUI日志输出对象，则同时在GUI中显示日志
        if self.gui_logger:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if level == LogLevel.DEBUG:
                self.gui_logger.append(f"{timestamp} - DEBUG: {message}")
            elif level == LogLevel.INFO:
                self.gui_logger.append(f"{timestamp} - INFO: {message}")
            elif level == LogLevel.WARNING:
                self.gui_logger.append(f"⚠️ {timestamp} - WARNING: {message}")
            elif level == LogLevel.ERROR:
                self.gui_logger.append(f"❌ {timestamp} - ERROR: {message}")
            elif level == LogLevel.CRITICAL:
                self.gui_logger.append(f"🔥 {timestamp} - CRITICAL: {message}")

# 创建全局日志管理器实例
logger = LogManager()