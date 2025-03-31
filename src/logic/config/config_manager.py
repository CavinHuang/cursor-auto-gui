import os
import json
from src.logic.utils.utils import get_app_config_path
from src.logic.log.log_manager import logger, LogLevel
class ConfigManager:
    def __init__(self):
        # 构建配置文件的完整路径
        config_path = get_app_config_path()
        logger.log(f"配置文件路径: {config_path}", LogLevel.INFO)
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self):
        if not os.path.exists(self.config_path):
            return {}
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.log(f"加载配置文件失败: {e}", LogLevel.ERROR)
            return {}

    def get_config(self):
        return self.config

    def get_config_value(self, key, default=None):
        return self.config.get(key, default)

    def update_config(self, new_config):
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(new_config, f, ensure_ascii=False, indent=4)
            self.config = new_config
            return True
        except Exception as e:
            logger.log(f"保存配置文件失败: {e}", LogLevel.ERROR)
            return False