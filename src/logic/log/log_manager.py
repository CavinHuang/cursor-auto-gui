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

        # 主题设置，默认为浅色
        self.is_dark_theme = False

        # 日志缓存，用于主题切换时重新应用样式
        self.log_cache = []

    def set_gui_logger(self, text_edit):
        """设置GUI日志输出对象"""
        if isinstance(text_edit, QTextEdit):
            self.gui_logger = text_edit
            # 设置日志区域后，应用已缓存的日志
            if self.log_cache and text_edit:
                self.reapply_logs()

    def set_dark_theme(self, is_dark):
        """设置是否使用深色主题"""
        if self.is_dark_theme != is_dark:
            self.is_dark_theme = is_dark
            # 如果有日志区域，重新应用所有日志
            if self.gui_logger:
                self.reapply_logs()

    def reapply_logs(self):
        """重新应用所有日志，用于主题切换时"""
        if not self.gui_logger:
            return

        # 清空当前日志显示
        self.gui_logger.clear()

        # 重新应用所有缓存的日志
        for log_item in self.log_cache:
            timestamp, level, message = log_item
            self._append_styled_log(timestamp, level, message)

    def _append_styled_log(self, timestamp, level, message):
        """根据当前主题添加带样式的日志"""
        if not self.gui_logger:
            return

        if self.is_dark_theme:
            # 深色主题下的颜色设置
            if level == LogLevel.DEBUG:
                self.gui_logger.append(f'<span style="color: #a0a0a0;">{timestamp} - DEBUG: {message}</span>')
            elif level == LogLevel.INFO:
                self.gui_logger.append(f'<span style="color: #e0e0e0;">{timestamp} - INFO: {message}</span>')
            elif level == LogLevel.WARNING:
                self.gui_logger.append(f'<span style="color: #ffc107;">⚠️ {timestamp} - WARNING: {message}</span>')
            elif level == LogLevel.ERROR:
                self.gui_logger.append(f'<span style="color: #ff6b6b;">❌ {timestamp} - ERROR: {message}</span>')
            elif level == LogLevel.CRITICAL:
                self.gui_logger.append(f'<span style="color: #ff5252;">🔥 {timestamp} - CRITICAL: {message}</span>')
        else:
            # 浅色主题下的颜色设置
            if level == LogLevel.DEBUG:
                self.gui_logger.append(f'<span style="color: #505050;">{timestamp} - DEBUG: {message}</span>')
            elif level == LogLevel.INFO:
                self.gui_logger.append(f'<span style="color: #101010;">{timestamp} - INFO: {message}</span>')
            elif level == LogLevel.WARNING:
                self.gui_logger.append(f'<span style="color: #d95c00;">⚠️ {timestamp} - WARNING: {message}</span>')
            elif level == LogLevel.ERROR:
                self.gui_logger.append(f'<span style="color: #cc0000;">❌ {timestamp} - ERROR: {message}</span>')
            elif level == LogLevel.CRITICAL:
                self.gui_logger.append(f'<span style="color: #b50000;">🔥 {timestamp} - CRITICAL: {message}</span>')

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

        # 获取当前时间戳
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 缓存日志
        self.log_cache.append((timestamp, level, message))

        # 如果设置了GUI日志输出对象，则同时在GUI中显示日志
        if self.gui_logger:
            self._append_styled_log(timestamp, level, message)

# 创建全局日志管理器实例
logger = LogManager()