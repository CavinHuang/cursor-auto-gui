#!/usr/bin/env python
"""
Cursor Pro 权限启动器
负责检查管理员权限，无需弹窗提示直接请求系统授权
整个流程中不会显示任何应用程序自己的对话框，只会显示系统的授权对话框
- 已有权限：直接启动主程序
- 无权限：直接弹出系统授权对话框
- 授权成功：自动启动主程序
- 授权失败：显示一个错误消息并退出
"""

import sys
import os
import platform
import subprocess
import time
import traceback
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt
from src.logic.utils.admin_helper import is_admin, restart_as_admin

def is_frozen():
    """检查当前是否在打包环境中运行"""
    return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')

def get_app_path():
    """获取应用程序的路径，适用于开发环境和打包环境"""
    if is_frozen():
        # 打包环境，返回应用包的路径
        if platform.system() == 'Darwin':  # macOS
            # 向上查找直到找到.app目录
            app_path = os.path.abspath(sys.executable)
            while not app_path.endswith('.app') and app_path != '/':
                app_path = os.path.dirname(app_path)

            if app_path == '/':
                print("警告: 无法找到.app包路径，使用当前目录")
                return os.getcwd()

            return app_path
        else:
            # Windows或Linux
            return os.path.dirname(sys.executable)
    else:
        # 开发环境，返回当前工作目录
        return os.getcwd()

def find_executable(app_path):
    """查找可执行文件的路径，适用于macOS环境"""
    if platform.system() == 'Darwin':
        # 首先检查默认位置
        default_exe = os.path.join(app_path, "Contents/MacOS/CursorPro")
        if os.path.exists(default_exe) and os.access(default_exe, os.X_OK):
            return default_exe

        # 如果默认可执行文件不存在，搜索MacOS目录下的所有可执行文件
        macos_dir = os.path.join(app_path, "Contents/MacOS")
        if os.path.exists(macos_dir):
            print(f"搜索可执行文件: {macos_dir}")
            for file in os.listdir(macos_dir):
                exe_path = os.path.join(macos_dir, file)
                if os.path.isfile(exe_path) and os.access(exe_path, os.X_OK):
                    print(f"找到可执行文件: {exe_path}")
                    return exe_path

        # 如果MacOS目录下没有找到，尝试在相同目录下查找main.py
        main_py = os.path.join(os.path.dirname(sys.executable), "main.py")
        if os.path.exists(main_py):
            print(f"找到main.py: {main_py}")
            return main_py

        print(f"警告: 在 {app_path} 中未找到可执行文件")

    # 对于非macOS或找不到可执行文件的情况，返回None
    return None

