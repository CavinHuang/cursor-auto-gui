import os
import sys
import platform
import subprocess
import tempfile

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
                print(f"检查 macOS 管理员权限时出错: {e}")
                return False
        else:  # Linux 和其他系统
            return os.geteuid() == 0
    except Exception as e:
        print(f"检查管理员权限时出错: {e}")
        return False

def restart_as_admin():
    """以管理员权限重启程序"""
    try:
        if platform.system() == 'Windows':
            import ctypes
            # 获取当前脚本的路径
            script = sys.executable
            params = sys.argv

            # 以管理员权限重新启动程序
            try:
                ctypes.windll.shell32.ShellExecuteW(None, "runas", script, " ".join(params[1:]), None, 1)
                return True
            except Exception as e:
                print(f"Windows 平台请求管理员权限失败: {e}")
                return False

        elif platform.system() == 'Darwin':  # macOS
            try:
                print("=== macOS平台权限请求开始 ===")
                print(f"当前工作目录: {os.getcwd()}")
                print(f"当前Python解释器: {sys.executable}")
                print(f"命令行参数: {sys.argv}")

                # 获取当前工作目录
                current_dir = os.getcwd()

                # 创建临时脚本文件，包含完整的命令和当前工作目录
                with tempfile.NamedTemporaryFile(suffix='.sh', delete=False) as temp:
                    temp_path = temp.name
                    script_content = f"""#!/bin/bash
echo "=== 管理员权限脚本开始执行 ==="
cd "{current_dir}"
echo "当前目录: $(pwd)"
"{sys.executable}" {' '.join([f'"{arg}"' for arg in sys.argv[1:]])}
echo "=== 管理员权限脚本执行完成 ==="
"""
                    temp.write(script_content.encode())
                    print(f"临时脚本路径: {temp_path}")
                    print(f"脚本内容:\n{script_content}")

                # 给临时脚本添加执行权限
                os.chmod(temp_path, 0o755)
                print(f"已设置脚本执行权限: {oct(os.stat(temp_path).st_mode)}")

                # 构建 AppleScript 命令并直接执行
                applescript = f'''
                do shell script "\\"{temp_path}\\"" with administrator privileges
                '''

                # 输出完整的AppleScript命令用于调试
                print(f"AppleScript:\n{applescript}")

                # 使用临时文件写入AppleScript
                with tempfile.NamedTemporaryFile(suffix='.scpt', delete=False) as scpt:
                    scpt_path = scpt.name
                    scpt.write(applescript.encode())

                # 给AppleScript文件添加执行权限
                os.chmod(scpt_path, 0o755)

                # 执行AppleScript命令
                cmd = ['osascript', scpt_path]
                print(f"执行命令: {' '.join(cmd)}")

                # 改用subprocess.run以等待命令完成，并捕获输出
                process = subprocess.Popen(cmd,
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE)

                print("AppleScript命令已启动，等待授权对话框...")
                print("=== macOS平台权限请求结束 ===")
                return True
            except Exception as e:
                print(f"macOS平台请求管理员权限失败，错误详情: {str(e)}")
                import traceback
                traceback.print_exc()
                return False
        else:  # Linux 和其他系统
            try:
                # 尝试使用 pkexec
                cmd = ['pkexec', sys.executable] + sys.argv[1:]
                subprocess.Popen(cmd)
                return True
            except Exception as e1:
                print(f"pkexec 失败: {e1}")
                try:
                    # 如果 pkexec 失败，尝试 gksudo
                    cmd = ['gksudo', sys.executable] + sys.argv[1:]
                    subprocess.Popen(cmd)
                    return True
                except Exception as e2:
                    print(f"gksudo 失败: {e2}")
                    try:
                        # 最后尝试 sudo
                        cmd = ['sudo', sys.executable] + sys.argv[1:]
                        subprocess.Popen(cmd)
                        return True
                    except Exception as e3:
                        print(f"sudo 失败: {e3}")
                        return False
    except Exception as e:
        print(f"请求管理员权限时出现未知错误: {e}")
        return False