# CursorPro

CursorPro is a simple and efficient cursor keep-alive tool that prevents your system from entering sleep mode, ideal for scenarios requiring the computer to stay active for extended periods.

## Features

- Prevents computer from automatically sleeping
- Periodically moves mouse cursor or simulates key presses
- Low resource consumption, lightweight operation
- Supports multiple operating system platforms
- Simple and easy-to-use interface

## Supported Platforms

- Windows
- macOS (Intel and Apple Silicon/ARM64)
- Linux

## Download and Installation

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

## How to Use

1. Launch the application
2. Set the activity interval (default is 60 seconds)
3. Click the "Start" button to activate the program
4. The program will automatically run in the background, periodically simulating user activity to keep the system active

## Common Issues

### Note for macOS Users

If you encounter issues opening the application on macOS, please check the detailed [macOS Installation Guide](docs/macos_install_guide.md), which includes steps to resolve macOS security restrictions.

### Application Crashes or Fails to Start

- Make sure you've downloaded the version matching your operating system
- Check if any antivirus software is blocking the application
- Try running the program with administrator/root privileges

## License

This project is licensed under [CC BY-NC-ND 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0/).
This means you can:

- Share — copy and redistribute the material in any medium or format
But you must follow these conditions:
- NonCommercial — You may not use the material for commercial purposes

## Disclaimer

- This project is for educational and personal use only. Do not use for commercial purposes.
- This project assumes no legal responsibility. Any consequences arising from the use of this project are the sole responsibility of the user.

## Special Thanks

The development of this project received support and help from many open source projects and community members. Special thanks to:

### Open Source Projects

- [go-cursor-help](https://github.com/yuaotian/go-cursor-help) - An excellent Cursor machine code reset tool. This project implements the machine code reset function using this project. It has received 9.1k Stars and is one of the most popular Cursor auxiliary tools.
- [cursor-auto-free](https://github.com/chengazhen/cursor-auto-free.git) - An excellent Cursor automatic renewal tool. This project implements the automatic renewal function using this project.

## Contributing

Issue reports, feature suggestions, and code contributions are welcome!