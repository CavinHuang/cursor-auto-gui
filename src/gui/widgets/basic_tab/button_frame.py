import customtkinter as ctk

class ButtonFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.reset_account_btn = ctk.CTkButton(self, text="立即重置账号", command=self.reset_account)
        self.reset_account_btn.pack(side="left", padx=10)

        self.reset_machine_btn = ctk.CTkButton(self, text="立即重置机器码", command=self.reset_machine_code)
        self.reset_machine_btn.pack(side="left", padx=10)

    def reset_account(self):
        # TODO: 实现账号重置逻辑
        pass

    def reset_machine_code(self):
        # TODO: 实现机器码重置逻辑
        pass