from datetime import datetime
import time
import re
import random
import requests
import email
import imaplib
import poplib
from email.parser import Parser

from src.logic.log import logger

from .config import Config

class EmailVerificationHandler:
    def __init__(self,account):
        self.imap = Config().get_imap()
        self.username = None
        self.epin = None
        self.session = requests.Session()
        self.emailExtension = None
        # 获取协议类型，默认为 POP3
        self.protocol = Config().get_protocol() or 'POP3'
        self.account = account

    def get_verification_code(self, max_retries=5, retry_interval=60):
        """
        获取验证码，带有重试机制。

        Args:
            max_retries: 最大重试次数。
            retry_interval: 重试间隔时间（秒）。

        Returns:
            验证码 (字符串或 None)。
        """

        logger.info(f"开始获取验证码...2")
        print(f"开始获取验证码...2")

        for attempt in range(max_retries):
            try:
                logger.info(f"尝试获取验证码 (第 {attempt + 1}/{max_retries} 次)...")

                logger.info(f"使用 IMAP 获取验证码...")
                print(f"使用 IMAP 获取验证码..., 协议类型: {self.protocol}")
                if self.protocol.upper() == 'IMAP':
                    verify_code = self._get_mail_code_by_imap()
                else:
                    verify_code = self._get_mail_code_by_pop3()
                if verify_code is not None:
                    return verify_code

                if attempt < max_retries - 1:  # 除了最后一次尝试，都等待
                    logger.warning(f"未获取到验证码，{retry_interval} 秒后重试...")
                    time.sleep(retry_interval)

            except Exception as e:
                logger.error(f"获取验证码失败: {e}")  # 记录更一般的异常
                if attempt < max_retries - 1:
                    logger.error(f"发生错误，{retry_interval} 秒后重试...")
                    time.sleep(retry_interval)
                else:
                    raise Exception(f"获取验证码失败且已达最大重试次数: {e}") from e

        raise Exception(f"经过 {max_retries} 次尝试后仍未获取到验证码。")

    # 使用imap获取邮件
    def _get_mail_code_by_imap(self, retry = 0):
        if retry > 0:
            time.sleep(3)
        if retry >= 20:
            raise Exception("获取验证码超时")
        try:
            # 连接到IMAP服务器
            logger.info(f"连接到 IMAP 服务器: {self.imap['imap_server']}, 端口: {self.imap['imap_port']}, 用户名: {self.imap['imap_user']}, imap_dir: {self.imap['imap_dir']}")
            print(f"连接到 IMAP 服务器: {self.imap['imap_server']}, 端口: {self.imap['imap_port']}, 用户名: {self.imap['imap_user']}, imap_dir: {self.imap['imap_dir']}, account: {self.account}")
            mail = imaplib.IMAP4_SSL(self.imap['imap_server'], self.imap['imap_port'])
            mail.login(self.imap['imap_user'], self.imap['imap_pass'])
            search_by_date=False
            # 针对网易系邮箱，imap登录后需要附带联系信息，且后续邮件搜索逻辑更改为获取当天的未读邮件
            if self.imap['imap_user'].endswith(('@163.com', '@126.com', '@yeah.net')):
                imap_id = ("name", self.imap['imap_user'].split('@')[0], "contact", self.imap['imap_user'], "version", "1.0.0", "vendor", "imaplib")
                mail.xatom('ID', '("' + '" "'.join(imap_id) + '")')
                search_by_date=True
                print(f"连接成功1${search_by_date}")
            mail.select(self.imap['imap_dir'])
            # 选择收件箱
            mail.select('inbox')
            logger.info(f"连接成功${search_by_date}")
            if search_by_date:
                date = datetime.now().strftime("%d-%b-%Y")
                status, messages = mail.search(None, f'ON {date} UNSEEN')
            else:
                status, messages = mail.search(None, 'TO', '"'+self.account+'"')
            if status != 'OK':
                return None

            mail_ids = messages[0].split()
            logger.info(f"获取到邮件数量: ${len(mail_ids)}")
            if not mail_ids:
                # 没有获取到，就在获取一次
                return self._get_mail_code_by_imap(retry=retry + 1)

            for mail_id in reversed(mail_ids):
                status, msg_data = mail.fetch(mail_id, '(RFC822)')
                if status != 'OK':
                    continue
                raw_email = msg_data[0][1]
                email_message = email.message_from_bytes(raw_email)

                # 如果是按日期搜索的邮件，需要进一步核对收件人地址是否对应
                if search_by_date and email_message['to'] !=self.account:
                    continue
                body = self._extract_imap_body(email_message)
                if body:
                    code_match = re.search(r"\b\d{6}\b", body)
                    if code_match:
                        code = code_match.group()
                        # 删除找到验证码的邮件
                        mail.store(mail_id, '+FLAGS', '\\Deleted')
                        mail.expunge()
                        mail.logout()
                        return code
            # print("未找到验证码")
            mail.logout()
            return None
        except Exception as e:
            print(f"获取验证码发生错误: {e}")
            return None

    def _extract_imap_body(self, email_message):
        # 提取邮件正文
        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    charset = part.get_content_charset() or 'utf-8'
                    try:
                        body = part.get_payload(decode=True).decode(charset, errors='ignore')
                        return body
                    except Exception as e:
                        logger.error(f"解码邮件正文失败: {e}")
        else:
            content_type = email_message.get_content_type()
            if content_type == "text/plain":
                charset = email_message.get_content_charset() or 'utf-8'
                try:
                    body = email_message.get_payload(decode=True).decode(charset, errors='ignore')
                    return body
                except Exception as e:
                    logger.error(f"解码邮件正文失败: {e}")
        return ""

    # 使用 POP3 获取邮件
    def _get_mail_code_by_pop3(self, retry = 0):
        if retry > 0:
            time.sleep(3)
        if retry >= 20:
            raise Exception("获取验证码超时")

        pop3 = None
        try:
            # 连接到服务器前先等待一小段随机时间，避免并发连接
            time.sleep(random.uniform(0.5, 2))

            # 连接到服务器
            pop3 = poplib.POP3_SSL(self.imap['imap_server'], int(self.imap['imap_port']))
            pop3.user(self.imap['imap_user'])
            pop3.pass_(self.imap['imap_pass'])

            # 获取最新的10封邮件
            num_messages = len(pop3.list()[1])
            for i in range(num_messages, max(1, num_messages-9), -1):
                try:
                    response, lines, octets = pop3.retr(i)
                    msg_content = b'\r\n'.join(lines).decode('utf-8')
                    msg = Parser().parsestr(msg_content)

                    # 检查发件人
                    if 'no-reply@cursor.sh' in msg.get('From', ''):
                        # 提取邮件正文
                        body = self._extract_pop3_body(msg)
                        if body:
                            # 查找验证码
                            code_match = re.search(r"\b\d{6}\b", body)
                            if code_match:
                                code = code_match.group()
                                pop3.quit()
                                return code
                except Exception as e:
                    logger.error(f"处理邮件 {i} 时出错: {e}")
                    continue

            if pop3:
                pop3.quit()
            # 增加重试间隔时间，避免频繁连接
            time.sleep(random.uniform(2, 5))
            return self._get_mail_code_by_pop3(retry=retry + 1)

        except Exception as e:
            logger.error(f"POP3连接发生错误: {e}")
            if pop3:
                try:
                    pop3.quit()
                except:
                    pass
            # 连接失败时增加等待时间
            time.sleep(random.uniform(3, 7))
            return None

    def _extract_pop3_body(self, email_message):
        # 提取邮件正文
        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    try:
                        body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        return body
                    except Exception as e:
                        logger.error(f"解码邮件正文失败: {e}")
        else:
            try:
                body = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
                return body
            except Exception as e:
                logger.error(f"解码邮件正文失败: {e}")
        return ""

    # 手动输入验证码
    def _get_latest_mail_code(self):
        # 获取邮件列表
        mail_list_url = f"https://tempmail.plus/api/mails?email={self.username}{self.emailExtension}&limit=20&epin={self.epin}"
        mail_list_response = self.session.get(mail_list_url)
        mail_list_data = mail_list_response.json()
        time.sleep(0.5)
        if not mail_list_data.get("result"):
            return None, None

        # 获取最新邮件的ID
        first_id = mail_list_data.get("first_id")
        if not first_id:
            return None, None

        # 获取具体邮件内容
        mail_detail_url = f"https://tempmail.plus/api/mails/{first_id}?email={self.username}{self.emailExtension}&epin={self.epin}"
        mail_detail_response = self.session.get(mail_detail_url)
        mail_detail_data = mail_detail_response.json()
        time.sleep(0.5)
        if not mail_detail_data.get("result"):
            return None, None

        # 从邮件文本中提取6位数字验证码
        mail_text = mail_detail_data.get("text", "")
        mail_subject = mail_detail_data.get("subject", "")
        logger.info(f"找到邮件主题: {mail_subject}")
        # 修改正则表达式，确保 6 位数字不紧跟在字母或域名相关符号后面
        code_match = re.search(r"(?<![a-zA-Z@.])\b\d{6}\b", mail_text)

        if code_match:
            return code_match.group(), first_id
        return None, None

    def _cleanup_mail(self, first_id):
        # 构造删除请求的URL和数据
        delete_url = "https://tempmail.plus/api/mails/"
        payload = {
            "email": f"{self.username}{self.emailExtension}",
            "first_id": first_id,
            "epin": f"{self.epin}",
        }

        # 最多尝试5次
        for _ in range(5):
            response = self.session.delete(delete_url, data=payload)
            try:
                result = response.json().get("result")
                if result is True:
                    return True
            except:
                pass

            # 如果失败,等待0.5秒后重试
            time.sleep(0.5)

        return False


if __name__ == "__main__":
    email_handler = EmailVerificationHandler()
    code = email_handler.get_verification_code()
    print(code)