def launch_app():
    """在确认有管理员权限后，启动主应用程序"""
    print("=== 启动主应用程序 ===")

    # 创建日志目录
    log_dir = os.path.expanduser("~/Library/Logs/CursorPro")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "launcher_log.txt")

    with open(log_file, "a") as f:
        f.write(f"\n\n=== 启动尝试: {time.strftime('%Y-%m-%d %H:%M:%S')} ===\n")
        f.write(f"Python版本: {sys.version}\n")
        f.write(f"可执行文件: {sys.executable}\n")
        f.write(f"当前工作目录: {os.getcwd()}\n")
        f.write(f"命令行参数: {sys.argv}\n")
        f.write(f"是否打包环境: {is_frozen()}\n")

    # 使用子进程启动主程序
    try:
        # 检查是否在打包环境中
        if is_frozen():
            # 打包环境
            if platform.system() == 'Darwin':  # macOS
                app_path = get_app_path()
                with open(log_file, "a") as f:
                    f.write(f"应用路径: {app_path}\n")

                # 策略0: 优先使用bootstrap.py
                bootstrap_path = os.path.join(app_path, "Contents/Resources/bootstrap.py")
                with open(log_file, "a") as f:
                    f.write(f"查找bootstrap.py路径: {bootstrap_path}\n")

                if os.path.exists(bootstrap_path):
                    with open(log_file, "a") as f:
                        f.write(f"找到bootstrap.py: {bootstrap_path}\n")

                    # 尝试找到合适的Python解释器
                    # 首先尝试系统解释器，因为PyInstaller打包的Python可能有问题
                    python_path = "/usr/bin/python3"
                    if not os.path.exists(python_path):
                        python_path = "/usr/bin/python"

                    with open(log_file, "a") as f:
                        f.write(f"使用Python解释器: {python_path}\n")

                    # 设置环境变量
                    process_env = os.environ.copy()
                    resources_dir = os.path.dirname(bootstrap_path)

                    # 添加额外的环境变量以确保Python找到所有模块
                    frameworks_dir = os.path.join(app_path, "Contents/Frameworks")
                    if os.path.exists(frameworks_dir):
                        python_path_entries = [
                            resources_dir,
                            frameworks_dir,
                            os.path.join(frameworks_dir, "lib-dynload")
                        ]
                        process_env['PYTHONPATH'] = os.pathsep.join(python_path_entries)
                        with open(log_file, "a") as f:
                            f.write(f"设置PYTHONPATH: {process_env['PYTHONPATH']}\n")

                    # 确保PATH中包含MacOS目录
                    macos_dir = os.path.join(app_path, "Contents/MacOS")
                    if os.path.exists(macos_dir):
                        process_env['PATH'] = f"{macos_dir}:{process_env.get('PATH', '')}"
                        with open(log_file, "a") as f:
                            f.write(f"设置PATH: {process_env['PATH']}\n")

                    # 启动引导脚本
                    args = [python_path, bootstrap_path, "--skip-admin-check"]
                    with open(log_file, "a") as f:
                        f.write(f"执行命令: {' '.join(args)}\n")

                    process = subprocess.Popen(
                        args,
                        env=process_env,
                        cwd=resources_dir,
                        # 重定向标准输出和错误到日志文件
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )

                    # 等待一小段时间确保程序启动
                    time.sleep(2)

                    # 检查进程是否成功启动
                    if process.poll() is None:  # None表示进程仍在运行
                        with open(log_file, "a") as f:
                            f.write("使用bootstrap.py成功启动主程序\n")

                        # 如果使用Popen，我们可以捕获它的输出
                        stdout_data, stderr_data = process.communicate(timeout=1)
                        with open(log_file, "a") as f:
                            f.write("\n--- bootstrap.py 输出 ---\n")
                            f.write(stdout_data.decode('utf-8', errors='ignore'))
                            if stderr_data:
                                f.write("\n--- bootstrap.py 错误 ---\n")
                                f.write(stderr_data.decode('utf-8', errors='ignore'))
                            f.write("\n--- 输出结束 ---\n")

                        return True
                    else:
                        with open(log_file, "a") as f:
                            f.write(f"bootstrap.py进程退出，返回码: {process.returncode}\n")

                            # 捕获输出
                            stdout_data, stderr_data = process.communicate()
                            f.write("\n--- bootstrap.py 输出 ---\n")
                            f.write(stdout_data.decode('utf-8', errors='ignore'))
                            if stderr_data:
                                f.write("\n--- bootstrap.py 错误 ---\n")
                                f.write(stderr_data.decode('utf-8', errors='ignore'))
                            f.write("\n--- 输出结束 ---\n")

                # 如果bootstrap.py不存在或启动失败，创建一个简单的包装脚本
                with open(log_file, "a") as f:
                    f.write("\n尝试生成临时包装脚本...\n")

                # 创建临时脚本目录
                temp_dir = os.path.join(log_dir, "temp_scripts")
                os.makedirs(temp_dir, exist_ok=True)

                # 生成一个简单的包装脚本
                wrapper_script_path = os.path.join(temp_dir, "run_cursor_pro.py")
                with open(wrapper_script_path, "w") as wrapper_file:
                    wrapper_file.write(f"""#!/usr/bin/env python
# 自动生成的CursorPro包装脚本
import os
import sys
import subprocess
import time

# 添加必要的路径
app_path = "{app_path}"
resources_dir = os.path.join(app_path, "Contents/Resources")
frameworks_dir = os.path.join(app_path, "Contents/Frameworks")
sys.path.insert(0, resources_dir)
sys.path.insert(0, frameworks_dir)

# 设置环境变量
os.environ['PYTHONPATH'] = os.pathsep.join([resources_dir, frameworks_dir])

# 尝试运行main.py
main_path = os.path.join(resources_dir, "main.py")
if os.path.exists(main_path):
    print(f"执行main.py: {{main_path}}")
    sys.argv.append("--skip-admin-check")

    # 方式1: 使用exec执行
    try:
        with open(main_path, 'r') as main_file:
            code = main_file.read()
        exec(code, {{'__file__': main_path, '__name__': '__main__'}})
    except Exception as e:
        print(f"执行失败: {{e}}")

        # 方式2: 使用子进程执行
        try:
            subprocess.call([sys.executable, main_path, "--skip-admin-check"])
        except Exception as e:
            print(f"子进程执行失败: {{e}}")
""")

                # 使脚本可执行
                os.chmod(wrapper_script_path, 0o755)

                with open(log_file, "a") as f:
                    f.write(f"创建了临时包装脚本: {wrapper_script_path}\n")

                # 使用系统Python执行包装脚本
                python_path = "/usr/bin/python3"
                if not os.path.exists(python_path):
                    python_path = "/usr/bin/python"

                with open(log_file, "a") as f:
                    f.write(f"使用Python解释器执行包装脚本: {python_path}\n")

                process = subprocess.Popen(
                    [python_path, wrapper_script_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )

                # 等待一小段时间确保程序启动
                time.sleep(2)

                # 检查进程是否成功启动
                if process.poll() is None:  # None表示进程仍在运行
                    with open(log_file, "a") as f:
                        f.write("使用包装脚本成功启动主程序\n")
                    return True
                else:
                    with open(log_file, "a") as f:
                        f.write(f"包装脚本进程退出，返回码: {process.returncode}\n")

                        # 捕获输出
                        stdout_data, stderr_data = process.communicate()
                        f.write("\n--- 包装脚本输出 ---\n")
                        f.write(stdout_data.decode('utf-8', errors='ignore'))
                        if stderr_data:
                            f.write("\n--- 包装脚本错误 ---\n")
                            f.write(stderr_data.decode('utf-8', errors='ignore'))
                        f.write("\n--- 输出结束 ---\n")

                # 如果前面的方法都失败，继续使用原来的策略
            else:
                # Windows或Linux
                exe_path = sys.executable
                args = [exe_path, "--skip-admin-check"]
        else:
            # 开发环境
            current_dir = os.getcwd()
            args = [sys.executable, os.path.join(current_dir, "main.py"), "--skip-admin-check"]

        with open(log_file, "a") as f:
            f.write(f"最终执行命令: {' '.join(args)}\n")

        # 使用subprocess.Popen启动进程，并等待它完成
        process = subprocess.Popen(args)

        # 等待一小段时间确保程序启动
        time.sleep(2)

        # 检查进程是否成功启动
        if process.poll() is None:  # None表示进程仍在运行
            with open(log_file, "a") as f:
                f.write("主程序成功启动\n")
            return True
        else:
            with open(log_file, "a") as f:
                f.write(f"主程序启动失败，返回码: {process.returncode}\n")
            return False
    except Exception as e:
        with open(log_file, "a") as f:
            f.write(f"启动主程序失败: {e}\n")
            f.write(traceback.format_exc())
        return False

def main():
    """主函数，检查权限并在需要时请求"""
    print("=== 权限启动器启动 ===")
    print(f"Python版本: {sys.version}")
    print(f"运行路径: {sys.executable}")
    print(f"当前工作目录: {os.getcwd()}")
    print(f"命令行参数: {sys.argv}")
    print(f"是否打包环境: {is_frozen()}")

    app = QApplication(sys.argv)

    # 显示自定义图标，即使处于打包环境中
    app_icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "icon.png")
    if os.path.exists(app_icon_path):
        from PySide6.QtGui import QIcon
        app.setWindowIcon(QIcon(app_icon_path))

    # 如果是从管理员模式重启，直接启动应用程序
    if "--restart-as-admin" in sys.argv:
        print("检测到管理员权限重启标志")
        # 再次检查权限，确认确实获得了管理员权限
        has_admin = is_admin()
        if has_admin:
            print("确认已获得管理员权限，无弹窗启动应用程序")
            # 直接启动，不显示任何错误弹窗
            launch_app()
            return 0
        else:
            print("警告：权限请求可能未成功，但仍尝试启动应用程序")
            # 尝试启动应用，无论成功与否都不显示弹窗
            launch_app()
            return 0

    # 如果命令行中包含--skip-admin-check参数，则跳过权限检查
    if "--skip-admin-check" in sys.argv:
        print("跳过管理员权限检查")
        return 0

    # 检查是否已经有管理员权限
    has_admin = is_admin()
    current_platform = platform.system()
    print(f"当前操作系统: {current_platform}")
    print(f"当前是否有管理员权限: {has_admin}")

    if has_admin:
        print("已拥有管理员权限，直接启动应用程序")
        # 直接启动，忽略启动结果
        launch_app()
        return 0
    else:
        print("需要请求管理员权限，直接进行系统授权")

        try:
            # 检查打包环境下的应用程序路径
            if is_frozen() and platform.system() == 'Darwin':
                app_path = get_app_path()
                print(f"应用程序路径: {app_path}")

                # 列出MacOS目录内容
                macos_dir = os.path.join(app_path, "Contents/MacOS")
                if os.path.exists(macos_dir):
                    print(f"MacOS目录内容:")
                    for item in os.listdir(macos_dir):
                        file_path = os.path.join(macos_dir, item)
                        is_executable = os.access(file_path, os.X_OK)
                        print(f"  {item} {'(可执行)' if is_executable else ''}")

            # 直接请求管理员权限，不显示询问对话框
            success = restart_as_admin()
            print(f"请求管理员权限结果: {'成功' if success else '失败'}")

            if success:
                # 成功请求了权限，直接退出当前进程，管理员权限的进程会自动启动
                print("权限请求成功，程序将以管理员权限重新启动")
                return 0
            else:
                # 请求失败，显示错误消息
                error_msg = QMessageBox()
                error_msg.setWindowTitle("权限请求失败")
                error_msg.setText("无法获取管理员权限。")
                error_msg.setInformativeText("程序将退出。")
                error_msg.setIcon(QMessageBox.Critical)
                error_msg.exec()
                return 1
        except Exception as e:
            # 捕获任何异常，显示给用户
            error_msg = QMessageBox()
            error_msg.setWindowTitle("发生错误")
            error_msg.setText("请求管理员权限时出现错误。")
            error_msg.setDetailedText(f"错误详情: {str(e)}\n\n{traceback.format_exc()}")
            error_msg.setIcon(QMessageBox.Critical)
            error_msg.exec()
            return 1

if __name__ == "__main__":
    sys.exit(main())