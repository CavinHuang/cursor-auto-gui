#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import time
import json
import uuid
import secrets
import shutil
import ctypes
import random
import glob
from datetime import datetime
from pathlib import Path
import tempfile
from src.logic.log import logger

# 平台检测
is_windows = sys.platform.startswith('win')

# 条件导入winreg模块(仅Windows系统)
if is_windows:
    import winreg

# 颜色定义
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
NC = "\033[0m"  # No Color

# 配置文件路径
APPDATA = os.environ.get("APPDATA", "")
LOCALAPPDATA = os.environ.get("LOCALAPPDATA", "")
STORAGE_FILE = os.path.join(APPDATA, "Cursor", "User", "globalStorage", "storage.json")
BACKUP_DIR = os.path.join(APPDATA, "Cursor", "User", "globalStorage", "backups")

# 常量定义
MAX_RETRIES = 5
WAIT_TIME = 1

# 检查管理员权限
def is_admin():
    """
    检查当前程序是否以管理员权限运行
    相当于PowerShell脚本中的Test-Administrator函数

    Returns:
        bool: 如果是管理员权限返回True，否则返回False
    """
    # 在非Windows平台上，返回False
    if not is_windows:
        return False

    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

# 获取Cursor版本
def get_cursor_version():
    """
    获取当前安装的Cursor版本
    相当于PowerShell脚本中的Get-CursorVersion函数

    Returns:
        str: Cursor版本号，如果未找到返回None
    """
    try:
        # 主要检测路径
        package_path = os.path.join(LOCALAPPDATA, "Programs", "cursor", "resources", "app", "package.json")

        if os.path.isfile(package_path):
            with open(package_path, 'r', encoding='utf-8') as f:
                package_json = json.load(f)
                if 'version' in package_json:
                    logger.info(f"当前安装的Cursor版本: v{package_json['version']}")
                    return package_json['version']

        # 备用路径检测
        alt_path = os.path.join(LOCALAPPDATA, "cursor", "resources", "app", "package.json")
        if os.path.isfile(alt_path):
            with open(alt_path, 'r', encoding='utf-8') as f:
                package_json = json.load(f)
                if 'version' in package_json:
                    logger.info(f"当前安装的Cursor版本: v{package_json['version']}")
                    return package_json['version']

        logger.warning("无法检测到Cursor版本")
        logger.warning("请确保Cursor已正确安装")
        return None
    except Exception as e:
        logger.error(f"获取Cursor版本失败: {e}")
        return None

# 获取进程详情
def get_process_details(process_name):
    """
    获取指定进程的详细信息
    相当于PowerShell脚本中的Get-ProcessDetails函数

    Args:
        process_name (str): 进程名称

    Returns:
        str: 进程信息文本
    """
    logger.debug(f"正在获取 {process_name} 进程详细信息")

    # 在非Windows平台上，使用适用于该平台的命令
    if not is_windows:
        try:
            if sys.platform == "darwin":  # macOS
                cmd = f"ps -ef | grep -i '{process_name}' | grep -v grep"
            else:  # Linux和其他UNIX-like系统
                cmd = f"ps -ef | grep -i '{process_name}' | grep -v grep"

            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.stdout.strip():
                logger.debug(result.stdout)
            return result.stdout.strip()
        except Exception as e:
            logger.error(f"获取进程详情失败: {e}")
            return ""

    try:
        # 使用wmic获取进程信息
        result = subprocess.run(
            f"wmic process where name='{process_name}' get ProcessId,ExecutablePath,CommandLine /format:list",
            shell=True,
            capture_output=True,
            text=True
        )
        if result.stdout.strip():
            logger.debug(result.stdout)
        return result.stdout.strip()
    except Exception as e:
        logger.error(f"获取进程详情失败: {e}")
        return ""

