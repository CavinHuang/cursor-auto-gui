
from src.logic.cursor_pro.get_email_code import EmailVerificationHandler


if __name__ == "__main__":
    account = "aerionna149@terminalxp.site"  # 替换为实际的邮箱账号
    email_handler = EmailVerificationHandler(account)
    code = email_handler.get_verification_code()
    print(code)