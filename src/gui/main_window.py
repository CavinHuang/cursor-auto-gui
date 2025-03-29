from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout,
                                QHBoxLayout, QPushButton, QLabel, QTextEdit,
                                QFrame, QStackedWidget, QScrollArea, QSizePolicy)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QFont
from src.logic.log.log_manager import logger, LogLevel
from src.logic.config.config_manager import ConfigManager
# 导入页面模块
from .pages.home import HomePage
from .pages.settings import SettingsPage
from .pages.about import AboutPage

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 初始化配置管理器
        self.config_manager = ConfigManager()

        # 加载主题设置
        config = self.config_manager.get_config()
        self.is_dark_theme = config.get("is_dark_theme", False)

        logger.log(f'配置中的主题设置: {"深色" if self.is_dark_theme else "浅色"}', LogLevel.INFO)

        # 设置窗口标题和大小
        self.setWindowTitle("Cursor Pro")
        self.resize(960, 600)

        # 设置应用程序图标
        self.setWindowIcon(QIcon(":/icons/app_icon.png"))

        # 创建中央窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 创建左侧菜单（传入主题信息）
        self.left_menu = self.create_left_menu(is_dark=self.is_dark_theme)
        main_layout.addWidget(self.left_menu)

        # 创建右侧内容区域（传入主题信息）
        self.content_area = self.create_content_area(is_dark=self.is_dark_theme)
        main_layout.addWidget(self.content_area)

        # 设置布局比例
        main_layout.setStretch(0, 1)  # 左侧菜单
        main_layout.setStretch(1, 4)  # 右侧内容

        # 默认显示主页
        self.show_home_page()

        # 记录启动日志
        logger.log("Cursor Pro 应用程序已启动", LogLevel.INFO)

    def create_left_menu(self, is_dark=False):
        """创建左侧菜单"""
        left_frame = QFrame()
        left_frame.setFixedWidth(200)  # 设置固定宽度

        # 根据主题设置不同的背景色
        if is_dark:
            left_frame.setStyleSheet("background-color: #333;")
        else:
            left_frame.setStyleSheet("background-color: #f4f4f4;")

        left_frame.setObjectName("leftMenu")

        layout = QVBoxLayout(left_frame)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # 标题
        title_label = QLabel("Cursor Pro")
        title_label.setStyleSheet("color: #41cd52; font-size: 22px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(title_label)

        # 系统类型
        os_label = QLabel("系统类型: macOS")
        os_label.setStyleSheet("color: #666; font-size: 12px;")
        layout.addWidget(os_label)

        # 添加一些间距
        layout.addSpacing(20)

        # 主页按钮
        self.home_btn = QPushButton("  🏠  主页")
        if is_dark:
            self.home_btn.setStyleSheet(
                "QPushButton {"
                "   background-color: transparent;"
                "   color: #f0f0f0;"
                "   text-align: left;"
                "   padding: 12px 15px;"
                "   border-radius: 6px;"
                "   font-size: 14px;"
                "   font-weight: bold;"
                "}"
                "QPushButton:hover {"
                "   background-color: rgba(65, 205, 82, 0.2);"
                "}"
                "QPushButton:pressed {"
                "   background-color: rgba(65, 205, 82, 0.3);"
                "}"
            )
        else:
            self.home_btn.setStyleSheet(
                "QPushButton {"
                "   background-color: transparent;"
                "   color: #333;"
                "   text-align: left;"
                "   padding: 12px 15px;"
                "   border-radius: 6px;"
                "   font-size: 14px;"
                "   font-weight: bold;"
                "}"
                "QPushButton:hover {"
                "   background-color: rgba(65, 205, 82, 0.1);"
                "}"
                "QPushButton:pressed {"
                "   background-color: rgba(65, 205, 82, 0.2);"
                "}"
            )
        self.home_btn.clicked.connect(self.show_home_page)
        layout.addWidget(self.home_btn)

        # 设置按钮
        self.settings_btn = QPushButton("  ⚙️  设置")
        self.settings_btn.setStyleSheet(
            "QPushButton {"
            "   background-color: #41cd52;"
            "   color: white;"
            "   text-align: left;"
            "   padding: 12px 15px;"
            "   border-radius: 6px;"
            "   font-size: 14px;"
            "   font-weight: bold;"
            "}"
            "QPushButton:hover {"
            "   background-color: #3dbd4e;"
            "}"
            "QPushButton:pressed {"
            "   background-color: #38b049;"
            "}"
        )
        self.settings_btn.clicked.connect(self.show_settings_page)
        layout.addWidget(self.settings_btn)

        # 关于按钮
        self.about_btn = QPushButton("  ℹ️  关于")
        if is_dark:
            self.about_btn.setStyleSheet(
                "QPushButton {"
                "   background-color: transparent;"
                "   color: #f0f0f0;"
                "   text-align: left;"
                "   padding: 12px 15px;"
                "   border-radius: 6px;"
                "   font-size: 14px;"
                "   font-weight: bold;"
                "}"
                "QPushButton:hover {"
                "   background-color: rgba(65, 205, 82, 0.2);"
                "}"
                "QPushButton:pressed {"
                "   background-color: rgba(65, 205, 82, 0.3);"
                "}"
            )
        else:
            self.about_btn.setStyleSheet(
                "QPushButton {"
                "   background-color: transparent;"
                "   color: #333;"
                "   text-align: left;"
                "   padding: 12px 15px;"
                "   border-radius: 6px;"
                "   font-size: 14px;"
                "   font-weight: bold;"
                "}"
                "QPushButton:hover {"
                "   background-color: rgba(65, 205, 82, 0.1);"
                "}"
                "QPushButton:pressed {"
                "   background-color: rgba(65, 205, 82, 0.2);"
                "}"
            )
        self.about_btn.clicked.connect(self.show_about_page)
        layout.addWidget(self.about_btn)

        # 添加弹性空间
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(spacer)

        # 主题切换按钮
        if is_dark:
            self.theme_btn = QPushButton("  ☀️  切换到浅色主题")
            self.theme_btn.setStyleSheet(
                "QPushButton {"
                "   background-color: transparent;"
                "   color: #f0f0f0;"
                "   text-align: left;"
                "   padding: 12px 15px;"
                "   border-radius: 6px;"
                "   font-size: 14px;"
                "}"
                "QPushButton:hover {"
                "   background-color: rgba(65, 205, 82, 0.2);"
                "}"
                "QPushButton:pressed {"
                "   background-color: rgba(65, 205, 82, 0.3);"
                "}"
            )
        else:
            self.theme_btn = QPushButton("  🌙  切换到深色主题")
            self.theme_btn.setStyleSheet(
                "QPushButton {"
                "   background-color: transparent;"
                "   color: #333;"
                "   text-align: left;"
                "   padding: 12px 15px;"
                "   border-radius: 6px;"
                "   font-size: 14px;"
                "}"
                "QPushButton:hover {"
                "   background-color: rgba(65, 205, 82, 0.1);"
                "}"
                "QPushButton:pressed {"
                "   background-color: rgba(65, 205, 82, 0.2);"
                "}"
            )
        self.theme_btn.clicked.connect(self.toggle_theme)
        layout.addWidget(self.theme_btn)

        # 底部标签
        footer_label = QLabel("By Ctrler")
        footer_label.setStyleSheet("color: #666; font-size: 12px; margin-top: 10px;")
        footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(footer_label)

        return left_frame

    def create_content_area(self, is_dark=False):
        """创建右侧内容区域"""
        content_frame = QFrame()

        # 根据主题设置不同的背景色
        if is_dark:
            content_frame.setStyleSheet("background-color: #222;")
        else:
            content_frame.setStyleSheet("background-color: white;")

        layout = QVBoxLayout(content_frame)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # 创建堆叠窗口部件用于切换页面
        self.stacked_widget = QStackedWidget()

        # 创建主页
        self.home_page = HomePage()
        # 设置主页主题
        self.home_page.set_theme(is_dark)
        self.stacked_widget.addWidget(self.home_page)

        # 创建设置页
        self.settings_page = SettingsPage()
        # 设置设置页面主题
        self.settings_page.set_theme_state(is_dark)
        # 连接设置页的主题变更信号
        self.settings_page.theme_changed.connect(self.on_theme_changed)
        self.stacked_widget.addWidget(self.settings_page)

        # 创建关于页
        self.about_page = AboutPage()
        # 设置关于页面主题
        self.about_page.set_theme(is_dark)
        self.stacked_widget.addWidget(self.about_page)

        layout.addWidget(self.stacked_widget)

        return content_frame

    def on_theme_changed(self, is_dark):
        """响应主题变更信号"""
        if is_dark:
            self.set_dark_theme()
        else:
            self.set_light_theme()

    def toggle_theme(self):
        """切换主题"""
        if self.is_dark_theme:
            self.set_light_theme()
        else:
            self.set_dark_theme()

    def set_light_theme(self):
        """设置浅色主题"""
        if self.is_dark_theme:
            logger.log("切换到浅色主题", LogLevel.INFO)
            self.is_dark_theme = False

            # 更新设置页面的主题状态
            self.settings_page.set_theme_state(False)

            # 更新关于页面的主题状态
            self.about_page.set_theme(False)

            # 更新主页的主题状态
            self.home_page.set_theme(False)

            # 更新主题切换按钮文本
            self.theme_btn.setText("  🌙  切换到深色主题")

            # 更新左侧菜单样式
            self.left_menu.setStyleSheet("background-color: #f4f4f4;")

            # 更新主题切换按钮样式
            self.theme_btn.setStyleSheet(
                "QPushButton {"
                "   background-color: transparent;"
                "   color: #333;"
                "   text-align: left;"
                "   padding: 12px 15px;"
                "   border-radius: 6px;"
                "   font-size: 14px;"
                "}"
                "QPushButton:hover {"
                "   background-color: rgba(65, 205, 82, 0.1);"
                "}"
                "QPushButton:pressed {"
                "   background-color: rgba(65, 205, 82, 0.2);"
                "}"
            )

            # 更新内容区域样式
            self.content_area.setStyleSheet("background-color: white;")

            # 更新菜单按钮样式
            self.update_menu_button_styles(self.stacked_widget.currentIndex())

            # 保存主题设置到配置文件
            self.save_theme_setting(False)

    def set_dark_theme(self):
        """设置深色主题"""
        if not self.is_dark_theme:
            logger.log("切换到深色主题", LogLevel.INFO)
            self.is_dark_theme = True

            # 更新设置页面的主题状态
            self.settings_page.set_theme_state(True)

            # 更新关于页面的主题状态
            self.about_page.set_theme(True)

            # 更新主页的主题状态
            self.home_page.set_theme(True)

            # 更新主题切换按钮文本
            self.theme_btn.setText("  ☀️  切换到浅色主题")

            # 更新左侧菜单样式
            self.left_menu.setStyleSheet("background-color: #333;")

            # 更新主题切换按钮样式
            self.theme_btn.setStyleSheet(
                "QPushButton {"
                "   background-color: transparent;"
                "   color: #f0f0f0;"
                "   text-align: left;"
                "   padding: 12px 15px;"
                "   border-radius: 6px;"
                "   font-size: 14px;"
                "}"
                "QPushButton:hover {"
                "   background-color: rgba(65, 205, 82, 0.2);"
                "}"
                "QPushButton:pressed {"
                "   background-color: rgba(65, 205, 82, 0.3);"
                "}"
            )

            # 更新内容区域样式
            self.content_area.setStyleSheet("background-color: #222;")

            # 更新菜单按钮样式
            self.update_menu_button_styles(self.stacked_widget.currentIndex())

            # 保存主题设置到配置文件
            self.save_theme_setting(True)

    def save_theme_setting(self, is_dark):
        """保存主题设置到配置文件"""
        config = self.config_manager.get_config()
        config["is_dark_theme"] = is_dark
        self.config_manager.update_config(config)
        logger.log(f"主题设置已保存: {'深色' if is_dark else '浅色'}", LogLevel.INFO)

    def show_home_page(self):
        """显示主页"""
        self.stacked_widget.setCurrentIndex(0)
        # 显示样例日志
        self.home_page.show_sample_logs()
        # 更新按钮样式
        self.update_menu_button_styles(0)

    def show_settings_page(self):
        """显示设置页"""
        self.stacked_widget.setCurrentIndex(1)
        # 更新按钮样式
        self.update_menu_button_styles(1)

    def show_about_page(self):
        """显示关于页"""
        self.stacked_widget.setCurrentIndex(2)
        # 更新按钮样式
        self.update_menu_button_styles(2)

    def update_menu_button_styles(self, active_index):
        """更新菜单按钮样式"""
        # 根据当前主题和活动页面索引设置按钮样式
        if self.is_dark_theme:
            # 深色主题
            inactive_style = (
                "QPushButton {"
                "   background-color: transparent;"
                "   color: #f0f0f0;"
                "   text-align: left;"
                "   padding: 12px 15px;"
                "   border-radius: 6px;"
                "   font-size: 14px;"
                "   font-weight: bold;"
                "}"
                "QPushButton:hover {"
                "   background-color: rgba(65, 205, 82, 0.2);"
                "}"
                "QPushButton:pressed {"
                "   background-color: rgba(65, 205, 82, 0.3);"
                "}"
            )
            active_style = (
                "QPushButton {"
                "   background-color: #41cd52;"
                "   color: white;"
                "   text-align: left;"
                "   padding: 12px 15px;"
                "   border-radius: 6px;"
                "   font-size: 14px;"
                "   font-weight: bold;"
                "}"
                "QPushButton:hover {"
                "   background-color: #3dbd4e;"
                "}"
                "QPushButton:pressed {"
                "   background-color: #38b049;"
                "}"
            )
        else:
            # 浅色主题
            inactive_style = (
                "QPushButton {"
                "   background-color: transparent;"
                "   color: #333;"
                "   text-align: left;"
                "   padding: 12px 15px;"
                "   border-radius: 6px;"
                "   font-size: 14px;"
                "   font-weight: bold;"
                "}"
                "QPushButton:hover {"
                "   background-color: rgba(65, 205, 82, 0.1);"
                "}"
                "QPushButton:pressed {"
                "   background-color: rgba(65, 205, 82, 0.2);"
                "}"
            )
            active_style = (
                "QPushButton {"
                "   background-color: #41cd52;"
                "   color: white;"
                "   text-align: left;"
                "   padding: 12px 15px;"
                "   border-radius: 6px;"
                "   font-size: 14px;"
                "   font-weight: bold;"
                "}"
                "QPushButton:hover {"
                "   background-color: #3dbd4e;"
                "}"
                "QPushButton:pressed {"
                "   background-color: #38b049;"
                "}"
            )

        # 设置按钮样式
        self.home_btn.setStyleSheet(active_style if active_index == 0 else inactive_style)
        self.settings_btn.setStyleSheet(active_style if active_index == 1 else inactive_style)
        self.about_btn.setStyleSheet(active_style if active_index == 2 else inactive_style)
