from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import QSize
import os
from config.config import project_root
class IconManager:
    """图标管理类，用于加载和管理应用程序中使用的图标"""

    _icon_cache = {}  # 用于缓存已加载的图标
    _base_path = os.path.join(project_root, "resources")

    @classmethod
    def get_icon(cls, icon_path):
        """
        获取图标
        :param icon_path: 图标路径（相对于resources目录）
        :return: QIcon对象
        """
        if icon_path in cls._icon_cache:
            return cls._icon_cache[icon_path]

        full_path = os.path.join(cls._base_path, icon_path)
        if not os.path.exists(full_path):
            print(f"警告: 图标文件不存在 {full_path}")
            return QIcon()

        icon = QIcon(full_path)
        cls._icon_cache[icon_path] = icon
        return icon

    @classmethod
    def get_pixmap(cls, icon_path):
        """
        获取图片
        :param icon_path: 图片路径（相对于resources目录）
        :return: QPixmap对象
        """
        full_path = os.path.join(cls._base_path, icon_path)
        if not os.path.exists(full_path):
            print(f"警告: 图片文件不存在 {full_path}")
            return QPixmap()
        print(f"获取图片: {full_path}")
        return QPixmap(full_path)

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