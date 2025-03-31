import logging
from enum import Enum, auto
from PySide6.QtWidgets import QTextEdit
import datetime
import time
import os
import sys
import platform
from logging.handlers import RotatingFileHandler

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

        # 设置日志格式
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)

        # 添加控制台处理器
        self.logger.addHandler(console_handler)
        self.console_handler = console_handler

        # 文件处理器，默认不启用
        self.file_handler = None
        self.log_file_path = None

        # GUI日志输出对象
        self.gui_logger = None

        # 日志去重机制
        self.recent_logs = {}
        self.dedup_window = 2  # 2秒内的相同日志会被去重

        # 默认日志文本颜色（浅色主题）
        self.text_color = "#333333"

        # 日志级别对应的颜色（浅色主题）
        self.level_colors = {
            LogLevel.DEBUG: "blue",
            LogLevel.INFO: "green",
            LogLevel.WARNING: "orange",
            LogLevel.ERROR: "red",
            LogLevel.CRITICAL: "darkred"
        }

        # 深色主题下的日志级别颜色
        self.dark_level_colors = {
            LogLevel.DEBUG: "#81a1c1",    # 淡蓝色
            LogLevel.INFO: "#a3be8c",     # 淡绿色
            LogLevel.WARNING: "#ebcb8b",  # 淡黄色
            LogLevel.ERROR: "#bf616a",    # 淡红色
            LogLevel.CRITICAL: "#d08770"  # 淡橙色
        }

    def set_text_color(self, color):
        """设置日志文本颜色

        Args:
            color (str): 颜色代码，如 "#333333" 或 "#e0e0e0"
        """
        self.text_color = color

        # 根据文本颜色判断是否为深色主题
        is_dark_theme = color.lower() == "#e0e0e0"

        # 根据主题选择对应的日志级别颜色
        if is_dark_theme:
            self.level_colors = self.dark_level_colors
        else:
            self.level_colors = {
                LogLevel.DEBUG: "blue",
                LogLevel.INFO: "green",
                LogLevel.WARNING: "orange",
                LogLevel.ERROR: "red",
                LogLevel.CRITICAL: "darkred"
            }

    def set_gui_logger(self, text_edit):
        """设置GUI日志输出对象"""
        if isinstance(text_edit, QTextEdit):
            self.gui_logger = text_edit

    def set_file_logger(self, log_dir=None, log_file=None, max_size_mb=10, backup_count=5):
        """设置文件日志

        Args:
            log_dir (str, optional): 日志目录路径，默认在用户目录下的.cursor_pro/logs
            log_file (str, optional): 日志文件名，默认为cursor_pro_日期时间.log
            max_size_mb (int, optional): 单个日志文件最大大小，单位MB，默认10MB
            backup_count (int, optional): 保留的旧日志文件数量，默认5个
        """
        # 移除现有的文件处理器
        if self.file_handler:
            self.logger.removeHandler(self.file_handler)
            self.file_handler = None

        # 设置日志目录
        if not log_dir:
            log_dir = os.path.join(os.path.expanduser("~"), ".cursor_pro", "logs")

        # 确保日志目录存在
        os.makedirs(log_dir, exist_ok=True)

        # 设置日志文件名
        if not log_file:
            current_date = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = f"cursor_pro_{current_date}.log"

        # 完整日志文件路径
        self.log_file_path = os.path.join(log_dir, log_file)

        # 创建具有轮转功能的文件处理器 (RotatingFileHandler)
        max_bytes = max_size_mb * 1024 * 1024  # 转换为字节
        file_handler = RotatingFileHandler(
            self.log_file_path,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )

        # 设置日志级别和格式
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)

        # 添加到日志器
        self.logger.addHandler(file_handler)
        self.file_handler = file_handler

        # 记录日志已开始
        self.logger.info(f"===== 文件日志开始 =====")
        self.logger.info(f"日志文件路径: {self.log_file_path}")
        self.logger.info(f"操作系统: {platform.system()} {platform.release()}")
        self.logger.info(f"Python版本: {sys.version}")

        return self.log_file_path

    def get_log_file_path(self):
        """获取当前日志文件路径"""
        return self.log_file_path

    def disable_file_logger(self):
        """禁用文件日志"""
        if self.file_handler:
            self.logger.info("===== 文件日志结束 =====")
            self.logger.removeHandler(self.file_handler)
            self.file_handler = None
            self.log_file_path = None

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

            # 获取对应级别的颜色
            level_color = self.level_colors.get(level, "inherit")

            # 构建HTML格式的日志消息
            if level == LogLevel.DEBUG:
                log_html = f'<span style="color:{self.text_color};">{timestamp} - <span style="color:{level_color};">DEBUG</span>: {message}</span>'
            elif level == LogLevel.INFO:
                log_html = f'<span style="color:{self.text_color};">{timestamp} - <span style="color:{level_color};">INFO</span>: {message}</span>'
            elif level == LogLevel.WARNING:
                log_html = f'<span style="color:{self.text_color};">⚠️ {timestamp} - <span style="color:{level_color};">WARNING</span>: {message}</span>'
            elif level == LogLevel.ERROR:
                log_html = f'<span style="color:{self.text_color};">❌ {timestamp} - <span style="color:{level_color};">ERROR</span>: {message}</span>'
            elif level == LogLevel.CRITICAL:
                log_html = f'<span style="color:{self.text_color};">🔥 {timestamp} - <span style="color:{level_color};">CRITICAL</span>: {message}</span>'

            # 向GUI日志输出添加HTML格式的日志消息
            self.gui_logger.insertHtml(log_html + "<br>")
            self.gui_logger.ensureCursorVisible()

    def info(self, message):
        """记录INFO级别日志"""
        self.log(message, LogLevel.INFO)

    def debug(self, message):
        """记录DEBUG级别日志"""
        self.log(message, LogLevel.DEBUG)

    def warning(self, message):
        """记录WARNING级别日志"""
        self.log(message, LogLevel.WARNING)

    def error(self, message):
        """记录ERROR级别日志"""
        self.log(message, LogLevel.ERROR)

    def critical(self, message):
        """记录CRITICAL级别日志"""
        self.log(message, LogLevel.CRITICAL)

    def clean_old_logs(self, current_time):
        """清理超过时间窗口的日志记录"""
        expired_logs = []
        for log_id, timestamp in self.recent_logs.items():
            if current_time - timestamp > self.dedup_window * 5:  # 超过时间窗口的5倍时清理
                expired_logs.append(log_id)

        for log_id in expired_logs:
            del self.recent_logs[log_id]

    def set_level(self, level):
        """设置日志级别

        Args:
            level: 可以是LogLevel枚举值或者logging模块的级别常量
        """
        # 转换LogLevel枚举值到logging模块的级别常量
        if isinstance(level, LogLevel):
            if level == LogLevel.DEBUG:
                log_level = logging.DEBUG
            elif level == LogLevel.INFO:
                log_level = logging.INFO
            elif level == LogLevel.WARNING:
                log_level = logging.WARNING
            elif level == LogLevel.ERROR:
                log_level = logging.ERROR
            elif level == LogLevel.CRITICAL:
                log_level = logging.CRITICAL
            else:
                log_level = logging.INFO
        else:
            # 直接使用logging模块的级别常量
            log_level = level

        # 设置日志级别
        self.logger.setLevel(log_level)

        # 同时更新控制台处理器和文件处理器的级别
        if self.console_handler:
            self.console_handler.setLevel(log_level)

        if self.file_handler:
            self.file_handler.setLevel(log_level)

    def clean_old_log_files(self, log_dir=None, max_days=30):
        """清理旧的日志文件

        Args:
            log_dir: 日志目录路径，默认使用当前日志文件的目录
            max_days: 保留的最大天数，默认30天
        """
        # 如果没有指定日志目录，使用当前日志文件的目录
        if not log_dir and self.log_file_path:
            log_dir = os.path.dirname(self.log_file_path)

        # 如果仍然没有日志目录，使用默认目录
        if not log_dir:
            log_dir = os.path.join(os.path.expanduser("~"), ".cursor_pro", "logs")

        # 确保目录存在
        if not os.path.exists(log_dir):
            return

        # 当前时间
        now = time.time()
        deleted_count = 0

        # 遍历日志目录中的所有文件
        for filename in os.listdir(log_dir):
            if filename.startswith("cursor_pro_") and filename.endswith(".log"):
                file_path = os.path.join(log_dir, filename)

                # 获取文件最后修改时间
                file_mtime = os.path.getmtime(file_path)

                # 如果文件超过最大天数，删除它
                if now - file_mtime > max_days * 86400:  # 86400秒 = 1天
                    try:
                        os.remove(file_path)
                        deleted_count += 1
                    except Exception as e:
                        self.error(f"无法删除旧日志文件 {file_path}: {e}")

        if deleted_count > 0:
            self.info(f"已清理 {deleted_count} 个超过 {max_days} 天的旧日志文件")

# 创建全局日志管理器实例
logger = LogManager()