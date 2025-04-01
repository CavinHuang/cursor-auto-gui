import os
import subprocess
import sys
import time
import shutil
import getpass
import secrets
import uuid
import json
import tempfile
import glob
import re
from datetime import datetime
from src.logic.log import logger

home = os.path.expanduser("~")
# 定义配置文件路径
STORAGE_FILE=f"{home}/Library/Application Support/Cursor/User/globalStorage/storage.json"
BACKUP_DIR=f"{home}/Library/Application Support/Cursor/User/globalStorage/backups"

# 定义 Cursor 应用程序路径
CURSOR_APP_PATH="/Applications/Cursor.app"


# 检查并关闭 Cursor 进程
def check_and_kill_cursor():
  logger.info("检查 Cursor 进程...")

  attempt = 1
  max_attempts = 5

  # 函数：获取进程详细信息
  def get_process_details(process_name):
      logger.debug(f"正在获取 {process_name} 进程详细信息：")
      result = subprocess.run(
          "ps aux | grep -i \"/Applications/Cursor.app\" | grep -v grep",
          shell=True,
          text=True,
          capture_output=True
      )
      if result.stdout:
          logger.debug(result.stdout)
      return result.stdout

  while attempt <= max_attempts:
      # 使用更精确的匹配来获取 Cursor 进程
      result = subprocess.run(
          "ps aux | grep -i \"/Applications/Cursor.app\" | grep -v grep | awk '{print $2}'",
          shell=True,
          text=True,
          capture_output=True
      )

      cursor_pids = result.stdout.strip().split('\n') if result.stdout.strip() else []

      if not cursor_pids or cursor_pids == [""]:
          logger.info("未发现运行中的 Cursor 进程")
          return 0

      logger.warning("发现 Cursor 进程正在运行")
      get_process_details("cursor")

      logger.warning("尝试关闭 Cursor 进程...")

      for pid in cursor_pids:
          if pid:
              try:
                  if attempt == max_attempts:
                      logger.warning("尝试强制终止进程...")
                      os.kill(int(pid), 9)  # SIGKILL
                  else:
                      os.kill(int(pid), 15)  # SIGTERM
              except ProcessLookupError:
                  pass
              except Exception as e:
                  logger.error(f"终止进程 {pid} 时出错: {e}")

      time.sleep(1)

      # 检查进程是否还在运行
      check_result = subprocess.run(
          "ps aux | grep -i \"/Applications/Cursor.app\" | grep -v grep",
          shell=True,
          text=True,
          capture_output=True
      )

      if not check_result.stdout.strip():
          logger.info("Cursor 进程已成功关闭")
          return 0

      logger.warning(f"等待进程关闭，尝试 {attempt}/{max_attempts}...")
      attempt += 1

  logger.error(f"在 {max_attempts} 次尝试后仍无法关闭 Cursor 进程")
  get_process_details("cursor")
  logger.error("请手动关闭进程后重试")
  return 1  # 返回错误代码，而不是直接退出

# 备份配置文件
def backup_config():
    if not os.path.exists(STORAGE_FILE):
        logger.warning("配置文件不存在，跳过备份")
        return 0

    # 创建备份目录（如果不存在）
    os.makedirs(BACKUP_DIR, exist_ok=True)

    # 生成带时间戳的备份文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"{BACKUP_DIR}/storage.json.backup_{timestamp}"

    try:
        # 复制配置文件到备份位置
        shutil.copy2(STORAGE_FILE, backup_file)

        # 设置权限和所有者
        os.chmod(backup_file, 0o644)  # 设置为 644 权限
        current_user = getpass.getuser()

        # 在 macOS 中需要使用 subprocess 调用 chown，因为 Python 的 os.chown 需要 uid 和 gid
        subprocess.run(f"chown {current_user} '{backup_file}'", shell=True, check=True)

        logger.info(f"配置已备份到: {backup_file}")
        return 0
    except Exception as e:
        logger.error(f"备份失败: {e}")
        return 1  # 返回错误代码，而不是直接退出

# 生成随机 ID
def generate_random_id():
    """
    生成32字节(64个十六进制字符)的随机数
    相当于 Shell 中的 openssl rand -hex 32
    """
    # 使用 secrets 模块生成安全的随机字节
    random_bytes = secrets.token_bytes(32)
    # 转换为十六进制字符串
    return random_bytes.hex()

# 生成随机 UUID
def generate_uuid():
    """
    生成随机 UUID 并转换为小写
    相当于 Shell 中的 uuidgen | tr '[:upper:]' '[:lower:]'
    """
    # 使用 uuid 模块生成 UUID 并转换为小写字符串
    return str(uuid.uuid4()).lower()

