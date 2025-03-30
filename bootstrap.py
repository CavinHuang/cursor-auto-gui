#!/usr/bin/env python
"""
Cursor Pro 启动引导脚本
这个脚本负责设置正确的环境变量和路径，然后启动主程序
"""

import os
import sys
import traceback
import subprocess
import time

def setup_paths():
    """设置正确的路径和环境变量"""
    # 获取当前脚本的目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"脚本目录: {script_dir}")

    # 将当前目录添加到Python路径
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)

    # 获取应用程序根目录
    if 'Resources' in script_dir:
        app_root = os.path.dirname(os.path.dirname(script_dir))
        print(f"应用程序根目录: {app_root}")
        frameworks_dir = os.path.join(app_root, 'Frameworks')
        if os.path.exists(frameworks_dir) and frameworks_dir not in sys.path:
            sys.path.insert(0, frameworks_dir)
            print(f"添加Frameworks目录到路径: {frameworks_dir}")

        # 添加MacOS目录到PATH环境变量
        macos_dir = os.path.join(app_root, 'MacOS')
        if os.path.exists(macos_dir):
            os.environ['PATH'] = f"{macos_dir}:{os.environ.get('PATH', '')}"
            print(f"添加MacOS目录到PATH: {macos_dir}")

    # 将src目录添加到Python路径
    src_dir = os.path.join(script_dir, 'src')
    if os.path.exists(src_dir) and src_dir not in sys.path:
        sys.path.insert(0, src_dir)
        print(f"添加src目录到路径: {src_dir}")

    # 确保命令行参数中包含--skip-admin-check
    if "--skip-admin-check" not in sys.argv:
        sys.argv.append("--skip-admin-check")
        print("添加--skip-admin-check到命令行参数")

    # 设置PYTHONHOME和PYTHONPATH环境变量
    if 'Resources' in script_dir:
        app_root = os.path.dirname(os.path.dirname(script_dir))
        os.environ['PYTHONHOME'] = app_root
        print(f"设置PYTHONHOME为: {app_root}")

        python_path = [
            script_dir,
            os.path.join(app_root, 'Frameworks'),
            os.path.join(app_root, 'Frameworks/lib-dynload')
        ]
        os.environ['PYTHONPATH'] = os.pathsep.join(python_path)
        print(f"设置PYTHONPATH为: {os.environ['PYTHONPATH']}")

    # 打印调试信息
    print(f"当前工作目录: {os.getcwd()}")
    print(f"Python可执行文件: {sys.executable}")
    print(f"Python版本: {sys.version}")
    print(f"Python路径: {sys.path}")
    print(f"命令行参数: {sys.argv}")
    print(f"环境变量PATH: {os.environ.get('PATH')}")

def run_main():
    """运行主程序"""
    try:
        # 设置正确的路径
        print("设置路径和环境变量...")
        setup_paths()

        # 模式1: 尝试使用子进程启动main.py
        try:
            print("\n尝试模式1: 使用子进程执行main.py...")
            main_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "main.py")

            if os.path.exists(main_path):
                print(f"找到main.py: {main_path}")

                # 使用与当前脚本相同的Python解释器
                python_exe = sys.executable
                if not python_exe or not os.path.exists(python_exe) or python_exe.endswith('CursorPro'):
                    # 在MacOS目录中查找Python解释器
                    if 'Resources' in os.path.abspath(__file__):
                        app_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                        macos_dir = os.path.join(app_root, 'MacOS')
                        python_candidates = ['python', 'python3', 'Python']

                        for candidate in python_candidates:
                            candidate_path = os.path.join(macos_dir, candidate)
                            if os.path.exists(candidate_path) and os.access(candidate_path, os.X_OK):
                                python_exe = candidate_path
                                print(f"找到Python解释器: {python_exe}")
                                break

                    # 如果仍未找到，使用系统Python
                    if not python_exe or not os.path.exists(python_exe) or python_exe.endswith('CursorPro'):
                        python_exe = "/usr/bin/python3"
                        print(f"使用系统Python解释器: {python_exe}")

                print(f"使用Python解释器: {python_exe}")

                # 准备环境变量
                env = os.environ.copy()

                # 设置工作目录为Resources目录
                resources_dir = os.path.dirname(main_path)

                # 使用子进程启动main.py
                cmd = [python_exe, main_path, "--skip-admin-check"]
                print(f"执行命令: {' '.join(cmd)}")

                process = subprocess.Popen(
                    cmd,
                    env=env,
                    cwd=resources_dir
                )

                # 等待一小段时间确保程序启动
                time.sleep(2)

                # 检查进程是否成功启动
                if process.poll() is None:  # None表示进程仍在运行
                    print("主程序成功启动（子进程方式）")
                    # 让主进程继续运行，而不是等待它结束
                    return 0
                else:
                    print(f"主程序启动失败，返回码: {process.returncode}")
            else:
                print(f"未找到main.py: {main_path}")
        except Exception as e:
            print(f"使用子进程执行main.py失败: {e}")
            traceback.print_exc()

        # 模式2: 尝试直接导入main模块
        try:
            print("\n尝试模式2: 直接导入main模块...")
            import main
            if hasattr(main, 'main'):
                print("找到main.main函数，执行...")
                exit_code = main.main()
                print(f"main.main()执行完成，返回码: {exit_code}")
                return exit_code
            else:
                print("main模块中没有找到main函数")
        except ImportError as e:
            print(f"导入main模块失败: {e}")
            traceback.print_exc()

        # 模式3: 尝试直接导入src.main模块
        try:
            print("\n尝试模式3: 直接导入src.main模块...")
            from src.main import main as run_main
            print("找到src.main.main函数，执行...")
            exit_code = run_main()
            print(f"src.main.main()执行完成，返回码: {exit_code}")
            return exit_code
        except ImportError as e:
            print(f"导入src.main失败: {e}")
            traceback.print_exc()

        # 模式4: 尝试读取和执行main.py文件
        try:
            print("\n尝试模式4: 使用exec执行main.py...")
            main_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "main.py")
            if os.path.exists(main_path):
                # 读取main.py内容
                with open(main_path, 'r') as main_file:
                    main_code = main_file.read()

                # 将main.py内容作为模块执行
                main_globals = {'__file__': main_path, '__name__': '__main__'}
                print(f"执行main.py: {main_path}")
                exec(main_code, main_globals)
                print("main.py执行完成")
                return 0
            else:
                print(f"无法找到main.py文件: {main_path}")
        except Exception as e:
            print(f"使用exec执行main.py失败: {e}")
            traceback.print_exc()

        # 所有尝试都失败了
        print("\n所有启动尝试都失败了")
        return 1
    except Exception as e:
        print(f"运行主程序时出错: {e}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    print(f"\n==== Cursor Pro 启动引导脚本启动 {time.strftime('%Y-%m-%d %H:%M:%S')} ====")
    exit_code = run_main()
    print(f"\n==== 引导脚本退出，返回码: {exit_code} ====")
    sys.exit(exit_code)