import os

project_root = os.path.dirname(os.path.dirname(__file__))

app_name = "Cursor Pro"
version = "0.0.1"

def read_version():
    """读取version文件获取版本号"""
    version_file = os.path.join(project_root, "version")
    if os.path.exists(version_file):
        with open(version_file, "r", encoding="utf-8") as f:
            _text =  f.read().strip()
            _info = _text.split("\n")
            app_name = _info[0] if len(_info) > 0 else "Cursor Pro"
            version = _info[1] if len(_info) > 1 else "0.0.1"
    return app_name, version

app_name, version = read_version()


system_config = {
    "app_name": app_name,
    "app_version": version,
    "app_author": "Minato 水门",
    "app_email": "minato@minato.com",
    "app_url": "https://minato.com",
    "app_github_url": "https://github.com/CavinHuang",
    "app_github_repo": "CavinHuang/cursor-pro",
    "mp_wechat_name": "AI星图部落",
    "mp_wechat_qrcode": "images/mp_wechat_qrcode.png",
    "app_config_path": ".cursor_pro",
}