from enum import Enum
import json
import os
import random
import time
from typing import Optional
from src.logic.cursor_pro import go_cursor_help, patch_cursor_get_machine_id
from src.logic.cursor_pro.cursor_auth_manager import CursorAuthManager
from src.logic.cursor_pro.email_generator import EmailGenerator
from src.logic.cursor_pro.get_email_code import EmailVerificationHandler
from src.logic.cursor_pro.reset_machine import MachineIDResetter
from src.logic.log import logger
from fake_useragent import UserAgent
from src.utils.browser_utils import BrowserManager

def check_cursor_version():
    """检查cursor版本"""
    pkg_path, main_path = patch_cursor_get_machine_id.get_cursor_paths()
    with open(pkg_path, "r", encoding="utf-8") as f:
        version = json.load(f)["version"]
    return patch_cursor_get_machine_id.version_check(version, min_version="0.45.0")

def get_cursor_session_token(tab, max_attempts=3, retry_interval=2):
    """
    获取Cursor会话token，带有重试机制
    :param tab: 浏览器标签页
    :param max_attempts: 最大尝试次数
    :param retry_interval: 重试间隔(秒)
    :return: session token 或 None
    """
    logger.info("开始获取cookie")
    attempts = 0

    while attempts < max_attempts:
        try:
            cookies = tab.cookies()
            for cookie in cookies:
                if cookie.get("name") == "WorkosCursorSessionToken":
                    return cookie["value"].split("%3A%3A")[1]

            attempts += 1
            if attempts < max_attempts:
                logger.warning(
                    f"第 {attempts} 次尝试未获取到CursorSessionToken，{retry_interval}秒后重试..."
                )
                time.sleep(retry_interval)
            else:
                logger.error(
                    f"已达到最大尝试次数({max_attempts})，获取CursorSessionToken失败"
                )

        except Exception as e:
            logger.error(f"获取cookie失败: {str(e)}")
            attempts += 1
            if attempts < max_attempts:
                logger.info(f"将在 {retry_interval} 秒后重试...")
                time.sleep(retry_interval)

    return None


class TurnstileError(Exception):
    """Turnstile 验证相关异常"""

    pass


def save_screenshot(tab, stage: str, timestamp: bool = True) -> None:
    """
    保存页面截图

    Args:
        tab: 浏览器标签页对象
        stage: 截图阶段标识
        timestamp: 是否添加时间戳
    """
    try:
        # 创建 screenshots 目录
        screenshot_dir = "screenshots"
        if not os.path.exists(screenshot_dir):
            os.makedirs(screenshot_dir)

        # 生成文件名
        if timestamp:
            filename = f"turnstile_{stage}_{int(time.time())}.png"
        else:
            filename = f"turnstile_{stage}.png"

        filepath = os.path.join(screenshot_dir, filename)

        # 保存截图
        tab.get_screenshot(filepath)
        logger.debug(f"截图已保存: {filepath}")
    except Exception as e:
        logger.warning(f"截图保存失败: {str(e)}")

class VerificationStatus(Enum):
    """验证状态枚举"""

    PASSWORD_PAGE = "@name=password"
    CAPTCHA_PAGE = "@data-index=0"
    ACCOUNT_SETTINGS = "Account Settings"

def check_verification_success(tab) -> Optional[VerificationStatus]:
    """
    检查验证是否成功

    Returns:
        VerificationStatus: 验证成功时返回对应状态，失败返回 None
    """
    for status in VerificationStatus:
        if tab.ele(status.value):
            logger.info(f"验证成功 - 已到达{status.name}页面")
            return status
    return None


