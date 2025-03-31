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
        logger.info(f"执行macOS命令: {cmd}")
        try:
            output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
            logger.info(f"命令执行输出: {output.decode()}")
        except subprocess.CalledProcessError as e:
            logger.error(f"命令执行失败: {e.output.decode()}")
            return False
    elif system == "Linux":
        cmd = f'curl -fsSL {base_url}/cursor_linux_id_modifier.sh | sudo bash'
        logger.info(f"执行Linux命令: {cmd}")
        try:
            output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
            logger.info(f"命令执行输出: {output.decode()}")
        except subprocess.CalledProcessError as e:
            logger.error(f"命令执行失败: {e.output.decode()}")
            return False
    elif system == "Windows":
        cmd = f'irm {base_url}/cursor_win_id_modifier.ps1 | iex'
        logger.info(f"执行Windows命令: {cmd}")
        try:
            output = subprocess.check_output(["powershell", "-Command", cmd], stderr=subprocess.STDOUT)
            logger.info(f"命令执行输出: {output.decode()}")
        except subprocess.CalledProcessError as e:
            logger.error(f"命令执行失败: {e.output.decode()}")
            return False
    else:
        logger.error(f"不支持的操作系统: {system}")
        return False

    return True
