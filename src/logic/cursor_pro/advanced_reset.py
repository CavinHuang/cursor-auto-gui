import os
import sys
import json
import uuid
import hashlib
import tempfile
import shutil
import subprocess
import platform
import re
from pathlib import Path
from datetime import datetime

from src.logic.log import logger
from src.logic.log.log_manager import LogLevel

class AdvancedMachineIDResetter:
    """高版本Cursor (0.45+) 的机器码重置实现

    直接用Python实现原本需要外部脚本的功能，避免进程和内存问题
    """

    def __init__(self):
        """初始化重置器"""
        self.system = platform.system()
        self.setup_paths()

    def setup_paths(self):
        """根据操作系统设置相关路径"""
        # 基础路径
        if self.system == "Darwin":  # macOS
            self.cursor_app_path = "/Applications/Cursor.app"
            self.home_dir = os.path.expanduser("~")
            self.cursor_data_path = os.path.join(self.home_dir, "Library/Application Support/Cursor")
            self.cursor_storage_path = os.path.join(self.cursor_data_path, "User/globalStorage")
            self.cursor_state_db = os.path.join(self.cursor_storage_path, "state.vscdb")
        elif self.system == "Windows":
            appdata = os.getenv("APPDATA")
            local_appdata = os.getenv("LOCALAPPDATA")
            self.cursor_app_path = os.path.join(local_appdata, "Programs", "Cursor")
            self.cursor_data_path = os.path.join(appdata, "Cursor") if appdata else None
            self.cursor_storage_path = os.path.join(self.cursor_data_path, "User/globalStorage") if self.cursor_data_path else None
            self.cursor_state_db = os.path.join(self.cursor_storage_path, "state.vscdb") if self.cursor_storage_path else None
        elif self.system == "Linux":
            self.home_dir = os.path.expanduser("~")
            self.cursor_app_path = "/opt/Cursor"
            if not os.path.exists(self.cursor_app_path):
                self.cursor_app_path = "/usr/share/cursor"
            self.cursor_data_path = os.path.join(self.home_dir, ".config/Cursor")
            self.cursor_storage_path = os.path.join(self.cursor_data_path, "User/globalStorage")
            self.cursor_state_db = os.path.join(self.cursor_storage_path, "state.vscdb")
        else:
            logger.error(f"不支持的操作系统: {self.system}")
            raise NotImplementedError(f"不支持的操作系统: {self.system}")

        # 存储文件路径
        self.storage_file = os.path.join(self.cursor_storage_path, "storage.json")

        # 通用应用更新路径
        self.app_update_yml = os.path.join(self.cursor_app_path, "resources/app/product.json")

        # 检查路径是否存在
        if not os.path.exists(self.cursor_data_path):
            logger.warning(f"找不到Cursor数据目录: {self.cursor_data_path}")

        # 创建备份目录
        self.backup_dir = os.path.join(self.home_dir, ".cursor_backups")
        os.makedirs(self.backup_dir, exist_ok=True)

        # 日志目录
        self.log_dir = os.path.join(self.home_dir, ".cursor_logs")
        os.makedirs(self.log_dir, exist_ok=True)

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

    def generate_new_tokens(self):
        """生成新的随机令牌"""
        auth_token = str(uuid.uuid4())
        session_id = str(uuid.uuid4())

        return {
            "authentication.token": auth_token,
            "session.id": session_id
        }

    def create_backup(self, file_path, backup_name=None):
        """创建文件备份"""
        if not os.path.exists(file_path):
            logger.warning(f"无法备份不存在的文件: {file_path}")
            return None

        # 创建备份文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        basename = os.path.basename(file_path)

        if backup_name:
            backup_file = os.path.join(self.backup_dir, f"{basename}.{backup_name}.{timestamp}")
        else:
            backup_file = os.path.join(self.backup_dir, f"{basename}.backup_{timestamp}")

        # 复制文件
        try:
            shutil.copy2(file_path, backup_file)
            logger.info(f"已创建备份: {backup_file}")
            return backup_file
        except Exception as e:
            logger.error(f"创建备份失败: {str(e)}")
            return None

    def modify_app_update_settings(self):
        """修改应用更新设置，禁用自动更新"""
        if not os.path.exists(self.app_update_yml):
            logger.warning(f"找不到应用配置文件: {self.app_update_yml}")
            return False

        logger.info(f"正在修改应用更新配置: {self.app_update_yml}")

        # 创建备份
        self.create_backup(self.app_update_yml, "original")

        try:
            # 读取原始配置
            with open(self.app_update_yml, 'r', encoding='utf-8') as f:
                content = f.read()

            # 使用正则表达式修改自动更新配置
            # 注意：这种方法可能需要根据实际文件格式调整
            if '"updateUrl":' in content:
                # 修改更新URL为无效URL
                new_content = re.sub(r'"updateUrl"\s*:\s*"[^"]*"', '"updateUrl": "https://invalid.url"', content)

                # 保存修改后的文件
                with open(self.app_update_yml, 'w', encoding='utf-8') as f:
                    f.write(new_content)

                logger.info("已修改应用更新配置")
                return True
            else:
                logger.warning("无法找到更新URL配置项")
                return False

        except Exception as e:
            logger.error(f"修改应用更新配置失败: {str(e)}")
            return False

    def reset_machine_ids(self):
        """重置机器ID和认证信息"""
        temp_file = None
        success = False

        try:
            logger.info(f"开始高级重置过程...")
            logger.info(f"正在检查配置文件...")

            # 检查存储文件
            if not os.path.exists(self.storage_file):
                logger.error(f"存储文件不存在: {self.storage_file}")
                return False

            # 检查文件权限
            if not os.access(self.storage_file, os.R_OK | os.W_OK):
                logger.error(f"无法读写存储文件，请检查权限: {self.storage_file}")
                return False

            # 创建备份
            storage_backup = self.create_backup(self.storage_file)
            if not storage_backup:
                logger.warning("无法创建存储文件备份，继续执行...")

            # 检查状态数据库
            if os.path.exists(self.cursor_state_db):
                if os.access(self.cursor_state_db, os.R_OK | os.W_OK):
                    logger.info(f"已检测到认证状态数据库")
                    state_db_backup = self.create_backup(self.cursor_state_db)
                    if not state_db_backup:
                        logger.warning("无法创建状态数据库备份，继续执行...")
                else:
                    logger.warning(f"无法访问状态数据库，可能需要手动处理: {self.cursor_state_db}")

            # 读取存储文件
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    storage_data = json.load(f)

                # 生成新ID
                logger.info("生成新的机器标识...")
                new_ids = self.generate_new_ids()

                # 更新存储数据
                storage_data.update(new_ids)

                # 使用临时文件保存新配置
                with tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8') as temp_file:
                    json.dump(storage_data, temp_file, indent=4)
                    temp_file_path = temp_file.name

                # 替换原文件
                shutil.move(temp_file_path, self.storage_file)
                temp_file = None  # 防止finally块中再次尝试清理

                # 记录新ID
                logger.info("新的机器标识生成完成:")
                for key, value in new_ids.items():
                    logger.info(f"{key}: {value}")

                # 尝试修改更新设置
                if os.path.exists(self.app_update_yml):
                    self.modify_app_update_settings()

                success = True

            except json.JSONDecodeError as e:
                logger.error(f"解析存储文件失败: {str(e)}")
                return False
            except Exception as e:
                logger.error(f"处理存储文件时出错: {str(e)}")
                return False

            return success

        except Exception as e:
            logger.error(f"重置过程出错: {str(e)}")
            return False
        finally:
            # 清理临时文件
            if temp_file and hasattr(temp_file, 'name') and os.path.exists(temp_file.name):
                try:
                    os.unlink(temp_file.name)
                except Exception:
                    pass

    def reset(self):
        """执行完整的重置流程"""
        logger.info(f"开始执行Cursor高级重置...")

        # 执行各项重置操作
        result = self.reset_machine_ids()

        if result:
            logger.info("Cursor高级重置成功完成")
            return True
        else:
            logger.error("Cursor高级重置失败")
            return False


# 测试函数
if __name__ == "__main__":
    resetter = AdvancedMachineIDResetter()
    resetter.reset()