import threading
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                              QPushButton, QLabel, QTextEdit, QFrame, QMessageBox)
from PySide6.QtCore import Qt
from src.logic.cursor_pro.keep_alive import check_cursor_version, init_keep_alive, reset_machine_id
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

        # 为日志区域创建一个框架，与上方区域保持一致的风格
        log_frame = QFrame()
        log_frame.setStyleSheet("border: 1px solid #ddd; border-radius: 8px; padding: 0px;")
        log_layout = QVBoxLayout(log_frame)
        log_layout.setContentsMargins(0, 0, 0, 0)  # 清除内部布局边距
        log_layout.setSpacing(0)  # 消除内部元素间的间距

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            border: none;
            padding: 10px 10px;
            font-family: 'Courier New';
            background-color: transparent;
            font-size: 12px;
            line-height: 22px;
        """)
        self.log_text.setMinimumHeight(200)
        log_layout.addWidget(self.log_text)

        # 将日志框架添加到主布局
        layout.addWidget(log_frame)

        # 连接信号和槽
        self.reset_button.clicked.connect(self.reset_machine_code)
        self.reg_button.clicked.connect(self.register_new_account)

        # 保存UI元素的引用，以便在切换主题时更新样式
        self.section_labels = [quick_op_label, log_label]
        self.frames = [reset_frame, reg_frame, log_frame]  # 添加log_frame到框架列表
        self.action_labels = [reset_label, reg_label]
        self.desc_labels = [reset_desc, reg_desc]
        self.action_buttons = [self.reset_button, self.reg_button]

    def show_sample_logs(self):
        """初始化日志显示区域"""
        # 设置日志管理器的GUI日志输出对象
        logger.set_gui_logger(self.log_text)

        # 设置日志文本颜色
        logger.set_text_color("#e0e0e0" if self.is_dark_theme else "#333333")

        # 仅在日志中显示权限状态，不重复记录启动信息
        has_admin = is_admin()
        if has_admin:
            logger.log("当前已具有管理员权限状态", LogLevel.INFO)
            logger.log("所有功能可以正常使用", LogLevel.INFO)
        else:
            logger.log("当前无管理员权限", LogLevel.WARNING)
            logger.log("部分功能可能受限", LogLevel.WARNING)

        # 添加已从配置文件加载设置的日志
        logger.log("已从配置文件加载设置", LogLevel.INFO)

    def reset_machine_code(self):
        """重置机器码"""
        logger.log("开始重置机器码...", LogLevel.INFO)
        greater_than_0_45 = check_cursor_version()
        def reset_thread():
            try:
                reset_machine_id(greater_than_0_45)
            except Exception as e:
                logger.log(f"重置机器码失败: {str(e)}", LogLevel.ERROR)

        # 启动线程
        threading.Thread(target=reset_thread, daemon=True).start()

    def register_new_account(self):
        """注册新账号"""
        logger.log("开始注册新账号...", LogLevel.INFO)
        self.reg_button.configure(state="disabled", text="注册中...")
        # 创建新线程执行重置操作
        def reset_thread():
            try:
                init_keep_alive()
                # 重置完成后，在主线程中更新UI
                self.after(0, lambda: self.reg_button.configure(state="normal", text="立即注册账号"))
            except Exception as e:
                # 发生错误时，在主线程中更新UI
                self.after(0, lambda: [
                    self.reg_button.configure(state="normal", text="立即注册账号"),
                    print(f"注册失败: {str(e)}")
                ])

        # 启动线程
        threading.Thread(target=reset_thread, daemon=True).start()

    def set_theme(self, is_dark):
        """设置主题"""
        if self.is_dark_theme != is_dark:
            self.is_dark_theme = is_dark
            self.apply_theme_styles()

            # 更新日志记录器的日志文本颜色
            logger.set_text_color("#e0e0e0" if is_dark else "#333333")

            # 刷新现有日志文本的颜色
            self.refresh_log_text_colors()

    def apply_theme_styles(self):
        """应用主题样式"""
        if self.is_dark_theme:
            # 深色主题样式
            self.setStyleSheet("background-color: #222;")

            # 更新区域标题样式
            for label in self.section_labels:
                label.setStyleSheet("font-size: 16px; font-weight: bold; color: #f0f0f0; margin-bottom: 10px;")

            # 更新框架样式
            for i, frame in enumerate(self.frames):
                if frame == self.frames[-1]:  # 如果是日志框架（最后一个）
                    print(frame)
                    frame.setStyleSheet("border: 1px solid #444; border-radius: 8px; padding: 0px; background-color: #2d2d2d;")
                else:  # 对于其他框架
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

            # 更新日志文本区域样式 - 无需设置边框，因为边框在框架上
            self.log_text.setStyleSheet("""
                border: none;
                padding: 15px 18px;
                font-family: 'Courier New';
                background-color: transparent;
                color: #e0e0e0;

                /* 深色主题滚动条样式 */
                QScrollBar:vertical {
                   background: #2d2d2d;
                   width: 6px;
                   margin: 0px;
                }
                QScrollBar::handle:vertical {
                   background: #555555;
                   min-height: 30px;
                   border-radius: 3px;
                }
                QScrollBar::handle:vertical:hover {
                   background: #666666;
                }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                   height: 0px;
                }
                QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                   background: transparent;
                }

                /* 深色主题水平滚动条样式 */
                QScrollBar:horizontal {
                   background: #2d2d2d;
                   height: 6px;
                   margin: 0px;
                }
                QScrollBar::handle:horizontal {
                   background: #555555;
                   min-width: 30px;
                   border-radius: 3px;
                }
                QScrollBar::handle:horizontal:hover {
                   background: #666666;
                }
                QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                   width: 0px;
                }
                QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
                   background: transparent;
                }
            """)

        else:
            # 浅色主题样式
            self.setStyleSheet("background-color: white;")

            # 更新区域标题样式
            for label in self.section_labels:
                label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")

            # 更新框架样式
            for i, frame in enumerate(self.frames):
                if frame == self.frames[-1]:  # 如果是日志框架（最后一个）
                    frame.setStyleSheet("border: 1px solid #ddd; border-radius: 8px; padding: 0px;")
                else:  # 对于其他框架
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

            # 更新日志文本区域样式 - 无需设置边框，因为边框在框架上
            self.log_text.setStyleSheet("""
                border: none;
                padding: 15px 18px;
                font-family: 'Courier New';
                background-color: transparent;

                /* 浅色主题滚动条样式 */
                QScrollBar:vertical {
                   background: #f5f5f5;
                   width: 6px;
                   margin: 0px;
                }
                QScrollBar::handle:vertical {
                   background: #c0c0c0;
                   min-height: 30px;
                   border-radius: 3px;
                }
                QScrollBar::handle:vertical:hover {
                   background: #a0a0a0;
                }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                   height: 0px;
                }
                QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                   background: transparent;
                }

                /* 浅色主题水平滚动条样式 */
                QScrollBar:horizontal {
                   background: #f5f5f5;
                   height: 6px;
                   margin: 0px;
                }
                QScrollBar::handle:horizontal {
                   background: #c0c0c0;
                   min-width: 30px;
                   border-radius: 3px;
                }
                QScrollBar::handle:horizontal:hover {
                   background: #a0a0a0;
                }
                QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                   width: 0px;
                }
                QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
                   background: transparent;
                }
            """)

    def refresh_log_text_colors(self):
        """刷新日志文本的颜色以适应当前主题"""
        current_text = self.log_text.toHtml()

        # 保存当前光标位置和滚动条位置
        cursor = self.log_text.textCursor()
        cursor_position = cursor.position()
        scroll_value = self.log_text.verticalScrollBar().value()

        if self.is_dark_theme:
            # 深色主题：替换文本颜色为浅色
            # 替换默认文本颜色
            current_text = current_text.replace('color:#000000;', 'color:#e0e0e0;')
            current_text = current_text.replace('color:#333333;', 'color:#e0e0e0;')

            # 替换不同日志级别的文本颜色
            current_text = current_text.replace('color:blue;', 'color:#81a1c1;')     # 调试信息颜色
            current_text = current_text.replace('color:green;', 'color:#a3be8c;')    # 一般信息颜色
            current_text = current_text.replace('color:orange;', 'color:#ebcb8b;')   # 警告信息颜色
            current_text = current_text.replace('color:red;', 'color:#bf616a;')      # 错误信息颜色
        else:
            # 浅色主题：替换文本颜色为深色
            # 替换默认文本颜色
            current_text = current_text.replace('color:#e0e0e0;', 'color:#333333;')

            # 替换不同日志级别的文本颜色
            current_text = current_text.replace('color:#81a1c1;', 'color:blue;')     # 调试信息颜色
            current_text = current_text.replace('color:#a3be8c;', 'color:green;')    # 一般信息颜色
            current_text = current_text.replace('color:#ebcb8b;', 'color:orange;')   # 警告信息颜色
            current_text = current_text.replace('color:#bf616a;', 'color:red;')      # 错误信息颜色

        # 设置替换后的HTML内容
        self.log_text.setHtml(current_text)

        # 恢复光标位置和滚动条位置
        cursor.setPosition(cursor_position)
        self.log_text.setTextCursor(cursor)
        self.log_text.verticalScrollBar().setValue(scroll_value)