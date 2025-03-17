import customtkinter as ctk
import threading
from src.logic.cursor_pro.keep_alive import init_keep_alive

class ButtonFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.reset_account_btn = ctk.CTkButton(self, text="立即重置账号", command=self.reset_account)
        self.reset_account_btn.pack(side="left", padx=10)

        self.reset_machine_btn = ctk.CTkButton(self, text="立即重置机器码", command=self.reset_machine_code)
        self.reset_machine_btn.pack(side="left", padx=10)

    def reset_account(self):
        # 禁用按钮，防止重复点击
        self.reset_account_btn.configure(state="disabled", text="重置中...")

        # 创建新线程执行重置操作
        def reset_thread():
            try:
                init_keep_alive()
                # 重置完成后，在主线程中更新UI
                self.after(0, lambda: self.reset_account_btn.configure(state="normal", text="立即重置账号"))
            except Exception as e:
                # 发生错误时，在主线程中更新UI
                self.after(0, lambda: [
                    self.reset_account_btn.configure(state="normal", text="立即重置账号"),
                    print(f"重置失败: {str(e)}")
                ])

        # 启动线程
        threading.Thread(target=reset_thread, daemon=True).start()

    def reset_machine_code(self):
        # TODO: 实现机器码重置逻辑
        pass