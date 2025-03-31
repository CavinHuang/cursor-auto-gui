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
from pathlib import Path
from PySide6.QtWidgets import QApplication, QDialog, QLineEdit, QPushButton, QVBoxLayout, QLabel, QHBoxLayout, QMessageBox
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon, QPixmap

# 导入主程序模块
try:
    from src.main import main as main_entry_point
except ImportError:
    # 如果无法直接导入，设置一个标记以后再尝试
    main_entry_point = None

# 判断是否为打包环境
def is_frozen():
    """判断当前是否在打包环境中运行"""
    return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')

# 获取应用程序路径
def get_app_path():
    """获取应用程序路径，兼容开发和打包环境"""
    if is_frozen():
        # 打包环境
        if platform.system() == 'Darwin':  # macOS
            # 在macOS下查找.app包
            app_path = os.path.abspath(sys.executable)
            while not app_path.endswith('.app') and app_path != '/':
                app_path = os.path.dirname(app_path)
            return app_path if app_path != '/' else os.path.dirname(sys.executable)
        else:
            # Windows或Linux
            return os.path.dirname(sys.executable)
    else:
        # 开发环境
        return os.path.dirname(os.path.abspath(__file__))

# 检查当前是否具有管理员权限
def is_admin():
    """检查当前是否具有管理员权限"""
    try:
        if platform.system() == 'Windows':
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        elif platform.system() == 'Darwin':  # macOS
            try:
                result = subprocess.run(
                    ['sudo', '-n', 'true'],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    check=False
                )
                return result.returncode == 0
            except Exception:
                # 非交互模式检查失败，可能需要密码
                return False
        else:  # Linux
            return os.geteuid() == 0
    except Exception as e:
        print(f"检查管理员权限时出错: {e}")
        return False

# 以管理员权限重启程序
def restart_as_admin(password=None):
    """以管理员权限重启程序"""
    try:
        current_path = os.path.abspath(sys.argv[0])
        args = sys.argv[1:]
        # 添加--restart-as-admin参数，避免循环重启
        if "--restart-as-admin" not in args:
            args.append("--restart-as-admin")

        if platform.system() == 'Windows':
            # Windows: 使用ShellExecute以管理员权限启动
            import ctypes
            if is_frozen():
                executable = sys.executable
                params = " ".join(args)
            else:
                executable = sys.executable
                params = f'"{current_path}" {" ".join(args)}'

            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", executable, params, None, 1
            )
            return True

        elif platform.system() == 'Darwin':  # macOS
            # macOS: 使用osascript或sudo启动
            if password:
                # 创建临时脚本
                with tempfile.NamedTemporaryFile(delete=False, suffix='.sh', mode='w') as script_file:
                    script_path = script_file.name

                    if is_frozen():
                        # 打包环境
                        app_path = get_app_path()
                        if app_path.endswith('.app'):
                            exe_path = find_executable_in_app(app_path)
                            if not exe_path:
                                return False

                            # 写入脚本内容
                            script_file.write(f"""#!/bin/bash
echo {password} | sudo -S "{exe_path}" {' '.join(args)}
""")
                        else:
                            # 找不到.app，使用当前可执行文件
                            script_file.write(f"""#!/bin/bash
echo {password} | sudo -S "{sys.executable}" {' '.join(args)}
""")
                    else:
                        # 开发环境
                        script_file.write(f"""#!/bin/bash
echo {password} | sudo -S "{sys.executable}" "{current_path}" {' '.join(args)}
""")

                # 设置脚本可执行权限
                os.chmod(script_path, 0o700)

                # 执行脚本
                subprocess.Popen(script_path, shell=True)

                # 延迟删除临时脚本
                def delayed_delete():
                    try:
                        os.unlink(script_path)
                    except:
                        pass

                timer = QTimer()
                timer.singleShot(3000, delayed_delete)

                return True
            else:
                return False

        elif platform.system() == 'Linux':  # Linux
            # Linux: 使用pkexec或sudo启动
            if password:
                # 创建临时脚本
                with tempfile.NamedTemporaryFile(delete=False, suffix='.sh', mode='w') as script_file:
                    script_path = script_file.name

                    if is_frozen():
                        script_file.write(f"""#!/bin/bash
echo {password} | sudo -S "{sys.executable}" {' '.join(args)}
""")
                    else:
                        script_file.write(f"""#!/bin/bash
echo {password} | sudo -S "{sys.executable}" "{current_path}" {' '.join(args)}
""")

                # 设置脚本可执行权限
                os.chmod(script_path, 0o700)

                # 执行脚本
                subprocess.Popen(script_path, shell=True)

                # 延迟删除临时脚本
                def delayed_delete():
                    try:
                        os.unlink(script_path)
                    except:
                        pass

                timer = QTimer()
                timer.singleShot(3000, delayed_delete)

                return True
            else:
                return False
    except Exception as e:
        print(f"以管理员权限重启程序时出错: {e}")
        return False

