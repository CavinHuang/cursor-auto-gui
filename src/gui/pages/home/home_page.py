from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                              QPushButton, QLabel, QTextEdit, QFrame)
from PySide6.QtCore import Qt
from src.logic.log.log_manager import logger, LogLevel

class HomePage(QWidget):
    """主页类，显示主要功能和日志输出"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setup_ui()

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

    def show_sample_logs(self):
        """显示样例日志信息"""
        # 设置日志管理器的GUI日志输出对象
        logger.set_gui_logger(self.log_text)

        # 添加样例日志
        logger.log("Cursor Pro v3.0.0 启动中...", LogLevel.INFO)
        logger.log("操作系统: macOS", LogLevel.INFO)
        logger.log("当前用户: cavinhuang", LogLevel.INFO)
        logger.log("当前程序已拥有管理员权限，可以正常执行所有功能", LogLevel.INFO)
        logger.log("当前用户: cavinhuang", LogLevel.INFO)
        logger.log("主题检测方式: defaults 命令", LogLevel.INFO)
        logger.log("检测结果: 浅色", LogLevel.INFO)

    def reset_machine_code(self):
        """重置机器码"""
        logger.log("开始重置机器码...", LogLevel.INFO)
        # 模拟重置机器码的过程
        logger.log("正在生成新的随机机器ID...", LogLevel.INFO)
        logger.log("机器码重置成功！", LogLevel.INFO)

    def register_new_account(self):
        """注册新账号"""
        logger.log("开始执行完整注册流程...", LogLevel.INFO)
        # 先重置机器码
        logger.log("步骤1：重置机器码", LogLevel.INFO)
        self.reset_machine_code()
        # 再注册新账号
        logger.log("步骤2：注册新账号", LogLevel.INFO)
        logger.log("正在生成随机账号信息...", LogLevel.INFO)
        logger.log("正在提交注册请求...", LogLevel.INFO)
        logger.log("账号注册成功！", LogLevel.INFO)
        logger.log("完整注册流程执行完毕！", LogLevel.INFO)