# 修改现有文件
def modify_or_add_config(key, value, file_path):
    """
    在JSON配置文件中修改或添加指定键值对
    相当于Shell脚本中的modify_or_add_config函数

    Args:
        key: 要修改或添加的键名
        value: 对应的值
        file_path: 配置文件路径

    Returns:
        int: 成功返回0，失败返回1
    """
    if not os.path.isfile(file_path):
        logger.error(f"文件不存在: {file_path}")
        return 1

    try:
        # 确保文件可写
        try:
            os.chmod(file_path, 0o644)
        except Exception as e:
            logger.error(f"无法修改文件权限: {file_path} - {e}")
            return 1

        # 创建临时文件
        fd, temp_file = tempfile.mkstemp()
        os.close(fd)

        try:
            # 读取JSON文件
            with open(file_path, 'r', encoding='utf-8') as f:
                try:
                    config = json.load(f)
                except json.JSONDecodeError as e:
                    logger.error(f"JSON解析错误: {e}")
                    return 1

            # 修改或添加键值对
            config[key] = value

            # 写入临时文件
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)

            # 检查临时文件是否为空
            if os.path.getsize(temp_file) == 0:
                logger.error("生成的临时文件为空")
                os.unlink(temp_file)
                return 1

            # 替换原文件内容
            shutil.copy2(temp_file, file_path)

            # 恢复文件权限
            os.chmod(file_path, 0o444)

            logger.info(f"已成功{'修改' if key in config else '添加'}配置: {key}")
            return 0

        finally:
            # 删除临时文件
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    except Exception as e:
        logger.error(f"修改配置失败: {e}")
        # 尝试恢复文件权限
        try:
            os.chmod(file_path, 0o444)
        except:
            pass
        return 1

# 生成新的配置
def generate_new_config():
    """
    处理Cursor配置文件
    相当于Shell脚本中的generate_new_config函数

    Returns:
        int: 成功返回0
    """
    print()  # 空行
    logger.warning("机器码处理")

    # 默认不重置机器码
    reset_choice = 0

    # 记录日志以便调试
    with open(os.environ.get("LOG_FILE", "/tmp/cursor_helper.log"), "a") as log_file:
        log_file.write(f"[INPUT_DEBUG] 机器码重置选项: 不重置 (默认)\n")

    # 处理 - 默认为不重置
    logger.info("默认不重置机器码，将仅修改js文件")

    # 确保配置文件目录存在
    if os.path.isfile(STORAGE_FILE):
        logger.info(f"发现已有配置文件: {STORAGE_FILE}")

        # 备份现有配置（以防万一）
        backup_config()
    else:
        logger.warning("未找到配置文件，这是正常的，脚本将跳过ID修改")

    print()  # 空行
    logger.info("配置处理完成")

    return 0

# 清理 Cursor 之前的修改
def clean_cursor_app():
    """
    尝试清理Cursor之前的修改，通过恢复备份
    相当于Shell脚本中的clean_cursor_app函数

    Returns:
        int: 成功返回0，失败返回1
    """
    logger.info("尝试清理 Cursor 之前的修改...")

    # 如果存在备份，直接恢复备份
    latest_backup = ""

    # 查找最新的备份（按时间排序）
    try:
        backup_dirs = glob.glob("/tmp/Cursor.app.backup_*")
        # 过滤出目录
        backup_dirs = [d for d in backup_dirs if os.path.isdir(d)]
        # 按修改时间倒序排序
        backup_dirs.sort(key=lambda x: os.path.getmtime(x), reverse=True)

        if backup_dirs:
            latest_backup = backup_dirs[0]
    except Exception as e:
        logger.error(f"查找备份时出错: {e}")

    if latest_backup and os.path.isdir(latest_backup):
        logger.info(f"找到现有备份: {latest_backup}")
        logger.info("正在恢复原始版本...")

        # 停止 Cursor 进程
        check_and_kill_cursor()

        # 恢复备份 (使用sudo权限)
        current_user = getpass.getuser()

        try:
            # 删除现有应用
            subprocess.run(f"sudo rm -rf '{CURSOR_APP_PATH}'", shell=True, check=True)

            # 复制备份
            subprocess.run(f"sudo cp -R '{latest_backup}' '{CURSOR_APP_PATH}'", shell=True, check=True)

            # 设置所有权
            subprocess.run(f"sudo chown -R {current_user}:staff '{CURSOR_APP_PATH}'", shell=True, check=True)

            # 设置权限
            subprocess.run(f"sudo chmod -R 755 '{CURSOR_APP_PATH}'", shell=True, check=True)

            logger.info("已恢复原始版本")
            return 0
        except subprocess.CalledProcessError as e:
            logger.error(f"恢复备份时出错: {e}")
            return 1
    else:
        logger.warning("未找到现有备份，尝试重新安装 Cursor...")
        print("您可以从 https://cursor.sh 下载并重新安装 Cursor")
        print("或者继续执行此脚本，将尝试修复现有安装")

        # 可以在这里添加重新下载和安装的逻辑
        return 1

