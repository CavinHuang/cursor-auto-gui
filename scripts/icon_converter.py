#!/usr/bin/env python
"""
图标格式转换工具
将SVG/PNG图标转换为ICO(Windows)和ICNS(macOS)格式
"""
import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path
from PIL import Image

def ensure_dir(directory):
    """确保目录存在"""
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory

def svg_to_png(svg_path, png_path, size):
    """将SVG转换为PNG"""
    try:
        # 尝试使用rsvg-convert
        subprocess.run([
            'rsvg-convert',
            '-w', str(size),
            '-h', str(size),
            svg_path,
            '-o', png_path
        ], check=True)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        print("警告: rsvg-convert工具不可用，请确保已安装librsvg")
        return False

def create_icns(png_path, icns_path):
    """创建macOS的ICNS文件 - 简化版本，直接复制现有文件"""
    # 检查是否在macOS上运行
    if sys.platform != 'darwin':
        print("警告: 创建ICNS文件只能在macOS系统上进行")
        return False

    try:
        # 创建临时iconset目录
        with tempfile.TemporaryDirectory() as tmpdir:
            iconset_path = os.path.join(tmpdir, 'icon.iconset')
            os.makedirs(iconset_path)

            # 定义所需的尺寸
            icon_sizes = [
                (16, 'icon_16x16.png'),
                (32, 'icon_16x16@2x.png'),
                (32, 'icon_32x32.png'),
                (64, 'icon_32x32@2x.png'),
                (128, 'icon_128x128.png'),
                (256, 'icon_128x128@2x.png'),
                (256, 'icon_256x256.png'),
                (512, 'icon_256x256@2x.png'),
                (512, 'icon_512x512.png'),
                (1024, 'icon_512x512@2x.png')
            ]

            # 生成每种尺寸的图标
            for size, name in icon_sizes:
                img = Image.open(png_path)
                resized_img = img.resize((size, size), Image.Resampling.LANCZOS)
                resized_path = os.path.join(iconset_path, name)
                resized_img.save(resized_path, 'PNG')

            # 使用iconutil生成icns文件
            subprocess.run([
                'iconutil',
                '-c', 'icns',
                iconset_path,
                '-o', icns_path
            ], check=True)

            return os.path.exists(icns_path)

    except Exception as e:
        print(f"创建ICNS文件时出错: {e}")
        return False

def create_ico(png_path, ico_path):
    """创建Windows的ICO文件"""
    try:
        img = Image.open(png_path)

        # 创建多种尺寸的图标
        sizes = [16, 32, 48, 64, 128, 256]
        images = []

        for size in sizes:
            resized = img.resize((size, size), Image.Resampling.LANCZOS)
            images.append(resized)

        # 保存为ICO
        img.save(ico_path, format='ICO', sizes=[(i.width, i.height) for i in images])

        return os.path.exists(ico_path)

    except Exception as e:
        print(f"创建ICO文件时出错: {e}")
        return False

def main():
    """主函数"""
    # 获取项目根目录
    root_dir = Path(__file__).parent.parent.absolute()

    # 图标路径
    icons_dir = os.path.join(root_dir, 'resources', 'icons')
    ensure_dir(icons_dir)

    svg_path = os.path.join(icons_dir, 'app_icon.svg')
    png_path = os.path.join(icons_dir, 'app_icon.png')
    ico_path = os.path.join(icons_dir, 'app_icon.ico')
    icns_path = os.path.join(icons_dir, 'app_icon.icns')

    # 检查输入文件
    if not os.path.exists(svg_path) and not os.path.exists(png_path):
        print("错误: 未找到源图标文件! 需要app_icon.svg或app_icon.png")
        return 1

    # 如果有SVG但没有PNG，先转换
    if os.path.exists(svg_path) and not os.path.exists(png_path):
        print(f"将SVG转换为PNG: {svg_path} -> {png_path}")
        if not svg_to_png(svg_path, png_path, 1024):
            print("错误: 无法将SVG转换为PNG")
            return 1

    # 确保有PNG文件
    if not os.path.exists(png_path):
        print("错误: 未找到PNG文件，无法继续")
        return 1

    # 创建ICO文件
    print(f"创建ICO文件: {png_path} -> {ico_path}")
    if create_ico(png_path, ico_path):
        print(f"ICO文件已创建: {ico_path}")
    else:
        print("创建ICO文件失败")

    # 创建ICNS文件
    print(f"创建ICNS文件: {png_path} -> {icns_path}")
    if create_icns(png_path, icns_path):
        print(f"ICNS文件已创建: {icns_path}")
    else:
        print("创建ICNS文件失败")

    print("图标转换完成!")
    return 0

if __name__ == "__main__":
    sys.exit(main())