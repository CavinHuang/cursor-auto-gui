import customtkinter as ctk
import importlib
from .widgets.basic_tab import AccountFrame, CursorFrame, ButtonFrame
from .widgets.setting_tab import SettingFrame
from .widgets.log_tab.log_frame import LogFrame
from src.utils.file_watcher import FileWatcher
from src.logic.log.log_manager import LogManager

class MainWindow:
    def __init__(self):
        ctk.set_appearance_mode("light")  # 设置主题："light" 或 "dark"
        ctk.set_default_color_theme("blue")  # 设置颜色主题

        self.window = ctk.CTk()

        # 初始化日志管理器
        self.log_manager = LogManager()

        # 初始化文件监听器
        self.file_watcher = FileWatcher("src", self.on_file_changed)
        self.window.title("Cursor Auto GUI")
        self.window.geometry("600x500")

        # 创建顶部标签页
        self.tabview = ctk.CTkTabview(self.window)
        self.tabview.pack(fill="x", padx=10, pady=10)

        # 添加标签页
        self.tabview.add("基础")
        self.tabview.add("设置")
        self.tabview.add("日志")

        # 使用组件化的界面元素
        self.account_frame = AccountFrame(self.tabview.tab("基础"))
        self.account_frame.pack(fill="x", padx=10, pady=5)

        self.cursor_frame = CursorFrame(self.tabview.tab("基础"))
        self.cursor_frame.pack(fill="x", padx=10, pady=5)

        self.button_frame = ButtonFrame(self.tabview.tab("基础"))
        self.button_frame.pack(fill="x", padx=10, pady=10)

        # 设置页面
        self.setting_frame = SettingFrame(self.tabview.tab("设置"))
        self.setting_frame.pack(fill="both", padx=10, pady=5)

        # 日志页面
        self.log_frame = LogFrame(self.tabview.tab("日志"))
        self.log_frame.pack(fill="both", padx=10, pady=5)

        # 设置日志管理器的GUI日志输出对象
        self.log_manager.set_gui_logger(self.log_frame)

    def create(self):
        # 启动文件监听
        self.file_watcher.start()
        return self.window

    def on_file_changed(self, file_path):
        """处理文件变化"""
        try:
            # 获取模块路径
            module_path = file_path.replace("/", ".").replace(".py", "")
            if module_path.startswith("src."):
                # 重新加载模块
                module = importlib.import_module(module_path)
                importlib.reload(module)

                # 重新创建并更新组件
                self.recreate_widgets()
        except Exception as e:
            print(f"重新加载模块失败: {e}")

    def recreate_widgets(self):
        """重新创建所有组件"""
        # 清除现有组件
        for widget in self.tabview.tab("基础").winfo_children():
            widget.destroy()
        for widget in self.tabview.tab("设置").winfo_children():
            widget.destroy()
        for widget in self.tabview.tab("日志").winfo_children():
            widget.destroy()

        # 重新创建组件
        self.account_frame = AccountFrame(self.tabview.tab("基础"))
        self.account_frame.pack(fill="x", padx=10, pady=5)

        self.cursor_frame = CursorFrame(self.tabview.tab("基础"))
        self.cursor_frame.pack(fill="x", padx=10, pady=5)

        self.button_frame = ButtonFrame(self.tabview.tab("基础"))
        self.button_frame.pack(fill="x", padx=10, pady=10)

        # 设置页面
        self.setting_frame = SettingFrame(self.tabview.tab("设置"))
        self.setting_frame.pack(fill="both", padx=10, pady=5)

        # 日志页面
        self.log_frame = LogFrame(self.tabview.tab("日志"))
        self.log_frame.pack(fill="both", padx=10, pady=5)