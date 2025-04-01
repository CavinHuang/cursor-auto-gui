import os
import sys
import platform
import requests
import tempfile
import shutil
import subprocess
from pathlib import Path
from packaging import version
from PySide6.QtCore import QObject, Signal, Slot, QThread
from config.config import system_config

class UpdateChecker(QObject):
    """GitHub Release 版本更新检查器"""
    update_available = Signal(str, str)  # 信号：有新版本可用 (版本号, 下载URL)
    update_not_available = Signal()      # 信号：没有新版本
    update_error = Signal(str)           # 信号：更新检查出错
    download_progress = Signal(int)      # 信号：下载进度
    download_complete = Signal(str)      # 信号：下载完成 (文件路径)
    download_error = Signal(str)         # 信号：下载出错

    def __init__(self, parent=None):
        super().__init__(parent)
        self.github_api_url = f"https://api.github.com/repos/{self._get_repo_owner_name()}/releases/latest"
        self.current_version = system_config["app_version"]
        self.system = platform.system()
        self.download_thread = None
        self.temp_dir = None
        # 判断是否为开发环境
        self.is_dev_env = self._is_development_environment()

    def _is_development_environment(self):
        """判断是否为开发环境"""
        # 检查是否有开发环境标记
        if 'dev' in self.current_version.lower() or 'development' in self.current_version.lower():
            return True

        # 检查是否从源代码目录运行（存在.git目录或setup.py）
        current_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(os.path.dirname(current_dir))

        if (os.path.exists(os.path.join(root_dir, '.git')) or
            os.path.exists(os.path.join(root_dir, 'setup.py'))):
            return True

        # 检查是否设置了开发环境变量
        if os.environ.get('APP_ENV', '').lower() == 'development':
            return True

        return False

    def _get_repo_owner_name(self):
        """从 GitHub URL 获取仓库所有者和名称"""
        github_url = system_config.get("app_github_url", "")
        # 默认值
        default_repo = f"{system_config['app_github_repo']}"

        # 假设格式为 https://github.com/owner/repo
        if github_url and "github.com" in github_url:
            parts = github_url.rstrip("/").split("github.com/")
            if len(parts) > 1 and "/" in parts[1]:
                # 提取owner/repo部分
                repo_path = parts[1]
                # 移除URL中可能存在的额外路径和参数
                repo_path = repo_path.split("/", 2)[0:2]
                if len(repo_path) == 2:
                    return "/".join(repo_path)

        return default_repo  # 返回默认值

    @Slot()
    def check_for_updates(self):
        """检查更新"""
        try:
            response = requests.get(self.github_api_url, timeout=10)
            response.raise_for_status()

            release_data = response.json()
            latest_version = release_data["tag_name"].lstrip("v")
            print(f"latest_version: {latest_version}")

            # 比较版本
            if version.parse(latest_version) > version.parse(self.current_version):
                # 找到匹配当前系统的资源
                download_url = None
                for asset in release_data["assets"]:
                    print(f"asset: {asset['name']}")
                    if self.system == "Windows" and "Windows" in asset["name"]:
                        download_url = asset["browser_download_url"]
                        break
                    elif self.system == "Darwin" and "MacOS" in asset["name"]:
                        download_url = asset["browser_download_url"]
                        break

                if download_url:
                    self.update_available.emit(latest_version, download_url)
                    return
                else:
                    self.update_error.emit(f"未找到适用于 {self.system} 的安装包")
            else:
                self.update_not_available.emit()
        except Exception as e:
            self.update_error.emit(f"检查更新失败: {str(e)}")

    @Slot(str)
    def download_update(self, url):
        """在单独的线程中下载更新"""
        self.temp_dir = tempfile.mkdtemp()
        self.download_thread = DownloadThread(url, self.temp_dir, self.system)
        self.download_thread.progress.connect(self.download_progress)
        self.download_thread.complete.connect(self.download_complete)
        self.download_thread.error.connect(self.download_error)
        self.download_thread.start()


