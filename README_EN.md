<!-- markdownlint-disable -->
<p align="center">
  <img width="240" src="./resources/icons/app_icon.png?raw=true" style="text-align: center;"/>
</p>
<h1 align="center">Cursor Pro</h1>
<h4 align="center">A Simple and Efficient Cursor Automation Tool</h4>

## 🌟 Features

- ✅ Automatically renew Cursor
- ✅ Reset machine code, automatically generate new random machine ID
- ✅ Complete registration process, automatically create new accounts
- ✅ Clean and intuitive user interface
- ✅ Support for light/dark theme switching
- ✅ Multi-platform support
- ✅ Detailed operation logs

## 💻 Supported Platforms

- Windows
- macOS (Intel and Apple Silicon/ARM64)
- Linux

## 📥 Download and Installation

Download the version suitable for your operating system from the [Releases](https://github.com/your-username/CursorPro/releases) page:

- Windows: `CursorPro-Windows-vX.X.X.zip`
- macOS ARM64 (Apple Silicon): `CursorPro-MacOS-ARM64-vX.X.X.zip`
- macOS Intel: `CursorPro-MacOS-Intel-vX.X.X.zip`
- Linux: `CursorPro-Linux-vX.X.X.zip`

### Installation Instructions

#### Windows

1. Extract the downloaded ZIP file
2. Double-click `CursorPro.exe` to run

#### macOS

1. Extract the downloaded ZIP file
2. Drag CursorPro.app to your Applications folder
3. Right-click the app icon and select "Open" when running for the first time
4. If you encounter issues opening the app, please refer to the [macOS Installation Guide](docs/macos_install_guide.md)

#### Linux

1. Extract the downloaded ZIP file
2. Add execution permission to the executable: `chmod +x CursorPro`
3. Run the program: `./CursorPro`

## 🚀 How to Use

1. Launch the application
2. The program will automatically detect system permissions and request necessary privileges
3. The main interface provides the following functions:
   - **Reset Machine Code**: Generate a new random machine ID to reset usage limits
   - **Automatic Registration**: Complete the registration process and automatically create a new account
   - **Renewal Management**: Automatically implement Cursor renewal operations

## 🔧 Development Guide

If you want to participate in development or run the source code locally, please follow these steps:

### Requirements

- Python 3.8+
- PySide6

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run the Program

```bash
python main.py
```

## 📂 Project Structure

```
cursor-auto-gui/
├── main.py                 # Program entry
├── launcher.py             # Permission verification launcher
├── requirements.txt        # Project dependencies
├── src/                    # Source code directory
│   ├── gui/                # Graphical interface module
│   │   ├── widgets/        # UI components
│   │   ├── pages/          # Page component module
│   │   ├── main_window.py  # Main window
│   ├── logic/              # Business logic
│   │   ├── log/            # Log management
│   ├── utils/              # Utility functions
└── resources/              # Resource files
    ├── icons/              # Icon resources
```

## 📷 Application Screenshots

![Home](screenshots/turnstile_start_1743489653.png)

## ❓ Common Issues

### Note for macOS Users

If you encounter issues opening the application on macOS, please check the detailed [macOS Installation Guide](docs/macos_install_guide.md), which includes steps to resolve macOS security restrictions.

### Application Crashes or Fails to Start

- Make sure you've downloaded the version matching your operating system
- Check if any antivirus software is blocking the application
- Try running the program with administrator/root privileges

## 📜 License

This project is licensed under [CC BY-NC-ND 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0/).
This means you can:

- Share — copy and redistribute the material in any medium or format

But you must follow these conditions:
- NonCommercial — You may not use the material for commercial purposes

## ⚠️ Disclaimer

- This project is for educational and personal use only. Do not use for commercial purposes.
- This project assumes no legal responsibility. Any consequences arising from the use of this project are the sole responsibility of the user.

## 🙏 Special Thanks

The development of this project received support and help from many open source projects and community members. Special thanks to:

### Open Source Projects

- [go-cursor-help](https://github.com/yuaotian/go-cursor-help) - An excellent Cursor machine code reset tool. This project's machine code reset functionality references the implementation of this project. It has received 9.1k Stars and is one of the most popular Cursor auxiliary tools.
- [cursor-auto-free](https://github.com/chengazhen/cursor-auto-free.git) - An excellent Cursor automatic renewal tool. This project's automatic renewal functionality references the implementation of this project.

## 👨‍💻 Developer

- Minator 水门

## 🤝 Contributing

Issue reports, feature suggestions, and code contributions are welcome! If you're interested in participating in project development, please follow these steps:

1. Fork this repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request