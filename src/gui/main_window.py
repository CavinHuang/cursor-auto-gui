import customtkinter as ctk
from .widgets.basic_tab import AccountFrame, CursorFrame, ButtonFrame
from .widgets.setting_tab import SettingFrame
from .widgets.log_tab.log_frame import LogFrame
from src.logic.log.log_manager import LogManager

class MainWindow:
    def __init__(self):
        ctk.set_appearance_mode("light")  # 设置主题："light" 或 "dark"
        ctk.set_default_color_theme("blue")  # 设置颜色主题

        self.window = ctk.CTk()

        # 初始化日志管理器
        self.log_manager = LogManager()

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
        return self.window