def handle_turnstile(tab, max_retries: int = 2, retry_interval: tuple = (1, 2)) -> bool:
    """
    处理 Turnstile 验证

    Args:
        tab: 浏览器标签页对象
        max_retries: 最大重试次数
        retry_interval: 重试间隔时间范围(最小值, 最大值)

    Returns:
        bool: 验证是否成功

    Raises:
        TurnstileError: 验证过程中出现异常
    """
    logger.info("正在检测 Turnstile 验证...")
    save_screenshot(tab, "start")

    retry_count = 0

    try:
        while retry_count < max_retries:
            retry_count += 1
            logger.debug(f"第 {retry_count} 次尝试验证")

            try:
                # 定位验证框元素
                challenge_check = (
                    tab.ele("@id=cf-turnstile", timeout=2)
                    .child()
                    .shadow_root.ele("tag:iframe")
                    .ele("tag:body")
                    .sr("tag:input")
                )

                if challenge_check:
                    logger.info("检测到 Turnstile 验证框，开始处理...")
                    # 随机延时后点击验证
                    time.sleep(random.uniform(1, 3))
                    challenge_check.click()
                    time.sleep(2)

                    # 保存验证后的截图
                    save_screenshot(tab, "clicked")

                    # 检查验证结果
                    if check_verification_success(tab):
                        logger.info("Turnstile 验证通过")
                        save_screenshot(tab, "success")
                        return True

            except Exception as e:
                logger.debug(f"当前尝试未成功: {str(e)}")

            # 检查是否已经验证成功
            if check_verification_success(tab):
                return True

            # 随机延时后继续下一次尝试
            time.sleep(random.uniform(*retry_interval))

        # 超出最大重试次数
        logger.error(f"验证失败 - 已达到最大重试次数 {max_retries}")
        logger.error(
            "请前往开源项目查看更多信息：https://github.com/chengazhen/cursor-auto-free"
        )
        save_screenshot(tab, "failed")
        return False

    except Exception as e:
        error_msg = f"Turnstile 验证过程发生异常: {str(e)}"
        logger.error(error_msg)
        save_screenshot(tab, "error")
        raise TurnstileError(error_msg)

def get_user_agent():
    """获取user_agent"""
    try:
        # 使用JavaScript获取user agent
        browser_manager = BrowserManager()
        browser = browser_manager.init_browser()
        user_agent = browser.latest_tab.run_js("return navigator.userAgent")
        browser_manager.quit()
        return user_agent
    except Exception as e:
        logger.error(f"获取user agent失败: {str(e)}")
        return None

def sign_up_account(
        browser,
        tab,
        sign_up_url,
        first_name,
        last_name,
        account,
        password,
        settings_url,
        email_handler):
    logger.info("=== 开始注册账号流程 ===")
    logger.info(f"正在访问注册页面: {sign_up_url}")
    tab.get(sign_up_url)

    try:
        if tab.ele("@name=first_name"):
            logger.info("正在填写个人信息...")
            tab.actions.click("@name=first_name").input(first_name)
            logger.info(f"已输入名字: {first_name}")
            time.sleep(random.uniform(1, 3))

            tab.actions.click("@name=last_name").input(last_name)
            logger.info(f"已输入姓氏: {last_name}")
            time.sleep(random.uniform(1, 3))

            tab.actions.click("@name=email").input(account)
            logger.info(f"已输入邮箱: {account}")
            time.sleep(random.uniform(1, 3))

            logger.info("提交个人信息...")
            tab.actions.click("@type=submit")

    except Exception as e:
        logger.error(f"注册页面访问失败: {str(e)}")
        return False

    handle_turnstile(tab)

    try:
        if tab.ele("@name=password"):
            logger.info("正在设置密码...")
            tab.ele("@name=password").input(password)
            time.sleep(random.uniform(1, 3))

            logger.info("提交密码...")
            tab.ele("@type=submit").click()
            logger.info("密码设置完成，等待系统响应...")

    except Exception as e:
        logger.error(f"密码设置失败: {str(e)}")
        return False

    if tab.ele("This email is not available."):
        logger.error("注册失败：邮箱已被使用")
        return False

    handle_turnstile(tab)

    while True:
        try:
            if tab.ele("Account Settings"):
                logger.info("注册成功 - 已进入账户设置页面")
                break
            if tab.ele("@data-index=0"):
                logger.info("正在获取邮箱验证码...")
                code = email_handler.get_verification_code()
                if not code:
                    logger.error("获取验证码失败")
                    return False

                logger.info(f"成功获取验证码: {code}")
                logger.info("正在输入验证码...")
                i = 0
                for digit in code:
                    tab.ele(f"@data-index={i}").input(digit)
                    time.sleep(random.uniform(0.1, 0.3))
                    i += 1
                logger.info("验证码输入完成")
                break
        except Exception as e:
            logger.error(f"验证码处理过程出错: {str(e)}")

    handle_turnstile(tab)
    wait_time = random.randint(3, 6)
    for i in range(wait_time):
        logger.info(f"等待系统处理中... 剩余 {wait_time-i} 秒")
        time.sleep(1)

    logger.info("正在获取账户信息...")
    tab.get(settings_url)
    try:
        usage_selector = (
            "css:div.col-span-2 > div > div > div > div > "
            "div:nth-child(1) > div.flex.items-center.justify-between.gap-2 > "
            "span.font-mono.text-sm\\/\\[0\\.875rem\\]"
        )
        usage_ele = tab.ele(usage_selector)
        if usage_ele:
            usage_info = usage_ele.text
            total_usage = usage_info.split("/")[-1].strip()
            logger.info(f"账户可用额度上限: {total_usage}")
            logger.info(
                "请前往开源项目查看更多信息：https://github.com/chengazhen/cursor-auto-free"
            )
    except Exception as e:
        logger.error(f"获取账户额度信息失败: {str(e)}")

    logger.info("\n=== 注册完成 ===")
    account_info = f"Cursor 账号信息:\n邮箱: {account}\n密码: {password}"
    logger.info(account_info)
    time.sleep(5)
    return True

