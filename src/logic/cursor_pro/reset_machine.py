import os
import sys
import json
import uuid
import hashlib
import tempfile
import shutil
from colorama import Fore, Style, init
from src.logic.log import logger
from src.logic.log.log_manager import LogLevel

# 初始化colorama
init()

# 定义emoji和颜色常量
EMOJI = {
    "FILE": "📄",
    "BACKUP": "💾",
    "SUCCESS": "✅",
    "ERROR": "❌",
    "INFO": "ℹ️",
    "RESET": "🔄",
}


class MachineIDResetter:
    def __init__(self):
        # 判断操作系统
        if sys.platform == "win32":  # Windows
            appdata = os.getenv("APPDATA")
            if appdata is None:
                raise EnvironmentError("APPDATA 环境变量未设置")
            self.db_path = os.path.join(
                appdata, "Cursor", "User", "globalStorage", "storage.json"
            )
        elif sys.platform == "darwin":  # macOS
            self.db_path = os.path.abspath(
                os.path.expanduser(
                    "~/Library/Application Support/Cursor/User/globalStorage/storage.json"
                )
            )
        elif sys.platform == "linux":  # Linux 和其他类Unix系统
            self.db_path = os.path.abspath(
                os.path.expanduser("~/.config/Cursor/User/globalStorage/storage.json")
            )
        else:
            raise NotImplementedError(f"不支持的操作系统: {sys.platform}")

    def generate_new_ids(self):
        """生成新的机器ID"""
        # 生成新的UUID
        dev_device_id = str(uuid.uuid4())

        # 生成新的machineId (64个字符的十六进制)
        machine_id = hashlib.sha256(os.urandom(32)).hexdigest()

        # 生成新的macMachineId (128个字符的十六进制)
        mac_machine_id = hashlib.sha512(os.urandom(64)).hexdigest()

        # 生成新的sqmId
        sqm_id = "{" + str(uuid.uuid4()).upper() + "}"

        return {
            "telemetry.devDeviceId": dev_device_id,
            "telemetry.macMachineId": mac_machine_id,
            "telemetry.machineId": machine_id,
            "telemetry.sqmId": sqm_id,
        }

    def reset_machine_ids(self):
        """重置机器ID并备份原文件"""
        temp_file = None
        try:
            logger.log(f"正在检查配置文件...", LogLevel.INFO)
            print(f"{Fore.CYAN}{EMOJI['INFO']} 正在检查配置文件...{Style.RESET_ALL}")

            # 检查文件是否存在
            if not os.path.exists(self.db_path):
                error_msg = f"配置文件不存在: {self.db_path}"
                logger.log(error_msg, LogLevel.ERROR)
                print(f"{Fore.RED}{EMOJI['ERROR']} {error_msg}{Style.RESET_ALL}")
                return False

            # 检查文件权限
            if not os.access(self.db_path, os.R_OK | os.W_OK):
                error_msg = "无法读写配置文件，请检查文件权限！"
                logger.log(error_msg, LogLevel.ERROR)
                error_msg2 = "如果你使用过 go-cursor-help 来修改 ID; 请修改文件只读权限"
                logger.log(f"{error_msg2} {self.db_path}", LogLevel.ERROR)
                print(f"{Fore.RED}{EMOJI['ERROR']} {error_msg}{Style.RESET_ALL}")
                print(f"{Fore.RED}{EMOJI['ERROR']} {error_msg2} {self.db_path} {Style.RESET_ALL}")
                return False

            # 创建备份
            backup_path = f"{self.db_path}.bak"
            logger.log(f"创建配置文件备份: {backup_path}", LogLevel.INFO)
            print(f"{Fore.CYAN}{EMOJI['BACKUP']} 创建配置文件备份...{Style.RESET_ALL}")
            try:
                shutil.copy2(self.db_path, backup_path)
            except Exception as e:
                error_msg = f"创建备份失败: {str(e)}"
                logger.log(error_msg, LogLevel.WARNING)
                print(f"{Fore.YELLOW}{EMOJI['WARNING']} {error_msg}{Style.RESET_ALL}")
                # 备份失败不阻止继续执行，只是警告

            # 读取现有配置
            logger.log(f"读取当前配置...", LogLevel.INFO)
            print(f"{Fore.CYAN}{EMOJI['FILE']} 读取当前配置...{Style.RESET_ALL}")

            config = None
            try:
                with open(self.db_path, "r", encoding="utf-8") as f:
                    config_text = f.read()
                config = json.loads(config_text)
            except json.JSONDecodeError as e:
                error_msg = f"配置文件JSON解析错误: {str(e)}"
                logger.log(error_msg, LogLevel.ERROR)
                print(f"{Fore.RED}{EMOJI['ERROR']} {error_msg}{Style.RESET_ALL}")
                return False
            except Exception as e:
                error_msg = f"读取配置文件时出错: {str(e)}"
                logger.log(error_msg, LogLevel.ERROR)
                print(f"{Fore.RED}{EMOJI['ERROR']} {error_msg}{Style.RESET_ALL}")
                return False

            if not config:
                error_msg = "配置文件为空或无效"
                logger.log(error_msg, LogLevel.ERROR)
                print(f"{Fore.RED}{EMOJI['ERROR']} {error_msg}{Style.RESET_ALL}")
                return False

            # 生成新的ID
            logger.log(f"生成新的机器标识...", LogLevel.INFO)
            print(f"{Fore.CYAN}{EMOJI['RESET']} 生成新的机器标识...{Style.RESET_ALL}")
            new_ids = self.generate_new_ids()

            # 更新配置
            config.update(new_ids)

            # 使用临时文件保存新配置，然后原子替换
            logger.log(f"保存新配置...", LogLevel.INFO)
            print(f"{Fore.CYAN}{EMOJI['FILE']} 保存新配置...{Style.RESET_ALL}")

            # 创建临时文件
            with tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8') as temp_file:
                json.dump(config, temp_file, indent=4)
                temp_file_path = temp_file.name

            # 原子替换原文件
            shutil.move(temp_file_path, self.db_path)

            logger.log(f"机器标识重置成功！", LogLevel.INFO)
            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} 机器标识重置成功！{Style.RESET_ALL}")

            logger.log(f"新的机器标识:", LogLevel.INFO)
            print(f"\n{Fore.CYAN}新的机器标识:{Style.RESET_ALL}")
            for key, value in new_ids.items():
                logger.log(f"{key}: {value}", LogLevel.INFO)
                print(f"{EMOJI['INFO']} {key}: {Fore.GREEN}{value}{Style.RESET_ALL}")

            return True

        except PermissionError as e:
            error_msg = f"权限错误: {str(e)}"
            logger.log(error_msg, LogLevel.ERROR)
            logger.log("请尝试以管理员身份运行此程序", LogLevel.INFO)
            print(f"{Fore.RED}{EMOJI['ERROR']} {error_msg}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}{EMOJI['INFO']} 请尝试以管理员身份运行此程序{Style.RESET_ALL}")
            return False
        except Exception as e:
            error_msg = f"重置过程出错: {str(e)}"
            logger.log(error_msg, LogLevel.ERROR)
            print(f"{Fore.RED}{EMOJI['ERROR']} {error_msg}{Style.RESET_ALL}")
            return False
        finally:
            # 清理临时文件
            if temp_file and hasattr(temp_file, 'name') and os.path.exists(temp_file.name):
                try:
                    os.unlink(temp_file.name)
                except Exception:
                    pass


if __name__ == "__main__":
    print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{EMOJI['RESET']} Cursor 机器标识重置工具{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")

    resetter = MachineIDResetter()
    resetter.reset_machine_ids()

    print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    input(f"{EMOJI['INFO']} 按回车键退出...")
