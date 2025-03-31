#!/usr/bin/env python
"""
Cursor Pro 启动器
在主程序启动前显示管理员权限验证对话框
"""
import sys
import os
import platform
import subprocess
import tempfile
import json
import hashlib
import logging
import datetime
import traceback
from pathlib import Path
from PySide6.QtWidgets import QApplication, QDialog, QLineEdit, QPushButton, QVBoxLayout, QLabel, QHBoxLayout, QMessageBox
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon, QPixmap

# 全局变量和常量
APP_NAME = "Cursor Pro"
LOG_DIR = os.path.join(os.path.expanduser("~"), ".cursor_pro", "logs")
IS_FROZEN = getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')

# 环境变量键名
ENV_SKIP_ADMIN_CHECK = "CURSOR_PRO_SKIP_ADMIN"  # 跳过管理员权限检查的环境变量
ENV_RESTARTED_AS_ADMIN = "CURSOR_PRO_RESTARTED" # 以管理员权限重启的环境变量
ENV_LOG_FILE = "CURSOR_PRO_LOG_FILE"            # 日志文件路径的环境变量

# 导入日志管理器
try:
    # 尝试导入日志管理器
    from src.logic.log.log_manager import logger, LogLevel
    _has_log_manager = True
except ImportError:
    _has_log_manager = False
    # 如果导入失败，将继续使用基本日志设置

# 设置日志记录
def setup_logging():
    """设置日志记录"""
    os.makedirs(LOG_DIR, exist_ok=True)
    log_file = os.path.join(LOG_DIR, f"cursor_pro_launcher_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

    if _has_log_manager:
        # 使用LogManager设置文件日志
        log_file = logger.set_file_logger(LOG_DIR, log_file=None)
        logger.info("===== Cursor Pro 启动器日志开始 =====")
        logger.info(f"操作系统: {platform.system()} {platform.version()}")
        logger.info(f"Python版本: {sys.version}")
        logger.info(f"工作目录: {os.getcwd()}")
        logger.info(f"启动参数: {sys.argv}")
        logger.info(f"是否为打包环境: {IS_FROZEN}")
        if IS_FROZEN:
            logger.info(f"MEIPASS路径: {sys._MEIPASS}")
    else:
        # 配置基本日志格式
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s [%(levelname)s] %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )

        logging.info("===== Cursor Pro 启动器日志开始 =====")
        logging.info(f"操作系统: {platform.system()} {platform.version()}")
        logging.info(f"Python版本: {sys.version}")
        logging.info(f"工作目录: {os.getcwd()}")
        logging.info(f"启动参数: {sys.argv}")
        logging.info(f"是否为打包环境: {IS_FROZEN}")
        if IS_FROZEN:
            logging.info(f"MEIPASS路径: {sys._MEIPASS}")

    # 将日志文件路径保存到环境变量，便于主程序访问
    os.environ[ENV_LOG_FILE] = log_file
    if _has_log_manager:
        logger.info(f"设置环境变量 {ENV_LOG_FILE}={log_file}")
    else:
        logging.info(f"设置环境变量 {ENV_LOG_FILE}={log_file}")

    return log_file

# 获取应用程序路径
def get_app_path():
    """获取应用程序路径，兼容开发和打包环境"""
    if IS_FROZEN:
        if platform.system() == 'Darwin':  # macOS
            app_path = os.path.abspath(sys.executable)
            if _has_log_manager:
                logger.debug(f"macOS打包环境初始可执行文件路径: {app_path}")
            else:
                logging.debug(f"macOS打包环境初始可执行文件路径: {app_path}")
            while not app_path.endswith('.app') and app_path != '/':
                app_path = os.path.dirname(app_path)
            result_path = app_path if app_path != '/' else os.path.dirname(sys.executable)
        else:
            result_path = os.path.dirname(sys.executable)
    else:
        result_path = os.path.dirname(os.path.abspath(__file__))

    if _has_log_manager:
        logger.info(f"应用程序路径: {result_path}")
    else:
        logging.info(f"应用程序路径: {result_path}")
    return result_path

