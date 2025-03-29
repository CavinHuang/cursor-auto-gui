from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize
import os

class IconManager:
    """图标管理类，用于加载和管理应用程序中使用的图标"""

    @staticmethod
    def get_icon_path(icon_name):
        """获取图标文件的路径"""
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        icons_dir = os.path.join(base_dir, 'resources', 'icons')
        icon_path = os.path.join(icons_dir, icon_name)
        return icon_path if os.path.exists(icon_path) else None

    @staticmethod
    def get_app_icon():
        """获取应用程序图标"""
        icon_path = IconManager.get_icon_path('icon.png')
        return QIcon(icon_path) if icon_path else QIcon()

    @staticmethod
    def get_home_icon():
        """获取主页图标"""
        return QIcon.fromTheme("go-home")

    @staticmethod
    def get_settings_icon():
        """获取设置图标"""
        return QIcon.fromTheme("preferences-system")

    @staticmethod
    def get_about_icon():
        """获取关于图标"""
        return QIcon.fromTheme("help-about")

    @staticmethod
    def get_theme_icon():
        """获取主题图标"""
        return QIcon.fromTheme("preferences-desktop-theme")