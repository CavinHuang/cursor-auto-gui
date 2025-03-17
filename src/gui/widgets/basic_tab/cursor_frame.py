import customtkinter as ctk

class CursorFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        ctk.CTkLabel(self, text="cursor信息:").pack(anchor="w", padx=10, pady=5)

        # cursor信息字段
        cursor_fields = {
            "安装目录:": "/Users/username/Applications/Cursor",
            "版本号:": "v1.2.3"
        }
        for field, value in cursor_fields.items():
            field_frame = ctk.CTkFrame(self)
            field_frame.pack(fill="x", padx=10, pady=2)
            ctk.CTkLabel(field_frame, text=field, width=80).pack(side="left")
            ctk.CTkLabel(field_frame, text=value).pack(side="left", fill="x", expand=True, padx=(0, 10))