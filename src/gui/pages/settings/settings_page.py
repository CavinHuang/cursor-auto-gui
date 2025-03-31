from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QFrame, QComboBox,
                             QCheckBox, QLineEdit, QGroupBox, QFormLayout,
                             QSpinBox,
                             QScrollArea, QRadioButton, QButtonGroup, QToolButton,
                             QMessageBox, QTextEdit)
from PySide6.QtCore import Qt, Signal
from src.logic.log.log_manager import logger, LogLevel
from src.logic.config.config_manager import ConfigManager
import platform
import subprocess
import re

class SettingsPage(QWidget):
    """设置页面类，提供应用程序各种设置选项"""

    # 主题变更信号
    theme_changed = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)

        # 初始化配置管理器
        self.config_manager = ConfigManager()

        # 默认设置值
        self.set_default_values()

        # 从配置文件加载设置
        self.load_settings()

        # 设置UI界面
        self.setup_ui()

    def set_default_values(self):
        """设置默认值"""
        # 基本设置
        self.is_dark_theme = False
        self.language = "中文"
        self.enable_auto_update = True

        # 基础配置
        self.domain = "xx.me"

        # 邮箱配置
        self.use_temp_mail = False
        self.use_imap = True

        # 临时邮箱配置
        self.temp_mail = "xx@mailto.plus"
        self.temp_mail_epin = ""  # 临时邮箱PIN码
        self.temp_mail_ext = "@mailto.plus"

        # IMAP邮箱配置
        self.imap_server = "imap.gmail.com"
        self.imap_port = 993
        self.imap_user = "your.email@gmail.com"
        self.imap_pass = ""
        self.imap_dir = "INBOX"

        # 浏览器配置
        self.browser_path = ""
        self.browser_user_agent = "bKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.92 Safari/537.36"
        self.browser_headless = True

        # 代理配置
        self.use_proxy = False
        self.proxy_address = ""
        self.proxy_port = 8080
        self.log_level = LogLevel.INFO

    def load_settings(self):
        """从配置文件加载设置"""
        config = self.config_manager.get_config()
        if not config:
            logger.log("未发现配置文件，使用默认设置", LogLevel.INFO)
            return

        # 加载基本设置
        self.is_dark_theme = config.get("is_dark_theme", self.is_dark_theme)
        self.language = config.get("language", self.language)
        self.enable_auto_update = config.get("enable_auto_update", self.enable_auto_update)

        # 加载基础配置
        self.domain = config.get("domain", self.domain)

        # 加载邮箱选项配置
        self.use_temp_mail = config.get("use_temp_mail", self.use_temp_mail)
        self.use_imap = config.get("use_imap", self.use_imap)

        # 加载临时邮箱配置
        self.temp_mail = config.get("temp_mail", self.temp_mail)
        self.temp_mail_epin = config.get("temp_mail_epin", self.temp_mail_epin)
        self.temp_mail_ext = config.get("temp_mail_ext", self.temp_mail_ext)

        # 加载IMAP配置
        self.imap_server = config.get("imap_server", self.imap_server)
        self.imap_port = config.get("imap_port", self.imap_port)
        self.imap_user = config.get("imap_user", self.imap_user)
        self.imap_pass = config.get("imap_pass", self.imap_pass)
        self.imap_dir = config.get("imap_dir", self.imap_dir)

        # 加载浏览器配置
        self.browser_path = config.get("browser_path", self.browser_path)
        self.browser_user_agent = config.get("browser_user_agent", self.browser_user_agent)
        self.browser_headless = config.get("browser_headless", self.browser_headless)

        # 加载网络设置
        self.use_proxy = config.get("use_proxy", self.use_proxy)
        self.proxy_address = config.get("proxy_address", self.proxy_address)
        self.proxy_port = config.get("proxy_port", self.proxy_port)

        # 加载日志级别设置
        log_level_value = config.get("log_level")
        if log_level_value is not None:
            try:
                self.log_level = LogLevel(log_level_value)
            except ValueError:
                self.log_level = LogLevel.INFO

        logger.log("已从配置文件加载设置", LogLevel.INFO)

    def setup_ui(self):
        """设置UI界面"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # 设置滚动条样式
        scroll_area.setStyleSheet("""
            QScrollBar:vertical {
                background: transparent;
                width: 3px;
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
        """)

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(20)  # 增加各部分之间的间距
        scroll_layout.setContentsMargins(0, 20, 20, 20)  # 增加边距

        # ===== 基础配置 =====
        self.add_basic_settings(scroll_layout)

        # ===== 邮箱配置 =====
        self.add_email_settings(scroll_layout)

        # ===== IMAP邮箱配置 =====
        self.add_imap_settings(scroll_layout)

        # ===== 临时邮箱配置 =====
        self.add_temp_mail_settings(scroll_layout)

        # ===== 浏览器配置 =====
        self.add_browser_settings(scroll_layout)

        # ===== 外观设置 =====
        self.add_appearance_settings(scroll_layout)

        # ===== 系统设置 =====
        self.add_system_settings(scroll_layout)

        # ===== 网络设置 =====
        self.add_network_settings(scroll_layout)

        # ===== 底部按钮 =====
        self.add_bottom_buttons(scroll_layout)

        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)

        # 初始化时应用当前主题样式
        self.apply_theme_styles(self.is_dark_theme)

    def add_basic_settings(self, layout):
        """添加基础配置部分"""
        basic_group = QGroupBox("基础配置")
        basic_layout = QVBoxLayout(basic_group)
        basic_layout.setContentsMargins(16, 16, 16, 16)  # 去除padding值
        basic_layout.setSpacing(8)

        # DOMAIN域名配置
        domain_layout = QHBoxLayout()
        domain_layout.setSpacing(20)

        # 左侧标题和说明
        domain_left = QVBoxLayout()
        domain_left.setSpacing(4)  # 调整标题和说明间的间距为4像素
        self.domain_label = QLabel("DOMAIN")
        domain_left.addWidget(self.domain_label)

        domain_desc = QLabel("你的CF负载均衡的域名，用于生成临时邮箱和访问服务")
        domain_desc.setStyleSheet("color: #666; font-size: 12px;")
        domain_desc.setWordWrap(True)
        domain_left.addWidget(domain_desc)
        domain_left.setStretch(0, 0)
        domain_left.setStretch(1, 1)

        # 右侧输入框
        self.domain_edit = QTextEdit()
        self.domain_edit.setPlainText(self.domain)
        self.domain_edit.setFixedHeight(60)
        self.domain_edit.setStyleSheet("""
            QTextEdit {
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 8px;
                background: white;
                selection-background-color: #41cd52;
            }
            QTextEdit:focus {
                border: 1px solid #41cd52;
            }
        """)

        # 添加到水平布局
        domain_layout.addLayout(domain_left, 1)  # 左侧占1份
        domain_layout.addWidget(self.domain_edit, 1)  # 右侧占1份

        basic_layout.addLayout(domain_layout)
        layout.addWidget(basic_group)

    def add_email_settings(self, layout):
        """添加邮箱配置部分"""
        email_group = QGroupBox("邮箱配置")
        email_layout = QHBoxLayout(email_group)
        email_layout.setContentsMargins(16, 16, 16, 16)  # 去除padding值
        email_layout.setSpacing(15)

        # 临时邮箱复选框
        self.temp_mail_check = QCheckBox("临时邮箱")
        self.temp_mail_check.setStyleSheet("font-weight: normal;")
        self.temp_mail_check.setChecked(self.use_temp_mail)
        self.temp_mail_check.toggled.connect(self.on_temp_mail_toggled)
        email_layout.addWidget(self.temp_mail_check)

        email_layout.addStretch()

        # IMAP复选框
        self.imap_check = QCheckBox("IMAP")
        self.imap_check.setStyleSheet("color: #41cd52; font-weight: normal;")
        self.imap_check.setChecked(self.use_imap)
        self.imap_check.toggled.connect(self.on_imap_toggled)
        email_layout.addWidget(self.imap_check)

        layout.addWidget(email_group)

    def add_imap_settings(self, layout):
        """添加IMAP邮箱配置部分"""
        imap_group = QGroupBox("IMAP邮箱配置")
        imap_layout = QVBoxLayout(imap_group)
        imap_layout.setContentsMargins(16, 16, 16, 16)  # 去除padding值
        imap_layout.setSpacing(15)

        # IMAP_SERVER
        server_layout = QHBoxLayout()
        server_layout.setSpacing(20)

        # 左侧标题和说明
        server_left = QVBoxLayout()
        server_left.setSpacing(4)  # 调整标题和说明间的间距为4像素
        self.imap_server_label = QLabel("IMAP_SERVER")
        server_left.addWidget(self.imap_server_label)

        imap_server_desc = QLabel("IMAP服务器地址，例如Gmail的IMAP服务器为imap.gmail.com")
        imap_server_desc.setStyleSheet("color: #666; font-size: 12px;")
        imap_server_desc.setWordWrap(True)
        server_left.addWidget(imap_server_desc)

        # 右侧输入框
        self.imap_server_edit = QLineEdit(self.imap_server)

        # 添加到水平布局
        server_layout.addLayout(server_left, 1)  # 左侧占1份
        server_layout.addWidget(self.imap_server_edit, 1)  # 右侧占1份

        imap_layout.addLayout(server_layout)
        imap_layout.addSpacing(10)

        # IMAP_PORT
        port_layout = QHBoxLayout()
        port_layout.setSpacing(20)

        # 左侧标题和说明
        port_left = QVBoxLayout()
        port_left.setSpacing(4)  # 调整标题和说明间的间距为4像素
        self.imap_port_label = QLabel("IMAP_PORT")
        port_left.addWidget(self.imap_port_label)

        imap_port_desc = QLabel("IMAP服务器端口，993为SSL加密连接（推荐）")
        imap_port_desc.setStyleSheet("color: #666; font-size: 12px;")
        imap_port_desc.setWordWrap(True)
        port_left.addWidget(imap_port_desc)

        # 右侧输入框
        self.imap_port_edit = QLineEdit(str(self.imap_port))

        # 添加到水平布局
        port_layout.addLayout(port_left, 1)  # 左侧占1份
        port_layout.addWidget(self.imap_port_edit, 1)  # 右侧占1份

        imap_layout.addLayout(port_layout)
        imap_layout.addSpacing(10)

        # IMAP_USER
        user_layout = QHBoxLayout()
        user_layout.setSpacing(20)

        # 左侧标题和说明
        user_left = QVBoxLayout()
        user_left.setSpacing(4)  # 调整标题和说明间的间距为4像素
        self.imap_user_label = QLabel("IMAP_USER")
        user_left.addWidget(self.imap_user_label)

        imap_user_desc = QLabel("IMAP用户名，通常是完整的邮箱地址")
        imap_user_desc.setStyleSheet("color: #666; font-size: 12px;")
        imap_user_desc.setWordWrap(True)
        user_left.addWidget(imap_user_desc)

        # 右侧输入框
        self.imap_user_edit = QLineEdit(self.imap_user)

        # 添加到水平布局
        user_layout.addLayout(user_left, 1)  # 左侧占1份
        user_layout.addWidget(self.imap_user_edit, 1)  # 右侧占1份

        imap_layout.addLayout(user_layout)
        imap_layout.addSpacing(10)

        # IMAP_PASS
        pass_layout = QHBoxLayout()
        pass_layout.setSpacing(20)

        # 左侧标题和说明
        pass_left = QVBoxLayout()
        pass_left.setSpacing(4)  # 调整标题和说明间的间距为4像素
        self.imap_pass_label = QLabel("IMAP_PASS")
        pass_left.addWidget(self.imap_pass_label)

        imap_pass_desc = QLabel("IMAP密码，对于Gmail需要使用应用专用密码")
        imap_pass_desc.setStyleSheet("color: #666; font-size: 12px;")
        imap_pass_desc.setWordWrap(True)
        pass_left.addWidget(imap_pass_desc)

        # 右侧密码框和眼睛按钮
        pass_right = QHBoxLayout()
        pass_right.setSpacing(0)

        # 密码输入框
        self.imap_pass_edit = QLineEdit(self.imap_pass)
        self.imap_pass_edit.setEchoMode(QLineEdit.Password)
        self.imap_pass_edit.setPlaceholderText("•••••••••••••••")
        self.imap_pass_edit.setFixedHeight(36)  # 使用固定高度
        self.imap_pass_edit.setStyleSheet("""
            QLineEdit {
                border-top-right-radius: 0px;
                border-bottom-right-radius: 0px;
                padding-right: 0px;
            }
        """)
        pass_right.addWidget(self.imap_pass_edit)

        # 眼睛按钮
        self.imap_pass_toggle = QToolButton()
        self.imap_pass_toggle.setCursor(Qt.PointingHandCursor)
        self.imap_pass_toggle.setFixedHeight(40)  # 使用固定高度
        self.imap_pass_toggle.setStyleSheet("""
            QToolButton {
                border: 1px solid #e0e0e0;
                border-left: none;
                background-color: white;
                border-top-right-radius: 6px;
                border-bottom-right-radius: 6px;
                padding: 0 6px;
            }
            QToolButton:hover {
                background-color: #f8f8f8;
            }
        """)
        self.imap_pass_toggle.setText("👁️")
        self.imap_pass_toggle.clicked.connect(self.toggle_imap_pass_visibility)
        pass_right.addWidget(self.imap_pass_toggle)

        # 添加到水平布局
        pass_layout.addLayout(pass_left, 1)  # 左侧占1份
        pass_layout.addLayout(pass_right, 1)  # 右侧占1份

        imap_layout.addLayout(pass_layout)
        imap_layout.addSpacing(10)

        # IMAP_DIR
        dir_layout = QHBoxLayout()
        dir_layout.setSpacing(20)

        # 左侧标题和说明
        dir_left = QVBoxLayout()
        dir_left.setSpacing(4)  # 调整标题和说明间的间距为4像素
        self.imap_dir_label = QLabel("IMAP_DIR")
        dir_left.addWidget(self.imap_dir_label)

        imap_dir_desc = QLabel("IMAP收件箱目录，Gmail使用INBOX作为收件箱目录")
        imap_dir_desc.setStyleSheet("color: #666; font-size: 12px;")
        imap_dir_desc.setWordWrap(True)
        dir_left.addWidget(imap_dir_desc)

        # 右侧输入框
        self.imap_dir_edit = QLineEdit(self.imap_dir)

        # 添加到水平布局
        dir_layout.addLayout(dir_left, 1)  # 左侧占1份
        dir_layout.addWidget(self.imap_dir_edit, 1)  # 右侧占1份

        imap_layout.addLayout(dir_layout)

        # 根据IMAP是否选中显示或隐藏设置
        imap_group.setVisible(self.use_imap)

        # 保存引用以便后续更新可见性
        self.imap_settings_group = imap_group

        layout.addWidget(imap_group)

    def add_temp_mail_settings(self, layout):
        """添加临时邮箱配置部分"""
        temp_mail_group = QGroupBox("临时邮箱配置")
        temp_mail_layout = QVBoxLayout(temp_mail_group)
        temp_mail_layout.setContentsMargins(16, 16, 16, 16)  # 去除padding值
        temp_mail_layout.setSpacing(15)

        # TEMP_MAIL
        mail_layout = QHBoxLayout()
        mail_layout.setSpacing(20)

        # 左侧标题和说明
        mail_left = QVBoxLayout()
        mail_left.setSpacing(4)  # 调整标题和说明间的间距为4像素
        self.temp_mail_label = QLabel("TEMP_MAIL")
        mail_left.addWidget(self.temp_mail_label)

        temp_mail_desc = QLabel("临时邮箱完整地址（包括@后面部分）")
        temp_mail_desc.setStyleSheet("color: #666; font-size: 12px;")
        temp_mail_desc.setWordWrap(True)
        mail_left.addWidget(temp_mail_desc)

        # 右侧输入框
        self.temp_mail_edit = QLineEdit(self.temp_mail)

        # 添加到水平布局
        mail_layout.addLayout(mail_left, 1)  # 左侧占1份
        mail_layout.addWidget(self.temp_mail_edit, 1)  # 右侧占1份

        temp_mail_layout.addLayout(mail_layout)
        temp_mail_layout.addSpacing(10)

        # TEMP_MAIL_EPIN
        epin_layout = QHBoxLayout()
        epin_layout.setSpacing(20)

        # 左侧标题和说明
        epin_left = QVBoxLayout()
        epin_left.setSpacing(4)  # 调整标题和说明间的间距为4像素
        self.temp_mail_epin_label = QLabel("TEMP_MAIL_EPIN")
        epin_left.addWidget(self.temp_mail_epin_label)

        temp_mail_epin_desc = QLabel("临时邮箱PIN码，用于访问临时邮箱服务")
        temp_mail_epin_desc.setStyleSheet("color: #666; font-size: 12px;")
        temp_mail_epin_desc.setWordWrap(True)
        epin_left.addWidget(temp_mail_epin_desc)

        # 右侧密码框和眼睛按钮
        epin_right = QHBoxLayout()
        epin_right.setSpacing(0)

        # 密码输入框
        self.temp_mail_epin_edit = QLineEdit(self.temp_mail_epin)
        self.temp_mail_epin_edit.setEchoMode(QLineEdit.Password)
        self.temp_mail_epin_edit.setPlaceholderText("•••••")
        self.temp_mail_epin_edit.setFixedHeight(36)
        self.temp_mail_epin_edit.setStyleSheet("""
            QLineEdit {
                border-top-right-radius: 0px;
                border-bottom-right-radius: 0px;
                padding-right: 0px;
            }
        """)
        epin_right.addWidget(self.temp_mail_epin_edit)

        # 眼睛按钮
        self.temp_mail_epin_toggle = QToolButton()
        self.temp_mail_epin_toggle.setCursor(Qt.PointingHandCursor)
        self.temp_mail_epin_toggle.setFixedHeight(40)
        self.temp_mail_epin_toggle.setStyleSheet("""
            QToolButton {
                border: 1px solid #e0e0e0;
                border-left: none;
                background-color: white;
                border-top-right-radius: 6px;
                border-bottom-right-radius: 6px;
                padding: 0 8px;
            }
            QToolButton:hover {
                background-color: #f8f8f8;
            }
        """)
        self.temp_mail_epin_toggle.setText("👁️")
        self.temp_mail_epin_toggle.clicked.connect(self.toggle_temp_mail_epin_visibility)
        epin_right.addWidget(self.temp_mail_epin_toggle)

        # 添加到水平布局
        epin_layout.addLayout(epin_left, 1)  # 左侧占1份
        epin_layout.addLayout(epin_right, 1)  # 右侧占1份

        temp_mail_layout.addLayout(epin_layout)
        temp_mail_layout.addSpacing(10)

        # TEMP_MAIL_EXT
        ext_layout = QHBoxLayout()
        ext_layout.setSpacing(20)

        # 左侧标题和说明
        ext_left = QVBoxLayout()
        ext_left.setSpacing(4)  # 调整标题和说明间的间距为4像素
        self.temp_mail_ext_label = QLabel("TEMP_MAIL_EXT")
        ext_left.addWidget(self.temp_mail_ext_label)

        temp_mail_ext_desc = QLabel("临时邮箱后缀，包括@符号")
        temp_mail_ext_desc.setStyleSheet("color: #666; font-size: 12px;")
        temp_mail_ext_desc.setWordWrap(True)
        ext_left.addWidget(temp_mail_ext_desc)

        # 右侧输入框
        self.temp_mail_ext_edit = QLineEdit(self.temp_mail_ext)

        # 添加到水平布局
        ext_layout.addLayout(ext_left, 1)  # 左侧占1份
        ext_layout.addWidget(self.temp_mail_ext_edit, 1)  # 右侧占1份

        temp_mail_layout.addLayout(ext_layout)

        # 根据临时邮箱是否选中显示或隐藏设置
        temp_mail_group.setVisible(self.use_temp_mail)

        # 保存引用以便后续更新可见性
        self.temp_mail_settings_group = temp_mail_group

        layout.addWidget(temp_mail_group)

    def add_browser_settings(self, layout):
        """添加浏览器配置部分"""
        browser_group = QGroupBox("浏览器配置")
        browser_layout = QVBoxLayout(browser_group)
        browser_layout.setContentsMargins(16, 16, 16, 16)  # 去除padding值
        browser_layout.setSpacing(15)

        # BROWSER_PATH
        path_layout = QHBoxLayout()
        path_layout.setSpacing(20)

        # 左侧标题和说明
        path_left = QVBoxLayout()
        path_left.setSpacing(4)  # 调整标题和说明间的间距为4像素
        self.browser_path_label = QLabel("BROWSER_PATH")
        path_left.addWidget(self.browser_path_label)

        browser_path_desc = QLabel("各家浏览器可执行文件路径，留空则使用系统默认浏览器")
        browser_path_desc.setStyleSheet("color: #666; font-size: 12px;")
        browser_path_desc.setWordWrap(True)
        path_left.addWidget(browser_path_desc)

        # 右侧输入框
        self.browser_path_edit = QLineEdit(self.browser_path)

        # 添加到水平布局
        path_layout.addLayout(path_left, 1)  # 左侧占1份
        path_layout.addWidget(self.browser_path_edit, 1)  # 右侧占1份

        browser_layout.addLayout(path_layout)
        browser_layout.addSpacing(10)

        # BROWSER_USER_AGENT
        ua_layout = QHBoxLayout()
        ua_layout.setSpacing(20)

        # 左侧标题和说明
        ua_left = QVBoxLayout()
        ua_left.setSpacing(4)  # 调整标题和说明间的间距为4像素
        self.browser_ua_label = QLabel("BROWSER_USER_AGENT")
        ua_left.addWidget(self.browser_ua_label)

        browser_ua_desc = QLabel("浏览器User-Agent，用于模拟特定浏览器")
        browser_ua_desc.setStyleSheet("color: #666; font-size: 12px;")
        browser_ua_desc.setWordWrap(True)
        ua_left.addWidget(browser_ua_desc)

        # 右侧输入框
        self.browser_ua_edit = QLineEdit(self.browser_user_agent)

        # 添加到水平布局
        ua_layout.addLayout(ua_left, 1)  # 左侧占1份
        ua_layout.addWidget(self.browser_ua_edit, 1)  # 右侧占1份

        browser_layout.addLayout(ua_layout)
        browser_layout.addSpacing(10)

        # BROWSER_HEADLESS
        headless_layout = QHBoxLayout()
        headless_layout.setSpacing(20)

        # 左侧标题和说明
        headless_left = QVBoxLayout()
        headless_left.setSpacing(4)  # 调整标题和说明间的间距为4像素
        self.browser_headless_label = QLabel("BROWSER_HEADLESS")
        headless_left.addWidget(self.browser_headless_label)

        browser_headless_desc = QLabel("无头模式设置，True为浏览器在后台运行不显示界面")
        browser_headless_desc.setStyleSheet("color: #666; font-size: 12px;")
        browser_headless_desc.setWordWrap(True)
        headless_left.addWidget(browser_headless_desc)

        # 右侧单选按钮
        radio_layout = QHBoxLayout()
        radio_layout.setSpacing(10)  # 减小单选按钮之间的间距

        # 创建单选按钮组
        self.headless_group = QButtonGroup(self)

        # True选项
        self.browser_headless_true = QRadioButton("True (不显示浏览器界面)")
        self.browser_headless_true.setStyleSheet("color: #41cd52; font-weight: normal;")
        self.browser_headless_true.setChecked(self.browser_headless)
        self.headless_group.addButton(self.browser_headless_true)
        radio_layout.addWidget(self.browser_headless_true)

        # False选项
        self.browser_headless_false = QRadioButton("False (显示浏览器界面)")
        self.browser_headless_false.setStyleSheet("font-weight: normal;")
        self.browser_headless_false.setChecked(not self.browser_headless)
        self.headless_group.addButton(self.browser_headless_false)
        radio_layout.addWidget(self.browser_headless_false)

        # 连接信号
        self.browser_headless_true.toggled.connect(self.on_headless_toggled)

        # 添加到水平布局
        headless_layout.addLayout(headless_left, 1)  # 左侧占1份
        headless_layout.addLayout(radio_layout, 1)  # 右侧占1份

        browser_layout.addLayout(headless_layout)

        layout.addWidget(browser_group)

    def on_headless_toggled(self, checked):
        """当浏览器无头模式选项切换时触发"""
        if self.browser_headless_true.isChecked():
            self.browser_headless = True
            self.browser_headless_true.setStyleSheet("color: #41cd52; font-weight: normal;")
            self.browser_headless_false.setStyleSheet("font-weight: normal;")
        else:
            self.browser_headless = False
            self.browser_headless_false.setStyleSheet("color: #41cd52; font-weight: normal;")
            self.browser_headless_true.setStyleSheet("font-weight: normal;")

    def add_appearance_settings(self, layout):
        """添加外观设置部分"""
        appearance_group = QGroupBox("外观")
        appearance_layout = QVBoxLayout(appearance_group)
        appearance_layout.setContentsMargins(16, 16, 16, 16)  # 去除padding值
        appearance_layout.setSpacing(15)

        # 主题选择
        theme_layout = QHBoxLayout()
        theme_layout.setSpacing(20)

        # 左侧标题和说明
        theme_left = QVBoxLayout()
        theme_left.setSpacing(4)  # 调整标题和说明间的间距为4像素
        theme_label = QLabel("主题:")
        theme_left.addWidget(theme_label)

        theme_desc = QLabel("选择应用程序界面的主题风格")
        theme_desc.setStyleSheet("color: #666; font-size: 12px;")
        theme_desc.setWordWrap(True)
        theme_left.addWidget(theme_desc)

        # 右侧下拉框
        self.theme_combo = QComboBox()
        self.theme_combo.addItem("浅色")
        self.theme_combo.addItem("深色")
        self.theme_combo.setCurrentIndex(1 if self.is_dark_theme else 0)
        self.theme_combo.currentIndexChanged.connect(self.on_theme_changed)

        # 添加到水平布局
        theme_layout.addLayout(theme_left, 1)  # 左侧占1份
        theme_layout.addWidget(self.theme_combo, 1)  # 右侧占1份

        appearance_layout.addLayout(theme_layout)
        appearance_layout.addSpacing(10)

        # 语言选择
        language_layout = QHBoxLayout()
        language_layout.setSpacing(20)

        # 左侧标题和说明
        language_left = QVBoxLayout()
        language_left.setSpacing(4)  # 调整标题和说明间的间距为4像素
        language_label = QLabel("语言:")
        language_left.addWidget(language_label)

        language_desc = QLabel("选择应用程序界面的显示语言")
        language_desc.setStyleSheet("color: #666; font-size: 12px;")
        language_desc.setWordWrap(True)
        language_left.addWidget(language_desc)

        # 右侧下拉框
        self.language_combo = QComboBox()
        self.language_combo.addItem("中文")
        self.language_combo.addItem("English")
        # 设置当前语言（如果不是中文或English，默认设置为中文）
        self.language_combo.setCurrentIndex(1 if self.language == "English" else 0)

        # 添加到水平布局
        language_layout.addLayout(language_left, 1)  # 左侧占1份
        language_layout.addWidget(self.language_combo, 1)  # 右侧占1份

        appearance_layout.addLayout(language_layout)

        layout.addWidget(appearance_group)

    def add_system_settings(self, layout):
        """添加系统设置部分"""
        system_group = QGroupBox("系统")
        system_layout = QVBoxLayout(system_group)
        system_layout.setContentsMargins(16, 16, 16, 16)  # 去除padding值
        system_layout.setSpacing(15)

        # 自动更新
        update_layout = QHBoxLayout()
        update_layout.setSpacing(20)

        # 左侧标题和说明
        update_left = QVBoxLayout()
        update_left.setSpacing(4)  # 调整标题和说明间的间距为4像素
        update_label = QLabel("自动更新:")
        update_left.addWidget(update_label)

        update_desc = QLabel("启用后将自动检查和安装新版本")
        update_desc.setStyleSheet("color: #666; font-size: 12px;")
        update_desc.setWordWrap(True)
        update_left.addWidget(update_desc)

        # 右侧复选框
        update_right = QVBoxLayout()
        self.update_check = QCheckBox("启用自动更新")
        self.update_check.setStyleSheet("font-weight: normal;")
        self.update_check.setChecked(self.enable_auto_update)
        update_right.addWidget(self.update_check)
        update_right.addStretch()

        # 添加到水平布局
        update_layout.addLayout(update_left, 1)  # 左侧占1份
        update_layout.addLayout(update_right, 1)  # 右侧占1份

        system_layout.addLayout(update_layout)
        system_layout.addSpacing(10)

        # 日志级别
        log_level_layout = QHBoxLayout()
        log_level_layout.setSpacing(20)

        # 左侧标题和说明
        log_level_left = QVBoxLayout()
        log_level_left.setSpacing(4)  # 调整标题和说明间的间距为4像素
        log_level_label = QLabel("日志级别:")
        log_level_left.addWidget(log_level_label)

        log_level_desc = QLabel("设置记录的日志详细程度")
        log_level_desc.setStyleSheet("color: #666; font-size: 12px;")
        log_level_desc.setWordWrap(True)
        log_level_left.addWidget(log_level_desc)

        # 右侧下拉框
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItem("调试", LogLevel.DEBUG)
        self.log_level_combo.addItem("信息", LogLevel.INFO)
        self.log_level_combo.addItem("警告", LogLevel.WARNING)
        self.log_level_combo.addItem("错误", LogLevel.ERROR)

        # 设置当前日志级别
        current_log_level_index = 1  # 默认INFO级别
        for i in range(self.log_level_combo.count()):
            if self.log_level_combo.itemData(i) == self.log_level:
                current_log_level_index = i
                break
        self.log_level_combo.setCurrentIndex(current_log_level_index)

        self.log_level_combo.currentIndexChanged.connect(self.on_log_level_changed)

        # 添加到水平布局
        log_level_layout.addLayout(log_level_left, 1)  # 左侧占1份
        log_level_layout.addWidget(self.log_level_combo, 1)  # 右侧占1份

        system_layout.addLayout(log_level_layout)

        layout.addWidget(system_group)

    def add_network_settings(self, layout):
        """添加网络设置部分"""
        network_group = QGroupBox("网络")
        network_layout = QVBoxLayout(network_group)
        network_layout.setContentsMargins(16, 16, 16, 16)  # 去除padding值
        network_layout.setSpacing(20)

        # 代理设置
        proxy_layout = QHBoxLayout()
        proxy_layout.setSpacing(20)

        # 左侧标题和说明
        proxy_left = QVBoxLayout()
        proxy_left.setSpacing(4)  # 调整标题和说明间的间距为4像素
        proxy_label = QLabel("代理设置:")
        proxy_left.addWidget(proxy_label)

        proxy_desc = QLabel("启用代理服务器连接互联网")
        proxy_desc.setStyleSheet("color: #666; font-size: 12px;")
        proxy_desc.setWordWrap(True)
        proxy_left.addWidget(proxy_desc)

        # 右侧复选框
        proxy_right = QVBoxLayout()
        proxy_right.setSpacing(5)  # 减小右侧控件间距
        self.proxy_check = QCheckBox("使用代理")
        self.proxy_check.setStyleSheet("font-weight: normal;")
        self.proxy_check.setChecked(self.use_proxy)
        self.proxy_check.toggled.connect(self.on_proxy_toggled)
        proxy_right.addWidget(self.proxy_check)

        # 添加代理地址和端口
        proxy_form = QFormLayout()
        proxy_form.setVerticalSpacing(10)  # 减小表单项之间的垂直间距
        proxy_form.setHorizontalSpacing(10)  # 减小标签和输入框之间的水平间距
        proxy_form.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)  # 允许输入框扩展
        proxy_form.setLabelAlignment(Qt.AlignLeft)  # 标签左对齐

        self.proxy_address_edit = QLineEdit(self.proxy_address)
        self.proxy_address_edit.setPlaceholderText("例如：127.0.0.1")
        self.proxy_address_edit.setEnabled(self.use_proxy)
        proxy_form.addRow("地址:", self.proxy_address_edit)

        self.proxy_port_spin = QSpinBox()
        self.proxy_port_spin.setRange(0, 65535)
        self.proxy_port_spin.setValue(self.proxy_port)
        self.proxy_port_spin.setEnabled(self.use_proxy)
        proxy_form.addRow("端口:", self.proxy_port_spin)

        proxy_right.addLayout(proxy_form)

        # 添加到水平布局
        proxy_layout.addLayout(proxy_left, 1)  # 左侧占1份
        proxy_layout.addLayout(proxy_right, 1)  # 右侧占1份

        network_layout.addLayout(proxy_layout)

        layout.addWidget(network_group)

    def add_bottom_buttons(self, layout):
        """添加底部按钮"""
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(16, 16, 16, 16)

        self.reset_button = QPushButton("恢复默认设置")
        self.reset_button.setFixedHeight(40)
        self.reset_button.setMinimumWidth(140)
        self.reset_button.clicked.connect(self.reset_to_defaults)
        button_layout.addWidget(self.reset_button)

        button_layout.addStretch()

        self.save_button = QPushButton("保存设置")
        self.save_button.setFixedHeight(40)
        self.save_button.setMinimumWidth(140)
        self.save_button.clicked.connect(self.save_settings)
        button_layout.addWidget(self.save_button)

        layout.addLayout(button_layout)

    def on_theme_changed(self, index):
        """当主题选择变更时触发"""
        self.is_dark_theme = (index == 1)
        # 应用新的主题样式
        self.apply_theme_styles(self.is_dark_theme)
        # 发射主题变更信号
        self.theme_changed.emit(self.is_dark_theme)
        logger.log(f"主题已切换为: {'深色' if self.is_dark_theme else '浅色'}", LogLevel.INFO)

    def on_log_level_changed(self, index):
        """当日志级别变更时触发"""
        selected_level = self.log_level_combo.currentData()
        self.log_level = selected_level
        # 记录日志级别变更，但不调用不存在的方法
        logger.log(f"日志级别已设置为: {self.log_level_combo.currentText()}", LogLevel.INFO)

    def set_theme_state(self, is_dark):
        """设置主题状态，并更新页面样式"""
        self.is_dark_theme = is_dark
        if hasattr(self, 'theme_combo'):
            self.theme_combo.setCurrentIndex(1 if is_dark else 0)

        # 应用主题样式
        self.apply_theme_styles(is_dark)

    def apply_theme_styles(self, is_dark):
        """应用主题样式"""
        scroll_area = self.findChild(QScrollArea)
        scroll_content = scroll_area.widget()

        if is_dark:
            # 深色主题样式
            scroll_content.setStyleSheet("background-color: transparent;")  # 设置为透明

            # 更新滚动条样式
            scroll_area.setStyleSheet("""
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
            """)

            self.setStyleSheet("""
                QGroupBox {
                    border: 1px solid #3d3d3d;
                    border-radius: 8px;
                    background-color: transparent;  /* 设置为透明 */
                    margin-top: 0px;
                    padding-top: 25px;
                    font-weight: normal;
                    color: #e0e0e0;
                }

                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 15px;
                    top: 8px;
                    padding: 0px 5px;
                    background-color: transparent;
                    color: #e0e0e0;
                }

                QLabel {
                    color: #e0e0e0;
                    font-weight: normal;
                }

                QCheckBox, QRadioButton {
                    spacing: 5px;
                    color: #e0e0e0;
                }

                QCheckBox::indicator, QRadioButton::indicator {
                    width: 18px;
                    height: 18px;
                }

                QCheckBox::indicator:unchecked, QRadioButton::indicator:unchecked {
                    border: 1px solid #555555;
                    border-radius: 3px;
                    background-color: #484848;
                }

                QCheckBox::indicator:checked, QRadioButton::indicator:checked {
                    border: 1px solid #41cd52;
                    border-radius: 3px;
                    background-color: #41cd52;
                }

                QRadioButton::indicator:unchecked {
                    border-radius: 9px;
                }

                QRadioButton::indicator:checked {
                    border-radius: 9px;
                }

                QLineEdit, QComboBox, QSpinBox {
                    border: 1px solid #555555;
                    border-radius: 6px;
                    padding: 8px;
                    background: #484848;
                    color: #e0e0e0;
                    selection-background-color: #41cd52;
                    min-height: 20px;
                }

                QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
                    border: 1px solid #41cd52;
                }

                QPushButton {
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-size: 13px;
                }

                QComboBox::drop-down {
                    subcontrol-origin: padding;
                    subcontrol-position: top right;
                    border-left: 1px solid #555555;
                    width: 20px;
                }

                QComboBox QAbstractItemView {
                    background-color: #484848;
                    color: #e0e0e0;
                    border: 1px solid #555555;
                    selection-background-color: #41cd52;
                    border-radius: 4px;
                }

                QSpinBox::up-button, QSpinBox::down-button {
                    background-color: #555555;
                    width: 16px;
                    border-radius: 3px;
                }

                QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                    background-color: #666666;
                }

                QSpinBox::up-arrow {
                    image: url(:/icons/arrow_up_white.png);
                    width: 10px;
                    height: 10px;
                }

                QSpinBox::down-arrow {
                    image: url(:/icons/arrow_down_white.png);
                    width: 10px;
                    height: 10px;
                }
            """)

            # 更新说明文字样式
            for desc_label in self.findChildren(QLabel):
                if "font-size: 12px;" in desc_label.styleSheet():
                    desc_label.setStyleSheet("color: #999; font-size: 12px;")

            # 更新复选框和单选按钮样式
            self.update_toggle_styles()

            # 更新恢复默认设置按钮样式
            self.reset_button.setStyleSheet(
                "QPushButton {"
                "   background-color: #484848;"
                "   color: #e0e0e0;"
                "   border: 1px solid #555555;"
                "   border-radius: 6px;"
                "   padding: 8px 16px;"
                "}"
                "QPushButton:hover {"
                "   background-color: #535353;"
                "}"
                "QPushButton:pressed {"
                "   background-color: #5e5e5e;"
                "}"
            )

            # 更新保存设置按钮样式
            self.save_button.setStyleSheet(
                "QPushButton {"
                "   background-color: #41cd52;"
                "   color: white;"
                "   border: none;"
                "   border-radius: 6px;"
                "   padding: 8px 16px;"
                "}"
                "QPushButton:hover {"
                "   background-color: #3dbd4e;"
                "}"
                "QPushButton:pressed {"
                "   background-color: #38b049;"
                "}"
            )

            # 更新眼睛按钮样式
            self.imap_pass_toggle.setStyleSheet("""
                QToolButton {
                    border: 1px solid #555555;
                    border-left: none;
                    background-color: #484848;
                    border-top-right-radius: 6px;
                    border-bottom-right-radius: 6px;
                    padding: 0 8px;
                }
                QToolButton:hover {
                    background-color: #555555;
                }
            """)

            self.temp_mail_epin_toggle.setStyleSheet("""
                QToolButton {
                    border: 1px solid #555555;
                    border-left: none;
                    background-color: #484848;
                    border-top-right-radius: 6px;
                    border-bottom-right-radius: 6px;
                    padding: 0 8px;
                }
                QToolButton:hover {
                    background-color: #555555;
                }
            """)

            # 更新密码输入框样式
            self.imap_pass_edit.setStyleSheet("""
                QLineEdit {
                    border: 1px solid #555555;
                    border-top-right-radius: 0px;
                    border-bottom-right-radius: 0px;
                    padding: 8px;
                    background: #484848;
                    color: #e0e0e0;
                    selection-background-color: #41cd52;
                    min-height: 20px;
                    padding-right: 0px;
                }
                QLineEdit:focus {
                    border: 1px solid #41cd52;
                    border-right: none;
                }
            """)

            self.temp_mail_epin_edit.setStyleSheet("""
                QLineEdit {
                    border: 1px solid #555555;
                    border-top-right-radius: 0px;
                    border-bottom-right-radius: 0px;
                    padding: 8px;
                    background: #484848;
                    color: #e0e0e0;
                    selection-background-color: #41cd52;
                    min-height: 20px;
                    padding-right: 0px;
                }
                QLineEdit:focus {
                    border: 1px solid #41cd52;
                    border-right: none;
                }
            """)

            # 更新域名输入框样式
            self.domain_edit.setStyleSheet("""
                QTextEdit {
                    border: 1px solid #555555;
                    border-radius: 6px;
                    padding: 8px;
                    background: transparent;
                    color: #e0e0e0;
                }
                QTextEdit:focus {
                    border: 1px solid #41cd52;
                }
            """)

        else:
            # 浅色主题样式
            scroll_content.setStyleSheet("background-color: transparent;")  # 设置为透明

            # 更新滚动条样式
            scroll_area.setStyleSheet("""
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
            """)

            self.setStyleSheet("""
                QGroupBox {
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
                    background-color: transparent;  /* 设置为透明 */
                    margin-top: 0px;
                    padding-top: 25px;
                    font-weight: normal;
                }

                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 15px;
                    top: 8px;
                    padding: 0px 5px;
                    background-color: transparent;
                }

                QLabel {
                    font-weight: normal;
                }

                QCheckBox {
                    spacing: 5px;
                }

                QCheckBox::indicator, QRadioButton::indicator {
                    width: 18px;
                    height: 18px;
                }

                QCheckBox::indicator:unchecked, QRadioButton::indicator:unchecked {
                    border: 1px solid #cccccc;
                    border-radius: 3px;
                    background-color: white;
                }

                QCheckBox::indicator:checked, QRadioButton::indicator:checked {
                    border: 1px solid #41cd52;
                    border-radius: 3px;
                    background-color: #41cd52;
                }

                QRadioButton::indicator:unchecked {
                    border-radius: 9px;
                }

                QRadioButton::indicator:checked {
                    border-radius: 9px;
                }

                QLineEdit, QComboBox, QSpinBox {
                    border: 1px solid #e0e0e0;
                    border-radius: 6px;
                    padding: 8px;
                    background: white;
                    selection-background-color: #41cd52;
                    min-height: 20px;
                }

                QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
                    border: 1px solid #41cd52;
                }

                QPushButton {
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-size: 13px;
                }

                QComboBox::drop-down {
                    subcontrol-origin: padding;
                    subcontrol-position: top right;
                    border-left: 1px solid #e0e0e0;
                    width: 20px;
                }

                QComboBox QAbstractItemView {
                    background-color: white;
                    border: 1px solid #e0e0e0;
                    selection-background-color: #41cd52;
                    border-radius: 4px;
                }

                QSpinBox::up-button, QSpinBox::down-button {
                    background-color: #f0f0f0;
                    width: 16px;
                    border-radius: 3px;
                }

                QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                    background-color: #e0e0e0;
                }

                QSpinBox::up-arrow {
                    image: url(:/icons/arrow_up.png);
                    width: 10px;
                    height: 10px;
                }

                QSpinBox::down-arrow {
                    image: url(:/icons/arrow_down.png);
                    width: 10px;
                    height: 10px;
                }
            """)

            # 更新说明文字样式
            for desc_label in self.findChildren(QLabel):
                if "font-size: 12px;" in desc_label.styleSheet():
                    desc_label.setStyleSheet("color: #666; font-size: 12px;")

            # 更新复选框和单选按钮样式
            self.update_toggle_styles()

            # 更新恢复默认设置按钮样式
            self.reset_button.setStyleSheet(
                "QPushButton {"
                "   background-color: #f0f0f0;"
                "   color: #333;"
                "   border: 1px solid #d0d0d0;"
                "   border-radius: 6px;"
                "   padding: 8px 16px;"
                "}"
                "QPushButton:hover {"
                "   background-color: #e0e0e0;"
                "}"
                "QPushButton:pressed {"
                "   background-color: #d0d0d0;"
                "}"
            )

            # 更新保存设置按钮样式
            self.save_button.setStyleSheet(
                "QPushButton {"
                "   background-color: #41cd52;"
                "   color: white;"
                "   border: none;"
                "   border-radius: 6px;"
                "   padding: 8px 16px;"
                "}"
                "QPushButton:hover {"
                "   background-color: #3dbd4e;"
                "}"
                "QPushButton:pressed {"
                "   background-color: #38b049;"
                "}"
            )

            # 更新眼睛按钮样式
            self.imap_pass_toggle.setStyleSheet("""
                QToolButton {
                    border: 1px solid #e0e0e0;
                    border-left: none;
                    background-color: white;
                    border-top-right-radius: 6px;
                    border-bottom-right-radius: 6px;
                    padding: 0 8px;
                }
                QToolButton:hover {
                    background-color: #f8f8f8;
                }
            """)

            self.temp_mail_epin_toggle.setStyleSheet("""
                QToolButton {
                    border: 1px solid #e0e0e0;
                    border-left: none;
                    background-color: white;
                    border-top-right-radius: 6px;
                    border-bottom-right-radius: 6px;
                    padding: 0 8px;
                }
                QToolButton:hover {
                    background-color: #f8f8f8;
                }
            """)

            # 更新密码输入框样式
            self.imap_pass_edit.setStyleSheet("""
                QLineEdit {
                    border: 1px solid #e0e0e0;
                    border-top-right-radius: 0px;
                    border-bottom-right-radius: 0px;
                    padding: 8px;
                    background: white;
                    selection-background-color: #41cd52;
                    min-height: 20px;
                    padding-right: 0px;
                }
                QLineEdit:focus {
                    border: 1px solid #41cd52;
                    border-right: none;
                }
            """)

            self.temp_mail_epin_edit.setStyleSheet("""
                QLineEdit {
                    border: 1px solid #e0e0e0;
                    border-top-right-radius: 0px;
                    border-bottom-right-radius: 0px;
                    padding: 8px;
                    background: white;
                    selection-background-color: #41cd52;
                    min-height: 20px;
                    padding-right: 0px;
                }
                QLineEdit:focus {
                    border: 1px solid #41cd52;
                    border-right: none;
                }
            """)

            # 更新域名输入框样式
            self.domain_edit.setStyleSheet("""
                QTextEdit {
                    border: 1px solid #e0e0e0;
                    border-radius: 6px;
                    padding: 8px;
                    background: white;
                    selection-background-color: #41cd52;
                }
                QTextEdit:focus {
                    border: 1px solid #41cd52;
                }
            """)

    def update_toggle_styles(self):
        """更新开关类控件样式"""
        # 更新临时邮箱复选框样式
        if self.temp_mail_check.isChecked():
            self.temp_mail_check.setStyleSheet("color: #41cd52; font-weight: normal;")
        else:
            self.temp_mail_check.setStyleSheet("font-weight: normal;")

        # 更新IMAP复选框样式
        if self.imap_check.isChecked():
            self.imap_check.setStyleSheet("color: #41cd52; font-weight: normal;")
        else:
            self.imap_check.setStyleSheet("font-weight: normal;")

        # 更新浏览器无头模式单选按钮样式
        if self.browser_headless_true.isChecked():
            self.browser_headless_true.setStyleSheet("color: #41cd52; font-weight: normal;")
            self.browser_headless_false.setStyleSheet("font-weight: normal;")
        else:
            self.browser_headless_false.setStyleSheet("color: #41cd52; font-weight: normal;")
            self.browser_headless_true.setStyleSheet("font-weight: normal;")

    def on_proxy_toggled(self, checked):
        """当代理选项切换时触发"""
        self.use_proxy = checked
        self.proxy_address_edit.setEnabled(checked)
        self.proxy_port_spin.setEnabled(checked)

        # 如果开启代理，尝试获取系统代理配置
        if checked:
            system_proxy = self.get_system_proxy()
            if system_proxy:
                proxy_host, proxy_port = system_proxy
                self.proxy_address_edit.setText(proxy_host)
                self.proxy_port_spin.setValue(proxy_port)
                logger.log(f"已获取系统代理配置: {proxy_host}:{proxy_port}", LogLevel.INFO)

    def get_system_proxy(self):
        """获取系统代理配置

        返回:
            tuple: (代理地址, 代理端口) 或者 None (如果没有找到代理配置)
        """
        system = platform.system()

        try:
            if system == "Darwin":  # macOS
                # 获取当前活跃的网络服务
                services_output = subprocess.check_output(
                    ["networksetup", "-listallnetworkservices"],
                    universal_newlines=True
                )
                active_services = [
                    service for service in services_output.split('\n')[1:]
                    if service and not service.startswith('*')
                ]

                # 遍历活跃的网络服务，查找代理设置
                for service in active_services:
                    proxy_output = subprocess.check_output(
                        ["networksetup", "-getwebproxy", service],
                        universal_newlines=True
                    )

                    # 检查代理是否启用
                    enabled_match = re.search(r"Enabled: (Yes|No)", proxy_output)
                    if enabled_match and enabled_match.group(1) == "Yes":
                        # 获取代理服务器和端口
                        server_match = re.search(r"Server: ([\w\.]+)", proxy_output)
                        port_match = re.search(r"Port: (\d+)", proxy_output)

                        if server_match and port_match:
                            proxy_host = server_match.group(1)
                            proxy_port = int(port_match.group(1))
                            return (proxy_host, proxy_port)

            elif system == "Windows":
                # Windows系统获取代理设置
                reg_query = subprocess.check_output(
                    ["reg", "query", "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings"],
                    universal_newlines=True
                )

                # 检查代理是否启用
                proxy_enable = re.search(r"ProxyEnable\s+REG_DWORD\s+0x([0-9a-f]+)", reg_query)
                if proxy_enable and proxy_enable.group(1) == "1":
                    # 获取代理服务器设置
                    proxy_server = re.search(r"ProxyServer\s+REG_SZ\s+([\w\.:]+)", reg_query)
                    if proxy_server:
                        proxy_str = proxy_server.group(1)
                        if ":" in proxy_str:
                            host, port_str = proxy_str.split(":", 1)
                            try:
                                port = int(port_str)
                                return (host, port)
                            except ValueError:
                                pass

            elif system == "Linux":
                # Linux系统尝试获取环境变量中的代理设置
                env_vars = ["http_proxy", "HTTP_PROXY"]
                for var in env_vars:
                    proxy_str = subprocess.check_output(f"echo ${var}", shell=True, universal_newlines=True).strip()
                    if proxy_str:
                        # 移除协议前缀
                        proxy_str = proxy_str.replace("http://", "").replace("https://", "")
                        if ":" in proxy_str:
                            host, port_str = proxy_str.split(":", 1)
                            try:
                                port = int(port_str)
                                return (host, port)
                            except ValueError:
                                pass

        except Exception as e:
            logger.log(f"获取系统代理配置时出错: {str(e)}", LogLevel.ERROR)

        return None

    def on_temp_mail_toggled(self, checked):
        """当临时邮箱选项切换时触发"""
        self.use_temp_mail = checked

        # 如果选中临时邮箱，则取消选中IMAP
        if checked:
            self.imap_check.setChecked(False)
            self.temp_mail_check.setStyleSheet("color: #41cd52; font-weight: normal;")
            self.imap_check.setStyleSheet("font-weight: normal;")
        else:
            self.temp_mail_check.setStyleSheet("font-weight: normal;")

        # 更新设置组的可见性
        self.temp_mail_settings_group.setVisible(checked)

    def on_imap_toggled(self, checked):
        """当IMAP选项切换时触发"""
        self.use_imap = checked

        # 如果选中IMAP，则取消选中临时邮箱
        if checked:
            self.temp_mail_check.setChecked(False)
            self.imap_check.setStyleSheet("color: #41cd52; font-weight: normal;")
            self.temp_mail_check.setStyleSheet("font-weight: normal;")
        else:
            self.imap_check.setStyleSheet("font-weight: normal;")

        # 更新设置组的可见性
        self.imap_settings_group.setVisible(checked)

    def create_themed_message_box(self, icon, title, text):
        """创建一个与当前主题一致的消息框"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(text)
        msg_box.setIcon(icon)

        # 设置样式
        if self.is_dark_theme:
            # 深色主题样式
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: #2d2d2d;
                    color: #e0e0e0;
                }
                QMessageBox QLabel {
                    color: #e0e0e0;
                }
                QMessageBox QPushButton {
                    background-color: #41cd52;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 6px 12px;
                    min-width: 80px;
                }
                QMessageBox QPushButton:hover {
                    background-color: #3dbd4e;
                }
                QMessageBox QPushButton:pressed {
                    background-color: #38b049;
                }
            """)
        else:
            # 浅色主题样式
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: white;
                    color: #333;
                }
                QMessageBox QLabel {
                    color: #333;
                }
                QMessageBox QPushButton {
                    background-color: #41cd52;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 6px 12px;
                    min-width: 80px;
                }
                QMessageBox QPushButton:hover {
                    background-color: #3dbd4e;
                }
                QMessageBox QPushButton:pressed {
                    background-color: #38b049;
                }
            """)

        return msg_box

    def save_settings(self):
        """保存设置"""
        # 收集基本设置
        self.is_dark_theme = (self.theme_combo.currentIndex() == 1) if hasattr(self, 'theme_combo') else False
        self.language = self.language_combo.currentText() if hasattr(self, 'language_combo') else "中文"
        self.enable_auto_update = self.update_check.isChecked() if hasattr(self, 'update_check') else True

        # 收集基础配置
        self.domain = self.domain_edit.text()

        # 收集邮箱配置 - 已通过toggle设置

        # 收集临时邮箱配置
        if self.use_temp_mail:
            self.temp_mail = self.temp_mail_edit.text()
            self.temp_mail_epin = self.temp_mail_epin_edit.text()
            self.temp_mail_ext = self.temp_mail_ext_edit.text()

        # 收集IMAP配置
        if self.use_imap:
            self.imap_server = self.imap_server_edit.text()
            self.imap_port = int(self.imap_port_edit.text()) if self.imap_port_edit.text().isdigit() else 993
            self.imap_user = self.imap_user_edit.text()
            self.imap_pass = self.imap_pass_edit.text()
            self.imap_dir = self.imap_dir_edit.text()

        # 收集浏览器配置
        self.browser_path = self.browser_path_edit.text()
        self.browser_user_agent = self.browser_ua_edit.text()
        # browser_headless 已通过单选按钮设置

        # 收集网络设置
        self.use_proxy = self.proxy_check.isChecked() if hasattr(self, 'proxy_check') else False
        self.proxy_address = self.proxy_address_edit.text() if hasattr(self, 'proxy_address_edit') else ""
        self.proxy_port = self.proxy_port_spin.value() if hasattr(self, 'proxy_port_spin') else 8080
        self.log_level = self.log_level_combo.currentData() if hasattr(self, 'log_level_combo') else LogLevel.INFO

        # 创建配置字典
        config = {
            # 基本设置
            "is_dark_theme": self.is_dark_theme,
            "language": self.language,
            "enable_auto_update": self.enable_auto_update,

            # 基础配置
            "domain": self.domain,

            # 邮箱选项
            "use_temp_mail": self.use_temp_mail,
            "use_imap": self.use_imap,

            # 临时邮箱配置
            "temp_mail": self.temp_mail,
            "temp_mail_epin": self.temp_mail_epin,
            "temp_mail_ext": self.temp_mail_ext,

            # IMAP配置
            "imap_server": self.imap_server,
            "imap_port": self.imap_port,
            "imap_user": self.imap_user,
            "imap_pass": self.imap_pass,
            "imap_dir": self.imap_dir,
            "imap_protocol": "IMAP",  # 默认使用IMAP协议

            # 浏览器配置
            "browser_path": self.browser_path,
            "browser_user_agent": self.browser_user_agent,
            "browser_headless": self.browser_headless,

            # 网络设置
            "use_proxy": self.use_proxy,
            "proxy_address": self.proxy_address,
            "proxy_port": self.proxy_port,

            # 日志级别
            "log_level": self.log_level.value
        }

        # 保存配置到文件
        if self.config_manager.update_config(config):
            logger.log("设置已成功保存到配置文件", LogLevel.INFO)
            # 显示成功提示框
            msg_box = self.create_themed_message_box(QMessageBox.Information, "保存成功", "设置已保存成功！")
            msg_box.exec()
        else:
            logger.log("保存设置失败", LogLevel.ERROR)
            # 显示错误提示框
            msg_box = self.create_themed_message_box(QMessageBox.Critical, "保存失败", "设置保存失败，请重试！")
            msg_box.exec()

    def reset_to_defaults(self):
        """重置为默认设置"""
        # 基本设置
        if hasattr(self, 'theme_combo'):
            self.theme_combo.setCurrentIndex(0)  # 浅色主题
        if hasattr(self, 'language_combo'):
            self.language_combo.setCurrentIndex(0)  # 中文
        if hasattr(self, 'update_check'):
            self.update_check.setChecked(True)  # 启用自动更新

        # 基础配置
        self.domain_edit.setText("xx.me")

        # 邮箱配置
        self.temp_mail_check.setChecked(False)
        self.temp_mail_check.setStyleSheet("font-weight: normal;")
        self.imap_check.setChecked(True)
        self.imap_check.setStyleSheet("color: #41cd52; font-weight: normal;")

        # 更新配置区域可见性
        self.temp_mail_settings_group.setVisible(False)
        self.imap_settings_group.setVisible(True)

        # 临时邮箱配置
        self.temp_mail_edit.setText("zz@mailto.plus")
        self.temp_mail_epin_edit.setText("")
        self.temp_mail_ext_edit.setText("@mailto.plus")

        # IMAP配置
        self.imap_server_edit.setText("imap.gmail.com")
        self.imap_port_edit.setText("993")
        self.imap_user_edit.setText("your.email@gmail.com")
        self.imap_pass_edit.setText("")
        self.imap_dir_edit.setText("INBOX")

        # 浏览器配置
        self.browser_path_edit.setText("")
        self.browser_ua_edit.setText("bKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.92 Safari/537.36")
        self.browser_headless_true.setChecked(True)

        # 网络设置
        if hasattr(self, 'proxy_check'):
            self.proxy_check.setChecked(False)  # 不使用代理
        if hasattr(self, 'proxy_address_edit'):
            self.proxy_address_edit.setText("")
        if hasattr(self, 'proxy_port_spin'):
            self.proxy_port_spin.setValue(8080)
        if hasattr(self, 'log_level_combo'):
            self.log_level_combo.setCurrentIndex(1)  # INFO级别

        # 手动触发保存以更新内部状态
        self.save_settings()

        logger.log("设置已重置为默认值", LogLevel.INFO)

        # 显示恢复默认设置成功提示
        msg_box = self.create_themed_message_box(QMessageBox.Information, "恢复默认", "已将所有设置恢复为默认值！")
        msg_box.exec()

    def toggle_imap_pass_visibility(self):
        """切换IMAP密码显示/隐藏状态"""
        if self.imap_pass_edit.echoMode() == QLineEdit.Password:
            self.imap_pass_edit.setEchoMode(QLineEdit.Normal)
            self.imap_pass_toggle.setText("🔒")
        else:
            self.imap_pass_edit.setEchoMode(QLineEdit.Password)
            self.imap_pass_toggle.setText("👁️")

    def toggle_temp_mail_epin_visibility(self):
        """切换临时邮箱PIN码显示/隐藏状态"""
        if self.temp_mail_epin_edit.echoMode() == QLineEdit.Password:
            self.temp_mail_epin_edit.setEchoMode(QLineEdit.Normal)
            self.temp_mail_epin_toggle.setText("🔒")
        else:
            self.temp_mail_epin_edit.setEchoMode(QLineEdit.Password)
            self.temp_mail_epin_toggle.setText("👁️")