# 检查当前是否具有管理员权限
def is_admin():
    """检查当前是否具有管理员权限"""
    try:
        if _has_log_manager:
            logger.info(f"检查管理员权限: 操作系统 {platform.system()}")
        else:
            logging.info(f"检查管理员权限: 操作系统 {platform.system()}")

        if platform.system() == 'Windows':
            import ctypes
            is_admin_result = ctypes.windll.shell32.IsUserAnAdmin() != 0
            if _has_log_manager:
                logger.info(f"Windows管理员权限检查结果: {is_admin_result}")
            else:
                logging.info(f"Windows管理员权限检查结果: {is_admin_result}")
            return is_admin_result
        elif platform.system() == 'Darwin':  # macOS
            try:
                result = subprocess.run(
                    ['sudo', '-n', 'true'],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    check=False
                )
                is_admin_result = result.returncode == 0
                if _has_log_manager:
                    logger.info(f"macOS管理员权限检查结果: {is_admin_result}, 返回码: {result.returncode}")
                else:
                    logging.info(f"macOS管理员权限检查结果: {is_admin_result}, 返回码: {result.returncode}")
                return is_admin_result
            except Exception as e:
                if _has_log_manager:
                    logger.warning(f"检查macOS管理员权限失败: {e}")
                else:
                    logging.warning(f"检查macOS管理员权限失败: {e}")
                return False
        else:  # Linux
            is_admin_result = os.geteuid() == 0
            if _has_log_manager:
                logger.info(f"Linux管理员权限检查结果: {is_admin_result}, euid: {os.geteuid()}")
            else:
                logging.info(f"Linux管理员权限检查结果: {is_admin_result}, euid: {os.geteuid()}")
            return is_admin_result
    except Exception as e:
        if _has_log_manager:
            logger.error(f"检查管理员权限时出错: {e}")
            logger.error(traceback.format_exc())
        else:
            logging.error(f"检查管理员权限时出错: {e}")
            logging.error(traceback.format_exc())
        return False

# 在macOS中查找应用包中的可执行文件
def find_executable_in_app(app_path):
    """在macOS应用包中查找可执行文件"""
    if _has_log_manager:
        logger.info(f"在macOS应用包中查找可执行文件: {app_path}")
    else:
        logging.info(f"在macOS应用包中查找可执行文件: {app_path}")

    if not app_path.endswith('.app'):
        if _has_log_manager:
            logger.warning(f"路径不是.app包: {app_path}")
        else:
            logging.warning(f"路径不是.app包: {app_path}")
        return None

    # MacOS目录
    macos_dir = os.path.join(app_path, "Contents/MacOS")
    if not os.path.exists(macos_dir):
        if _has_log_manager:
            logger.error(f"MacOS目录不存在: {macos_dir}")
        else:
            logging.error(f"MacOS目录不存在: {macos_dir}")
        return None

    # 尝试查找与应用名称相同的可执行文件
    app_name = os.path.basename(app_path).replace('.app', '')
    exe_path = os.path.join(macos_dir, app_name)

    if os.path.isfile(exe_path) and os.access(exe_path, os.X_OK):
        if _has_log_manager:
            logger.info(f"找到匹配应用名称的可执行文件: {exe_path}")
        else:
            logging.info(f"找到匹配应用名称的可执行文件: {exe_path}")
        return exe_path

    # 查找任何可执行文件
    for item in os.listdir(macos_dir):
        file_path = os.path.join(macos_dir, item)
        if os.path.isfile(file_path) and os.access(file_path, os.X_OK):
            if _has_log_manager:
                logger.info(f"找到可执行文件: {file_path}")
            else:
                logging.info(f"找到可执行文件: {file_path}")
            return file_path

    if _has_log_manager:
        logger.error(f"在{macos_dir}中未找到可执行文件")
    else:
        logging.error(f"在{macos_dir}中未找到可执行文件")
    return None

