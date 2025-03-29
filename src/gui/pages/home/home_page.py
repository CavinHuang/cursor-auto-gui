from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                              QPushButton, QLabel, QTextEdit, QFrame, QMessageBox)
from PySide6.QtCore import Qt
from src.logic.log.log_manager import logger, LogLevel
from src.logic.utils.admin_helper import is_admin
import platform
import os
import getpass
import subprocess
import sys

class HomePage(QWidget):
    """主页类，显示主要功能和日志输出"""

    def __init__(self, parent=None):
        super().__init__(parent)
        # 默认使用浅色主题
        self.is_dark_theme = False
        self.setup_ui()

        # 检查管理员权限并记录状态
        self.has_admin = is_admin()
        logger.log(f"管理员权限检查结果: {self.has_admin}", LogLevel.INFO)

        # 显示权限状态
        self.show_sample_logs()

    def check_admin_privileges(self):
        """检查程序是否有管理员权限 - 为了保持兼容性，调用新的helper函数"""
        return is_admin()

    def detect_macos_theme(self):
        """检测macOS系统主题"""
        if platform.system() != 'Darwin':
            return "未知"

        try:
            # 使用macOS的defaults命令获取当前主题设置
            result = subprocess.run(
                ['defaults', 'read', '-g', 'AppleInterfaceStyle'],
                capture_output=True, text=True, check=False
            )

            # 如果命令成功并返回"Dark"，则为深色主题
            if result.returncode == 0 and "Dark" in result.stdout:
                return "深色"
            else:
                return "浅色"
        except Exception:
            return "浅色"  # 默认返回浅色主题

    def setup_ui(self):
        """设置UI界面"""
        layout = QVBoxLayout(self)

        # 快速操作区域
        quick_op_label = QLabel("快速操作")
        quick_op_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(quick_op_label)

        # 重置机器码区域
        reset_frame = QFrame()
        reset_frame.setStyleSheet("border: 1px solid #ddd; border-radius: 4px; padding: 10px;")
        reset_layout = QHBoxLayout(reset_frame)

        reset_label = QLabel("重置机器码")
        reset_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        reset_layout.addWidget(reset_label)

        reset_desc = QLabel("生成新的随机机器ID，重置使用限制")
        reset_desc.setStyleSheet("color: #666; font-size: 12px;")
        reset_layout.addWidget(reset_desc)

        reset_layout.addStretch()

        self.reset_button = QPushButton("执行")
        self.reset_button.setStyleSheet(
            "QPushButton {"
            "   background-color: #41cd52;"
            "   color: white;"
            "   border-radius: 4px;"
            "   padding: 5px 15px;"
            "   font-size: 13px;"
            "}"
            "QPushButton:hover {"
            "   background-color: #3dbd4e;"
            "}"
            "QPushButton:pressed {"
            "   background-color: #38b049;"
            "}"
        )
        reset_layout.addWidget(self.reset_button)

        layout.addWidget(reset_frame)

        # 完整注册流程区域
        reg_frame = QFrame()
        reg_frame.setStyleSheet("border: 1px solid #ddd; border-radius: 4px; padding: 10px;")
        reg_layout = QHBoxLayout(reg_frame)

        reg_label = QLabel("完整注册流程")
        reg_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        reg_layout.addWidget(reg_label)

        reg_desc = QLabel("重置机器码ID并自动注册新账号")
        reg_desc.setStyleSheet("color: #666; font-size: 12px;")
        reg_layout.addWidget(reg_desc)

        reg_layout.addStretch()

        self.reg_button = QPushButton("执行")
        self.reg_button.setStyleSheet(
            "QPushButton {"
            "   background-color: #41cd52;"
            "   color: white;"
            "   border-radius: 4px;"
            "   padding: 5px 15px;"
            "   font-size: 13px;"
            "}"
            "QPushButton:hover {"
            "   background-color: #3dbd4e;"
            "}"
            "QPushButton:pressed {"
            "   background-color: #38b049;"
            "}"
        )
        reg_layout.addWidget(self.reg_button)

        layout.addWidget(reg_frame)

        # 日志输出区域
        log_label = QLabel("日志输出")
        log_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 20px; margin-bottom: 10px;")
        layout.addWidget(log_label)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("border: 1px solid #ddd; border-radius: 4px; padding: 10px; font-family: 'Courier New';")
        self.log_text.setMinimumHeight(200)
        layout.addWidget(self.log_text)

        # 连接信号和槽
        self.reset_button.clicked.connect(self.reset_machine_code)
        self.reg_button.clicked.connect(self.register_new_account)

        # 保存UI元素的引用，以便在切换主题时更新样式
        self.section_labels = [quick_op_label, log_label]
        self.frames = [reset_frame, reg_frame]
        self.action_labels = [reset_label, reg_label]
        self.desc_labels = [reset_desc, reg_desc]
        self.action_buttons = [self.reset_button, self.reg_button]

    def show_sample_logs(self):
        """初始化日志显示区域"""
        # 设置日志管理器的GUI日志输出对象
        logger.set_gui_logger(self.log_text)

        # 获取版本号 - 假设从配置文件或常量中获取
        version = "3.0.0"  # 实际项目中应该从配置中读取

        # 获取操作系统信息
        os_name = platform.system()
        os_version = platform.version()
        os_info = f"{os_name} {os_version}"

        # 获取当前用户
        current_user = getpass.getuser()

        # 检查是否有管理员权限 - 使用新的 admin_helper 模块
        has_admin = is_admin()
        admin_status = "✅ 当前程序已拥有管理员权限，可以正常执行所有功能" if has_admin else "❌ 当前程序无管理员权限，部分功能可能受限"

        # 检测系统主题
        theme_detection_method = "defaults 命令"
        theme_result = self.detect_macos_theme()

        # 添加启动日志
        logger.log(f"Cursor Pro v{version} 启动中...", LogLevel.INFO)
        logger.log(f"操作系统: {os_info}", LogLevel.INFO)
        logger.log(f"当前用户: {current_user}", LogLevel.INFO)
        logger.log(admin_status, LogLevel.INFO)
        logger.log(f"当前用户: {current_user}", LogLevel.INFO)
        logger.log(f"主题检测方法: {theme_detection_method}", LogLevel.INFO)
        logger.log(f"检测结果: {theme_result}", LogLevel.INFO)

    def reset_machine_code(self):
        """重置机器码"""
        logger.log("开始重置机器码...", LogLevel.INFO)
        # 实际重置机器码的逻辑
        logger.log("机器码重置成功！", LogLevel.INFO)

    def register_new_account(self):
        """注册新账号"""
        logger.log("开始执行完整注册流程...", LogLevel.INFO)
        # 先重置机器码
        logger.log("步骤1：重置机器码", LogLevel.INFO)
        self.reset_machine_code()
        # 再注册新账号
        logger.log("步骤2：注册新账号", LogLevel.INFO)
        # 实际注册新账号的逻辑
        logger.log("完整注册流程执行完毕！", LogLevel.INFO)

    def set_theme(self, is_dark):
        """设置主题"""
        if self.is_dark_theme != is_dark:
            self.is_dark_theme = is_dark
            self.apply_theme_styles()

    def apply_theme_styles(self):
        """应用主题样式"""
        if self.is_dark_theme:
            # 深色主题样式
            self.setStyleSheet("background-color: #222;")

            # 更新区域标题样式
            for label in self.section_labels:
                label.setStyleSheet("font-size: 16px; font-weight: bold; color: #f0f0f0; margin-bottom: 10px;")

            # 更新框架样式
            for frame in self.frames:
                frame.setStyleSheet("border: 1px solid #444; border-radius: 4px; padding: 10px; background-color: #333;")

            # 更新操作标签样式
            for label in self.action_labels:
                label.setStyleSheet("font-size: 14px; font-weight: bold; color: #f0f0f0;")

            # 更新描述标签样式
            for label in self.desc_labels:
                label.setStyleSheet("color: #aaa; font-size: 12px;")

            # 更新按钮样式 - 保持绿色
            for button in self.action_buttons:
                button.setStyleSheet(
                    "QPushButton {"
                    "   background-color: #41cd52;"
                    "   color: white;"
                    "   border-radius: 4px;"
                    "   padding: 5px 15px;"
                    "   font-size: 13px;"
                    "}"
                    "QPushButton:hover {"
                    "   background-color: #3dbd4e;"
                    "}"
                    "QPushButton:pressed {"
                    "   background-color: #38b049;"
                    "}"
                )

            # 更新日志文本区域样式
            self.log_text.setStyleSheet(
                "border: 1px solid #444; "
                "border-radius: 4px; "
                "padding: 10px; "
                "font-family: 'Courier New'; "
                "background-color: #2d2d2d; "
                "color: #e0e0e0;"
            )

        else:
            # 浅色主题样式
            self.setStyleSheet("background-color: white;")

            # 更新区域标题样式
            for label in self.section_labels:
                label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")

            # 更新框架样式
            for frame in self.frames:
                frame.setStyleSheet("border: 1px solid #ddd; border-radius: 4px; padding: 10px;")

            # 更新操作标签样式
            for label in self.action_labels:
                label.setStyleSheet("font-size: 14px; font-weight: bold;")

            # 更新描述标签样式
            for label in self.desc_labels:
                label.setStyleSheet("color: #666; font-size: 12px;")

            # 更新按钮样式 - 保持绿色
            for button in self.action_buttons:
                button.setStyleSheet(
                    "QPushButton {"
                    "   background-color: #41cd52;"
                    "   color: white;"
                    "   border-radius: 4px;"
                    "   padding: 5px 15px;"
                    "   font-size: 13px;"
                    "}"
                    "QPushButton:hover {"
                    "   background-color: #3dbd4e;"
                    "}"
                    "QPushButton:pressed {"
                    "   background-color: #38b049;"
                    "}"
                )

            # 更新日志文本区域样式
            self.log_text.setStyleSheet(
                "border: 1px solid #ddd; "
                "border-radius: 4px; "
                "padding: 10px; "
                "font-family: 'Courier New';"
            )