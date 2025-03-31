import logging
from enum import Enum, auto
from PySide6.QtWidgets import QTextEdit
import datetime
import time

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

        # 日志去重机制
        self.recent_logs = {}
        self.dedup_window = 2  # 2秒内的相同日志会被去重

    def set_gui_logger(self, text_edit):
        """设置GUI日志输出对象"""
        if isinstance(text_edit, QTextEdit):
            self.gui_logger = text_edit

    def log(self, message, level=LogLevel.INFO):
        """记录日志，带去重功能"""
        # 构建日志唯一ID（日志级别+消息内容）
        log_id = f"{level.name}:{message}"
        current_time = time.time()

        # 检查是否是重复日志
        if log_id in self.recent_logs:
            last_time = self.recent_logs[log_id]
            # 如果上次记录的时间距离现在小于指定的时间窗口，则跳过本次记录
            if current_time - last_time < self.dedup_window:
                return

        # 更新日志记录时间
        self.recent_logs[log_id] = current_time

        # 清理过期的日志记录，避免内存持续增长
        self.clean_old_logs(current_time)

        # 调用原有的日志记录逻辑
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

    def clean_old_logs(self, current_time):
        """清理超过时间窗口的日志记录"""
        expired_logs = []
        for log_id, timestamp in self.recent_logs.items():
            if current_time - timestamp > self.dedup_window * 5:  # 超过时间窗口的5倍时清理
                expired_logs.append(log_id)

        for log_id in expired_logs:
            del self.recent_logs[log_id]

# 创建全局日志管理器实例
logger = LogManager()