# 以管理员权限重启程序
def restart_as_admin(password=None):
    """以管理员权限重启程序"""
    try:
        current_path = os.path.abspath(sys.argv[0])

        # 创建新的环境变量
        env = os.environ.copy()
        env[ENV_RESTARTED_AS_ADMIN] = "1"

        # 如果存在日志文件路径环境变量，保留它
        if ENV_LOG_FILE in os.environ:
            env[ENV_LOG_FILE] = os.environ[ENV_LOG_FILE]

        if _has_log_manager:
            logger.info(f"尝试以管理员权限重启程序: {current_path}")
            logger.info(f"设置环境变量 {ENV_RESTARTED_AS_ADMIN}=1")
        else:
            logging.info(f"尝试以管理员权限重启程序: {current_path}")
            logging.info(f"设置环境变量 {ENV_RESTARTED_AS_ADMIN}=1")

        if platform.system() == 'Windows':
            # Windows: 使用ShellExecute以管理员权限启动
            import ctypes
            if IS_FROZEN:
                executable = sys.executable
                params = ""
            else:
                executable = sys.executable
                params = f'"{current_path}"'

            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", executable, params, None, 1
            )
            return True

        elif platform.system() == 'Darwin':  # macOS
            # macOS: 使用sudo启动
            if password:
                # 创建临时脚本
                with tempfile.NamedTemporaryFile(delete=False, suffix='.sh', mode='w') as script_file:
                    script_path = script_file.name

                    if IS_FROZEN:
                        # 打包环境
                        app_path = get_app_path()
                        if app_path.endswith('.app'):
                            exe_path = find_executable_in_app(app_path)
                            if not exe_path:
                                if _has_log_manager:
                                    logger.error("在.app中找不到可执行文件，重启失败")
                                else:
                                    logging.error("在.app中找不到可执行文件，重启失败")
                                return False

                            # 写入脚本内容，包含环境变量设置
                            script_content = f"""#!/bin/bash
export {ENV_RESTARTED_AS_ADMIN}=1
echo {password} | sudo -S "{exe_path}"
"""
                        else:
                            # 找不到.app，使用当前可执行文件
                            script_content = f"""#!/bin/bash
export {ENV_RESTARTED_AS_ADMIN}=1
echo {password} | sudo -S "{sys.executable}"
"""
                    else:
                        # 开发环境
                        script_content = f"""#!/bin/bash
export {ENV_RESTARTED_AS_ADMIN}=1
echo {password} | sudo -S "{sys.executable}" "{current_path}"
"""

                    script_file.write(script_content)

                # 设置脚本可执行权限
                os.chmod(script_path, 0o700)

                # 执行脚本
                subprocess.Popen(script_path, shell=True)

                # 延迟删除临时脚本
                def delayed_delete():
                    try:
                        os.unlink(script_path)
                    except Exception as e:
                        if _has_log_manager:
                            logger.error(f"删除临时脚本失败: {e}")
                        else:
                            logging.error(f"删除临时脚本失败: {e}")

                timer = QTimer()
                timer.singleShot(3000, delayed_delete)
                return True
            else:
                if _has_log_manager:
                    logger.error("macOS环境需要密码才能以管理员权限重启，但未提供密码")
                else:
                    logging.error("macOS环境需要密码才能以管理员权限重启，但未提供密码")
                return False

        elif platform.system() == 'Linux':  # Linux
            # Linux: 使用sudo启动
            if password:
                # 创建临时脚本
                with tempfile.NamedTemporaryFile(delete=False, suffix='.sh', mode='w') as script_file:
                    script_path = script_file.name

                    if IS_FROZEN:
                        script_content = f"""#!/bin/bash
export {ENV_RESTARTED_AS_ADMIN}=1
echo {password} | sudo -S "{sys.executable}"
"""
                    else:
                        script_content = f"""#!/bin/bash
export {ENV_RESTARTED_AS_ADMIN}=1
echo {password} | sudo -S "{sys.executable}" "{current_path}"
"""

                    script_file.write(script_content)

                # 设置脚本可执行权限
                os.chmod(script_path, 0o700)

                # 执行脚本
                subprocess.Popen(script_path, shell=True)

                # 延迟删除临时脚本
                def delayed_delete():
                    try:
                        os.unlink(script_path)
                    except Exception as e:
                        if _has_log_manager:
                            logger.error(f"删除临时脚本失败: {e}")
                        else:
                            logging.error(f"删除临时脚本失败: {e}")

                timer = QTimer()
                timer.singleShot(3000, delayed_delete)
                return True
            else:
                if _has_log_manager:
                    logger.error("Linux环境需要密码才能以管理员权限重启，但未提供密码")
                else:
                    logging.error("Linux环境需要密码才能以管理员权限重启，但未提供密码")
                return False
    except Exception as e:
        if _has_log_manager:
            logger.error(f"以管理员权限重启程序时出错: {e}")
            logger.error(traceback.format_exc())
        else:
            logging.error(f"以管理员权限重启程序时出错: {e}")
            logging.error(traceback.format_exc())
        return False