# 关闭Cursor进程
def close_cursor_process(process_name):
    """
    尝试关闭指定的Cursor进程
    相当于PowerShell脚本中的Close-CursorProcess函数

    Args:
        process_name (str): 进程名称

    Returns:
        bool: 成功关闭返回True，否则返回False
    """
    # 在非Windows平台上，使用适用于该平台的命令
    if not is_windows:
        logger.warning(f"在非Windows平台上尝试关闭 {process_name} 进程")
        try:
            # 对于macOS/Linux系统，使用killall或pkill
            if sys.platform == "darwin":  # macOS
                subprocess.run(f"killall '{process_name}'", shell=True, stderr=subprocess.DEVNULL)
            else:  # Linux和其他UNIX-like系统
                subprocess.run(f"pkill -f '{process_name}'", shell=True, stderr=subprocess.DEVNULL)
            return True
        except Exception as e:
            logger.error(f"关闭进程出错: {e}")
            return False

    try:
        # 检查进程是否存在
        check_cmd = f"tasklist /FI \"IMAGENAME eq {process_name}\" 2>NUL | find /I /N \"{process_name}\""
        result = subprocess.run(check_cmd, shell=True, capture_output=True, text=True)

        if process_name.lower() in result.stdout.lower():
            logger.warning(f"发现 {process_name} 正在运行")
            get_process_details(process_name)

            logger.warning(f"尝试关闭 {process_name}...")
            subprocess.run(f"taskkill /F /IM {process_name}", shell=True)

            retry_count = 0
            while retry_count < MAX_RETRIES:
                # 再次检查进程是否仍在运行
                check_result = subprocess.run(check_cmd, shell=True, capture_output=True, text=True)
                if process_name.lower() not in check_result.stdout.lower():
                    break

                retry_count += 1
                if retry_count >= MAX_RETRIES:
                    logger.error(f"在 {MAX_RETRIES} 次尝试后仍无法关闭 {process_name}")
                    get_process_details(process_name)
                    logger.error("请手动关闭进程后重试")
                    return False

                logger.warning(f"等待进程关闭，尝试 {retry_count}/{MAX_RETRIES}...")
                time.sleep(WAIT_TIME)

            logger.info(f"{process_name} 已成功关闭")
        return True
    except Exception as e:
        logger.error(f"关闭进程出错: {e}")
        return False

# 生成随机的十六进制字符串
def get_random_hex(length):
    """
    生成指定长度的随机十六进制字符串
    相当于PowerShell脚本中的Get-RandomHex函数

    Args:
        length (int): 所需的字节长度，输出的十六进制字符串长度将是这个值的两倍

    Returns:
        str: 随机十六进制字符串
    """
    return secrets.token_hex(length)

# 生成标准机器ID (UUID格式)
def new_standard_machine_id():
    """
    生成符合UUID v4标准格式的随机ID
    相当于PowerShell脚本中的New-StandardMachineId函数

    Returns:
        str: 随机UUID字符串
    """
    return str(uuid.uuid4()).lower()