# 修改 Cursor 主程序文件（安全模式）
def modify_cursor_app_files():
    """
    安全修改Cursor主程序文件，替换设备ID生成机制
    相当于Shell脚本中的modify_cursor_app_files函数

    Returns:
        int: 成功返回0，失败返回1
    """
    logger.info("正在安全修改 Cursor 主程序文件...")
    log_file = os.environ.get("LOG_FILE", "/tmp/cursor_helper.log")
    logger.info(f"详细日志将记录到: {log_file}")

    # 先清理之前的修改
    clean_cursor_app()

    # 验证应用是否存在
    if not os.path.isdir(CURSOR_APP_PATH):
        logger.error(f"未找到 Cursor.app，请确认安装路径: {CURSOR_APP_PATH}")
        return 1

    # 定义目标文件 - 将extensionHostProcess.js放在最前面优先处理
    target_files = [
        f"{CURSOR_APP_PATH}/Contents/Resources/app/out/vs/workbench/api/node/extensionHostProcess.js",
        f"{CURSOR_APP_PATH}/Contents/Resources/app/out/main.js",
        f"{CURSOR_APP_PATH}/Contents/Resources/app/out/vs/code/node/cliProcessMain.js"
    ]

    # 检查文件是否存在并且是否已修改
    need_modification = False
    missing_files = False

    logger.debug("检查目标文件...")
    for file in target_files:
        if not os.path.isfile(file):
            logger.warning(f"文件不存在: {file.replace(CURSOR_APP_PATH+'/', '')}")
            with open(log_file, "a") as f:
                f.write(f"[FILE_CHECK] 文件不存在: {file}\n")
            missing_files = True
            continue

        with open(log_file, "a") as f:
            file_size = os.path.getsize(file)
            f.write(f"[FILE_CHECK] 文件存在: {file} ({file_size} 字节)\n")

        # 检查文件是否已修改
        with open(file, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            if "return crypto.randomUUID()" not in content:
                logger.info(f"文件需要修改: {file.replace(CURSOR_APP_PATH+'/', '')}")

                # 检查关键词并记录
                with open(log_file, "a") as log_f:
                    lines = content.split("\n")
                    platform_uuid_lines = []
                    for i, line in enumerate(lines):
                        if "IOPlatformUUID" in line:
                            platform_uuid_lines.append(f"{i+1}: {line}")
                            if len(platform_uuid_lines) >= 3:
                                break

                    if platform_uuid_lines:
                        log_f.write("\n".join(platform_uuid_lines) + "\n")
                    else:
                        log_f.write("[FILE_CHECK] 未找到 IOPlatformUUID\n")

                need_modification = True
                break
            else:
                logger.info(f"文件已修改: {file.replace(CURSOR_APP_PATH+'/', '')}")

    # 如果所有文件都已修改或不存在，则退出
    if missing_files:
        logger.error("部分目标文件不存在，请确认 Cursor 安装是否完整")
        return 1

    if not need_modification:
        logger.info("所有目标文件已经被修改过，无需重复操作")
        return 0

    # 创建临时工作目录
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_dir = f"/tmp/cursor_reset_{timestamp}"
    temp_app = f"{temp_dir}/Cursor.app"
    backup_app = f"/tmp/Cursor.app.backup_{timestamp}"

    logger.debug(f"创建临时目录: {temp_dir}")
    with open(log_file, "a") as f:
        f.write(f"[TEMP_DIR] 创建临时目录: {temp_dir}\n")

    # 清理可能存在的旧临时目录
    if os.path.exists(temp_dir):
        logger.info("清理已存在的临时目录...")
        try:
            shutil.rmtree(temp_dir)
        except Exception as e:
            logger.error(f"清理临时目录失败: {e}")
            return 1

    # 创建新的临时目录
    try:
        os.makedirs(temp_dir, exist_ok=True)
    except Exception as e:
        logger.error(f"无法创建临时目录: {temp_dir} - {e}")
        with open(log_file, "a") as f:
            f.write(f"[ERROR] 无法创建临时目录: {temp_dir}\n")
        return 1

    # 备份原应用
    logger.info("备份原应用...")
    with open(log_file, "a") as f:
        f.write(f"[BACKUP] 开始备份: {CURSOR_APP_PATH} -> {backup_app}\n")

    try:
        shutil.copytree(CURSOR_APP_PATH, backup_app)
    except Exception as e:
        logger.error(f"无法创建应用备份: {e}")
        with open(log_file, "a") as f:
            f.write(f"[ERROR] 备份失败: {CURSOR_APP_PATH} -> {backup_app}\n")
        shutil.rmtree(temp_dir, ignore_errors=True)
        return 1

    with open(log_file, "a") as f:
        f.write("[BACKUP] 备份完成\n")

    # 复制应用到临时目录
    logger.info("创建临时工作副本...")
    with open(log_file, "a") as f:
        f.write(f"[COPY] 开始复制: {CURSOR_APP_PATH} -> {temp_dir}\n")

    try:
        shutil.copytree(CURSOR_APP_PATH, temp_app)
    except Exception as e:
        logger.error(f"无法复制应用到临时目录: {e}")
        with open(log_file, "a") as f:
            f.write(f"[ERROR] 复制失败: {CURSOR_APP_PATH} -> {temp_dir}\n")
        shutil.rmtree(temp_dir, ignore_errors=True)
        shutil.rmtree(backup_app, ignore_errors=True)
        return 1

    with open(log_file, "a") as f:
        f.write("[COPY] 复制完成\n")

    # 确保临时目录的权限正确
    current_user = getpass.getuser()
    try:
        subprocess.run(f"chown -R {current_user}:staff '{temp_dir}'", shell=True, check=True)
        subprocess.run(f"chmod -R 755 '{temp_dir}'", shell=True, check=True)
    except subprocess.CalledProcessError as e:
        logger.warning(f"设置权限失败，但将继续执行: {e}")

    # 移除签名（增强兼容性）
    logger.info("移除应用签名...")
    with open(log_file, "a") as f:
        f.write(f"[CODESIGN] 移除签名: {temp_app}\n")

    try:
        result = subprocess.run(f"codesign --remove-signature '{temp_app}'",
                              shell=True,
                              capture_output=True,
                              text=True)

        with open(log_file, "a") as f:
            f.write(result.stderr)
    except Exception as e:
        logger.warning(f"移除应用签名失败: {e}")
        with open(log_file, "a") as f:
            f.write(f"[WARN] 移除签名失败: {temp_app}\n")

    # 移除所有相关组件的签名
    components = [
        f"{temp_app}/Contents/Frameworks/Cursor Helper.app",
        f"{temp_app}/Contents/Frameworks/Cursor Helper (GPU).app",
        f"{temp_app}/Contents/Frameworks/Cursor Helper (Plugin).app",
        f"{temp_app}/Contents/Frameworks/Cursor Helper (Renderer).app"
    ]

    for component in components:
        if os.path.exists(component):
            logger.info(f"正在移除签名: {component}")
            try:
                subprocess.run(f"codesign --remove-signature '{component}'", shell=True)
            except Exception as e:
                logger.warning(f"移除组件签名失败: {component} - {e}")

    # 修改目标文件 - 优先处理js文件
    modified_count = 0
    files = [
        f"{temp_app}/Contents/Resources/app/out/vs/workbench/api/node/extensionHostProcess.js",
        f"{temp_app}/Contents/Resources/app/out/main.js",
        f"{temp_app}/Contents/Resources/app/out/vs/code/node/cliProcessMain.js"
    ]

    for file in files:
        if not os.path.isfile(file):
            logger.warning(f"文件不存在: {file.replace(temp_dir+'/', '')}")
            continue

        logger.debug(f"处理文件: {file.replace(temp_dir+'/', '')}")
        with open(log_file, "a") as f:
            f.write(f"[PROCESS] 开始处理文件: {file}\n")
            f.write(f"[PROCESS] 文件大小: {os.path.getsize(file)} 字节\n")

        # 输出文件部分内容到日志
        try:
            with open(file, "r", encoding="utf-8", errors="ignore") as src_f:
                content = src_f.read()
                lines = content.split("\n")
                filtered_lines = [line for line in lines if line.strip()]
                head_lines = filtered_lines[:min(50, len(filtered_lines))]

                with open(log_file, "a") as log_f:
                    log_f.write("[FILE_CONTENT] 文件头部 100 行:\n")
                    log_f.write("\n".join(head_lines) + "\n")
                    log_f.write("[FILE_CONTENT] ...\n")
        except Exception as e:
            logger.error(f"读取文件内容失败: {e}")

        # 创建文件备份
        try:
            shutil.copy2(file, f"{file}.bak")
        except Exception as e:
            logger.error(f"无法创建文件备份: {file.replace(temp_dir+'/', '')} - {e}")
            with open(log_file, "a") as f:
                f.write(f"[ERROR] 无法创建文件备份: {file}\n")
            continue

        # 处理不同类型的文件
        file_modified = False

        # 使用Python的正则表达式功能来实现修改
        try:
            with open(file, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            if "extensionHostProcess.js" in file:
                logger.debug("处理 extensionHostProcess.js 文件...")
                with open(log_file, "a") as f:
                    f.write("[PROCESS_DETAIL] 开始处理 extensionHostProcess.js 文件\n")

                # 检查是否包含目标代码
                if 'i.header.set("x-cursor-checksum' in content:
                    logger.debug("找到 x-cursor-checksum 设置代码")
                    with open(log_file, "a") as f:
                        f.write("[FOUND] 找到 x-cursor-checksum 设置代码\n")
                        # 记录匹配的行到日志
                        for i, line in enumerate(content.split('\n')):
                            if 'i.header.set("x-cursor-checksum' in line:
                                f.write(f"{i+1}: {line}\n")

                    # 执行特定的替换
                    modified_content = re.sub(
                        r'i\.header\.set\("x-cursor-checksum",e===void 0\?\`\$\{p\}\$\{t\}\`:\`\$\{p\}\$\{t\}\\\/\$\{e\}\`\)',
                        r'i.header.set("x-cursor-checksum",e===void 0?`${p}${t}`:`${p}${t}\/${p}`)',
                        content
                    )

                    if modified_content != content:
                        # 写入修改后的内容
                        with open(file, "w", encoding="utf-8") as f:
                            f.write(modified_content)

                        logger.info("成功修改 x-cursor-checksum 设置代码")
                        with open(log_file, "a") as f:
                            f.write("[SUCCESS] 成功完成 x-cursor-checksum 设置代码替换\n")
                            # 记录修改后的行
                            for i, line in enumerate(modified_content.split('\n')):
                                if 'i.header.set("x-cursor-checksum' in line:
                                    f.write(f"{i+1}: {line}\n")

                        modified_count += 1
                        file_modified = True
                        logger.info(f"成功修改文件: {file.replace(temp_dir+'/', '')}")
                    else:
                        logger.error("修改 x-cursor-checksum 设置代码失败")
                        with open(log_file, "a") as f:
                            f.write("[ERROR] 替换 x-cursor-checksum 设置代码失败\n")
                        shutil.copy2(f"{file}.bak", file)
                else:
                    logger.warning("未找到 x-cursor-checksum 设置代码")
                    with open(log_file, "a") as f:
                        f.write("[FILE_CHECK] 未找到 x-cursor-checksum 设置代码\n")

                        # 记录文件部分内容到日志以便排查
                        f.write("[FILE_CONTENT] 文件中包含 'header.set' 的行:\n")
                        for i, line in enumerate(content.split('\n')):
                            if 'header.set' in line:
                                f.write(f"{i+1}: {line}\n")
                                if i >= 19:  # 最多记录20行
                                    break

                        f.write("[FILE_CONTENT] 文件中包含 'checksum' 的行:\n")
                        for i, line in enumerate(content.split('\n')):
                            if 'checksum' in line:
                                f.write(f"{i+1}: {line}\n")
                                if i >= 19:  # 最多记录20行
                                    break

                with open(log_file, "a") as f:
                    f.write("[PROCESS_DETAIL] 完成处理 extensionHostProcess.js 文件\n")

            elif "IOPlatformUUID" in content:
                logger.debug("找到 IOPlatformUUID 关键字")
                with open(log_file, "a") as f:
                    f.write("[FOUND] 找到 IOPlatformUUID 关键字\n")
                    # 记录包含IOPlatformUUID的行
                    for i, line in enumerate(content.split('\n')):
                        if "IOPlatformUUID" in line:
                            f.write(f"{i+1}: {line}\n")
                            if i >= 4:  # 最多记录5行
                                break

                # 定位 IOPlatformUUID 相关函数
                if "function a$" in content:
                    # 检查是否已经修改过
                    if "return crypto.randomUUID()" in content:
                        logger.info("文件已经包含 randomUUID 调用，跳过修改")
                        modified_count += 1
                        continue

                    # 针对 main.js 中发现的代码结构进行修改
                    modified_content = re.sub(
                        r'function a\$\(t\){switch',
                        r'function a$(t){return crypto.randomUUID(); switch',
                        content
                    )

                    if modified_content != content:
                        with open(file, "w", encoding="utf-8") as f:
                            f.write(modified_content)

                        logger.debug("成功注入 randomUUID 调用到 a$ 函数")
                        modified_count += 1
                        file_modified = True
                        logger.info(f"成功修改文件: {file.replace(temp_dir+'/', '')}")
                    else:
                        logger.error("修改 a$ 函数失败")
                        shutil.copy2(f"{file}.bak", file)

                elif "async function v5" in content:
                    # 检查是否已经修改过
                    if "return crypto.randomUUID()" in content:
                        logger.info("文件已经包含 randomUUID 调用，跳过修改")
                        modified_count += 1
                        continue

                    # 替代方法 - 修改 v5 函数
                    modified_content = re.sub(
                        r'async function v5\(t\){let e=',
                        r'async function v5(t){return crypto.randomUUID(); let e=',
                        content
                    )

                    if modified_content != content:
                        with open(file, "w", encoding="utf-8") as f:
                            f.write(modified_content)

                        logger.debug("成功注入 randomUUID 调用到 v5 函数")
                        modified_count += 1
                        file_modified = True
                        logger.info(f"成功修改文件: {file.replace(temp_dir+'/', '')}")
                    else:
                        logger.error("修改 v5 函数失败")
                        shutil.copy2(f"{file}.bak", file)
                else:
                    # 检查是否已经注入了自定义代码
                    if "// Cursor ID 修改工具注入" in content:
                        logger.info("文件已经包含自定义注入代码，跳过修改")
                        modified_count += 1
                        continue

                    # 使用更通用的注入方法
                    logger.warning("未找到具体函数，尝试使用通用修改方法")
                    timestamp = int(time.time())
                    inject_code = f"""
// Cursor ID 修改工具注入 - {datetime.now().strftime('%Y%m%d%H%M%S')}
// 随机设备ID生成器注入 - {timestamp}
const randomDeviceId_{timestamp} = () => {{
    try {{
        return require('crypto').randomUUID();
    }} catch (e) {{
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {{
            const r = Math.random() * 16 | 0;
            return (c === 'x' ? r : (r & 0x3 | 0x8)).toString(16);
        }});
    }}
}};
"""
                    # 将代码注入到文件开头
                    with open(file, "w", encoding="utf-8") as f:
                        f.write(inject_code + content)

                    # 替换调用点
                    with open(file, "r", encoding="utf-8") as f:
                        content = f.read()

                    modified_content = content.replace(
                        'await v5(!1)', f'randomDeviceId_{timestamp}()'
                    ).replace(
                        'a$(t)', f'randomDeviceId_{timestamp}()'
                    )

                    with open(file, "w", encoding="utf-8") as f:
                        f.write(modified_content)

                    logger.debug("完成通用修改")
                    modified_count += 1
                    file_modified = True
                    logger.info(f"使用通用方法成功修改文件: {file.replace(temp_dir+'/', '')}")
            else:
                # 未找到 IOPlatformUUID，可能是文件结构变化
                logger.warning("未找到 IOPlatformUUID，尝试替代方法")

                # 检查是否已经注入或修改过
                if "return crypto.randomUUID()" in content or "// Cursor ID 修改工具注入" in content:
                    logger.info("文件已经被修改过，跳过修改")
                    modified_count += 1
                    continue

                # 尝试找其他关键函数如 getMachineId 或 getDeviceId
                if "function t$()" in content or "async function y5" in content:
                    logger.debug("找到设备ID相关函数")

                    # 修改 MAC 地址获取函数
                    if "function t$()" in content:
                        modified_content = re.sub(
                            r'function t\$\(\){',
                            r'function t$(){return "00:00:00:00:00:00";',
                            content
                        )

                        with open(file, "w", encoding="utf-8") as f:
                            f.write(modified_content)

                        logger.debug("修改 MAC 地址获取函数成功")

                    # 修改设备ID获取函数
                    if "async function y5" in content:
                        modified_content = re.sub(
                            r'async function y5\(t\){',
                            r'async function y5(t){return crypto.randomUUID();',
                            content
                        )

                        with open(file, "w", encoding="utf-8") as f:
                            f.write(modified_content)

                        logger.debug("修改设备ID获取函数成功")

                    modified_count += 1
                    file_modified = True
                    logger.info(f"使用替代方法成功修改文件: {file.replace(temp_dir+'/', '')}")
                else:
                    # 最后尝试的通用方法 - 在文件顶部插入重写函数定义
                    logger.warning("未找到任何已知函数，使用最通用的方法")

                    new_uuid = str(uuid.uuid4()).lower()
                    machine_id = f"auth0|user_{secrets.token_hex(16)}"
                    device_id = str(uuid.uuid4()).lower()
                    mac_machine_id = secrets.token_hex(32)
                    timestamp = int(time.time())

                    inject_universal_code = f"""
// Cursor ID 修改工具注入 - {datetime.now().strftime('%Y%m%d%H%M%S')}
// 全局拦截设备标识符 - {timestamp}
const originalRequire_{timestamp} = require;
require = function(module) {{
    const result = originalRequire_{timestamp}(module);
    if (module === 'crypto' && result.randomUUID) {{
        const originalRandomUUID_{timestamp} = result.randomUUID;
        result.randomUUID = function() {{
            return '{new_uuid}';
        }};
    }}
    return result;
}};

// 覆盖所有可能的系统ID获取函数
global.getMachineId = function() {{ return '{machine_id}'; }};
global.getDeviceId = function() {{ return '{device_id}'; }};
global.macMachineId = '{mac_machine_id}';
"""
                    # 将代码注入到文件开头
                    with open(file, "w", encoding="utf-8") as f:
                        f.write(inject_universal_code + content)

                    logger.debug("完成通用覆盖")
                    modified_count += 1
                    file_modified = True
                    logger.info(f"使用最通用方法成功修改文件: {file.replace(temp_dir+'/', '')}")

            # 添加在关键操作后记录日志
            if file_modified:
                with open(log_file, "a") as f:
                    f.write("[MODIFIED] 文件修改后内容:\n")
                    with open(file, "r", encoding="utf-8", errors="ignore") as src_f:
                        for i, line in enumerate(src_f):
                            if "return crypto.randomUUID()" in line:
                                f.write(f"{i+1}: {line}")
                                if i >= 2:  # 最多记录3行
                                    break

            # 清理临时文件
            if os.path.exists(f"{file}.tmp"):
                os.unlink(f"{file}.tmp")
            if os.path.exists(f"{file}.bak"):
                os.unlink(f"{file}.bak")

            with open(log_file, "a") as f:
                f.write(f"[PROCESS] 文件处理完成: {file}\n")

        except Exception as e:
            logger.error(f"处理文件时出错: {e}")
            # 尝试恢复备份
            if os.path.exists(f"{file}.bak"):
                shutil.copy2(f"{file}.bak", file)
                os.unlink(f"{file}.bak")

    if modified_count == 0:
        logger.error("未能成功修改任何文件")
        shutil.rmtree(temp_dir, ignore_errors=True)
        return 1

    # 重新签名应用（增加重试机制）
    max_retry = 3
    retry_count = 0
    sign_success = False

    while retry_count < max_retry:
        retry_count += 1
        logger.info(f"尝试签名 (第 {retry_count} 次)...")

        # 使用更详细的签名参数
        try:
            codesign_log = "/tmp/codesign.log"
            result = subprocess.run(
                f"codesign --sign - --force --deep --preserve-metadata=entitlements,identifier,flags '{temp_app}' 2>&1",
                shell=True,
                text=True,
                capture_output=True
            )

            # 保存签名日志
            with open(codesign_log, "w") as f:
                f.write(result.stdout + "\n" + result.stderr)

            # 验证签名
            verify_result = subprocess.run(
                f"codesign --verify -vvvv '{temp_app}' 2>/dev/null",
                shell=True,
                check=False
            )

            if verify_result.returncode == 0:
                sign_success = True
                logger.info("应用签名验证通过")
                break
            else:
                logger.warning("签名验证失败，错误日志：")
                with open(codesign_log, "r") as f:
                    logger.warning(f.read())
        except Exception as e:
            logger.warning(f"签名过程出错: {e}")
            with open(codesign_log, "w") as f:
                f.write(f"签名错误: {e}\n")

        time.sleep(1)

    if not sign_success:
        logger.error(f"经过 {max_retry} 次尝试仍无法完成签名")
        logger.error("请手动执行以下命令完成签名：")

        # 使用彩色输出
        print(f"\033[34msudo codesign --sign - --force --deep '{temp_app}'\033[0m")
        print("\033[33m操作完成后，请手动将应用复制到原路径：\033[0m")
        print(f"\033[34msudo cp -R '{temp_app}' '/Applications/'\033[0m")

        logger.info(f"临时文件保留在：{temp_dir}")
        return 1

    # 替换原应用
    logger.info("安装修改版应用...")
    try:
        # 使用sudo权限执行操作
        subprocess.run(f"sudo rm -rf '{CURSOR_APP_PATH}'", shell=True, check=True)
        subprocess.run(f"sudo cp -R '{temp_app}' '/Applications/'", shell=True, check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"应用替换失败，正在恢复...: {e}")
        try:
            subprocess.run(f"sudo rm -rf '{CURSOR_APP_PATH}'", shell=True)
            subprocess.run(f"sudo cp -R '{backup_app}' '{CURSOR_APP_PATH}'", shell=True)
        except Exception as restore_e:
            logger.error(f"恢复原应用失败: {restore_e}")

        shutil.rmtree(temp_dir, ignore_errors=True)
        shutil.rmtree(backup_app, ignore_errors=True)
        return 1

    # 清理临时文件
    try:
        shutil.rmtree(temp_dir, ignore_errors=True)
        shutil.rmtree(backup_app, ignore_errors=True)
    except Exception as e:
        logger.warning(f"清理临时文件失败，但不影响程序运行: {e}")

    # 设置权限
    try:
        subprocess.run(f"sudo chown -R '{current_user}:staff' '{CURSOR_APP_PATH}'", shell=True, check=True)
        subprocess.run(f"sudo chmod -R 755 '{CURSOR_APP_PATH}'", shell=True, check=True)
    except Exception as e:
        logger.warning(f"设置应用权限失败: {e}")

    logger.info(f"Cursor 主程序文件修改完成！原版备份在: {backup_app.replace(home, '~')}")
    return 0

# 禁用自动更新
def disable_auto_update():
    """
    禁用Cursor自动更新功能
    相当于Shell脚本中的disable_auto_update函数

    通过修改app-update.yml和cursor-updater文件来实现

    Returns:
        int: 成功返回0，失败返回1（但仍继续执行）
    """
    updater_path = f"{home}/Library/Application Support/Caches/cursor-updater"
    app_update_yml = "/Applications/Cursor.app/Contents/Resources/app-update.yml"

    print()  # 空行
    logger.info("正在禁用 Cursor 自动更新...")

    success = True

    # 备份并清空 app-update.yml
    if os.path.isfile(app_update_yml):
        logger.info("备份并修改 app-update.yml...")

        # 备份文件
        try:
            subprocess.run(f"sudo cp '{app_update_yml}' '{app_update_yml}.bak'",
                          shell=True, check=True)
        except subprocess.SubprocessError:
            logger.warning("备份 app-update.yml 失败，继续执行...")

        # 清空并设置只读权限
        try:
            subprocess.run(f"sudo bash -c \"echo '' > '{app_update_yml}'\"",
                          shell=True, check=True)
            subprocess.run(f"sudo chmod 444 '{app_update_yml}'",
                          shell=True, check=True)
            logger.info("成功禁用 app-update.yml")
        except subprocess.SubprocessError as e:
            logger.error(f"修改 app-update.yml 失败: {e}")
            logger.error("请手动执行以下命令：")
            print(f"\033[34msudo cp \"{app_update_yml}\" \"{app_update_yml}.bak\"\033[0m")
            print(f"\033[34msudo bash -c 'echo \"\" > \"{app_update_yml}\"'\033[0m")
            print(f"\033[34msudo chmod 444 \"{app_update_yml}\"\033[0m")
            success = False
    else:
        logger.warning("未找到 app-update.yml 文件")

    # 同时也处理 cursor-updater
    logger.info("处理 cursor-updater...")
    try:
        # 删除现有文件/目录
        if os.path.exists(updater_path):
            subprocess.run(f"sudo rm -rf '{updater_path}'", shell=True, check=True)

        # 创建空文件并设置只读权限
        subprocess.run(f"sudo touch '{updater_path}'", shell=True, check=True)
        subprocess.run(f"sudo chmod 444 '{updater_path}'", shell=True, check=True)
        logger.info("成功禁用 cursor-updater")
    except subprocess.SubprocessError as e:
        logger.error(f"禁用 cursor-updater 失败: {e}")
        logger.error("请手动执行以下命令：")
        print(f"\033[34msudo rm -rf \"{updater_path}\" && sudo touch \"{updater_path}\" && sudo chmod 444 \"{updater_path}\"\033[0m")
        success = False

    print()  # 空行
    logger.info("验证方法：")
    print(f"1. 运行命令：ls -l \"{updater_path}\"")
    print(f"   确认文件权限显示为：r--r--r--")
    print(f"2. 运行命令：ls -l \"{app_update_yml}\"")
    print(f"   确认文件权限显示为：r--r--r--")
    print()
    logger.info("完成后请重启 Cursor")

    return 0 if success else 1

# 恢复配置文件
def restore_feature():
    """
    从备份目录中恢复Cursor配置文件
    相当于Shell脚本中的restore_feature函数

    允许用户选择备份文件进行恢复

    Returns:
        int: 成功返回0，失败返回1
    """
    logger.info("从备份中恢复配置...")

    # 检查备份目录是否存在
    if not os.path.isdir(BACKUP_DIR):
        logger.warning("备份目录不存在")
        return 1

    # 查找所有备份文件
    backup_files = []
    try:
        # 使用glob查找所有备份文件
        pattern = os.path.join(BACKUP_DIR, "*.backup_*")
        backup_files = sorted(glob.glob(pattern))
    except Exception as e:
        logger.error(f"查找备份文件出错: {e}")
        return 1

    # 检查是否找到备份文件
    if not backup_files:
        logger.warning("未找到任何备份文件")
        return 1

    print()  # 空行
    logger.info("可用的备份文件：")

    # 构建选项菜单
    print("0. 退出 - 不恢复任何文件")
    for i, file in enumerate(backup_files, 1):
        basename = os.path.basename(file)
        timestamp = basename.split("backup_")[1] if "backup_" in basename else "未知时间"
        print(f"{i}. {basename} (创建于: {timestamp})")

    # 获取用户选择
    choice = -1
    while choice < 0 or choice > len(backup_files):
        try:
            choice_input = input("\n请选择要恢复的备份文件 (0-{})：".format(len(backup_files)))
            choice = int(choice_input)
        except ValueError:
            print("请输入有效的数字")
            continue

    # 处理用户输入
    if choice == 0:
        logger.info("跳过恢复操作")
        return 0

    # 获取选择的备份文件
    selected_backup = backup_files[choice - 1]

    # 验证文件存在性和可读性
    if not os.path.isfile(selected_backup) or not os.access(selected_backup, os.R_OK):
        logger.error("无法访问选择的备份文件")
        return 1

    # 尝试恢复配置
    try:
        # 复制备份文件到配置文件位置
        shutil.copy2(selected_backup, STORAGE_FILE)

        # 设置权限和所有者
        os.chmod(STORAGE_FILE, 0o644)
        current_user = getpass.getuser()
        subprocess.run(f"chown {current_user} '{STORAGE_FILE}'", shell=True, check=True)

        logger.info(f"已从备份文件恢复配置: {os.path.basename(selected_backup)}")
        return 0
    except Exception as e:
        logger.error(f"恢复配置失败: {e}")
        return 1

# 解决"应用已损坏，无法打开"问题
def fix_damaged_app():
    """
    修复macOS报告的"应用已损坏，无法打开"问题
    相当于Shell脚本中的fix_damaged_app函数

    通过移除隔离属性和重新签名应用来解决问题

    Returns:
        int: 成功返回0，失败返回1
    """
    logger.info("正在修复\"应用已损坏\"问题...")

    # 检查Cursor应用是否存在
    if not os.path.isdir(CURSOR_APP_PATH):
        logger.error(f"未找到Cursor应用: {CURSOR_APP_PATH}")
        return 1

    logger.info("尝试移除隔离属性...")
    try:
        # 使用xattr命令移除隔离属性
        result = subprocess.run(
            f"sudo xattr -rd com.apple.quarantine '{CURSOR_APP_PATH}'",
            shell=True,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            logger.info("成功移除隔离属性")
        else:
            logger.warning("移除隔离属性失败，尝试其他方法...")
            if result.stderr:
                logger.debug(f"错误信息: {result.stderr}")
    except Exception as e:
        logger.warning(f"移除隔离属性时出错: {e}")

    logger.info("尝试重新签名应用...")
    try:
        # 使用codesign命令重新签名
        result = subprocess.run(
            f"sudo codesign --force --deep --sign - '{CURSOR_APP_PATH}'",
            shell=True,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            logger.info("应用重新签名成功")
        else:
            logger.warning("应用重新签名失败")
            if result.stderr:
                logger.debug(f"错误信息: {result.stderr}")
    except Exception as e:
        logger.warning(f"重新签名时出错: {e}")

    logger.info("修复完成！请尝试重新打开Cursor应用")
    logger.info("")
    logger.info("\033[33m如果仍然无法打开，您可以尝试以下方法：\033[0m")
    logger.info("1. 在系统偏好设置->安全性与隐私中，点击\"仍要打开\"按钮")
    logger.info("2. 暂时关闭Gatekeeper（不建议）: sudo spctl --master-disable")
    logger.info("3. 重新下载安装Cursor应用")
    logger.info("")
    logger.info("\033[34m参考链接: https://sysin.org/blog/macos-if-crashes-when-opening/\033[0m")

    return 0

def go_cursor_help_mac():
  check_and_kill_cursor()
  backup_config()

  # 处理配置文件，默认不重置机器码
  generate_new_config()

  # 执行主程序文件修改
  logger.info("正在执行主程序文件修改...")

  # 使用子shell执行修改，避免错误导致整个脚本退出
  if modify_cursor_app_files():
      logger.info("主程序文件修改成功！")
  else:
      logger.warn("主程序文件修改失败，但配置文件修改可能已成功")
      logger.warn("如果重启后 Cursor 仍然提示设备被禁用，请重新运行此脚本")

  disable_auto_update()

  logger.info("请重启 Cursor 以应用新的配置")

if __name__ == "__main__":
  sys.exit(go_cursor_help_mac())