# 验证系统管理员密码
def verify_system_admin_password(password):
    """验证系统管理员密码"""
    try:
        if _has_log_manager:
            logger.info("验证系统管理员密码")
        else:
            logging.info("验证系统管理员密码")
        if platform.system() == 'Windows':
            # Windows验证管理员密码比较复杂，一般通过UAC提升权限
            if _has_log_manager:
                logger.info("Windows平台：跳过密码验证，将通过UAC提升权限")
            else:
                logging.info("Windows平台：跳过密码验证，将通过UAC提升权限")
            return True
        elif platform.system() == 'Darwin':  # macOS
            # 使用sudo -S -v验证密码
            with tempfile.NamedTemporaryFile() as temp:
                cmd = f'echo {password} | sudo -S -v 2>{temp.name}'
                result = subprocess.run(cmd, shell=True, text=True, capture_output=True)
                verified = result.returncode == 0
                if _has_log_manager:
                    logger.info(f"macOS密码验证结果: {'成功' if verified else '失败'}, 返回码: {result.returncode}")
                else:
                    logging.info(f"macOS密码验证结果: {'成功' if verified else '失败'}, 返回码: {result.returncode}")
                return verified
        else:  # Linux
            # 使用sudo -S -v验证密码
            with tempfile.NamedTemporaryFile() as temp:
                cmd = f'echo {password} | sudo -S -v 2>{temp.name}'
                result = subprocess.run(cmd, shell=True, text=True, capture_output=True)
                verified = result.returncode == 0
                if _has_log_manager:
                    logger.info(f"Linux密码验证结果: {'成功' if verified else '失败'}, 返回码: {result.returncode}")
                else:
                    logging.info(f"Linux密码验证结果: {'成功' if verified else '失败'}, 返回码: {result.returncode}")
                return verified
    except Exception as e:
        if _has_log_manager:
            logger.error(f"验证系统管理员密码时出错: {e}")
            logger.error(traceback.format_exc())
        else:
            logging.error(f"验证系统管理员密码时出错: {e}")
            logging.error(traceback.format_exc())
        return False

