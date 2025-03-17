import customtkinter as ctk

class SettingFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        # 创建可滚动容器
        self.scrollable_frame = ctk.CTkScrollableFrame(self, height=350)
        self.scrollable_frame.pack(fill="x", padx=5, pady=5)

        # 域名设置
        self.domain_label = ctk.CTkLabel(self.scrollable_frame, text="域名设置:")
        self.domain_label.pack(anchor="w", padx=10, pady=(5, 0))
        self.domain_textbox = ctk.CTkTextbox(self.scrollable_frame, height=100)
        self.domain_textbox.pack(fill="x", padx=10, pady=(0, 10))

        # 邮箱服务地址
        self.mail_server_label = ctk.CTkLabel(self.scrollable_frame, text="邮箱服务地址:")
        self.mail_server_label.pack(anchor="w", padx=10, pady=(5, 0))
        self.mail_server_entry = ctk.CTkEntry(self.scrollable_frame)
        self.mail_server_entry.pack(fill="x", padx=10, pady=(0, 10))

        # 邮箱服务端口
        self.mail_port_label = ctk.CTkLabel(self.scrollable_frame, text="邮箱服务端口:")
        self.mail_port_label.pack(anchor="w", padx=10, pady=(5, 0))
        self.mail_port_entry = ctk.CTkEntry(self.scrollable_frame)
        self.mail_port_entry.pack(fill="x", padx=10, pady=(0, 10))

        # 邮箱地址
        self.mail_address_label = ctk.CTkLabel(self.scrollable_frame, text="邮箱地址:")
        self.mail_address_label.pack(anchor="w", padx=10, pady=(5, 0))
        self.mail_address_entry = ctk.CTkEntry(self.scrollable_frame)
        self.mail_address_entry.pack(fill="x", padx=10, pady=(0, 10))

        # 邮箱授权码
        self.mail_auth_label = ctk.CTkLabel(self.scrollable_frame, text="邮箱授权码:")
        self.mail_auth_label.pack(anchor="w", padx=10, pady=(5, 0))
        self.mail_auth_entry = ctk.CTkEntry(self.scrollable_frame, show="*")
        self.mail_auth_entry.pack(fill="x", padx=10, pady=(0, 10))

        # 邮箱协议
        self.mail_protocol_label = ctk.CTkLabel(self.scrollable_frame, text="邮箱协议:")
        self.mail_protocol_label.pack(anchor="w", padx=10, pady=(5, 0))
        self.mail_protocol_var = ctk.StringVar(value="IMAP")
        self.mail_protocol_radio = ctk.CTkRadioButton(self.scrollable_frame, text="IMAP", variable=self.mail_protocol_var, value="IMAP")
        self.mail_protocol_radio.pack(anchor="w", padx=10, pady=(0, 10))

        # 浏览器地址
        self.browser_url_label = ctk.CTkLabel(self.scrollable_frame, text="浏览器地址:")
        self.browser_url_label.pack(anchor="w", padx=10, pady=(5, 0))
        self.browser_url_entry = ctk.CTkEntry(self.scrollable_frame)
        self.browser_url_entry.pack(fill="x", padx=10, pady=(0, 10))

        # 浏览器用户标识
        self.browser_user_label = ctk.CTkLabel(self.scrollable_frame, text="浏览器用户标识:")
        self.browser_user_label.pack(anchor="w", padx=10, pady=(5, 0))
        self.browser_user_entry = ctk.CTkEntry(self.scrollable_frame)
        self.browser_user_entry.pack(fill="x", padx=10, pady=(0, 10))

        # 保存按钮
        self.save_button = ctk.CTkButton(self, text="保存设置", command=self.save_settings)
        self.save_button.pack(side="bottom", fill="x", padx=10, pady=10)

    def save_settings(self):
        # TODO: 实现保存设置的逻辑
        pass