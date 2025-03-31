
# 判断是否为打包环境
import os
import platform
import sys
from config.config import system_config

def is_frozen():
    """判断当前是否在打包环境中运行"""
    return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')

def get_user_home_path():
    """获取用户主目录路径"""
    return os.path.expanduser("~")

def get_app_config_path():
    """获取应用配置文件路径"""
    config_path = os.path.join(os.path.dirname(__file__), "..", "datas", "config.json")
    if is_frozen():
        config_path =  os.path.join(get_user_home_path(), system_config["app_config_path"], 'datas', "config.json")
    return config_path

def get_app_info():
    """获取应用版本号"""
    with open("version", "r") as f:
        content = f.read().strip()
    return content.split("\n")

def get_platform_info():
    """获取平台信息"""
    return {
        "platform": platform.system(),
        "platform_version": platform.version(),
    }

