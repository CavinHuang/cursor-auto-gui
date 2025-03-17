import sys
from typing import Optional
from datetime import datetime
from enum import Enum, auto

class LogLevel(Enum):
    DEBUG = auto()
    INFO = auto()
    WARNING = auto()
    ERROR = auto()

class LogManager:
    _instance: Optional['LogManager'] = None
    _gui_logger = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self._log_level = LogLevel.INFO

    def set_gui_logger(self, gui_logger):
        """设置GUI日志输出对象"""
        self._gui_logger = gui_logger

    def set_log_level(self, level: LogLevel):
        """设置日志级别"""
        self._log_level = level

    def _format_message(self, level: LogLevel, message: str) -> str:
        """格式化日志消息"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return f'[{timestamp}] [{level.name}] {message}'

    def _log(self, level: LogLevel, message: str):
        """输出日志"""
        if level.value < self._log_level.value:
            return

        formatted_message = self._format_message(level, message)

        # 输出到控制台
        print(formatted_message, file=sys.stderr if level == LogLevel.ERROR else sys.stdout)

        # 输出到GUI日志页面
        if self._gui_logger:
            self._gui_logger.append_log(formatted_message)

    def debug(self, message: str):
        """输出调试日志"""
        self._log(LogLevel.DEBUG, message)

    def info(self, message: str):
        """输出信息日志"""
        self._log(LogLevel.INFO, message)

    def warning(self, message: str):
        """输出警告日志"""
        self._log(LogLevel.WARNING, message)

    def error(self, message: str):
        """输出错误日志"""
        self._log(LogLevel.ERROR, message)