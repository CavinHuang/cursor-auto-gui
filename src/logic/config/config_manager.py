import os
import json
import sys

class ConfigManager:
    def __init__(self):
        # 开发环境使用的是当前项目的config.json
        # 获取应用程序的根目录路径
        if getattr(sys, "frozen", False):
            # 如果是打包后的可执行文件
            application_path = os.path.dirname(sys.executable)
        else:
            # 如果是开发环境
            application_path = os.path.join(os.path.dirname(__file__), '../../../')

        # 构建配置文件的完整路径
        config_path = os.path.join(application_path, 'datas/settings.json')
        print(config_path)
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self):
        if not os.path.exists(self.config_path):
            return {}
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载配置文件失败: {e}")
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
            print(f"保存配置文件失败: {e}")
            return False