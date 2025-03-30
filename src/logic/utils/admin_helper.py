import os
import sys
import platform
import subprocess
import tempfile
import shutil
import logging

# 配置日志
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('admin_helper')

def is_admin():
    """检查当前程序是否具有管理员权限"""
    try:
        if platform.system() == 'Windows':
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        elif platform.system() == 'Darwin':  # macOS
            # 在 macOS 上使用 sudo -n 命令检查是否有管理员权限
            # -n 选项表示非交互模式，如果需要密码就直接失败
            try:
                result = subprocess.run(
                    ['sudo', '-n', 'true'],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    check=False
                )
                if result.returncode == 0:
                    return True

                # 如果上述检查失败，再尝试写入一个需要管理员权限的目录
                test_dir = '/Library/Preferences'
                test_file = os.path.join(test_dir, f'cursor_pro_admin_test_{os.getpid()}.txt')
                try:
                    with open(test_file, 'w') as f:
                        f.write('test')
                    os.remove(test_file)
                    return True
                except (IOError, PermissionError):
                    return False
            except Exception as e:
                logger.error(f"检查 macOS 管理员权限时出错: {e}")
                return False
        else:  # Linux 和其他系统
            return os.geteuid() == 0
    except Exception as e:
        logger.error(f"检查管理员权限时出错: {e}")
        return False

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
                logger.warning("无法找到.app包路径，使用当前目录")
                return os.getcwd()

            return app_path
        else:
            # Windows或Linux
            return os.path.dirname(sys.executable)
    else:
        # 开发环境，返回当前工作目录
        return os.getcwd()

def find_executable_in_app(app_path):
    """在macOS应用包中查找可执行文件"""
    logger.info(f"在应用包中查找可执行文件: {app_path}")

    # 标准位置的可执行文件名称尝试列表
    possible_names = ["CursorPro", app_path.split("/")[-1].replace(".app", "")]

    # MacOS目录
    macos_dir = os.path.join(app_path, "Contents/MacOS")
    if not os.path.exists(macos_dir):
        logger.error(f"MacOS目录不存在: {macos_dir}")
        return None

    # 列出目录内容
    logger.info(f"MacOS目录内容:")
    for item in os.listdir(macos_dir):
        file_path = os.path.join(macos_dir, item)
        is_exec = os.access(file_path, os.X_OK) and os.path.isfile(file_path)
        logger.info(f"  {item} {'(可执行)' if is_exec else ''}")

    # 首先检查可能的标准名称
    for name in possible_names:
        exe_path = os.path.join(macos_dir, name)
        if os.path.exists(exe_path) and os.access(exe_path, os.X_OK):
            logger.info(f"找到标准名称可执行文件: {exe_path}")
            return exe_path

    # 如果未找到标准名称，查找任何可执行文件
    for item in os.listdir(macos_dir):
        file_path = os.path.join(macos_dir, item)
        if os.path.isfile(file_path) and os.access(file_path, os.X_OK):
            logger.info(f"找到替代可执行文件: {file_path}")
            return file_path

    logger.error(f"在应用包中未找到可执行文件")
    return None

