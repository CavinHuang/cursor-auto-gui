#!/usr/bin/env python
"""
Cursor Pro 主程序入口
"""
from src.main import main
import sys
import os
import platform
import subprocess

def check_launcher_exists():
    """检查launcher.py是否存在"""
    return os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), "launcher.py"))

def is_from_launcher():
    """检查是否从launcher启动"""
    # 检查命令行参数
    cmd_check = "--skip-admin-check" in sys.argv
    # 检查环境变量
    env_check = os.environ.get('SKIP_ADMIN_CHECK') == '1'
    return cmd_check or env_check

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

if __name__ == "__main__":
    # 检查是否从launcher启动
    if is_from_launcher():
        # 如果是通过launcher启动或设置了环境变量，移除命令行参数
        if "--skip-admin-check" in sys.argv:
            sys.argv.remove("--skip-admin-check")

        # 检查是否具有管理员权限并记录
        has_admin = is_admin()
        if has_admin:
            print("程序当前具有管理员权限")
        else:
            print("程序当前没有管理员权限，部分功能可能受限")

        try:
            exit_code = main()
            sys.exit(exit_code)
        except Exception as e:
            print(f"程序执行出错: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    else:
        # 检查launcher.py是否存在
        if not check_launcher_exists():
            print("警告: launcher.py 文件不存在，这可能会导致权限请求功能无法正常工作")
            print("请确保launcher.py文件存在于应用程序根目录")

            # 即使没有launcher.py，也尝试运行主程序
            print("尝试直接运行主程序...")
            try:
                exit_code = main()
                sys.exit(exit_code)
            except Exception as e:
                print(f"程序执行出错: {e}")
                import traceback
                traceback.print_exc()
                sys.exit(1)
        else:
            # 如果不是通过launcher启动的，则尝试启动launcher
            launcher_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "launcher.py")

            print("请使用 launcher.py 启动程序以进行管理员权限验证")
            print("正在自动重定向到launcher.py...")

            try:
                # 启动launcher.py
                if platform.system() == 'Windows':
                    os.system(f'start pythonw "{launcher_path}"')
                elif platform.system() == 'Darwin':  # macOS
                    os.system(f'python3 "{launcher_path}" &')
                else:  # Linux
                    os.system(f'python3 "{launcher_path}" &')
            except Exception as e:
                print(f"启动launcher.py失败: {e}")
                print("请手动运行launcher.py")

        sys.exit(1)