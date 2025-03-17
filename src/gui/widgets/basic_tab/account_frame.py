import customtkinter as ctk

class AccountFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        ctk.CTkLabel(self, text="账号信息:").pack(anchor="w", padx=10, pady=5)

        # 账号信息字段
        fields = {
            "账号:": "user123@example.com",
            "密码:": "********",
            "注册时间:": "2023-12-01 10:30:00",
            "过期时间:": "2024-12-01 10:30:00"
        }
        for field, value in fields.items():
            field_frame = ctk.CTkFrame(self)
            field_frame.pack(fill="x", padx=10, pady=2)
            ctk.CTkLabel(field_frame, text=field, width=80).pack(side="left")
            ctk.CTkLabel(field_frame, text=value).pack(side="left", fill="x", expand=True, padx=(0, 10))