# 更新Windows注册表中的MachineGuid
def update_machine_guid():
    """
    更新Windows注册表中的MachineGuid值
    相当于PowerShell脚本中的Update-MachineGuid函数

    Returns:
        bool: 成功返回True，失败返回False
    """
    # 在非Windows平台上，不执行注册表操作
    if not is_windows:
        logger.warning("注册表操作仅适用于Windows系统")
        return False

    try:
        # 检查是否有管理员权限
        if not is_admin():
            logger.error("需要管理员权限才能修改注册表")
            return False

        # 注册表路径
        registry_path = r"SOFTWARE\Microsoft\Cryptography"
        backup_file = None

        # 检查注册表路径是否存在
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, registry_path, 0, winreg.KEY_READ)
            winreg.CloseKey(key)
        except FileNotFoundError:
            logger.warning(f"注册表路径不存在: {registry_path}，正在创建...")
            try:
                key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, registry_path)
                winreg.CloseKey(key)
                logger.info("注册表路径创建成功")
            except Exception as e:
                logger.error(f"创建注册表路径失败: {e}")
                return False

        # 获取当前的MachineGuid
        original_guid = ""
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, registry_path, 0, winreg.KEY_READ)
            original_guid, _ = winreg.QueryValueEx(key, "MachineGuid")
            winreg.CloseKey(key)

            if original_guid:
                logger.info(f"当前注册表值：")
                logger.info(f"HKEY_LOCAL_MACHINE\\{registry_path}")
                logger.info(f"    MachineGuid    REG_SZ    {original_guid}")
        except FileNotFoundError:
            logger.warning("MachineGuid值不存在，将创建新值")
        except Exception as e:
            logger.warning(f"获取MachineGuid失败: {e}")

        # 创建备份目录（如果不存在）
        os.makedirs(BACKUP_DIR, exist_ok=True)

        # 备份当前注册表值
        if original_guid:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(BACKUP_DIR, f"MachineGuid_{timestamp}.reg")

            try:
                # 使用reg.exe导出注册表项
                result = subprocess.run(
                    f'reg export "HKEY_LOCAL_MACHINE\\{registry_path}" "{backup_file}"',
                    shell=True,
                    capture_output=True,
                    text=True
                )

                if result.returncode == 0:
                    logger.info(f"注册表项已备份到：{backup_file}")
                else:
                    logger.warning("备份创建失败，继续执行...")
            except Exception as e:
                logger.warning(f"创建备份失败: {e}")

        # 生成新GUID
        new_guid = str(uuid.uuid4())

        # 更新注册表值
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, registry_path, 0, winreg.KEY_WRITE)
            winreg.SetValueEx(key, "MachineGuid", 0, winreg.REG_SZ, new_guid)
            winreg.CloseKey(key)

            # 验证更新
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, registry_path, 0, winreg.KEY_READ)
            verify_guid, _ = winreg.QueryValueEx(key, "MachineGuid")
            winreg.CloseKey(key)

            if verify_guid != new_guid:
                raise Exception(f"注册表验证失败：更新后的值 ({verify_guid}) 与预期值 ({new_guid}) 不匹配")

            logger.info("注册表更新成功：")
            logger.info(f"HKEY_LOCAL_MACHINE\\{registry_path}")
            logger.info(f"    MachineGuid    REG_SZ    {new_guid}")
            return True

        except Exception as e:
            logger.error(f"注册表操作失败：{e}")

            # 尝试恢复备份
            if backup_file and os.path.exists(backup_file):
                logger.warning("正在从备份恢复...")
                try:
                    result = subprocess.run(
                        f'reg import "{backup_file}"',
                        shell=True,
                        capture_output=True,
                        text=True
                    )

                    if result.returncode == 0:
                        logger.info("已还原原始注册表值")
                    else:
                        logger.error(f"恢复失败，请手动导入备份文件：{backup_file}")
                except Exception as restore_e:
                    logger.error(f"恢复过程中出错: {restore_e}")
            else:
                logger.warning("未找到备份文件或备份创建失败，无法自动恢复")

            return False

    except Exception as e:
        logger.error(f"更新MachineGuid时出错: {e}")
        return False

# 备份配置文件
def backup_config():
    """
    备份Cursor配置文件

    Returns:
        str: 备份文件路径，如果备份失败则返回空字符串
    """
    if not os.path.exists(STORAGE_FILE):
        logger.warning("配置文件不存在，跳过备份")
        return ""

    # 创建备份目录（如果不存在）
    os.makedirs(BACKUP_DIR, exist_ok=True)

    # 生成带时间戳的备份文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(BACKUP_DIR, f"storage.json.backup_{timestamp}")

    try:
        # 复制配置文件到备份位置
        shutil.copy2(STORAGE_FILE, backup_file)
        logger.info(f"配置已备份到: {backup_file}")
        return backup_file
    except Exception as e:
        logger.error(f"备份失败: {e}")
        return ""

# 更新配置文件
def update_config(new_machine_id, new_mac_machine_id, new_uuid, new_sqm_id):
    """
    更新Cursor配置文件中的设备ID相关内容

    Args:
        new_machine_id (str): 新的machine ID
        new_mac_machine_id (str): 新的MAC machine ID
        new_uuid (str): 新的UUID
        new_sqm_id (str): 新的SQM ID

    Returns:
        bool: 成功返回True，失败返回False
    """
    try:
        # 检查配置文件是否存在
        if not os.path.exists(STORAGE_FILE):
            logger.error(f"未找到配置文件: {STORAGE_FILE}")
            logger.warning("请先安装并运行一次Cursor后再使用此脚本")
            return False

        # 读取现有配置文件
        try:
            with open(STORAGE_FILE, 'r', encoding='utf-8') as f:
                original_content = f.read()
                config = json.loads(original_content)

            # 备份当前值
            old_values = {
                'machineId': config.get('telemetry.machineId', ''),
                'macMachineId': config.get('telemetry.macMachineId', ''),
                'devDeviceId': config.get('telemetry.devDeviceId', ''),
                'sqmId': config.get('telemetry.sqmId', '')
            }

            # 更新特定的值
            config['telemetry.machineId'] = new_machine_id
            config['telemetry.macMachineId'] = new_mac_machine_id
            config['telemetry.devDeviceId'] = new_uuid
            config['telemetry.sqmId'] = new_sqm_id

            # 将更新后的对象转换回JSON并保存
            with open(STORAGE_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)

            logger.info("成功更新配置文件")
            return True

        except Exception as e:
            # 如果出错，尝试恢复原始内容
            if 'original_content' in locals():
                try:
                    with open(STORAGE_FILE, 'w', encoding='utf-8') as f:
                        f.write(original_content)
                except:
                    pass
            logger.error(f"处理JSON失败: {e}")
            return False

    except Exception as e:
        logger.error(f"更新配置文件失败: {e}")
        return False

