import platform
import os
import subprocess

from src.logic.log import logger

def go_cursor_help():
    system = platform.system()
    logger.info(f"当前操作系统: {system}")

    base_url = "https://aizaozao.com/accelerate.php/https://raw.githubusercontent.com/yuaotian/go-cursor-help/refs/heads/master/scripts/run"

    if system == "Darwin":  # macOS
        cmd = f'curl -fsSL {base_url}/cursor_mac_id_modifier.sh | sudo bash'
        logger.info("执行macOS命令")
        os.system(cmd)
    elif system == "Linux":
        cmd = f'curl -fsSL {base_url}/cursor_linux_id_modifier.sh | sudo bash'
        logger.info("执行Linux命令")
        os.system(cmd)
    elif system == "Windows":
        cmd = f'irm {base_url}/cursor_win_id_modifier.ps1 | iex'
        logger.info("执行Windows命令")
        # 在Windows上使用PowerShell执行命令
        subprocess.run(["powershell", "-Command", cmd], shell=True)
    else:
        logger.error(f"不支持的操作系统: {system}")
        return False

    return True
