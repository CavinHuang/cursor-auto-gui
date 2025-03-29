from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                              QLabel, QTextEdit, QFrame)
from PySide6.QtCore import Qt, QSize
from src.gui.widgets.icons import IconManager

class AboutPage(QWidget):
    """关于页类，显示应用信息、版本和开发者信息"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setup_ui()

    def setup_ui(self):
        """设置UI界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        about_label = QLabel("关于")
        about_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(about_label)

        # 应用信息区域
        app_frame = QFrame()
        app_frame.setStyleSheet("border: 1px solid #ddd; border-radius: 4px; padding: 20px;")
        app_layout = QVBoxLayout(app_frame)

        # 应用名称和版本
        title_layout = QHBoxLayout()

        # 应用图标
        icon_label = QLabel()
        icon_pixmap = IconManager.get_app_icon().pixmap(QSize(64, 64))
        icon_label.setPixmap(icon_pixmap)
        title_layout.addWidget(icon_label)

        title_info_layout = QVBoxLayout()
        app_name_label = QLabel("Cursor Pro")
        app_name_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        title_info_layout.addWidget(app_name_label)

        version_label = QLabel("版本：v3.0.0")
        version_label.setStyleSheet("font-size: 14px; color: #666;")
        title_info_layout.addWidget(version_label)

        title_layout.addLayout(title_info_layout)
        title_layout.addStretch()

        app_layout.addLayout(title_layout)

        # 分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("background-color: #ddd; margin: 10px 0;")
        app_layout.addWidget(separator)

        # 应用描述
        desc_label = QLabel("Cursor Pro 是一个自动化工具，用于管理和操作 Cursor IDE 的机器码和账号。")
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("font-size: 14px; line-height: 1.4;")
        app_layout.addWidget(desc_label)

        # 应用特性
        features_label = QLabel("主要功能：")
        features_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-top: 10px;")
        app_layout.addWidget(features_label)

        features_list = QTextEdit()
        features_list.setReadOnly(True)
        features_list.setStyleSheet("border: none; background-color: transparent; font-size: 14px;")
        features_list.setMaximumHeight(100)
        features_list.setText("• 重置机器码，自动生成新的随机机器ID\n• 完整的注册流程，自动创建新账号\n• 简洁直观的用户界面\n• 详细的操作日志")
        app_layout.addWidget(features_list)

        layout.addWidget(app_frame)

        # 开发者信息区域
        dev_frame = QFrame()
        dev_frame.setStyleSheet("border: 1px solid #ddd; border-radius: 4px; padding: 20px;")
        dev_layout = QVBoxLayout(dev_frame)

        dev_title = QLabel("开发者信息")
        dev_title.setStyleSheet("font-size: 14px; font-weight: bold;")
        dev_layout.addWidget(dev_title)

        dev_name = QLabel("开发者：Ctrler")
        dev_name.setStyleSheet("font-size: 14px; margin-top: 5px;")
        dev_layout.addWidget(dev_name)

        github_link = QLabel('<a href="https://github.com/ctrler">GitHub: https://github.com/ctrler</a>')
        github_link.setOpenExternalLinks(True)
        github_link.setStyleSheet("font-size: 14px; margin-top: 5px;")
        dev_layout.addWidget(github_link)

        layout.addWidget(dev_frame)

        # 版权信息
        copyright_label = QLabel("© 2024 Ctrler. 保留所有权利。")
        copyright_label.setStyleSheet("font-size: 12px; color: #999; margin-top: 20px;")
        copyright_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(copyright_label)

        layout.addStretch()