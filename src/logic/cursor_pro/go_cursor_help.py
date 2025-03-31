import platform
import os
import subprocess
import tempfile
import shlex
import time
import sys

from src.logic.log import logger

def go_cursor_help():
    """
    获取cursor-help脚本并提供给用户执行指令
    完全避免在进程中执行sudo命令，防止内存问题
    """
    system = platform.system()
    logger.info(f"当前操作系统: {system}")

    base_url = "https://aizaozao.com/accelerate.php/https://raw.githubusercontent.com/yuaotian/go-cursor-help/refs/heads/master/scripts/run"

    try:
        # 创建用户主目录下的临时目录
        home_dir = os.path.expanduser("~")
        script_dir = os.path.join(home_dir, ".cursor_reset_scripts")
        os.makedirs(script_dir, exist_ok=True)

        if system == "Darwin":  # macOS
            # 确定脚本路径
            script_path = os.path.join(script_dir, "cursor_mac_reset.sh")

            # 下载脚本
            logger.info(f"下载macOS重置脚本...")
            download_cmd = f'curl -o "{script_path}" -fsSL {base_url}/cursor_mac_id_modifier.sh'

            try:
                subprocess.run(download_cmd, shell=True, check=True)
                # 设置脚本执行权限
                os.chmod(script_path, 0o755)
                logger.info(f"脚本已保存至: {script_path}")

                # 给用户显示执行命令
                cmd_to_show = f"sudo bash '{script_path}'"
                logger.info("========================================")
                logger.info(f"请手动在终端中执行以下命令:")
                logger.info(cmd_to_show)
                logger.info("========================================")
                logger.info("执行后请按照提示操作，完成后重启Cursor应用")

                # 尝试打开终端并显示命令
                try:
                    # 尝试打开新终端窗口
                    terminal_cmd = f"osascript -e 'tell application \"Terminal\" to do script \"{cmd_to_show}\"'"
                    subprocess.run(terminal_cmd, shell=True)
                    logger.info("已尝试打开终端窗口，请检查并执行命令")
                except Exception as e:
                    logger.warning(f"无法自动打开终端: {str(e)}")

                return True

            except subprocess.CalledProcessError as e:
                logger.error(f"下载脚本失败: {str(e)}")
                return False

        elif system == "Windows":
            # Windows PowerShell脚本
            script_path = os.path.join(script_dir, "cursor_win_reset.ps1")

            # 下载脚本
            logger.info(f"下载Windows重置脚本...")
            download_cmd = f'curl -o "{script_path}" -fsSL {base_url}/cursor_win_id_modifier.ps1'

            try:
                # 使用subprocess.run确保下载成功
                subprocess.run(download_cmd, shell=True, check=True)
                logger.info(f"脚本已保存至: {script_path}")

                # 给用户显示执行命令
                cmd_to_show = f"powershell -ExecutionPolicy Bypass -File \"{script_path}\""
                logger.info("========================================")
                logger.info(f"请以管理员身份在PowerShell中执行以下命令:")
                logger.info(cmd_to_show)
                logger.info("========================================")

                # 尝试打开PowerShell
                try:
                    # 打开cmd并显示命令
                    subprocess.run(f'start cmd /k "echo 请以管理员身份执行: {cmd_to_show}"', shell=True)
                    logger.info("已尝试打开命令提示符窗口，请以管理员身份执行命令")
                except Exception as e:
                    logger.warning(f"无法自动打开命令提示符: {str(e)}")

                return True

            except subprocess.CalledProcessError as e:
                logger.error(f"下载脚本失败: {str(e)}")
                return False

        elif system == "Linux":
            # Linux bash脚本
            script_path = os.path.join(script_dir, "cursor_linux_reset.sh")

            # 下载脚本
            logger.info(f"下载Linux重置脚本...")
            download_cmd = f'curl -o "{script_path}" -fsSL {base_url}/cursor_linux_id_modifier.sh'

            try:
                subprocess.run(download_cmd, shell=True, check=True)
                # 设置脚本执行权限
                os.chmod(script_path, 0o755)
                logger.info(f"脚本已保存至: {script_path}")

                # 给用户显示执行命令
                cmd_to_show = f"sudo bash '{script_path}'"
                logger.info("========================================")
                logger.info(f"请在终端中执行以下命令:")
                logger.info(cmd_to_show)
                logger.info("========================================")

                # 尝试打开终端
                try:
                    # 根据不同桌面环境尝试打开终端
                    for terminal_cmd in ["gnome-terminal", "konsole", "xterm"]:
                        try:
                            subprocess.run(f"{terminal_cmd} -e 'echo \"请执行: {cmd_to_show}\"; bash'",
                                          shell=True, timeout=1)
                            break
                        except (subprocess.SubprocessError, FileNotFoundError):
                            continue
                    logger.info("已尝试打开终端窗口，请执行命令")
                except Exception as e:
                    logger.warning(f"无法自动打开终端: {str(e)}")

                return True

            except subprocess.CalledProcessError as e:
                logger.error(f"下载脚本失败: {str(e)}")
                return False

        else:
            logger.error(f"不支持的操作系统: {system}")
            return False

    except Exception as e:
        logger.error(f"准备重置脚本时发生错误: {str(e)}")
        return False