def restart_as_admin():
    """以管理员权限重启程序"""
    try:
        logger.info(f"重启为管理员权限 - 操作系统: {platform.system()}")
        logger.info(f"当前工作目录: {os.getcwd()}")
        logger.info(f"Python解释器: {sys.executable}")
        logger.info(f"命令行参数: {sys.argv}")
        logger.info(f"是否打包环境: {is_frozen()}")

        if platform.system() == 'Windows':
            import ctypes
            # 获取当前脚本的路径
            script = sys.executable
            # 始终使用launcher.py作为启动脚本
            params = ["launcher.py", "--restart-as-admin"]

            # 以管理员权限重新启动程序
            try:
                logger.info(f"Windows平台请求管理员权限: {script} {' '.join(params)}")
                ctypes.windll.shell32.ShellExecuteW(None, "runas", script, " ".join(params), None, 1)
                return True
            except Exception as e:
                logger.error(f"Windows平台请求管理员权限失败: {e}")
                return False

        elif platform.system() == 'Darwin':  # macOS
            try:
                logger.info("=== macOS平台权限请求开始 ===")

                # 获取当前可执行文件路径
                if is_frozen():
                    # 如果是打包环境，找到.app包的路径
                    app_path = get_app_path()
                    logger.info(f"应用包路径: {app_path}")

                    # 查找可执行文件
                    exe_path = find_executable_in_app(app_path)
                    if not exe_path:
                        logger.error("未能找到可用的可执行文件，无法启动")
                        return False

                    # 检查可执行文件权限
                    if not os.access(exe_path, os.X_OK):
                        logger.warning(f"可执行文件没有执行权限，尝试修复: {exe_path}")
                        try:
                            os.chmod(exe_path, 0o755)
                            logger.info("权限修复完成")
                        except Exception as e:
                            logger.error(f"修复权限失败: {e}")

                    exe_name = os.path.basename(exe_path)
                    logger.info(f"找到可执行文件: {exe_path}")

                    # 在打包环境中，直接使用open命令以管理员权限打开应用
                    with tempfile.NamedTemporaryFile(suffix='.sh', delete=False) as temp:
                        temp_path = temp.name
                        script_content = f"""#!/bin/bash
echo "=== 管理员权限启动脚本开始执行 ==="
echo "当前目录: $(pwd)"
echo "应用包路径: {app_path}"
echo "可执行文件: {exe_path}"

# 检查可执行文件是否存在
if [ ! -f "{exe_path}" ]; then
    echo "错误: 可执行文件不存在: {exe_path}"
    echo "MacOS目录内容:"
    ls -la "{app_path}/Contents/MacOS/"
    exit 1
fi

# 检查可执行文件权限
if [ ! -x "{exe_path}" ]; then
    echo "警告: 可执行文件没有执行权限，修复中..."
    chmod +x "{exe_path}"
    if [ $? -ne 0 ]; then
        echo "错误: 无法修复权限"
        exit 1
    fi
    echo "权限修复完成"
fi

# 使用sudo打开应用程序
echo "执行: sudo \\"{exe_path}\\" --restart-as-admin"
sudo "{exe_path}" --restart-as-admin
EXIT_CODE=$?
echo "退出状态: $EXIT_CODE"
echo "=== 管理员权限启动脚本执行完成 ==="
exit $EXIT_CODE
"""
                        temp.write(script_content.encode())

                    # 设置脚本可执行权限
                    os.chmod(temp_path, 0o755)
                    logger.info(f"临时脚本创建成功: {temp_path}")
                    logger.debug(f"临时脚本内容:\n{script_content}")

                    # 构建AppleScript
                    applescript = f'''
                    do shell script "\\"{temp_path}\\"" with administrator privileges
                    '''
                else:
                    # 开发环境中的启动逻辑
                    logger.info(f"开发环境运行")

                    # 获取当前工作目录
                    current_dir = os.getcwd()

                    # 始终使用launcher.py作为启动脚本
                    launcher_path = os.path.join(current_dir, "launcher.py")
                    if not os.path.exists(launcher_path):
                        logger.error(f"错误: launcher.py 不存在于 {launcher_path}")
                        return False

                    # 创建临时脚本文件，包含完整的命令和当前工作目录
                    with tempfile.NamedTemporaryFile(suffix='.sh', delete=False) as temp:
                        temp_path = temp.name
                        script_content = f"""#!/bin/bash
echo "=== 管理员权限脚本开始执行 ==="
cd "{current_dir}"
echo "当前目录: $(pwd)"
"{sys.executable}" "{launcher_path}" --restart-as-admin
EXIT_CODE=$?
echo "退出状态: $EXIT_CODE"
echo "=== 管理员权限脚本执行完成 ==="
exit $EXIT_CODE
"""
                        temp.write(script_content.encode())

                    # 给临时脚本添加执行权限
                    os.chmod(temp_path, 0o755)
                    logger.info(f"临时脚本创建成功: {temp_path}")
                    logger.debug(f"临时脚本内容:\n{script_content}")

                    # 构建AppleScript
                    applescript = f'''
                    do shell script "\\"{temp_path}\\"" with administrator privileges
                    '''

                # 使用临时文件写入AppleScript
                with tempfile.NamedTemporaryFile(suffix='.scpt', delete=False) as scpt:
                    scpt_path = scpt.name
                    scpt.write(applescript.encode())

                # 给AppleScript文件添加执行权限
                os.chmod(scpt_path, 0o755)
                logger.info(f"AppleScript创建成功: {scpt_path}")

                # 执行AppleScript命令
                cmd = ['osascript', scpt_path]
                logger.info(f"执行命令: {' '.join(cmd)}")

                # 启动进程并捕获输出（便于调试）
                process = subprocess.Popen(cmd,
                                          stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE)
                stdout, stderr = process.communicate()

                if stdout:
                    logger.info(f"AppleScript标准输出: {stdout.decode()}")
                if stderr:
                    logger.warning(f"AppleScript标准错误: {stderr.decode()}")

                logger.info(f"AppleScript命令已执行完毕，退出码: {process.returncode}")

                # 清理临时文件
                try:
                    os.remove(temp_path)
                    os.remove(scpt_path)
                    logger.info("临时文件已清理")
                except Exception as e:
                    logger.warning(f"清理临时文件失败: {e}")

                logger.info("=== macOS平台权限请求结束 ===")

                # 即使我们看到错误，也返回True，让主程序退出
                # 实际上无论是否成功，用户都会在AppleScript处看到结果
                return True
            except Exception as e:
                logger.error(f"macOS平台请求管理员权限失败，错误详情: {str(e)}")
                import traceback
                logger.error(traceback.format_exc())
                return False
        else:  # Linux 和其他系统
            try:
                # 尝试使用 pkexec
                logger.info("Linux平台请求管理员权限，尝试pkexec...")
                cmd = ['pkexec', sys.executable] + sys.argv
                subprocess.Popen(cmd)
                return True
            except Exception as e1:
                logger.warning(f"pkexec 失败: {e1}")
                try:
                    # 如果 pkexec 失败，尝试 gksudo
                    logger.info("尝试gksudo...")
                    cmd = ['gksudo', sys.executable] + sys.argv
                    subprocess.Popen(cmd)
                    return True
                except Exception as e2:
                    logger.warning(f"gksudo 失败: {e2}")
                    try:
                        # 最后尝试 sudo
                        logger.info("尝试sudo...")
                        cmd = ['sudo', sys.executable] + sys.argv
                        subprocess.Popen(cmd)
                        return True
                    except Exception as e3:
                        logger.error(f"sudo 失败: {e3}")
                        return False
    except Exception as e:
        logger.error(f"请求管理员权限时出现未知错误: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False