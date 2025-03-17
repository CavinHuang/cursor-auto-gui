import os
from src.logic.config.config_manager import ConfigManager
from src.logic.log import logger


class Config:
    def __init__(self):

        config = ConfigManager().get_config()

        self.imap = True
        self.imap_server = config['imap_server'].strip()
        self.imap_port = str(config['imap_port']).strip()
        self.imap_user = config['imap_user'].strip()
        self.imap_pass = config['imap_pass'].strip()
        self.domain = config['domain'].strip()
        self.imap_dir = 'inbox'

        self.check_config()

    def get_imap(self):
        if not self.imap:
            return False
        return {
            "imap_server": self.imap_server,
            "imap_port": self.imap_port,
            "imap_user": self.imap_user,
            "imap_pass": self.imap_pass,
            "imap_dir": self.imap_dir,
        }

    def get_domain(self):
        domain_arr = self.domain.split(";")
        # 随机返回一个域名
        import random
        domain = random.choice(domain_arr)
        return domain

    def get_protocol(self):
        """获取邮件协议类型

        Returns:
            str: 'IMAP' 或 'POP3'
        """
        return os.getenv('IMAP_PROTOCOL', 'POP3')

    def check_config(self):
        """检查配置项是否有效

        检查规则：
        1. 如果使用 tempmail.plus，需要配置 TEMP_MAIL 和 DOMAIN
        2. 如果使用 IMAP，需要配置 IMAP_SERVER、IMAP_PORT、IMAP_USER、IMAP_PASS
        3. IMAP_DIR 是可选的
        """
        # 基础配置检查
        required_configs = {
            "domain": "域名",
        }

        # 检查基础配置
        for key, name in required_configs.items():
            if not self.check_is_valid(getattr(self, key)):
                raise ValueError(f"{name}未配置，请在 .env 文件中设置 {key.upper()}")

        # IMAP 模式
        imap_configs = {
            "imap_server": "IMAP服务器",
            "imap_port": "IMAP端口",
            "imap_user": "IMAP用户名",
            "imap_pass": "IMAP密码",
        }

        for key, name in imap_configs.items():
            value = getattr(self, key)
            if value == "null" or not self.check_is_valid(value):
                raise ValueError(
                    f"{name}未配置，请在 .env 文件中设置 {key.upper()}"
                )

        # IMAP_DIR 是可选的，如果设置了就检查其有效性
        if self.imap_dir != "null" and not self.check_is_valid(self.imap_dir):
            raise ValueError(
                "IMAP收件箱目录配置无效，请在 .env 文件中正确设置 IMAP_DIR"
            )

    def check_is_valid(self, value):
        """检查配置项是否有效

        Args:
            value: 配置项的值

        Returns:
            bool: 配置项是否有效
        """
        return isinstance(value, str) and len(str(value).strip()) > 0

    def print_config(self):
        if self.imap:
            logger.info(f"\033[32mIMAP服务器: {self.imap_server}\033[0m")
            logger.info(f"\033[32mIMAP端口: {self.imap_port}\033[0m")
            logger.info(f"\033[32mIMAP用户名: {self.imap_user}\033[0m")
            logger.info(f"\033[32mIMAP密码: {'*' * len(self.imap_pass)}\033[0m")
            logger.info(f"\033[32mIMAP收件箱目录: {self.imap_dir}\033[0m")
        logger.info(f"\033[32m域名: {self.domain}\033[0m")


# 使用示例
if __name__ == "__main__":
    try:
        config = Config()
        print("环境变量加载成功！")
        config.print_config()
    except ValueError as e:
        print(f"错误: {e}")
