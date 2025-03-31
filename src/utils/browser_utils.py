from DrissionPage import ChromiumOptions, Chromium
import sys
import os
from src.logic.config.config_manager import ConfigManager
from src.logic.log.log_manager import logger

class BrowserManager:
    def __init__(self):
        self.browser = None

    def init_browser(self, user_agent=None):
        """初始化浏览器"""
        co = self._get_browser_options(user_agent)
        self.browser = Chromium(co)
        return self.browser

    def _get_browser_options(self, user_agent=None):
        """获取浏览器配置"""
        co = ChromiumOptions()
        try:
            extension_path = self._get_extension_path("resources/turnstilePatch")
            co.add_extension(extension_path)
        except FileNotFoundError as e:
            logger.warning(f"警告: {e}")

        config_manager = ConfigManager()
        browser_path = config_manager.get_config_value("browser_path")

        # 检查浏览器路径是否存在且有执行权限
        if browser_path:
            if os.path.exists(browser_path):
                if not os.access(browser_path, os.X_OK):
                    logger.warning(f"浏览器路径无执行权限: {browser_path}")
                    # 尝试添加执行权限
                    try:
                        os.chmod(browser_path, 0o755)
                        logger.info(f"已添加浏览器执行权限: {browser_path}")
                    except Exception as e:
                        logger.error(f"添加执行权限失败: {e}")
                        browser_path = None
            else:
                logger.warning(f"浏览器路径不存在: {browser_path}")
                browser_path = None

        # 如果没有有效的浏览器路径，尝试查找系统默认Chrome
        if not browser_path:
            default_paths = [
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                "/Applications/Chromium.app/Contents/MacOS/Chromium",
                "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"
            ]
            for path in default_paths:
                if os.path.exists(path) and os.access(path, os.X_OK):
                    browser_path = path
                    logger.info(f"使用系统默认浏览器: {browser_path}")
                    break

        if browser_path:
            co.set_paths(browser_path=browser_path)
        else:
            logger.error("未找到可用的浏览器，请在设置中指定正确的浏览器路径")

        co.set_pref("credentials_enable_service", False)
        co.set_argument("--hide-crash-restore-bubble")
        # proxy = os.getenv("BROWSER_PROXY")
        # if proxy:
        #     co.set_proxy(proxy)

        co.auto_port()
        if user_agent:
            co.set_user_agent(user_agent)

        co.headless(on_off=True)  # 生产环境使用无头模式

        # Mac 系统特殊处理
        if sys.platform == "darwin":
            co.set_argument("--no-sandbox")
            co.set_argument("--disable-gpu")

        return co

    def _get_extension_path(self,exname='turnstilePatch'):
        """获取插件路径"""
        root_dir = os.getcwd()
        extension_path = os.path.join(root_dir, exname)

        if hasattr(sys, "_MEIPASS"):
            extension_path = os.path.join(sys._MEIPASS, exname)

        if not os.path.exists(extension_path):
            raise FileNotFoundError(f"插件不存在: {extension_path}")

        return extension_path

    def quit(self):
        """关闭浏览器"""
        if self.browser:
            try:
                self.browser.quit()
            except:
                pass