# 在macOS中查找应用包中的可执行文件
def find_executable_in_app(app_path):
    """在macOS应用包中查找可执行文件"""
    if not app_path.endswith('.app'):
        return None

    # MacOS目录
    macos_dir = os.path.join(app_path, "Contents/MacOS")
    if not os.path.exists(macos_dir):
        return None

    # 尝试查找与应用名称相同的可执行文件
    app_name = os.path.basename(app_path).replace('.app', '')
    exe_path = os.path.join(macos_dir, app_name)
    if os.path.isfile(exe_path) and os.access(exe_path, os.X_OK):
        return exe_path

    # 查找任何可执行文件
    for item in os.listdir(macos_dir):
        file_path = os.path.join(macos_dir, item)
        if os.path.isfile(file_path) and os.access(file_path, os.X_OK):
            return file_path

    return None

# 验证系统管理员密码
def verify_system_admin_password(password):
    """验证系统管理员密码"""
    try:
        if platform.system() == 'Windows':
            # Windows验证管理员密码比较复杂，一般通过UAC提升权限
            # 这里只做简单返回，实际会通过ShellExecute的UAC弹窗验证
            return True
        elif platform.system() == 'Darwin':  # macOS
            # 使用sudo -S -v验证密码
            with tempfile.NamedTemporaryFile() as temp:
                cmd = f'echo {password} | sudo -S -v 2>{temp.name}'
                result = subprocess.run(cmd, shell=True, text=True, capture_output=True)
                return result.returncode == 0
        else:  # Linux
            # 使用sudo -S -v验证密码
            with tempfile.NamedTemporaryFile() as temp:
                cmd = f'echo {password} | sudo -S -v 2>{temp.name}'
                result = subprocess.run(cmd, shell=True, text=True, capture_output=True)
                return result.returncode == 0
    except Exception as e:
        print(f"验证系统管理员密码时出错: {e}")
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
        title_label = QLabel("Cursor Pro 需要管理员权限才能运行。")
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
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setObjectName("cancelButton")
        self.cancel_button.setCursor(Qt.PointingHandCursor)
        self.cancel_button.clicked.connect(self.reject)
        self.cancel_button.setMinimumWidth(100)
        self.cancel_button.setMinimumHeight(30)
        button_layout.addWidget(self.cancel_button)

        # 确认按钮
        self.ok_button = QPushButton("OK")
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

def run_main_program_direct():
    """直接在当前进程中运行主程序（不启动新进程）"""
    global main_entry_point

    # 如果入口点之前未加载，现在尝试加载
    if main_entry_point is None:
        try:
            # 添加当前目录到Python路径
            current_dir = os.path.dirname(os.path.abspath(__file__))
            if current_dir not in sys.path:
                sys.path.insert(0, current_dir)

            # 尝试导入主程序模块
            from src.main import main as main_func
            main_entry_point = main_func
        except ImportError as e:
            print(f"无法导入主程序模块: {e}")
            return False

    # 设置跳过管理员检查的环境变量
    os.environ['SKIP_ADMIN_CHECK'] = '1'

    try:
        # 直接调用主程序入口函数
        print("直接调用主程序入口函数")
        exit_code = main_entry_point()
        return exit_code
    except Exception as e:
        print(f"运行主程序时出错: {e}")
        import traceback
        traceback.print_exc()
        return False