def update_cursor_auth(email=None, access_token=None, refresh_token=None):
    """
    更新Cursor的认证信息的便捷函数
    """
    auth_manager = CursorAuthManager()
    return auth_manager.update_auth(email, access_token, refresh_token)

def reset_machine_id(greater_than_0_45):
    if greater_than_0_45:
        # 提示请手动执行脚本 https://github.com/chengazhen/cursor-auto-free/blob/main/patch_cursor_get_machine_id.py
        go_cursor_help.go_cursor_help()
    else:
        MachineIDResetter().reset_machine_ids()

def print_end_message():
    logger.info("\n\n\n\n\n")
    logger.info("=" * 30)
    logger.info("所有操作已完成")
    # logger.info("\n=== 获取更多信息 ===")
    # logger.info("📺 B站UP主: 想回家的前端")
    # logger.info("🔥 公众号: code 未来")
    # logger.info("=" * 30)
    # logger.info(
    #     "请前往开源项目查看更多信息：https://github.com/chengazhen/cursor-auto-free"
    # )


def init_keep_alive():
  greater_than_0_45 = check_cursor_version()
  try:
    logger.info("正在初始化浏览器...")
    # 获取user_agent
    user_agent = get_user_agent()
    if not user_agent:
        logger.error("获取user agent失败，使用默认值")
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

    # 剔除user_agent中的"HeadlessChrome"
    user_agent = user_agent.replace("HeadlessChrome", "Chrome")

    browser_manager = BrowserManager()
    browser = browser_manager.init_browser(user_agent)

    logger.info("============开始配置信息=============")
    login_url = "https://authenticator.cursor.sh"
    sign_up_url = "https://authenticator.cursor.sh/sign-up"
    settings_url = "https://www.cursor.com/settings"
    mail_url = "https://tempmail.plus"

    logger.info("正在生成随机账号信息...")

    email_generator = EmailGenerator()
    first_name = email_generator.default_first_name
    last_name = email_generator.default_last_name
    account = email_generator.generate_email()
    password = email_generator.default_password

    logger.info(f"生成的邮箱账号: {account}")

    logger.info("正在初始化邮箱验证模块...")
    email_handler = EmailVerificationHandler(account)

    auto_update_cursor_auth = True

    tab = browser.latest_tab

    logger.info("\n=== 开始注册流程 ===")
    logger.info(f"正在访问登录页面: {login_url}")
    tab.get(login_url)

    sign_res = sign_up_account(
        browser,
        tab,
        sign_up_url,
        first_name,
        last_name,
        account,
        password,
        settings_url,
        email_handler)
    if sign_res:
      logger.info("正在获取会话令牌...")
      token = get_cursor_session_token(tab)
      if token:
          logger.info("更新认证信息...")
          update_cursor_auth(
              email=account, access_token=token, refresh_token=token
          )
          # logger.info(
          #     "请前往开源项目查看更多信息：https://github.com/chengazhen/cursor-auto-free"
          # )
          logger.info("重置机器码...")
          reset_machine_id(greater_than_0_45)
          logger.info("所有操作已完成")
          print_end_message()
      else:
          logger.error("获取会话令牌失败，注册流程未完成")

  except Exception as e:
      logger.error(f"程序执行出现错误: {str(e)}")
      import traceback

      logger.error(traceback.format_exc())
  finally:
      if browser_manager:
          browser_manager.quit()