class AdminAuthDialog(QDialog):
    """管理员权限验证对话框"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("需要管理员权限")
        self.setFixedSize(400, 200)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)

        # 设置对话框背景颜色为深色
        self.setStyleSheet("""
            QDialog {
                background-color: #2D2D2D;
                color: white;
            }
            QLabel {
                color: white;
            }
            QLineEdit {
                background-color: #444444;
                color: white;
                border: 1px solid #4CD964;
                border-radius: 4px;
                padding: 5px;
                selection-background-color: #4CD964;
                font-size: 14px;
                height: 25px;
            }
            QLineEdit:focus {
                border: 2px solid #4CD964;
            }
            QPushButton {
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 14px;
                color: white;
            }
            QPushButton#cancelButton {
                background-color: #666666;
                border: none;
            }
            QPushButton#cancelButton:hover {
                background-color: #777777;
            }
            QPushButton#okButton {
                background-color: #4CD964;
                border: none;
            }
            QPushButton#okButton:hover {
                background-color: #65E078;
            }
        """)

        # 主布局
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # 标题标签
        title_label = QLabel(f"{APP_NAME} 需要管理员权限才能运行。")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: white;")
        layout.addWidget(title_label)

        # 密码提示标签
        password_label = QLabel("请输入您的系统管理员密码：")
        password_label.setAlignment(Qt.AlignLeft)
        layout.addWidget(password_label)

        # 密码输入框
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("输入系统管理员密码")
        self.password_input.setMinimumHeight(30)
        layout.addWidget(self.password_input)

        # 添加一些间距
        layout.addSpacing(10)

        # 按钮布局
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(10)

        # 添加弹性空间使按钮靠右
        button_layout.addStretch()

        # 取消按钮
        self.cancel_button = QPushButton("取消")
        self.cancel_button.setObjectName("cancelButton")
        self.cancel_button.setCursor(Qt.PointingHandCursor)
        self.cancel_button.clicked.connect(self.reject)
        self.cancel_button.setMinimumWidth(100)
        self.cancel_button.setMinimumHeight(30)
        button_layout.addWidget(self.cancel_button)

        # 确认按钮
        self.ok_button = QPushButton("确定")
        self.ok_button.setObjectName("okButton")
        self.ok_button.setCursor(Qt.PointingHandCursor)
        self.ok_button.clicked.connect(self.verify_password)
        self.ok_button.setDefault(True)
        self.ok_button.setMinimumWidth(100)
        self.ok_button.setMinimumHeight(30)
        button_layout.addWidget(self.ok_button)

        # 将按钮布局添加到主布局
        layout.addLayout(button_layout)

        # 设置对话框布局
        self.setLayout(layout)

        # 连接回车键到验证函数
        self.password_input.returnPressed.connect(self.verify_password)

        # 设置初始焦点
        self.password_input.setFocus()

        # 对话框显示后立即执行
        QTimer.singleShot(100, self.password_input.setFocus)

    def showEvent(self, event):
        """对话框显示事件"""
        super().showEvent(event)
        # 确保密码输入框获得焦点
        self.password_input.setFocus()

    def verify_password(self):
        """验证管理员密码"""
        password = self.password_input.text()

        if platform.system() == 'Windows':
            # Windows平台直接接受，之后会通过UAC验证
            self.accept()
        else:
            # macOS和Linux先验证密码
            if verify_system_admin_password(password):
                # 存储密码供重启时使用
                self.admin_password = password
                self.accept()
            else:
                # 密码错误，显示错误消息
                error_label = QLabel("密码错误，请重试！")
                error_label.setStyleSheet("color: #FF3B30; margin-top: 5px;")
                error_label.setAlignment(Qt.AlignCenter)

                # 找到当前布局中的错误标签（如果有）并移除
                for i in range(self.layout().count()):
                    widget = self.layout().itemAt(i).widget()
                    if isinstance(widget, QLabel) and "密码错误" in widget.text():
                        widget.deleteLater()

                # 在密码输入框之后添加错误标签
                self.layout().insertWidget(3, error_label)

                # 清空密码输入框并设置红色边框提示错误
                self.password_input.clear()
                self.password_input.setStyleSheet("""
                    background-color: #444444;
                    color: white;
                    border: 1px solid #FF3B30;
                    border-radius: 4px;
                    padding: 5px;
                """)
                self.password_input.setFocus()

                # 3秒后恢复正常样式
                QTimer.singleShot(3000, lambda: self.password_input.setStyleSheet(""))

def create_styled_message_box(parent, title, text, icon_type=QMessageBox.Warning):
    """创建样式化的消息对话框"""
    msg_box = QMessageBox(parent)
    msg_box.setWindowTitle(title)
    msg_box.setText(text)
    msg_box.setIcon(icon_type)

    # 设置样式
    msg_box.setStyleSheet("""
        QMessageBox {
            background-color: #2D2D2D;
            color: white;
        }
        QLabel {
            color: white;
        }
        QPushButton {
            background-color: #4CD964;
            color: white;
            border-radius: 5px;
            padding: 8px 16px;
            font-size: 14px;
            min-width: 80px;
        }
        QPushButton:hover {
            background-color: #65E078;
        }
    """)

    return msg_box

def start_main_program():
    """启动主程序（单一入口点）"""
    if _has_log_manager:
        logger.info("======= 开始启动主程序 =======")
    else:
        logging.info("======= 开始启动主程序 =======")

    try:
        # 设置必要的环境变量
        os.environ[ENV_SKIP_ADMIN_CHECK] = "1"
        if _has_log_manager:
            logger.info(f"设置环境变量 {ENV_SKIP_ADMIN_CHECK}=1")
        else:
            logging.info(f"设置环境变量 {ENV_SKIP_ADMIN_CHECK}=1")

        # 确保源代码目录在路径中
        if IS_FROZEN:
            # 添加必要的路径到sys.path
            if sys._MEIPASS not in sys.path:
                sys.path.insert(0, sys._MEIPASS)
                if _has_log_manager:
                    logger.info(f"已添加MEIPASS路径到sys.path: {sys._MEIPASS}")
                else:
                    logging.info(f"已添加MEIPASS路径到sys.path: {sys._MEIPASS}")

            # 添加src目录到sys.path
            src_path = os.path.join(sys._MEIPASS, 'src')
            if os.path.exists(src_path) and src_path not in sys.path:
                sys.path.insert(0, src_path)
                if _has_log_manager:
                    logger.info(f"已添加src路径到sys.path: {src_path}")
                else:
                    logging.info(f"已添加src路径到sys.path: {src_path}")
        else:
            # 开发环境
            current_dir = os.path.dirname(os.path.abspath(__file__))
            if current_dir not in sys.path:
                sys.path.insert(0, current_dir)
                if _has_log_manager:
                    logger.info(f"已添加当前目录到sys.path: {current_dir}")
                else:
                    logging.info(f"已添加当前目录到sys.path: {current_dir}")

            src_path = os.path.join(current_dir, 'src')
            if os.path.exists(src_path) and src_path not in sys.path:
                sys.path.insert(0, src_path)
                if _has_log_manager:
                    logger.info(f"已添加src路径到sys.path: {src_path}")
                else:
                    logging.info(f"已添加src路径到sys.path: {src_path}")

        if _has_log_manager:
            logger.info("当前sys.path:")
            for p in sys.path:
                logger.info(f"  - {p}")
        else:
            logging.info("当前sys.path:")
            for p in sys.path:
                logging.info(f"  - {p}")

        # 直接导入main.py
        try:
            if _has_log_manager:
                logger.info("尝试导入main模块...")
            else:
                logging.info("尝试导入main模块...")

            # 将当前工作目录设置为应用程序所在目录，避免相对导入问题
            app_dir = get_app_path()
            os.chdir(app_dir)
            if _has_log_manager:
                logger.info(f"已将工作目录设置为: {app_dir}")
            else:
                logging.info(f"已将工作目录设置为: {app_dir}")

            # 先尝试导入src.main
            try:
                if _has_log_manager:
                    logger.info("尝试导入src.main模块...")
                else:
                    logging.info("尝试导入src.main模块...")
                from src.main import main as main_entry_point
                if _has_log_manager:
                    logger.info("成功导入src.main模块")
                else:
                    logging.info("成功导入src.main模块")
            except ImportError as e:
                if _has_log_manager:
                    logger.warning(f"导入src.main失败: {e}")
                else:
                    logging.warning(f"导入src.main失败: {e}")

                # 再尝试直接导入main
                try:
                    if _has_log_manager:
                        logger.info("尝试直接导入main模块...")
                    else:
                        logging.info("尝试直接导入main模块...")
                    import main
                    main_entry_point = main.main
                    if _has_log_manager:
                        logger.info("成功导入main模块")
                    else:
                        logging.info("成功导入main模块")
                except ImportError as e:
                    if _has_log_manager:
                        logger.error(f"导入main模块失败: {e}")
                    else:
                        logging.error(f"导入main模块失败: {e}")
                    raise ImportError("无法导入主模块，请确保main.py文件存在且可访问")

            if _has_log_manager:
                logger.info("正在调用主程序入口函数...")
            else:
                logging.info("正在调用主程序入口函数...")
            # 调用主程序入口函数
            exit_code = main_entry_point()
            if _has_log_manager:
                logger.info(f"主程序执行完成，退出代码: {exit_code}")
            else:
                logging.info(f"主程序执行完成，退出代码: {exit_code}")
            return exit_code

        except Exception as e:
            if _has_log_manager:
                logger.error(f"导入或执行主模块时出错: {e}")
                logger.error(traceback.format_exc())
            else:
                logging.error(f"导入或执行主模块时出错: {e}")
                logging.error(traceback.format_exc())

            # 如果直接导入失败，尝试以子进程方式启动
            if _has_log_manager:
                logger.warning("直接导入失败，尝试以子进程方式启动...")
            else:
                logging.warning("直接导入失败，尝试以子进程方式启动...")

            # 构建环境变量
            env = os.environ.copy()
            env[ENV_SKIP_ADMIN_CHECK] = "1"
            if _has_log_manager:
                logger.info(f"设置环境变量 {ENV_SKIP_ADMIN_CHECK}=1 用于子进程")
            else:
                logging.info(f"设置环境变量 {ENV_SKIP_ADMIN_CHECK}=1 用于子进程")

            # 构建命令
            if IS_FROZEN:
                # 打包环境
                if platform.system() == 'Darwin':  # macOS
                    app_path = get_app_path()
                    if app_path.endswith('.app'):
                        exe_path = find_executable_in_app(app_path)
                        if exe_path:
                            cmd = [exe_path]
                        else:
                            cmd = [sys.executable]
                    else:
                        cmd = [sys.executable]
                else:
                    # Windows或Linux
                    cmd = [sys.executable]
            else:
                # 开发环境
                main_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'main.py')
                cmd = [sys.executable, main_path]

            if _has_log_manager:
                logger.info(f"启动命令: {cmd}")
            else:
                logging.info(f"启动命令: {cmd}")

            # 启动主程序
            if _has_log_manager:
                logger.info("正在启动主程序子进程...")
            else:
                logging.info("正在启动主程序子进程...")
            process = subprocess.Popen(cmd, env=env)
            if _has_log_manager:
                logger.info(f"子进程已启动，PID: {process.pid}")
            else:
                logging.info(f"子进程已启动，PID: {process.pid}")

            # 等待一小段时间，检查进程是否成功启动
            import time
            time.sleep(0.5)

            poll_result = process.poll()
            if poll_result is None:
                # 进程仍在运行，说明启动成功
                if _has_log_manager:
                    logger.info("主程序进程启动成功，仍在运行")
                else:
                    logging.info("主程序进程启动成功，仍在运行")
                return 0
            else:
                # 进程已退出，说明启动失败
                if _has_log_manager:
                    logger.error(f"主程序进程启动失败，已退出，退出代码: {poll_result}")
                else:
                    logging.error(f"主程序进程启动失败，已退出，退出代码: {poll_result}")
                return 1
    except Exception as e:
        if _has_log_manager:
            logger.error(f"启动主程序时出错: {e}")
            logger.error(traceback.format_exc())
        else:
            logging.error(f"启动主程序时出错: {e}")
            logging.error(traceback.format_exc())
        return 1

def main():
    """启动器主函数 - 单一入口点"""
    # 初始化日志
    log_file = setup_logging()
    if _has_log_manager:
        logger.info("========= 启动器主函数开始执行 =========")
    else:
        logging.info("========= 启动器主函数开始执行 =========")

    # 清理旧日志文件（保留30天）
    if _has_log_manager:
        try:
            logger.clean_old_log_files(LOG_DIR, 30)
        except Exception as e:
            logger.warning(f"清理旧日志文件失败: {e}")

    # 检查环境变量，确定启动状态
    was_restarted = os.environ.get(ENV_RESTARTED_AS_ADMIN) == "1"
    skip_admin_check = os.environ.get(ENV_SKIP_ADMIN_CHECK) == "1"

    # 记录当前状态
    if was_restarted:
        if _has_log_manager:
            logger.info(f"检测到环境变量 {ENV_RESTARTED_AS_ADMIN}=1，程序已以管理员权限重启")
        else:
            logging.info(f"检测到环境变量 {ENV_RESTARTED_AS_ADMIN}=1，程序已以管理员权限重启")
    if skip_admin_check:
        if _has_log_manager:
            logger.info(f"检测到环境变量 {ENV_SKIP_ADMIN_CHECK}=1，将跳过管理员权限检查")
        else:
            logging.info(f"检测到环境变量 {ENV_SKIP_ADMIN_CHECK}=1，将跳过管理员权限检查")

    # 检查是否已经有管理员权限或是否需要跳过管理员权限检查
    has_admin = is_admin()

    if has_admin or skip_admin_check or was_restarted:
        if _has_log_manager:
            logger.info("已具有管理员权限或跳过权限检查，直接启动主程序...")
        else:
            logging.info("已具有管理员权限或跳过权限检查，直接启动主程序...")
        return start_main_program()

    # 创建应用程序实例
    if _has_log_manager:
        logger.info("创建Qt应用程序实例")
    else:
        logging.info("创建Qt应用程序实例")
    app = QApplication(sys.argv)

    # 设置应用程序图标（如果有的话）
    app_path = get_app_path()
    icon_path = os.path.join(app_path, 'resources', 'icons', 'app_icon.png')
    fallback_icon_path = os.path.join(app_path, 'resources', 'icons', 'app_icon.ico')

    if os.path.exists(icon_path):
        if _has_log_manager:
            logger.info(f"设置应用图标: {icon_path}")
        else:
            logging.info(f"设置应用图标: {icon_path}")
        app.setWindowIcon(QIcon(icon_path))
    elif os.path.exists(fallback_icon_path):
        if _has_log_manager:
            logger.info(f"使用备用应用图标: {fallback_icon_path}")
        else:
            logging.info(f"使用备用应用图标: {fallback_icon_path}")
        app.setWindowIcon(QIcon(fallback_icon_path))
    else:
        if _has_log_manager:
            logger.warning("找不到应用图标")
        else:
            logging.warning("找不到应用图标")

    # 设置应用程序样式
    if _has_log_manager:
        logger.info("设置应用程序样式为Fusion")
    else:
        logging.info("设置应用程序样式为Fusion")
    app.setStyle("Fusion")

    # 创建管理员权限验证对话框
    dialog = AdminAuthDialog()

    # 居中显示对话框
    screen_geometry = app.primaryScreen().availableGeometry()
    x = (screen_geometry.width() - dialog.width()) // 2
    y = (screen_geometry.height() - dialog.height()) // 2
    dialog.move(x, y)

    # 显示对话框
    if _has_log_manager:
        logger.info("显示对话框，等待用户输入密码...")
    else:
        logging.info("显示对话框，等待用户输入密码...")
    result = dialog.exec()
    if _has_log_manager:
        logger.info(f"对话框结果: {result} (接受={QDialog.Accepted}, 拒绝={QDialog.Rejected})")
    else:
        logging.info(f"对话框结果: {result} (接受={QDialog.Accepted}, 拒绝={QDialog.Rejected})")

    if result == QDialog.Accepted:
        # 验证成功，以管理员权限重启程序
        if _has_log_manager:
            logger.info("管理员权限验证成功，正在以管理员权限重启程序...")
        else:
            logging.info("管理员权限验证成功，正在以管理员权限重启程序...")

        # 获取输入的密码(Windows平台不需要)
        admin_password = getattr(dialog, 'admin_password', None) if platform.system() != 'Windows' else None
        if _has_log_manager:
            logger.info(f"获取管理员密码: {'成功' if admin_password else '无需密码或未提供'}")
        else:
            logging.info(f"获取管理员密码: {'成功' if admin_password else '无需密码或未提供'}")

        if restart_as_admin(admin_password):
            if _has_log_manager:
                logger.info("以管理员权限重启成功")
            else:
                logging.info("以管理员权限重启成功")
            return 0
        else:
            # 重启失败，尝试直接启动
            if _has_log_manager:
                logger.warning("以管理员权限重启失败，尝试以普通权限运行")
            else:
                logging.warning("以管理员权限重启失败，尝试以普通权限运行")
            msg_box = create_styled_message_box(
                None,
                "提示",
                "无法以管理员权限启动，将尝试以普通权限运行。部分功能可能受限。"
            )
            if _has_log_manager:
                logger.info("显示警告消息框")
            else:
                logging.info("显示警告消息框")
            msg_box.exec()

            # 设置环境变量跳过管理员权限检查
            os.environ[ENV_SKIP_ADMIN_CHECK] = "1"
            if _has_log_manager:
                logger.info(f"设置环境变量 {ENV_SKIP_ADMIN_CHECK}=1")
            else:
                logging.info(f"设置环境变量 {ENV_SKIP_ADMIN_CHECK}=1")

            startup_result = start_main_program()
            if startup_result == 0:
                if _has_log_manager:
                    logger.info("以普通权限启动主程序成功")
                else:
                    logging.info("以普通权限启动主程序成功")
                return 0
            else:
                if _has_log_manager:
                    logger.error("以普通权限启动主程序失败")
                else:
                    logging.error("以普通权限启动主程序失败")
                error_box = create_styled_message_box(
                    None,
                    "启动失败",
                    "无法启动程序，请检查程序文件是否完整。",
                    QMessageBox.Critical
                )
                if _has_log_manager:
                    logger.info("显示错误消息框")
                else:
                    logging.info("显示错误消息框")
                error_box.exec()
                return 1
    else:
        # 用户取消了验证
        if _has_log_manager:
            logger.info("用户取消了管理员权限验证，程序退出")
        else:
            logging.info("用户取消了管理员权限验证，程序退出")
        return 1

if __name__ == "__main__":
    sys.exit(main())