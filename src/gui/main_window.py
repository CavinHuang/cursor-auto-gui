from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout,
                                QHBoxLayout, QPushButton, QLabel, QTextEdit,
                                QFrame, QStackedWidget, QScrollArea, QSizePolicy)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QFont
from .widgets.icons import IconManager
from src.logic.log.log_manager import logger, LogLevel
# 导入页面模块
from .pages.home import HomePage
from .pages.settings import SettingsPage
from .pages.about import AboutPage

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 主题状态
        self.is_dark_theme = False

        # 设置窗口标题和大小
        self.setWindowTitle("Cursor Pro")
        self.resize(800, 600)

        # 设置应用程序图标
        self.setWindowIcon(IconManager.get_app_icon())

        # 创建中央窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 创建左侧菜单
        self.left_menu = self.create_left_menu()
        main_layout.addWidget(self.left_menu)

        # 创建右侧内容区域
        self.content_area = self.create_content_area()
        main_layout.addWidget(self.content_area)

        # 设置布局比例
        main_layout.setStretch(0, 1)  # 左侧菜单
        main_layout.setStretch(1, 4)  # 右侧内容

        # 默认显示主页
        self.show_home_page()

        # 记录启动日志
        logger.log("Cursor Pro 应用程序已启动", LogLevel.INFO)

    def create_left_menu(self):
        """创建左侧菜单"""
        left_frame = QFrame()
        left_frame.setStyleSheet("background-color: #f4f4f4;")
        left_frame.setObjectName("leftMenu")

        layout = QVBoxLayout(left_frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # 标题
        title_label = QLabel("Cursor Pro")
        title_label.setStyleSheet("color: #41cd52; font-size: 20px; font-weight: bold; padding: 20px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(title_label)

        # 系统类型
        os_label = QLabel("系统类型: macOS")
        os_label.setStyleSheet("color: #666; font-size: 12px; padding-left: 20px; padding-bottom: 20px;")
        layout.addWidget(os_label)

        # 主页按钮
        self.home_btn = QPushButton("  主页")
        self.home_btn.setIcon(IconManager.get_home_icon())
        self.home_btn.setIconSize(QSize(16, 16))
        self.home_btn.setStyleSheet(
            "QPushButton {"
            "   background-color: transparent;"
            "   color: #333;"
            "   text-align: left;"
            "   padding: 10px 20px;"
            "   border: none;"
            "   font-size: 14px;"
            "}"
            "QPushButton:hover {"
            "   background-color: #e0e0e0;"
            "}"
            "QPushButton:pressed {"
            "   background-color: #d0d0d0;"
            "}"
        )
        self.home_btn.clicked.connect(self.show_home_page)
        layout.addWidget(self.home_btn)

        # 设置按钮
        self.settings_btn = QPushButton("  设置")
        self.settings_btn.setIcon(IconManager.get_settings_icon())
        self.settings_btn.setIconSize(QSize(16, 16))
        self.settings_btn.setStyleSheet(
            "QPushButton {"
            "   background-color: transparent;"
            "   color: #333;"
            "   text-align: left;"
            "   padding: 10px 20px;"
            "   border: none;"
            "   font-size: 14px;"
            "}"
            "QPushButton:hover {"
            "   background-color: #e0e0e0;"
            "}"
            "QPushButton:pressed {"
            "   background-color: #d0d0d0;"
            "}"
        )
        self.settings_btn.clicked.connect(self.show_settings_page)
        layout.addWidget(self.settings_btn)

        # 关于按钮
        self.about_btn = QPushButton("  关于")
        self.about_btn.setIcon(IconManager.get_about_icon())
        self.about_btn.setIconSize(QSize(16, 16))
        self.about_btn.setStyleSheet(
            "QPushButton {"
            "   background-color: transparent;"
            "   color: #333;"
            "   text-align: left;"
            "   padding: 10px 20px;"
            "   border: none;"
            "   font-size: 14px;"
            "}"
            "QPushButton:hover {"
            "   background-color: #e0e0e0;"
            "}"
            "QPushButton:pressed {"
            "   background-color: #d0d0d0;"
            "}"
        )
        self.about_btn.clicked.connect(self.show_about_page)
        layout.addWidget(self.about_btn)

        # 添加弹性空间
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(spacer)

        # 主题切换按钮
        self.theme_btn = QPushButton("  切换到深色主题")
        self.theme_btn.setIcon(IconManager.get_theme_icon())
        self.theme_btn.setIconSize(QSize(16, 16))
        self.theme_btn.setStyleSheet(
            "QPushButton {"
            "   background-color: transparent;"
            "   color: #333;"
            "   text-align: left;"
            "   padding: 10px 20px;"
            "   border: none;"
            "   font-size: 14px;"
            "}"
            "QPushButton:hover {"
            "   background-color: #e0e0e0;"
            "}"
            "QPushButton:pressed {"
            "   background-color: #d0d0d0;"
            "}"
        )
        self.theme_btn.clicked.connect(self.toggle_theme)
        layout.addWidget(self.theme_btn)

        # 底部标签
        footer_label = QLabel("By Ctrler")
        footer_label.setStyleSheet("color: #666; font-size: 12px; padding: 10px 20px;")
        footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(footer_label)

        return left_frame

    def create_content_area(self):
        """创建右侧内容区域"""
        content_frame = QFrame()
        content_frame.setStyleSheet("background-color: white;")

        layout = QVBoxLayout(content_frame)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # 创建堆叠窗口部件用于切换页面
        self.stacked_widget = QStackedWidget()

        # 创建主页
        self.home_page = HomePage()
        self.stacked_widget.addWidget(self.home_page)

        # 创建设置页
        self.settings_page = SettingsPage()
        # 连接设置页的主题变更信号
        self.settings_page.theme_changed.connect(self.on_theme_changed)
        self.stacked_widget.addWidget(self.settings_page)

        # 创建关于页
        self.about_page = AboutPage()
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

            # 更新主题切换按钮文本
            self.theme_btn.setText("  切换到深色主题")

            # 更新左侧菜单样式
            self.left_menu.setStyleSheet("background-color: #f4f4f4;")

            # 更新主页按钮样式
            self.home_btn.setStyleSheet(
                "QPushButton {"
                "   background-color: " + ("#e0e0e0" if self.stacked_widget.currentIndex() == 0 else "transparent") + ";"
                "   color: #333;"
                "   text-align: left;"
                "   padding: 10px 20px;"
                "   border: none;"
                "   font-size: 14px;"
                "}"
                "QPushButton:hover {"
                "   background-color: #e0e0e0;"
                "}"
                "QPushButton:pressed {"
                "   background-color: #d0d0d0;"
                "}"
            )

            # 更新设置按钮样式
            self.settings_btn.setStyleSheet(
                "QPushButton {"
                "   background-color: " + ("#e0e0e0" if self.stacked_widget.currentIndex() == 1 else "transparent") + ";"
                "   color: #333;"
                "   text-align: left;"
                "   padding: 10px 20px;"
                "   border: none;"
                "   font-size: 14px;"
                "}"
                "QPushButton:hover {"
                "   background-color: #e0e0e0;"
                "}"
                "QPushButton:pressed {"
                "   background-color: #d0d0d0;"
                "}"
            )

            # 更新关于按钮样式
            self.about_btn.setStyleSheet(
                "QPushButton {"
                "   background-color: " + ("#e0e0e0" if self.stacked_widget.currentIndex() == 2 else "transparent") + ";"
                "   color: #333;"
                "   text-align: left;"
                "   padding: 10px 20px;"
                "   border: none;"
                "   font-size: 14px;"
                "}"
                "QPushButton:hover {"
                "   background-color: #e0e0e0;"
                "}"
                "QPushButton:pressed {"
                "   background-color: #d0d0d0;"
                "}"
            )

            # 更新主题切换按钮样式
            self.theme_btn.setStyleSheet(
                "QPushButton {"
                "   background-color: transparent;"
                "   color: #333;"
                "   text-align: left;"
                "   padding: 10px 20px;"
                "   border: none;"
                "   font-size: 14px;"
                "}"
                "QPushButton:hover {"
                "   background-color: #e0e0e0;"
                "}"
                "QPushButton:pressed {"
                "   background-color: #d0d0d0;"
                "}"
            )

            # 更新内容区域样式
            self.content_area.setStyleSheet("background-color: white;")

    def set_dark_theme(self):
        """设置深色主题"""
        if not self.is_dark_theme:
            logger.log("切换到深色主题", LogLevel.INFO)
            self.is_dark_theme = True

            # 更新设置页面的主题状态
            self.settings_page.set_theme_state(True)

            # 更新主题切换按钮文本
            self.theme_btn.setText("  切换到浅色主题")

            # 更新左侧菜单样式
            self.left_menu.setStyleSheet("background-color: #333;")

            # 更新主页按钮样式
            self.home_btn.setStyleSheet(
                "QPushButton {"
                "   background-color: " + ("#444" if self.stacked_widget.currentIndex() == 0 else "transparent") + ";"
                "   color: #f0f0f0;"
                "   text-align: left;"
                "   padding: 10px 20px;"
                "   border: none;"
                "   font-size: 14px;"
                "}"
                "QPushButton:hover {"
                "   background-color: #444;"
                "}"
                "QPushButton:pressed {"
                "   background-color: #555;"
                "}"
            )

            # 更新设置按钮样式
            self.settings_btn.setStyleSheet(
                "QPushButton {"
                "   background-color: " + ("#444" if self.stacked_widget.currentIndex() == 1 else "transparent") + ";"
                "   color: #f0f0f0;"
                "   text-align: left;"
                "   padding: 10px 20px;"
                "   border: none;"
                "   font-size: 14px;"
                "}"
                "QPushButton:hover {"
                "   background-color: #444;"
                "}"
                "QPushButton:pressed {"
                "   background-color: #555;"
                "}"
            )

            # 更新关于按钮样式
            self.about_btn.setStyleSheet(
                "QPushButton {"
                "   background-color: " + ("#444" if self.stacked_widget.currentIndex() == 2 else "transparent") + ";"
                "   color: #f0f0f0;"
                "   text-align: left;"
                "   padding: 10px 20px;"
                "   border: none;"
                "   font-size: 14px;"
                "}"
                "QPushButton:hover {"
                "   background-color: #444;"
                "}"
                "QPushButton:pressed {"
                "   background-color: #555;"
                "}"
            )

            # 更新主题切换按钮样式
            self.theme_btn.setStyleSheet(
                "QPushButton {"
                "   background-color: transparent;"
                "   color: #f0f0f0;"
                "   text-align: left;"
                "   padding: 10px 20px;"
                "   border: none;"
                "   font-size: 14px;"
                "}"
                "QPushButton:hover {"
                "   background-color: #444;"
                "}"
                "QPushButton:pressed {"
                "   background-color: #555;"
                "}"
            )

            # 更新内容区域样式
            self.content_area.setStyleSheet("background-color: #222;")

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
        active_bg = "#444" if self.is_dark_theme else "#e0e0e0"
        normal_bg = "transparent"
        text_color = "#f0f0f0" if self.is_dark_theme else "#333"
        hover_bg = "#444" if self.is_dark_theme else "#e0e0e0"
        pressed_bg = "#555" if self.is_dark_theme else "#d0d0d0"

        # 主页按钮
        self.home_btn.setStyleSheet(
            "QPushButton {"
            f"   background-color: {active_bg if active_index == 0 else normal_bg};"
            f"   color: {text_color};"
            "   text-align: left;"
            "   padding: 10px 20px;"
            "   border: none;"
            "   font-size: 14px;"
            "}"
            "QPushButton:hover {"
            f"   background-color: {hover_bg};"
            "}"
            "QPushButton:pressed {"
            f"   background-color: {pressed_bg};"
            "}"
        )

        # 设置按钮
        self.settings_btn.setStyleSheet(
            "QPushButton {"
            f"   background-color: {active_bg if active_index == 1 else normal_bg};"
            f"   color: {text_color};"
            "   text-align: left;"
            "   padding: 10px 20px;"
            "   border: none;"
            "   font-size: 14px;"
            "}"
            "QPushButton:hover {"
            f"   background-color: {hover_bg};"
            "}"
            "QPushButton:pressed {"
            f"   background-color: {pressed_bg};"
            "}"
        )

        # 关于按钮
        self.about_btn.setStyleSheet(
            "QPushButton {"
            f"   background-color: {active_bg if active_index == 2 else normal_bg};"
            f"   color: {text_color};"
            "   text-align: left;"
            "   padding: 10px 20px;"
            "   border: none;"
            "   font-size: 14px;"
            "}"
            "QPushButton:hover {"
            f"   background-color: {hover_bg};"
            "}"
            "QPushButton:pressed {"
            f"   background-color: {pressed_bg};"
            "}"
        )
