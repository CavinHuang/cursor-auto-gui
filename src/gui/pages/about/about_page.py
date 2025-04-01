from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                              QLabel, QFrame, QPushButton, QProgressBar)
from PySide6.QtCore import Qt
from src.gui.widgets.icons import IconManager
import platform
import os
from config.config import system_config
from src.utils.update_checker import UpdateChecker

class AboutPage(QWidget):
    """关于页类，显示应用信息、版本和使用说明"""

    def __init__(self, parent=None):
        super().__init__(parent)
        # 默认使用浅色主题
        self.is_dark_theme = False
        # 创建更新检查器
        self.update_checker = UpdateChecker(self)
        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        """设置UI界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)  # 增加区域间距
        layout.setContentsMargins(20, 20, 20, 20)

        # 版本信息
        version_frame = self.create_section_frame("版本信息")
        version_layout = version_frame.layout()

        version_label = QLabel(f"{system_config['app_version']}")
        version_label.setStyleSheet("font-size: 15px; padding: 5px 0; border: none; background-color: transparent;")
        version_layout.addWidget(version_label)

        layout.addWidget(version_frame)

        # 添加更新功能区域
        update_frame = self.create_section_frame("检查更新")
        update_layout = update_frame.layout()

        update_container = QWidget()
        update_container.setStyleSheet("border: none; background-color: transparent;")
        update_container_layout = QVBoxLayout(update_container)
        update_container_layout.setContentsMargins(0, 0, 0, 0)

        # 更新状态标签
        self.update_status = QLabel("点击按钮检查更新")
        self.update_status.setStyleSheet("font-size: 13px; color: #555; border: none; background-color: transparent;")
        update_container_layout.addWidget(self.update_status)

        # 更新进度条（默认隐藏）
        self.update_progress = QProgressBar()
        self.update_progress.setRange(0, 100)
        self.update_progress.setValue(0)
        self.update_progress.setVisible(False)
        update_container_layout.addWidget(self.update_progress)

        # 检查更新按钮
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 10, 0, 0)

        self.check_update_btn = QPushButton("检查更新")
        self.check_update_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 15px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #888888;
            }
        """)
        button_layout.addWidget(self.check_update_btn)

        # 下载更新按钮（默认隐藏）
        self.download_update_btn = QPushButton("下载更新")
        self.download_update_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 15px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
            QPushButton:pressed {
                background-color: #0a69b7;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #888888;
            }
        """)
        self.download_update_btn.setVisible(False)
        button_layout.addWidget(self.download_update_btn)

        button_layout.addStretch()
        update_container_layout.addWidget(button_container)

        update_layout.addWidget(update_container)
        layout.addWidget(update_frame)

        # 微信公众号
        wechat_frame = self.create_section_frame("微信公众号")
        wechat_layout = wechat_frame.layout()

        # 创建水平布局来放置名称和二维码
        wechat_container = QWidget()
        wechat_container_layout = QHBoxLayout(wechat_container)
        wechat_container_layout.setContentsMargins(0, 0, 0, 0)

        # 公众号名称
        wechat_label = QLabel(system_config["mp_wechat_name"])
        wechat_label.setStyleSheet("font-size: 15px; color: #4CAF50; padding: 5px 0; border: none; background-color: transparent;")
        wechat_container_layout.addWidget(wechat_label)

        # 二维码图片
        qrcode_label = QLabel()
        qrcode_label.setFixedSize(100, 100)
        qrcode_label.setStyleSheet("border: 1px solid #ddd; border-radius: 4px;")

        # 使用get_pixmap替代get_icon，因为这是一个图片而不是图标
        qrcode_pixmap = IconManager.get_pixmap(system_config["mp_wechat_qrcode"])
        qrcode_label.setPixmap(qrcode_pixmap.scaled(
            100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
        ))
        wechat_container_layout.addWidget(qrcode_label)

        wechat_layout.addWidget(wechat_container)
        layout.addWidget(wechat_frame)

        # 使用说明
        usage_frame = self.create_section_frame("使用说明")
        usage_layout = usage_frame.layout()

        # 运行环境
        env_container = QWidget()
        env_container.setStyleSheet("border: none; background-color: transparent;")
        env_container_layout = QVBoxLayout(env_container)
        env_container_layout.setContentsMargins(0, 0, 0, 0)

        env_title = QLabel("运行环境")
        env_title.setStyleSheet("font-size: 14px; font-weight: bold; border: none; background-color: transparent;")
        env_container_layout.addWidget(env_title)

        env_desc = QLabel("运行环境需要 Chrome 浏览器")
        env_desc.setStyleSheet("font-size: 13px; color: #555; border: none; background-color: transparent;")
        env_container_layout.addWidget(env_desc)

        usage_layout.addWidget(env_container)

        # 分隔线
        self.add_separator(usage_layout)

        # 启动说明
        startup_container = QWidget()
        startup_container.setStyleSheet("border: none; background-color: transparent;")
        startup_container_layout = QVBoxLayout(startup_container)
        startup_container_layout.setContentsMargins(0, 0, 0, 0)

        startup_title = QLabel("启动说明")
        startup_title.setStyleSheet("font-size: 14px; font-weight: bold; border: none; background-color: transparent;")
        startup_container_layout.addWidget(startup_title)

        startup_desc = QLabel("启动时将自动关闭已运行的 Cursor")
        startup_desc.setStyleSheet("font-size: 13px; color: #555; border: none; background-color: transparent;")
        startup_container_layout.addWidget(startup_desc)

        usage_layout.addWidget(startup_container)

        # 分隔线
        self.add_separator(usage_layout)

        # 域名配置
        domain_container = QWidget()
        domain_container.setStyleSheet("border: none; background-color: transparent;")
        domain_container_layout = QVBoxLayout(domain_container)
        domain_container_layout.setContentsMargins(0, 0, 0, 0)

        domain_title = QLabel("域名配置")
        domain_title.setStyleSheet("font-size: 14px; font-weight: bold; border: none; background-color: transparent;")
        domain_container_layout.addWidget(domain_title)

        domain_desc = QLabel("如遇域名失效，请前往公众号获取最新配置或自行设置")
        domain_desc.setWordWrap(True)
        domain_desc.setStyleSheet("font-size: 13px; color: #555; border: none; background-color: transparent;")
        domain_container_layout.addWidget(domain_desc)

        usage_layout.addWidget(domain_container)

        layout.addWidget(usage_frame)

        # 配置文件路径
        config_frame = self.create_section_frame("配置文件路径")
        config_layout = config_frame.layout()

        # 平台和路径容器
        config_container = QWidget()
        config_container.setStyleSheet("border: none; background-color: transparent;")
        config_container_layout = QVBoxLayout(config_container)
        config_container_layout.setContentsMargins(0, 0, 0, 0)

        # 当前平台
        platform_name = "macOS" if platform.system() == "Darwin" else platform.system()
        platform_label = QLabel(f"当前平台：{platform_name}")
        platform_label.setStyleSheet("font-size: 13px; margin-top: 5px; border: none; background-color: transparent;")
        config_container_layout.addWidget(platform_label)

        # 配置文件路径
        home = os.path.expanduser("~")
        config_path = f"{home}/{system_config['app_config_path']}"
        config_path_label = QLabel(config_path)
        config_path_label.setStyleSheet("font-size: 13px; color: #4CAF50; border: none; background-color: transparent;")
        config_container_layout.addWidget(config_path_label)

        config_layout.addWidget(config_container)

        layout.addWidget(config_frame)

        # 添加空白区域
        layout.addStretch()

        # 保存UI元素的引用，以便在切换主题时更新样式
        self.frames = [version_frame, update_frame, wechat_frame, usage_frame, config_frame]
        self.containers = [update_container, env_container, startup_container, domain_container, config_container]
        self.titles = [env_title, startup_title, domain_title]
        self.descriptions = [self.update_status, env_desc, startup_desc, domain_desc, platform_label]
        self.special_labels = [version_label, wechat_label, config_path_label]
        self.buttons = [self.check_update_btn, self.download_update_btn]

    def connect_signals(self):
        """连接信号与槽"""
        # 连接检查更新按钮
        self.check_update_btn.clicked.connect(self.on_check_update)

        # 连接下载更新按钮
        self.download_update_btn.clicked.connect(self.on_download_update)

        # 连接更新检查器的信号
        self.update_checker.update_available.connect(self.on_update_available)
        self.update_checker.update_not_available.connect(self.on_update_not_available)
        self.update_checker.update_error.connect(self.on_update_error)
        self.update_checker.download_progress.connect(self.on_download_progress)
        self.update_checker.download_complete.connect(self.on_download_complete)
        self.update_checker.download_error.connect(self.on_download_error)

    def on_check_update(self):
        """检查更新按钮点击处理"""
        self.update_status.setText("正在检查更新...")
        self.check_update_btn.setEnabled(False)
        self.download_update_btn.setVisible(False)
        self.update_progress.setVisible(False)
        # 调用更新检查器检查更新
        self.update_checker.check_for_updates()

    def on_update_available(self, version, download_url):
        """有可用更新时的处理"""
        self.update_status.setText(f"发现新版本: v{version}")
        self.check_update_btn.setEnabled(True)
        self.download_update_btn.setVisible(True)
        # 保存下载URL
        self.download_url = download_url

    def on_update_not_available(self):
        """没有可用更新时的处理"""
        self.update_status.setText(f"当前已是最新版本 (v{system_config['app_version']})")
        self.check_update_btn.setEnabled(True)

    def on_update_error(self, error_msg):
        """更新检查出错时的处理"""
        self.update_status.setText(f"检查更新失败: {error_msg}")
        self.check_update_btn.setEnabled(True)

    def on_download_update(self):
        """下载更新按钮点击处理"""
        self.update_status.setText("正在下载更新...")
        self.check_update_btn.setEnabled(False)
        self.download_update_btn.setEnabled(False)
        self.update_progress.setValue(0)
        self.update_progress.setVisible(True)
        # 调用更新检查器下载更新
        self.update_checker.download_update(self.download_url)

    def on_download_progress(self, progress):
        """下载进度更新处理"""
        self.update_progress.setValue(progress)

    def on_download_complete(self, file_path):
        """下载完成处理"""
        from src.utils.update_checker import install_update

        self.update_status.setText("下载完成，正在安装...")
        self.update_progress.setVisible(False)

        # 调用安装更新函数
        if install_update(file_path):
            self.update_status.setText("更新已准备就绪，即将重启应用...")
        else:
            self.update_status.setText("安装更新失败，请手动安装")
            self.check_update_btn.setEnabled(True)
            self.download_update_btn.setEnabled(True)

    def on_download_error(self, error_msg):
        """下载出错处理"""
        self.update_status.setText(f"下载更新失败: {error_msg}")
        self.update_progress.setVisible(False)
        self.check_update_btn.setEnabled(True)
        self.download_update_btn.setEnabled(True)

    def create_section_frame(self, title):
        """创建带标题的区域框架"""
        frame = QFrame()
        frame.setStyleSheet("border: 1px solid #ddd; border-radius: 4px; background-color: transparent;")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(8)

        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 15px; font-weight: bold; border: none; background-color: transparent;")
        layout.addWidget(title_label)

        return frame

    def add_separator(self, layout):
        """添加分隔线"""
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("background-color: #e5e5e5; margin: 8px 0; border: none;")
        layout.addWidget(separator)

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

            # 更新框架样式
            for frame in self.frames:
                frame.setStyleSheet("border: 1px solid #444; border-radius: 4px; background-color: transparent;")

            # 更新容器样式
            for container in self.containers:
                container.setStyleSheet("border: none; background-color: transparent;")

            # 更新标题样式
            for title in self.titles:
                title.setStyleSheet("font-size: 14px; font-weight: bold; color: #f0f0f0; border: none; background-color: transparent;")

            # 更新描述文本样式
            for desc in self.descriptions:
                desc.setStyleSheet("font-size: 13px; color: #aaa; border: none; background-color: transparent;")

            # 更新特殊标签样式
            self.special_labels[0].setStyleSheet("font-size: 15px; color: #f0f0f0; padding: 5px 0; border: none; background-color: transparent;")  # version_label
            self.special_labels[1].setStyleSheet("font-size: 15px; color: #4CAF50; padding: 5px 0; border: none; background-color: transparent;")  # wechat_label
            self.special_labels[2].setStyleSheet("font-size: 13px; color: #4CAF50; border: none; background-color: transparent;")  # config_path_label

            # 更新分隔线样式
            for separator in self.findChildren(QFrame):
                if separator.frameShape() == QFrame.Shape.HLine:
                    separator.setStyleSheet("background-color: #444; margin: 8px 0; border: none;")

            # 更新所有标题标签
            for frame in self.frames:
                title_label = frame.layout().itemAt(0).widget()
                if isinstance(title_label, QLabel):
                    title_label.setStyleSheet("font-size: 15px; font-weight: bold; color: #f0f0f0; border: none; background-color: transparent;")

            # 更新按钮样式
            self.check_update_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 5px 15px;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
                QPushButton:pressed {
                    background-color: #3d8b40;
                }
                QPushButton:disabled {
                    background-color: #555555;
                    color: #999999;
                }
            """)

            self.download_update_btn.setStyleSheet("""
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 5px 15px;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background-color: #0b7dda;
                }
                QPushButton:pressed {
                    background-color: #0a69b7;
                }
                QPushButton:disabled {
                    background-color: #555555;
                    color: #999999;
                }
            """)

            # 更新进度条样式
            self.update_progress.setStyleSheet("""
                QProgressBar {
                    border: 1px solid #444;
                    border-radius: 3px;
                    background-color: #333;
                    color: #f0f0f0;
                    text-align: center;
                }
                QProgressBar::chunk {
                    background-color: #4CAF50;
                    border-radius: 2px;
                }
            """)

        else:
            # 浅色主题样式
            self.setStyleSheet("background-color: white;")

            # 更新框架样式
            for frame in self.frames:
                frame.setStyleSheet("border: 1px solid #ddd; border-radius: 4px; background-color: transparent;")

            # 更新容器样式
            for container in self.containers:
                container.setStyleSheet("border: none; background-color: transparent;")

            # 更新标题样式
            for title in self.titles:
                title.setStyleSheet("font-size: 14px; font-weight: bold; border: none; background-color: transparent;")

            # 更新描述文本样式
            for desc in self.descriptions:
                desc.setStyleSheet("font-size: 13px; color: #555; border: none; background-color: transparent;")

            # 更新特殊标签样式
            self.special_labels[0].setStyleSheet("font-size: 15px; padding: 5px 0; border: none; background-color: transparent;")  # version_label
            self.special_labels[1].setStyleSheet("font-size: 15px; color: #4CAF50; padding: 5px 0; border: none; background-color: transparent;")  # wechat_label
            self.special_labels[2].setStyleSheet("font-size: 13px; color: #4CAF50; border: none; background-color: transparent;")  # config_path_label

            # 更新分隔线样式
            for separator in self.findChildren(QFrame):
                if separator.frameShape() == QFrame.Shape.HLine:
                    separator.setStyleSheet("background-color: #e5e5e5; margin: 8px 0; border: none;")

            # 更新所有标题标签
            for frame in self.frames:
                title_label = frame.layout().itemAt(0).widget()
                if isinstance(title_label, QLabel):
                    title_label.setStyleSheet("font-size: 15px; font-weight: bold; color: #333; border: none; background-color: transparent;")

            # 更新按钮样式（恢复默认样式）
            self.check_update_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 5px 15px;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
                QPushButton:pressed {
                    background-color: #3d8b40;
                }
                QPushButton:disabled {
                    background-color: #cccccc;
                    color: #888888;
                }
            """)

            self.download_update_btn.setStyleSheet("""
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 5px 15px;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background-color: #0b7dda;
                }
                QPushButton:pressed {
                    background-color: #0a69b7;
                }
                QPushButton:disabled {
                    background-color: #cccccc;
                    color: #888888;
                }
            """)

            # 更新进度条样式
            self.update_progress.setStyleSheet("""
                QProgressBar {
                    border: 1px solid #ddd;
                    border-radius: 3px;
                    background-color: #f5f5f5;
                    color: #333;
                    text-align: center;
                }
                QProgressBar::chunk {
                    background-color: #4CAF50;
                    border-radius: 2px;
                }
            """)