# 禁用Cursor自动更新
def disable_auto_update():
    """
    禁用Cursor自动更新功能
    通过创建只读文件来阻止更新程序运行

    Returns:
        bool: 成功返回True，失败返回False
    """
    # 在非Windows平台上，使用适当的路径
    if not is_windows:
        logger.warning("在非Windows平台上尝试禁用自动更新")
        if sys.platform == "darwin":  # macOS
            updater_path = os.path.join(os.path.expanduser("~"), "Library/Application Support/Caches/cursor-updater")
        else:  # Linux和其他UNIX-like系统
            updater_path = os.path.join(os.path.expanduser("~"), ".config/cursor-updater")

        logger.info(f"使用平台特定路径: {updater_path}")
    else:
        updater_path = os.path.join(LOCALAPPDATA, "cursor-updater")

    logger.info("正在禁用Cursor自动更新...")

    # 定义显示手动设置教程的函数
    def show_manual_guide():
        logger.warning("自动设置失败，请尝试手动操作：")
        logger.warning("手动禁用更新步骤：")

        if is_windows:
            print("1. 以管理员身份打开PowerShell")
            print("2. 复制粘贴以下命令：")
            print(f"{BLUE}命令1 - 删除现有目录（如果存在）：{NC}")
            print(f'Remove-Item -Path "{updater_path}" -Force -Recurse -ErrorAction SilentlyContinue')
            print()
            print(f"{BLUE}命令2 - 创建阻止文件：{NC}")
            print(f'New-Item -Path "{updater_path}" -ItemType File -Force | Out-Null')
            print()
            print(f"{BLUE}命令3 - 设置只读属性：{NC}")
            print(f'Set-ItemProperty -Path "{updater_path}" -Name IsReadOnly -Value $true')
            print()
            print(f"{BLUE}命令4 - 设置权限（可选）：{NC}")
            print(f'icacls "{updater_path}" /inheritance:r /grant:r "$($env:USERNAME):(R)"')
        else:
            print("1. 打开终端")
            print("2. 复制粘贴以下命令：")
            print(f"{BLUE}命令1 - 删除现有目录（如果存在）：{NC}")
            print(f'rm -rf "{updater_path}"')
            print()
            print(f"{BLUE}命令2 - 创建阻止文件：{NC}")
            print(f'touch "{updater_path}"')
            print()
            print(f"{BLUE}命令3 - 设置只读属性：{NC}")
            print(f'chmod 444 "{updater_path}"')

        print()
        print(f"{YELLOW}验证方法：{NC}")
        if is_windows:
            print(f'1. 运行命令：Get-ItemProperty "{updater_path}"')
            print("2. 确认IsReadOnly属性为True")
            print(f'3. 运行命令：icacls "{updater_path}"')
            print("4. 确认只有读取权限")
        else:
            print(f'1. 运行命令：ls -l "{updater_path}"')
            print("2. 确认权限为r--r--r--")
        print()
        logger.warning("完成后请重启Cursor")

    try:
        # 检查cursor-updater是否存在
        if os.path.exists(updater_path):
            # 如果是文件，说明已经创建了阻止更新
            if os.path.isfile(updater_path):
                logger.info("已创建阻止更新文件，无需再次阻止")
                return True
            # 如果是目录，尝试删除
            elif os.path.isdir(updater_path):
                try:
                    shutil.rmtree(updater_path)
                    logger.info("成功删除cursor-updater目录")
                except Exception as e:
                    logger.error(f"删除cursor-updater目录失败: {e}")
                    show_manual_guide()
                    return False

        # 创建阻止文件
        try:
            # 确保父目录存在
            os.makedirs(os.path.dirname(updater_path), exist_ok=True)

            # 创建空文件
            with open(updater_path, 'w') as f:
                pass
            logger.info("成功创建阻止文件")
        except Exception as e:
            logger.error(f"创建阻止文件失败: {e}")
            show_manual_guide()
            return False

        # 设置文件权限
        try:
            # 设置文件为只读
            os.chmod(updater_path, 0o444)  # 设置为只读模式

            if is_windows:
                # 使用icacls设置权限
                username = os.environ.get("USERNAME", "")
                result = subprocess.run(
                    f'icacls "{updater_path}" /inheritance:r /grant:r "{username}:(R)"',
                    shell=True,
                    capture_output=True,
                    text=True
                )

                if result.returncode != 0:
                    raise Exception("icacls命令失败")

            logger.info("成功设置文件权限")
        except Exception as e:
            logger.error(f"设置文件权限失败: {e}")
            show_manual_guide()
            return False

        # 验证设置
        try:
            # 检查文件是否存在且为只读
            if not os.path.isfile(updater_path):
                raise Exception("文件不存在")

            # 检查文件是否只读
            if os.access(updater_path, os.W_OK):
                raise Exception("文件仍然可写入")

            logger.info("成功禁用自动更新")
            return True
        except Exception as e:
            logger.error(f"验证设置失败: {e}")
            show_manual_guide()
            return False

    except Exception as e:
        logger.error(f"禁用自动更新时出错: {e}")
        show_manual_guide()
        return False


