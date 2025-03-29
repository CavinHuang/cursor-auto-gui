#!/usr/bin/env python
"""
Cursor Pro 主程序入口
"""
from src.main import main
import sys
import os

if __name__ == "__main__":
    # 检查launcher.py是否存在，如果不存在则创建警告
    if not os.path.exists("launcher.py"):
        print("警告: launcher.py 文件不存在，这可能会导致权限请求功能无法正常工作")

    # 检查命令行参数，如果存在--skip-admin-check，则继续执行
    # 否则提示用户应该使用launcher.py启动程序
    if "--skip-admin-check" in sys.argv:
        # 删除参数，避免对后续代码造成影响
        sys.argv.remove("--skip-admin-check")
        try:
            exit_code = main()
            sys.exit(exit_code)
        except Exception as e:
            print(f"程序执行出错: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    else:
        print("请使用 launcher.py 启动程序以进行权限检查")
        print("示例: python launcher.py")
        sys.exit(1)