import customtkinter as ctk

class LogFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # 创建顶部按钮容器
        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.pack(fill="x", padx=5, pady=5)

        # 创建清空按钮
        self.clear_button = ctk.CTkButton(
            self.button_frame,
            text="清空",
            width=80,
            command=self.clear_log
        )
        self.clear_button.pack(side="right", padx=5)

        # 创建日志文本框
        self.log_text = ctk.CTkTextbox(self, height=400)
        self.log_text.pack(fill="both", expand=True, padx=5, pady=(0, 5))

    def clear_log(self):
        """清空日志内容"""
        self.log_text.delete("1.0", "end")

    def append_log(self, text):
        """添加日志内容"""
        self.log_text.insert("end", text + "\n")
        self.log_text.see("end")  # 自动滚动到最新内容