def start_main_program():
    """启动主程序（非管理员权限）"""
    # 尝试直接运行主程序
    print("尝试直接运行主程序...")
    result = run_main_program_direct()

    if result is not False:  # 可能返回0或其他退出码
        return True

    print("直接运行失败，尝试通过进程启动...")

    # 如果直接运行失败，回退到原来的启动方式
    main_script = get_main_script_path()

    try:
        # 构建启动命令
        if is_frozen():
            # 打包环境直接使用可执行文件
            cmd = [main_script, "--skip-admin-check"]
        else:
            # 开发环境使用Python解释器
            cmd = [sys.executable, "main.py", "--skip-admin-check"]

        # 添加其他命令行参数（除了--restart-as-admin）
        for arg in sys.argv[1:]:
            if arg != "--restart-as-admin":
                cmd.append(arg)

        # 启动主程序
        subprocess.Popen(cmd)
        return True
    except Exception as e:
        print(f"启动主程序失败: {e}")
        return False

def get_main_script_path():
    """获取主程序脚本路径"""
    if is_frozen():
        # 打包环境
        if platform.system() == 'Darwin':  # macOS
            app_path = get_app_path()
            if app_path.endswith('.app'):
                # 查找可执行文件
                exe_path = find_executable_in_app(app_path)
                if exe_path:
                    return exe_path
            # 如果没找到，返回当前可执行文件
            return sys.executable
        else:
            # Windows或Linux，使用当前可执行文件
            return sys.executable
    else:
        # 开发环境
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'main.py')

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

def main():
    """启动器主函数"""
    # 检查是否已经有管理员权限
    if is_admin():
        print("已具有管理员权限，直接启动主程序...")
        if "--restart-as-admin" in sys.argv:
            sys.argv.remove("--restart-as-admin")
        start_main_program()
        return 0

    # 检查是否是重启后的进程
    if "--restart-as-admin" in sys.argv:
        sys.argv.remove("--restart-as-admin")
        # 如果是通过管理员权限重启的，直接启动主程序
        start_main_program()
        return 0

    # 创建应用程序实例
    app = QApplication(sys.argv)

    # 设置应用程序图标（如果有的话）
    icon_path = os.path.join(get_app_path(), 'resources', 'icons', 'app_icon.png')
    fallback_icon_path = os.path.join(get_app_path(), 'resources', 'icons', 'app_icon.ico')

    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    elif os.path.exists(fallback_icon_path):
        app.setWindowIcon(QIcon(fallback_icon_path))

    # 设置应用程序样式
    app.setStyle("Fusion")  # 使用Fusion样式，在不同平台上有一致的外观

    # 创建管理员权限验证对话框
    dialog = AdminAuthDialog()

    # 居中显示对话框
    screen_geometry = app.primaryScreen().availableGeometry()
    x = (screen_geometry.width() - dialog.width()) // 2
    y = (screen_geometry.height() - dialog.height()) // 2
    dialog.move(x, y)

    # 显示对话框
    result = dialog.exec()

    if result == QDialog.Accepted:
        # 验证成功，以管理员权限重启程序
        print("管理员权限验证成功，正在以管理员权限重启程序...")

        # 获取输入的密码(Windows平台不需要)
        admin_password = getattr(dialog, 'admin_password', None) if platform.system() != 'Windows' else None

        if restart_as_admin(admin_password):
            return 0
        else:
            # 重启失败，尝试直接启动
            msg_box = create_styled_message_box(
                None,
                "提示",
                "无法以管理员权限启动，将尝试以普通权限运行。部分功能可能受限。",
                QMessageBox.Warning
            )
            msg_box.exec()

            if start_main_program():
                return 0
            else:
                error_box = create_styled_message_box(
                    None,
                    "启动失败",
                    "无法启动程序，请检查程序文件是否完整。",
                    QMessageBox.Critical
                )
                error_box.exec()
                return 1
    else:
        # 用户取消了验证
        print("用户取消了管理员权限验证，程序退出")
        return 1

if __name__ == "__main__":
    sys.exit(main())