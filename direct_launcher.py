#!/usr/bin/env python
"""
CursorPro直接启动器
这个启动器不使用任何复杂的逻辑，直接尝试启动主程序
它绕过了权限检查和多层调用，用于测试和诊断
"""

import os
import sys
import platform
import subprocess
import time
import traceback

def main():
    # 设置日志
    log_dir = os.path.expanduser("~/Library/Logs/CursorPro")
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, "direct_launcher.log")

    with open(log_path, "a") as log:
        log.write(f"\n\n=== 直接启动器启动: {time.strftime('%Y-%m-%d %H:%M:%S')} ===\n")
        log.write(f"Python版本: {sys.version}\n")
        log.write(f"可执行文件: {sys.executable}\n")
        log.write(f"当前工作目录: {os.getcwd()}\n")
        log.write(f"命令行参数: {sys.argv}\n")

        # 查找应用程序路径
        script_path = os.path.abspath(__file__)
        log.write(f"脚本路径: {script_path}\n")

        # 查找main.py
        if "Contents/Resources" in script_path:
            resources_dir = os.path.dirname(script_path)
        else:
            # 尝试猜测Resources目录
            if ".app/Contents/" in script_path:
                app_path = script_path.split(".app/Contents/")[0] + ".app"
                resources_dir = os.path.join(app_path, "Contents/Resources")
            else:
                # 假设我们在项目根目录
                resources_dir = os.getcwd()

        log.write(f"Resources目录: {resources_dir}\n")

        # 查找main.py
        main_path = os.path.join(resources_dir, "main.py")
        if not os.path.exists(main_path):
            log.write(f"未找到main.py: {main_path}\n")
            # 尝试在当前目录找
            main_path = os.path.join(os.path.dirname(script_path), "main.py")

        if os.path.exists(main_path):
            log.write(f"找到main.py: {main_path}\n")

            # 设置Python路径
            src_dir = os.path.join(resources_dir, "src")
            if os.path.exists(src_dir):
                sys.path.insert(0, src_dir)
                log.write(f"添加src目录到Python路径: {src_dir}\n")

            sys.path.insert(0, resources_dir)
            log.write(f"添加Resources目录到Python路径: {resources_dir}\n")

            # 设置跳过权限检查参数
            if "--skip-admin-check" not in sys.argv:
                sys.argv.append("--skip-admin-check")

            log.write(f"最终命令行参数: {sys.argv}\n")

            try:
                # 方法1: 直接执行main.py
                log.write("尝试直接执行main.py...\n")
                with open(main_path, 'r') as f:
                    main_code = f.read()

                # 更改工作目录到Resources
                os.chdir(resources_dir)
                log.write(f"更改工作目录到: {resources_dir}\n")

                # 执行main.py的代码
                main_globals = {
                    '__file__': main_path,
                    '__name__': '__main__'
                }

                log.write("开始执行main.py代码...\n")
                exec(main_code, main_globals)
                log.write("main.py执行完成\n")
                return 0
            except Exception as e:
                log.write(f"执行main.py失败: {e}\n")
                log.write(traceback.format_exc())

                # 方法2: 使用子进程
                try:
                    log.write("\n尝试使用子进程执行main.py...\n")

                    # 使用系统Python解释器
                    python_exe = "/usr/bin/python3"
                    if not os.path.exists(python_exe):
                        python_exe = "/usr/bin/python"

                    log.write(f"使用Python解释器: {python_exe}\n")

                    # 准备环境变量
                    env = os.environ.copy()
                    env['PYTHONPATH'] = resources_dir

                    # 执行命令
                    cmd = [python_exe, main_path, "--skip-admin-check"]
                    log.write(f"执行命令: {' '.join(cmd)}\n")

                    process = subprocess.Popen(
                        cmd,
                        env=env,
                        cwd=resources_dir
                    )

                    # 等待程序启动
                    time.sleep(2)

                    # 检查进程是否在运行
                    if process.poll() is None:
                        log.write("主程序成功启动\n")
                        return 0
                    else:
                        log.write(f"主程序启动失败，返回码: {process.returncode}\n")
                except Exception as e:
                    log.write(f"使用子进程执行main.py失败: {e}\n")
                    log.write(traceback.format_exc())
        else:
            log.write(f"未找到main.py，无法启动主程序\n")

        log.write("所有启动尝试都失败\n")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"直接启动器发生致命错误: {e}")
        traceback.print_exc()

        # 将错误写入日志
        log_dir = os.path.expanduser("~/Library/Logs/CursorPro")
        os.makedirs(log_dir, exist_ok=True)
        with open(os.path.join(log_dir, "direct_launcher_error.log"), "a") as error_log:
            error_log.write(f"\n=== 致命错误: {time.strftime('%Y-%m-%d %H:%M:%S')} ===\n")
            error_log.write(f"Python版本: {sys.version}\n")
            error_log.write(f"错误: {e}\n")
            error_log.write(traceback.format_exc())

        sys.exit(1)