# 主函数
def go_cursor_help_win():
    """
    主函数，执行所有必要的步骤
    """
    # 在非Windows平台上，显示错误信息
    if not is_windows:
        logger.error("此功能仅支持Windows系统")
        return 1

    # 检查管理员权限
    if not is_admin():
        logger.error("请以管理员身份运行此脚本")
        print("请右键点击脚本，选择'以管理员身份运行'")
        return 1

    # 获取并显示Cursor版本
    cursor_version = get_cursor_version()
    if cursor_version:
        logger.info(f"检测到Cursor版本: {cursor_version}，继续执行...")
    else:
        logger.warning("无法检测版本，将继续执行...")
    print()

    # 处理进程关闭
    logger.info("检查Cursor进程...")
    close_cursor_process("Cursor.exe")
    close_cursor_process("cursor.exe")

    # 创建备份目录
    os.makedirs(BACKUP_DIR, exist_ok=True)

    # 备份现有配置
    if os.path.exists(STORAGE_FILE):
        logger.info("正在备份配置文件...")
        backup_config()

    # 生成新的ID
    logger.info("正在生成新的ID...")
    mac_machine_id = new_standard_machine_id()
    uuid_value = str(uuid.uuid4()).lower()

    # 构建机器ID (auth0|user_前缀 + 随机十六进制)
    prefix = "auth0|user_"
    random_part = get_random_hex(16)
    machine_id = f"{prefix}{random_part}"

    # 生成SQM ID
    sqm_id = "{" + str(uuid.uuid4()).upper() + "}"

    # 更新配置文件
    logger.info("正在更新配置...")
    update_result = update_config(machine_id, mac_machine_id, uuid_value, sqm_id)

    if update_result:
        # 更新注册表
        update_machine_guid()

        # 显示结果
        print()
        logger.info("已更新配置:")
        logger.debug(f"machineId: {machine_id}")
        logger.debug(f"macMachineId: {mac_machine_id}")
        logger.debug(f"devDeviceId: {uuid_value}")
        logger.debug(f"sqmId: {sqm_id}")

        # 显示文件树结构
        print()
        logger.info("文件结构:")
        print(f"{BLUE}{APPDATA}\\Cursor\\User{NC}")
        print("├── globalStorage")
        print("│   ├── storage.json (已修改)")
        print("│   └── backups")

        # 列出备份文件
        backup_files = glob.glob(os.path.join(BACKUP_DIR, "*"))
        if backup_files:
            for file in backup_files:
                print(f"│       └── {os.path.basename(file)}")
        else:
            print("│       └── (空)")


        logger.info("请重启Cursor以应用新的配置")
        print()

    else:
        logger.error("配置更新失败")

    print()
    return 0

# 当作为脚本直接运行时执行main()
if __name__ == "__main__":
    sys.exit(go_cursor_help_win())