class DownloadThread(QThread):
    """下载线程"""
    progress = Signal(int)
    complete = Signal(str)
    error = Signal(str)

    def __init__(self, url, temp_dir, system):
        super().__init__()
        self.url = url
        self.temp_dir = temp_dir
        self.system = system

    def run(self):
        try:
            # 获取文件名
            file_name = os.path.basename(self.url)
            file_path = os.path.join(self.temp_dir, file_name)

            # 下载文件
            response = requests.get(self.url, stream=True, timeout=60)
            response.raise_for_status()

            # 获取文件大小
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0

            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            progress = int((downloaded / total_size) * 100)
                            self.progress.emit(progress)

            self.complete.emit(file_path)
        except Exception as e:
            self.error.emit(f"下载更新失败: {str(e)}")


def install_update(file_path):
    """安装更新

    根据不同平台执行不同的安装逻辑
    """
    system = platform.system()

    # 检查是否为开发环境
    is_dev_env = _is_development_environment()
    if is_dev_env:
        print("开发环境下，仅下载更新文件，不执行安装和清除操作")
        return True

    try:
        if system == "Windows":
            # Windows: 解压 ZIP 文件
            import zipfile
            extract_dir = os.path.join(tempfile.gettempdir(), "cursor_pro_update")

            # 清理旧的解压目录
            if os.path.exists(extract_dir):
                shutil.rmtree(extract_dir)
            os.makedirs(extract_dir)

            # 解压文件
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)

            # 启动安装程序或替换可执行文件
            exe_path = os.path.join(extract_dir, "CursorPro.exe")
            if os.path.exists(exe_path):
                # 创建批处理文件来替换现有的可执行文件
                batch_file = os.path.join(tempfile.gettempdir(), "update_cursor_pro.bat")
                current_exe = os.path.abspath(sys.argv[0])

                with open(batch_file, 'w') as f:
                    f.write(f"""@echo off
timeout /t 2 /nobreak > nul
copy /Y "{exe_path}" "{current_exe}"
start "" "{current_exe}"
del "%~f0"
""")

                # 运行批处理文件
                subprocess.Popen(["cmd", "/c", batch_file])
                sys.exit(0)

        elif system == "Darwin":
            # macOS: 解压 ZIP 文件
            extract_dir = os.path.join(tempfile.gettempdir(), "cursor_pro_update")

            # 清理旧的解压目录
            if os.path.exists(extract_dir):
                shutil.rmtree(extract_dir)
            os.makedirs(extract_dir)

            # 解压文件
            subprocess.run(["unzip", "-q", file_path, "-d", extract_dir], check=True)

            # 找到 .app 包
            app_path = None
            for item in os.listdir(extract_dir):
                if item.endswith(".app"):
                    app_path = os.path.join(extract_dir, item)
                    break

            if app_path:
                # 创建 AppleScript 来替换现有应用
                current_app = os.path.abspath(os.path.dirname(sys.argv[0]))
                if current_app.endswith(".app/Contents/MacOS"):
                    current_app = current_app[:current_app.index(".app") + 4]

                applescript = f"""
                do shell script "rm -rf '{current_app}' && cp -R '{app_path}' '{os.path.dirname(current_app)}' && open '{current_app}'" with administrator privileges
                """

                # 保存 AppleScript
                script_path = os.path.join(tempfile.gettempdir(), "update_cursor_pro.scpt")
                with open(script_path, 'w') as f:
                    f.write(applescript)

                # 运行 AppleScript
                subprocess.Popen(["osascript", script_path])
                sys.exit(0)
    except Exception as e:
        print(f"安装更新失败: {str(e)}")
        return False

    return True

def _is_development_environment():
    """判断是否为开发环境"""
    # 检查app_version是否包含开发版本标记
    if 'dev' in system_config.get('app_version', '').lower() or 'development' in system_config.get('app_version', '').lower():
        return True

    # 检查是否从源代码目录运行（存在.git目录或setup.py）
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(os.path.dirname(current_dir))

    if (os.path.exists(os.path.join(root_dir, '.git')) or
        os.path.exists(os.path.join(root_dir, 'setup.py'))):
        return True

    # 检查是否设置了开发环境变量
    if os.environ.get('APP_ENV', '').lower() == 'development':
        return True

    return False