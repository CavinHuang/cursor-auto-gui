<!-- markdownlint-disable -->
<p align="center">
  <img width="240" src="./resources/icons/icon.png?raw=true" style="text-align: center;"/>
</p>
<h1 align="center">CursorPro</h1>
<h4 align="center">一款简单高效的Cursor自动续期工具</h4>

## 功能特点

- 自动续期Cursor
- 支持多种操作系统平台
- 简洁易用的界面

## 支持的平台

- Windows
- macOS (Intel 和 Apple Silicon/ARM64)
- Linux

## 下载安装

从 [Releases](https://github.com/your-username/CursorPro/releases) 页面下载适合您操作系统的版本：

- Windows: `CursorPro-Windows-vX.X.X.zip`
- macOS ARM64 (Apple Silicon): `CursorPro-MacOS-ARM64-vX.X.X.zip`
- macOS Intel: `CursorPro-MacOS-Intel-vX.X.X.zip`
- Linux: `CursorPro-Linux-vX.X.X.zip`

### 安装说明

#### Windows

1. 解压下载的 ZIP 文件
2. 双击运行 `CursorPro.exe`

#### macOS

1. 解压下载的 ZIP 文件
2. 将 CursorPro.app 拖动到应用程序文件夹
3. 首次运行时右键点击应用图标并选择"打开"
4. 如遇到无法打开的情况，请参考 [macOS 安装指南](docs/macos_install_guide.md)

#### Linux

1. 解压下载的 ZIP 文件
2. 给执行文件添加执行权限：`chmod +x CursorPro`
3. 运行程序：`./CursorPro`

## 使用方法

1. 启动应用程序
2. 设置活动间隔时间（默认为60秒）
3. 点击"开始"按钮激活程序
4. 程序将自动在后台运行，定期模拟用户活动以保持系统活跃

## 常见问题

### macOS 用户注意事项

如果在 macOS 上遇到无法打开应用的问题，请查看详细的 [macOS 安装指南](docs/macos_install_guide.md)，其中包含解决 macOS 安全限制的步骤。

### 应用闪退或无法启动

- 确保您下载的是与您操作系统匹配的版本
- 检查是否有杀毒软件拦截了应用程序
- 尝试以管理员/root权限运行程序

## 许可证

本项目采用 [CC BY-NC-ND 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0/) 许可证。
这意味着您可以：

- 分享 — 在任何媒介以任何形式复制、发行本作品
但必须遵守以下条件：
- 非商业性使用 — 您不得将本作品用于商业目的

## 声明

- 本项目仅供学习交流使用，请勿用于商业用途。
- 本项目不承担任何法律责任，使用本项目造成的任何后果，由使用者自行承担。

## 特别鸣谢

本项目的开发过程中得到了众多开源项目和社区成员的支持与帮助，在此特别感谢：

### 开源项目

- [go-cursor-help](https://github.com/yuaotian/go-cursor-help) - 一个优秀的 Cursor 机器码重置工具，本项目的机器码重置功能使用该项目实现。该项目目前已获得 9.1k Stars，是最受欢迎的 Cursor 辅助工具之一。
- [cursor-auto-free](https://github.com/chengazhen/cursor-auto-free.git) - 一个优秀的 Cursor 自动续期工具，本项目的自动续期功能使用该项目实现。

## 贡献

欢迎提交问题报告和功能建议，也欢迎提交代码贡献！
