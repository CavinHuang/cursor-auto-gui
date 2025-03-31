from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                              QLabel, QTextEdit, QFrame)
from PySide6.QtCore import Qt, QSize
from src.gui.widgets.icons import IconManager
import platform
import os
from config.config import system_config
class AboutPage(QWidget):
    """关于页类，显示应用信息、版本和使用说明"""

    def __init__(self, parent=None):
        super().__init__(parent)
        # 默认使用浅色主题
        self.is_dark_theme = False
        self.setup_ui()

    def setup_ui(self):
        """设置UI界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)  # 增加区域间距
        layout.setContentsMargins(20, 20, 20, 20)

        # 版本信息
        version_frame = self.create_section_frame("版本信息")
        version_layout = version_frame.layout()

        version_label = QLabel(f"v{system_config['app_version']}")
        version_label.setStyleSheet("font-size: 15px; padding: 5px 0; border: none; background-color: transparent;")
        version_layout.addWidget(version_label)

        layout.addWidget(version_frame)

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
        self.frames = [version_frame, wechat_frame, usage_frame, config_frame]
        self.containers = [env_container, startup_container, domain_container, config_container]
        self.titles = [env_title, startup_title, domain_title]
        self.descriptions = [env_desc, startup_desc, domain_desc, platform_label]
        self.special_labels = [version_label, wechat_label, config_path_label]

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