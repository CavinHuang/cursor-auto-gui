#!/bin/bash

# 设置错误处理
set -e

# 定义日志文件路径
LOG_FILE="/tmp/cursor_mac_id_modifier.log"

# 初始化日志文件
initialize_log() {
    echo "========== Cursor ID 修改工具日志开始 $(date) ==========" > "$LOG_FILE"
    chmod 644 "$LOG_FILE"
}

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数 - 同时输出到终端和日志文件
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
    echo "[INFO] $(date '+%Y-%m-%d %H:%M:%S') $1" >> "$LOG_FILE"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
    echo "[WARN] $(date '+%Y-%m-%d %H:%M:%S') $1" >> "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    echo "[ERROR] $(date '+%Y-%m-%d %H:%M:%S') $1" >> "$LOG_FILE"
}

log_debug() {
    echo -e "${BLUE}[DEBUG]${NC} $1"
    echo "[DEBUG] $(date '+%Y-%m-%d %H:%M:%S') $1" >> "$LOG_FILE"
}

# 记录命令输出到日志文件
log_cmd_output() {
    local cmd="$1"
    local msg="$2"
    echo "[CMD] $(date '+%Y-%m-%d %H:%M:%S') 执行命令: $cmd" >> "$LOG_FILE"
    echo "[CMD] $msg:" >> "$LOG_FILE"
    eval "$cmd" 2>&1 | tee -a "$LOG_FILE"
    echo "" >> "$LOG_FILE"
}

# 获取当前用户
get_current_user() {
    if [ "$EUID" -eq 0 ]; then
        echo "$SUDO_USER"
    else
        echo "$USER"
    fi
}

CURRENT_USER=$(get_current_user)
if [ -z "$CURRENT_USER" ]; then
    log_error "无法获取用户名"
    exit 1
fi

# 定义配置文件路径
STORAGE_FILE="$HOME/Library/Application Support/Cursor/User/globalStorage/storage.json"
BACKUP_DIR="$HOME/Library/Application Support/Cursor/User/globalStorage/backups"

# 定义 Cursor 应用程序路径
CURSOR_APP_PATH="/Applications/Cursor.app"

# 检查权限
check_permissions() {
    if [ "$EUID" -ne 0 ]; then
        log_error "请使用 sudo 运行此脚本"
        echo "示例: sudo $0"
        exit 1
    fi
}

# 检查并关闭 Cursor 进程
check_and_kill_cursor() {
    log_info "检查 Cursor 进程..."

    local attempt=1
    local max_attempts=5

    # 函数：获取进程详细信息
    get_process_details() {
        local process_name="$1"
        log_debug "正在获取 $process_name 进程详细信息："
        ps aux | grep -i "/Applications/Cursor.app" | grep -v grep
    }

    while [ $attempt -le $max_attempts ]; do
        # 使用更精确的匹配来获取 Cursor 进程
        CURSOR_PIDS=$(ps aux | grep -i "/Applications/Cursor.app" | grep -v grep | awk '{print $2}')

        if [ -z "$CURSOR_PIDS" ]; then
            log_info "未发现运行中的 Cursor 进程"
            return 0
        fi

        log_warn "发现 Cursor 进程正在运行"
        get_process_details "cursor"

        log_warn "尝试关闭 Cursor 进程..."

        if [ $attempt -eq $max_attempts ]; then
            log_warn "尝试强制终止进程..."
            kill -9 $CURSOR_PIDS 2>/dev/null || true
        else
            kill $CURSOR_PIDS 2>/dev/null || true
        fi

        sleep 1

        # 同样使用更精确的匹配来检查进程是否还在运行
        if ! ps aux | grep -i "/Applications/Cursor.app" | grep -v grep > /dev/null; then
            log_info "Cursor 进程已成功关闭"
            return 0
        fi

        log_warn "等待进程关闭，尝试 $attempt/$max_attempts..."
        ((attempt++))
    done

    log_error "在 $max_attempts 次尝试后仍无法关闭 Cursor 进程"
    get_process_details "cursor"
    log_error "请手动关闭进程后重试"
    exit 1
}

# 备份配置文件
backup_config() {
    if [ ! -f "$STORAGE_FILE" ]; then
        log_warn "配置文件不存在，跳过备份"
        return 0
    fi

    mkdir -p "$BACKUP_DIR"
    local backup_file="$BACKUP_DIR/storage.json.backup_$(date +%Y%m%d_%H%M%S)"

    if cp "$STORAGE_FILE" "$backup_file"; then
        chmod 644 "$backup_file"
        chown "$CURRENT_USER" "$backup_file"
        log_info "配置已备份到: $backup_file"
    else
        log_error "备份失败"
        exit 1
    fi
}

# 生成随机 ID
generate_random_id() {
    # 生成32字节(64个十六进制字符)的随机数
    openssl rand -hex 32
}

# 生成随机 UUID
generate_uuid() {
    uuidgen | tr '[:upper:]' '[:lower:]'
}

# 修改现有文件
modify_or_add_config() {
    local key="$1"
    local value="$2"
    local file="$3"

    if [ ! -f "$file" ]; then
        log_error "文件不存在: $file"
        return 1
    fi

    # 确保文件可写
    chmod 644 "$file" || {
        log_error "无法修改文件权限: $file"
        return 1
    }

    # 创建临时文件
    local temp_file=$(mktemp)

    # 检查key是否存在
    if grep -q "\"$key\":" "$file"; then
        # key存在,执行替换
        sed "s/\"$key\":[[:space:]]*\"[^\"]*\"/\"$key\": \"$value\"/" "$file" > "$temp_file" || {
            log_error "修改配置失败: $key"
            rm -f "$temp_file"
            return 1
        }
    else
        # key不存在,添加新的key-value对
        sed "s/}$/,\n    \"$key\": \"$value\"\n}/" "$file" > "$temp_file" || {
            log_error "添加配置失败: $key"
            rm -f "$temp_file"
            return 1
        }
    fi

    # 检查临时文件是否为空
    if [ ! -s "$temp_file" ]; then
        log_error "生成的临时文件为空"
        rm -f "$temp_file"
        return 1
    fi

    # 使用 cat 替换原文件内容
    cat "$temp_file" > "$file" || {
        log_error "无法写入文件: $file"
        rm -f "$temp_file"
        return 1
    }

    rm -f "$temp_file"

    # 恢复文件权限
    chmod 444 "$file"

    return 0
}

# 生成新的配置
generate_new_config() {
    echo
    log_warn "机器码处理"

    # 默认不重置机器码
    reset_choice=0

    # 记录日志以便调试
    echo "[INPUT_DEBUG] 机器码重置选项: 不重置 (默认)" >> "$LOG_FILE"

    # 处理 - 默认为不重置
    log_info "默认不重置机器码，将仅修改js文件"

    # 确保配置文件目录存在
    if [ -f "$STORAGE_FILE" ]; then
        log_info "发现已有配置文件: $STORAGE_FILE"

        # 备份现有配置（以防万一）
        backup_config
    else
        log_warn "未找到配置文件，这是正常的，脚本将跳过ID修改"
    fi

    echo
    log_info "配置处理完成"
}

# 清理 Cursor 之前的修改
clean_cursor_app() {
    log_info "尝试清理 Cursor 之前的修改..."

    # 如果存在备份，直接恢复备份
    local latest_backup=""

    # 查找最新的备份
    latest_backup=$(find /tmp -name "Cursor.app.backup_*" -type d -print 2>/dev/null | sort -r | head -1)

    if [ -n "$latest_backup" ] && [ -d "$latest_backup" ]; then
        log_info "找到现有备份: $latest_backup"
        log_info "正在恢复原始版本..."

        # 停止 Cursor 进程
        check_and_kill_cursor

        # 恢复备份
        sudo rm -rf "$CURSOR_APP_PATH"
        sudo cp -R "$latest_backup" "$CURSOR_APP_PATH"
        sudo chown -R "$CURRENT_USER:staff" "$CURSOR_APP_PATH"
        sudo chmod -R 755 "$CURSOR_APP_PATH"

        log_info "已恢复原始版本"
        return 0
    else
        log_warn "未找到现有备份，尝试重新安装 Cursor..."
        echo "您可以从 https://cursor.sh 下载并重新安装 Cursor"
        echo "或者继续执行此脚本，将尝试修复现有安装"

        # 可以在这里添加重新下载和安装的逻辑
        return 1
    fi
}

# 修改 Cursor 主程序文件（安全模式）
modify_cursor_app_files() {
    log_info "正在安全修改 Cursor 主程序文件..."
    log_info "详细日志将记录到: $LOG_FILE"

    # 先清理之前的修改
    clean_cursor_app

    # 验证应用是否存在
    if [ ! -d "$CURSOR_APP_PATH" ]; then
        log_error "未找到 Cursor.app，请确认安装路径: $CURSOR_APP_PATH"
        return 1
    fi

    # 定义目标文件 - 将extensionHostProcess.js放在最前面优先处理
    local target_files=(
        "${CURSOR_APP_PATH}/Contents/Resources/app/out/vs/workbench/api/node/extensionHostProcess.js"
        "${CURSOR_APP_PATH}/Contents/Resources/app/out/main.js"
        "${CURSOR_APP_PATH}/Contents/Resources/app/out/vs/code/node/cliProcessMain.js"
    )

    # 检查文件是否存在并且是否已修改
    local need_modification=false
    local missing_files=false

    log_debug "检查目标文件..."
    for file in "${target_files[@]}"; do
        if [ ! -f "$file" ]; then
            log_warn "文件不存在: ${file/$CURSOR_APP_PATH\//}"
            echo "[FILE_CHECK] 文件不存在: $file" >> "$LOG_FILE"
            missing_files=true
            continue
        fi

        echo "[FILE_CHECK] 文件存在: $file ($(wc -c < "$file") 字节)" >> "$LOG_FILE"

        if ! grep -q "return crypto.randomUUID()" "$file" 2>/dev/null; then
            log_info "文件需要修改: ${file/$CURSOR_APP_PATH\//}"
            grep -n "IOPlatformUUID" "$file" | head -3 >> "$LOG_FILE" || echo "[FILE_CHECK] 未找到 IOPlatformUUID" >> "$LOG_FILE"
            need_modification=true
            break
        else
            log_info "文件已修改: ${file/$CURSOR_APP_PATH\//}"
        fi
    done

    # 如果所有文件都已修改或不存在，则退出
    if [ "$missing_files" = true ]; then
        log_error "部分目标文件不存在，请确认 Cursor 安装是否完整"
        return 1
    fi

    if [ "$need_modification" = false ]; then
        log_info "所有目标文件已经被修改过，无需重复操作"
        return 0
    fi

    # 创建临时工作目录
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local temp_dir="/tmp/cursor_reset_${timestamp}"
    local temp_app="${temp_dir}/Cursor.app"
    local backup_app="/tmp/Cursor.app.backup_${timestamp}"

    log_debug "创建临时目录: $temp_dir"
    echo "[TEMP_DIR] 创建临时目录: $temp_dir" >> "$LOG_FILE"

    # 清理可能存在的旧临时目录
    if [ -d "$temp_dir" ]; then
        log_info "清理已存在的临时目录..."
        rm -rf "$temp_dir"
    fi

    # 创建新的临时目录
    mkdir -p "$temp_dir" || {
        log_error "无法创建临时目录: $temp_dir"
        echo "[ERROR] 无法创建临时目录: $temp_dir" >> "$LOG_FILE"
        return 1
    }

    # 备份原应用
    log_info "备份原应用..."
    echo "[BACKUP] 开始备份: $CURSOR_APP_PATH -> $backup_app" >> "$LOG_FILE"

    cp -R "$CURSOR_APP_PATH" "$backup_app" || {
        log_error "无法创建应用备份"
        echo "[ERROR] 备份失败: $CURSOR_APP_PATH -> $backup_app" >> "$LOG_FILE"
        rm -rf "$temp_dir"
        return 1
    }

    echo "[BACKUP] 备份完成" >> "$LOG_FILE"

    # 复制应用到临时目录
    log_info "创建临时工作副本..."
    echo "[COPY] 开始复制: $CURSOR_APP_PATH -> $temp_dir" >> "$LOG_FILE"

    cp -R "$CURSOR_APP_PATH" "$temp_dir" || {
        log_error "无法复制应用到临时目录"
        echo "[ERROR] 复制失败: $CURSOR_APP_PATH -> $temp_dir" >> "$LOG_FILE"
        rm -rf "$temp_dir" "$backup_app"
        return 1
    }

    echo "[COPY] 复制完成" >> "$LOG_FILE"

    # 确保临时目录的权限正确
    chown -R "$CURRENT_USER:staff" "$temp_dir"
    chmod -R 755 "$temp_dir"

    # 移除签名（增强兼容性）
    log_info "移除应用签名..."
    echo "[CODESIGN] 移除签名: $temp_app" >> "$LOG_FILE"

    codesign --remove-signature "$temp_app" 2>> "$LOG_FILE" || {
        log_warn "移除应用签名失败"
        echo "[WARN] 移除签名失败: $temp_app" >> "$LOG_FILE"
    }

    # 移除所有相关组件的签名
    local components=(
        "$temp_app/Contents/Frameworks/Cursor Helper.app"
        "$temp_app/Contents/Frameworks/Cursor Helper (GPU).app"
        "$temp_app/Contents/Frameworks/Cursor Helper (Plugin).app"
        "$temp_app/Contents/Frameworks/Cursor Helper (Renderer).app"
    )

    for component in "${components[@]}"; do
        if [ -e "$component" ]; then
            log_info "正在移除签名: $component"
            codesign --remove-signature "$component" || {
                log_warn "移除组件签名失败: $component"
            }
        fi
    done

    # 修改目标文件 - 优先处理js文件
    local modified_count=0
    local files=(
        "${temp_app}/Contents/Resources/app/out/vs/workbench/api/node/extensionHostProcess.js"
        "${temp_app}/Contents/Resources/app/out/main.js"
        "${temp_app}/Contents/Resources/app/out/vs/code/node/cliProcessMain.js"
    )

    for file in "${files[@]}"; do
        if [ ! -f "$file" ]; then
            log_warn "文件不存在: ${file/$temp_dir\//}"
            continue
        fi

        log_debug "处理文件: ${file/$temp_dir\//}"
        echo "[PROCESS] 开始处理文件: $file" >> "$LOG_FILE"
        echo "[PROCESS] 文件大小: $(wc -c < "$file") 字节" >> "$LOG_FILE"

        # 输出文件部分内容到日志
        echo "[FILE_CONTENT] 文件头部 100 行:" >> "$LOG_FILE"
        head -100 "$file" 2>/dev/null | grep -v "^$" | head -50 >> "$LOG_FILE"
        echo "[FILE_CONTENT] ..." >> "$LOG_FILE"

        # 创建文件备份
        cp "$file" "${file}.bak" || {
            log_error "无法创建文件备份: ${file/$temp_dir\//}"
            echo "[ERROR] 无法创建文件备份: $file" >> "$LOG_FILE"
            continue
        }

        # 使用 sed 替换而不是字符串操作
        if [[ "$file" == *"extensionHostProcess.js"* ]]; then
            log_debug "处理 extensionHostProcess.js 文件..."
            echo "[PROCESS_DETAIL] 开始处理 extensionHostProcess.js 文件" >> "$LOG_FILE"

            # 检查是否包含目标代码
            if grep -q 'i.header.set("x-cursor-checksum' "$file"; then
                log_debug "找到 x-cursor-checksum 设置代码"
                echo "[FOUND] 找到 x-cursor-checksum 设置代码" >> "$LOG_FILE"

                # 记录匹配的行到日志
                grep -n 'i.header.set("x-cursor-checksum' "$file" >> "$LOG_FILE"

                # 执行特定的替换
                if sed -i.tmp 's/i\.header\.set("x-cursor-checksum",e===void 0?`${p}${t}`:`${p}${t}\/${e}`)/i.header.set("x-cursor-checksum",e===void 0?`${p}${t}`:`${p}${t}\/${p}`)/' "$file"; then
                    log_info "成功修改 x-cursor-checksum 设置代码"
                    echo "[SUCCESS] 成功完成 x-cursor-checksum 设置代码替换" >> "$LOG_FILE"
                    # 记录修改后的行
                    grep -n 'i.header.set("x-cursor-checksum' "$file" >> "$LOG_FILE"
                    ((modified_count++))
                    log_info "成功修改文件: ${file/$temp_dir\//}"
                else
                    log_error "修改 x-cursor-checksum 设置代码失败"
                    echo "[ERROR] 替换 x-cursor-checksum 设置代码失败" >> "$LOG_FILE"
                    cp "${file}.bak" "$file"
                fi
            else
                log_warn "未找到 x-cursor-checksum 设置代码"
                echo "[FILE_CHECK] 未找到 x-cursor-checksum 设置代码" >> "$LOG_FILE"

                # 记录文件部分内容到日志以便排查
                echo "[FILE_CONTENT] 文件中包含 'header.set' 的行:" >> "$LOG_FILE"
                grep -n "header.set" "$file" | head -20 >> "$LOG_FILE"

                echo "[FILE_CONTENT] 文件中包含 'checksum' 的行:" >> "$LOG_FILE"
                grep -n "checksum" "$file" | head -20 >> "$LOG_FILE"
            fi

            echo "[PROCESS_DETAIL] 完成处理 extensionHostProcess.js 文件" >> "$LOG_FILE"
        elif grep -q "IOPlatformUUID" "$file"; then
            log_debug "找到 IOPlatformUUID 关键字"
            echo "[FOUND] 找到 IOPlatformUUID 关键字" >> "$LOG_FILE"
            grep -n "IOPlatformUUID" "$file" | head -5 >> "$LOG_FILE"

            # 定位 IOPlatformUUID 相关函数
            if grep -q "function a\$" "$file"; then
                # 检查是否已经修改过
                if grep -q "return crypto.randomUUID()" "$file"; then
                    log_info "文件已经包含 randomUUID 调用，跳过修改"
                    ((modified_count++))
                    continue
                fi

                # 针对 main.js 中发现的代码结构进行修改
                if sed -i.tmp 's/function a\$(t){switch/function a\$(t){return crypto.randomUUID(); switch/' "$file"; then
                    log_debug "成功注入 randomUUID 调用到 a\$ 函数"
                    ((modified_count++))
                    log_info "成功修改文件: ${file/$temp_dir\//}"
                else
                    log_error "修改 a\$ 函数失败"
                    cp "${file}.bak" "$file"
                fi
            elif grep -q "async function v5" "$file"; then
                # 检查是否已经修改过
                if grep -q "return crypto.randomUUID()" "$file"; then
                    log_info "文件已经包含 randomUUID 调用，跳过修改"
                    ((modified_count++))
                    continue
                fi

                # 替代方法 - 修改 v5 函数
                if sed -i.tmp 's/async function v5(t){let e=/async function v5(t){return crypto.randomUUID(); let e=/' "$file"; then
                    log_debug "成功注入 randomUUID 调用到 v5 函数"
                    ((modified_count++))
                    log_info "成功修改文件: ${file/$temp_dir\//}"
                else
                    log_error "修改 v5 函数失败"
                    cp "${file}.bak" "$file"
                fi
            else
                # 检查是否已经注入了自定义代码
                if grep -q "// Cursor ID 修改工具注入" "$file"; then
                    log_info "文件已经包含自定义注入代码，跳过修改"
                    ((modified_count++))
                    continue
                fi

                # 使用更通用的注入方法
                log_warn "未找到具体函数，尝试使用通用修改方法"
                inject_code="
// Cursor ID 修改工具注入 - $(date +%Y%m%d%H%M%S)
// 随机设备ID生成器注入 - $(date +%s)
const randomDeviceId_$(date +%s) = () => {
    try {
        return require('crypto').randomUUID();
    } catch (e) {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
            const r = Math.random() * 16 | 0;
            return (c === 'x' ? r : (r & 0x3 | 0x8)).toString(16);
        });
    }
};
"
                # 将代码注入到文件开头
                echo "$inject_code" > "${file}.new"
                cat "$file" >> "${file}.new"
                mv "${file}.new" "$file"

                # 替换调用点
                sed -i.tmp 's/await v5(!1)/randomDeviceId_'"$(date +%s)"'()/g' "$file"
                sed -i.tmp 's/a\$(t)/randomDeviceId_'"$(date +%s)"'()/g' "$file"

                log_debug "完成通用修改"
                ((modified_count++))
                log_info "使用通用方法成功修改文件: ${file/$temp_dir\//}"
            fi
        else
            # 未找到 IOPlatformUUID，可能是文件结构变化
            log_warn "未找到 IOPlatformUUID，尝试替代方法"

            # 检查是否已经注入或修改过
            if grep -q "return crypto.randomUUID()" "$file" || grep -q "// Cursor ID 修改工具注入" "$file"; then
                log_info "文件已经被修改过，跳过修改"
                ((modified_count++))
                continue
            fi

            # 尝试找其他关键函数如 getMachineId 或 getDeviceId
            if grep -q "function t\$()" "$file" || grep -q "async function y5" "$file"; then
                log_debug "找到设备ID相关函数"

                # 修改 MAC 地址获取函数
                if grep -q "function t\$()" "$file"; then
                    sed -i.tmp 's/function t\$(){/function t\$(){return "00:00:00:00:00:00";/' "$file"
                    log_debug "修改 MAC 地址获取函数成功"
                fi

                # 修改设备ID获取函数
                if grep -q "async function y5" "$file"; then
                    sed -i.tmp 's/async function y5(t){/async function y5(t){return crypto.randomUUID();/' "$file"
                    log_debug "修改设备ID获取函数成功"
                fi

                ((modified_count++))
                log_info "使用替代方法成功修改文件: ${file/$temp_dir\//}"
            else
                # 最后尝试的通用方法 - 在文件顶部插入重写函数定义
                log_warn "未找到任何已知函数，使用最通用的方法"

                inject_universal_code="
// Cursor ID 修改工具注入 - $(date +%Y%m%d%H%M%S)
// 全局拦截设备标识符 - $(date +%s)
const originalRequire_$(date +%s) = require;
require = function(module) {
    const result = originalRequire_$(date +%s)(module);
    if (module === 'crypto' && result.randomUUID) {
        const originalRandomUUID_$(date +%s) = result.randomUUID;
        result.randomUUID = function() {
            return '${new_uuid}';
        };
    }
    return result;
};

// 覆盖所有可能的系统ID获取函数
global.getMachineId = function() { return '${machine_id}'; };
global.getDeviceId = function() { return '${device_id}'; };
global.macMachineId = '${mac_machine_id}';
"
                # 将代码注入到文件开头
                local new_uuid=$(uuidgen | tr '[:upper:]' '[:lower:]')
                local machine_id="auth0|user_$(openssl rand -hex 16)"
                local device_id=$(uuidgen | tr '[:upper:]' '[:lower:]')
                local mac_machine_id=$(openssl rand -hex 32)

                inject_universal_code=${inject_universal_code//\$\{new_uuid\}/$new_uuid}
                inject_universal_code=${inject_universal_code//\$\{machine_id\}/$machine_id}
                inject_universal_code=${inject_universal_code//\$\{device_id\}/$device_id}
                inject_universal_code=${inject_universal_code//\$\{mac_machine_id\}/$mac_machine_id}

                echo "$inject_universal_code" > "${file}.new"
                cat "$file" >> "${file}.new"
                mv "${file}.new" "$file"

                log_debug "完成通用覆盖"
                ((modified_count++))
                log_info "使用最通用方法成功修改文件: ${file/$temp_dir\//}"
            fi
        fi

        # 添加在关键操作后记录日志
        echo "[MODIFIED] 文件修改后内容:" >> "$LOG_FILE"
        grep -n "return crypto.randomUUID()" "$file" | head -3 >> "$LOG_FILE"

        # 清理临时文件
        rm -f "${file}.tmp" "${file}.bak"
        echo "[PROCESS] 文件处理完成: $file" >> "$LOG_FILE"
    done

    if [ "$modified_count" -eq 0 ]; then
        log_error "未能成功修改任何文件"
        rm -rf "$temp_dir"
        return 1
    fi

    # 重新签名应用（增加重试机制）
    local max_retry=3
    local retry_count=0
    local sign_success=false

    while [ $retry_count -lt $max_retry ]; do
        ((retry_count++))
        log_info "尝试签名 (第 $retry_count 次)..."

        # 使用更详细的签名参数
        if codesign --sign - --force --deep --preserve-metadata=entitlements,identifier,flags "$temp_app" 2>&1 | tee /tmp/codesign.log; then
            # 验证签名
            if codesign --verify -vvvv "$temp_app" 2>/dev/null; then
                sign_success=true
                log_info "应用签名验证通过"
                break
            else
                log_warn "签名验证失败，错误日志："
                cat /tmp/codesign.log
            fi
        else
            log_warn "签名失败，错误日志："
            cat /tmp/codesign.log
        fi

        sleep 1
    done

    if ! $sign_success; then
        log_error "经过 $max_retry 次尝试仍无法完成签名"
        log_error "请手动执行以下命令完成签名："
        echo -e "${BLUE}sudo codesign --sign - --force --deep '${temp_app}'${NC}"
        echo -e "${YELLOW}操作完成后，请手动将应用复制到原路径：${NC}"
        echo -e "${BLUE}sudo cp -R '${temp_app}' '/Applications/'${NC}"
        log_info "临时文件保留在：${temp_dir}"
        return 1
    fi

    # 替换原应用
    log_info "安装修改版应用..."
    if ! sudo rm -rf "$CURSOR_APP_PATH" || ! sudo cp -R "$temp_app" "/Applications/"; then
        log_error "应用替换失败，正在恢复..."
        sudo rm -rf "$CURSOR_APP_PATH"
        sudo cp -R "$backup_app" "$CURSOR_APP_PATH"
        rm -rf "$temp_dir" "$backup_app"
        return 1
    fi

    # 清理临时文件
    rm -rf "$temp_dir" "$backup_app"

    # 设置权限
    sudo chown -R "$CURRENT_USER:staff" "$CURSOR_APP_PATH"
    sudo chmod -R 755 "$CURSOR_APP_PATH"

    log_info "Cursor 主程序文件修改完成！原版备份在: ${backup_app/$HOME/\~}"
    return 0
}

# 显示文件树结构
show_file_tree() {
    local base_dir=$(dirname "$STORAGE_FILE")
    echo
    log_info "文件结构:"
    echo -e "${BLUE}$base_dir${NC}"
    echo "├── globalStorage"
    echo "│   ├── storage.json (已修改)"
    echo "│   └── backups"

    # 列出备份文件
    if [ -d "$BACKUP_DIR" ]; then
        local backup_files=("$BACKUP_DIR"/*)
        if [ ${#backup_files[@]} -gt 0 ]; then
            for file in "${backup_files[@]}"; do
                if [ -f "$file" ]; then
                    echo "│       └── $(basename "$file")"
                fi
            done
        else
            echo "│       └── (空)"
        fi
    fi
    echo
}

# 显示公众号信息
show_follow_info() {
    echo
    echo -e "${GREEN}================================${NC}"
    echo -e "${YELLOW}  关注公众号【煎饼果子卷AI】一起交流更多Cursor技巧和AI知识(脚本免费、关注公众号加群有更多技巧和大佬) ${NC}"
    echo -e "${GREEN}================================${NC}"
    echo
}

# 禁用自动更新
disable_auto_update() {
    local updater_path="$HOME/Library/Application Support/Caches/cursor-updater"
    local app_update_yml="/Applications/Cursor.app/Contents/Resources/app-update.yml"

    echo
    log_info "正在禁用 Cursor 自动更新..."

    # 备份并清空 app-update.yml
    if [ -f "$app_update_yml" ]; then
        log_info "备份并修改 app-update.yml..."
        if ! sudo cp "$app_update_yml" "${app_update_yml}.bak" 2>/dev/null; then
            log_warn "备份 app-update.yml 失败，继续执行..."
        fi

        if sudo bash -c "echo '' > \"$app_update_yml\"" && \
           sudo chmod 444 "$app_update_yml"; then
            log_info "成功禁用 app-update.yml"
        else
            log_error "修改 app-update.yml 失败，请手动执行以下命令："
            echo -e "${BLUE}sudo cp \"$app_update_yml\" \"${app_update_yml}.bak\"${NC}"
            echo -e "${BLUE}sudo bash -c 'echo \"\" > \"$app_update_yml\"'${NC}"
            echo -e "${BLUE}sudo chmod 444 \"$app_update_yml\"${NC}"
        fi
    else
        log_warn "未找到 app-update.yml 文件"
    fi

    # 同时也处理 cursor-updater
    log_info "处理 cursor-updater..."
    if sudo rm -rf "$updater_path" && \
       sudo touch "$updater_path" && \
       sudo chmod 444 "$updater_path"; then
        log_info "成功禁用 cursor-updater"
    else
        log_error "禁用 cursor-updater 失败，请手动执行以下命令："
        echo -e "${BLUE}sudo rm -rf \"$updater_path\" && sudo touch \"$updater_path\" && sudo chmod 444 \"$updater_path\"${NC}"
    fi

    echo
    log_info "验证方法："
    echo "1. 运行命令：ls -l \"$updater_path\""
    echo "   确认文件权限显示为：r--r--r--"
    echo "2. 运行命令：ls -l \"$app_update_yml\""
    echo "   确认文件权限显示为：r--r--r--"
    echo
    log_info "完成后请重启 Cursor"
}

# 新增恢复功能选项
restore_feature() {
    # 检查备份目录是否存在
    if [ ! -d "$BACKUP_DIR" ]; then
        log_warn "备份目录不存在"
        return 1
    fi

    # 使用 find 命令获取备份文件列表并存储到数组
    backup_files=()
    while IFS= read -r file; do
        [ -f "$file" ] && backup_files+=("$file")
    done < <(find "$BACKUP_DIR" -name "*.backup_*" -type f 2>/dev/null | sort)

    # 检查是否找到备份文件
    if [ ${#backup_files[@]} -eq 0 ]; then
        log_warn "未找到任何备份文件"
        return 1
    fi

    echo
    log_info "可用的备份文件："

    # 构建菜单选项字符串
    menu_options="退出 - 不恢复任何文件"
    for i in "${!backup_files[@]}"; do
        menu_options="$menu_options|$(basename "${backup_files[$i]}")"
    done

    # 使用菜单选择函数
    select_menu_option "请使用上下箭头选择要恢复的备份文件，按Enter确认:" "$menu_options" 0
    choice=$?

    # 处理用户输入
    if [ "$choice" = "0" ]; then
        log_info "跳过恢复操作"
        return 0
    fi

    # 获取选择的备份文件 (减1是因为第一个选项是"退出")
    local selected_backup="${backup_files[$((choice-1))]}"

    # 验证文件存在性和可读性
    if [ ! -f "$selected_backup" ] || [ ! -r "$selected_backup" ]; then
        log_error "无法访问选择的备份文件"
        return 1
    fi

    # 尝试恢复配置
    if cp "$selected_backup" "$STORAGE_FILE"; then
        chmod 644 "$STORAGE_FILE"
        chown "$CURRENT_USER" "$STORAGE_FILE"
        log_info "已从备份文件恢复配置: $(basename "$selected_backup")"
        return 0
    else
        log_error "恢复配置失败"
        return 1
    fi
}

# 解决"应用已损坏，无法打开"问题
fix_damaged_app() {
    log_info "正在修复"应用已损坏"问题..."

    # 检查Cursor应用是否存在
    if [ ! -d "$CURSOR_APP_PATH" ]; then
        log_error "未找到Cursor应用: $CURSOR_APP_PATH"
        return 1
    fi

    log_info "尝试移除隔离属性..."
    if sudo xattr -rd com.apple.quarantine "$CURSOR_APP_PATH" 2>/dev/null; then
        log_info "成功移除隔离属性"
    else
        log_warn "移除隔离属性失败，尝试其他方法..."
    fi

    log_info "尝试重新签名应用..."
    if sudo codesign --force --deep --sign - "$CURSOR_APP_PATH" 2>/dev/null; then
        log_info "应用重新签名成功"
    else
        log_warn "应用重新签名失败"
    fi

    echo
    log_info "修复完成！请尝试重新打开Cursor应用"
    echo
    echo -e "${YELLOW}如果仍然无法打开，您可以尝试以下方法：${NC}"
    echo "1. 在系统偏好设置->安全性与隐私中，点击"仍要打开"按钮"
    echo "2. 暂时关闭Gatekeeper（不建议）: sudo spctl --master-disable"
    echo "3. 重新下载安装Cursor应用"
    echo
    echo -e "${BLUE}参考链接: https://sysin.org/blog/macos-if-crashes-when-opening/${NC}"

    return 0
}

# 新增：通用菜单选择函数
# 参数:
# $1 - 提示信息
# $2 - 选项数组，格式为 "选项1|选项2|选项3"
# $3 - 默认选项索引 (从0开始)
# 返回: 选中的选项索引 (从0开始)
select_menu_option() {
    local prompt="$1"
    IFS='|' read -ra options <<< "$2"
    local default_index=${3:-0}
    local selected_index=$default_index
    local key_input
    local cursor_up='\033[A'
    local cursor_down='\033[B'
    local enter_key=$'\n'

    # 保存光标位置
    tput sc

    # 显示提示信息
    echo -e "$prompt"

    # 第一次显示菜单
    for i in "${!options[@]}"; do
        if [ $i -eq $selected_index ]; then
            echo -e " ${GREEN}►${NC} ${options[$i]}"
        else
            echo -e "   ${options[$i]}"
        fi
    done

    # 循环处理键盘输入
    while true; do
        # 读取单个按键
        read -rsn3 key_input

        # 检测按键
        case "$key_input" in
            # 上箭头键
            $'\033[A')
                if [ $selected_index -gt 0 ]; then
                    ((selected_index--))
                fi
                ;;
            # 下箭头键
            $'\033[B')
                if [ $selected_index -lt $((${#options[@]}-1)) ]; then
                    ((selected_index++))
                fi
                ;;
            # Enter键
            "")
                echo # 换行
                log_info "您选择了: ${options[$selected_index]}"
                return $selected_index
                ;;
        esac

        # 恢复光标位置
        tput rc

        # 重新显示菜单
        for i in "${!options[@]}"; do
            if [ $i -eq $selected_index ]; then
                echo -e " ${GREEN}►${NC} ${options[$i]}"
            else
                echo -e "   ${options[$i]}"
            fi
        done
    done
}

# 主函数
main() {

    # 初始化日志文件
    initialize_log
    log_info "脚本启动..."

    # 记录系统信息
    log_info "系统信息: $(uname -a)"
    log_info "当前用户: $CURRENT_USER"
    log_cmd_output "sw_vers" "macOS 版本信息"
    log_cmd_output "which codesign" "codesign 路径"
    log_cmd_output "ls -la \"$CURSOR_APP_PATH\"" "Cursor 应用信息"

    # 新增环境检查
    if [[ $(uname) != "Darwin" ]]; then
        log_error "本脚本仅支持 macOS 系统"
        exit 1
    fi

    clear
    # 显示 Logo
    echo -e "
    ██████╗██╗   ██╗██████╗ ███████╗ ██████╗ ██████╗
   ██╔════╝██║   ██║██╔══██╗██╔════╝██╔═══██╗██╔══██╗
   ██║     ██║   ██║██████╔╝███████╗██║   ██║██████╔╝
   ██║     ██║   ██║██╔══██╗╚════██║██║   ██║██╔══██╗
   ╚██████╗╚██████╔╝██║  ██║███████║╚██████╔╝██║  ██║
    ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝
    "
    echo -e "${BLUE}================================${NC}"
    echo -e "${GREEN}   Cursor 启动工具          ${NC}"
    echo -e "${YELLOW}  关注公众号【煎饼果子卷AI】     ${NC}"
    echo -e "${YELLOW}  一起交流更多Cursor技巧和AI知识(脚本免费、关注公众号加群有更多技巧和大佬)  ${NC}"
    echo -e "${BLUE}================================${NC}"
    echo
    echo -e "${YELLOW}[重要提示]${NC} 本工具优先修改js文件，更加安全可靠"
    echo -e "${YELLOW}[重要提示]${NC} 本工具免费，如果对您有帮助，请关注公众号【煎饼果子卷AI】"
    echo

    # 执行主要功能
    check_permissions
    check_and_kill_cursor
    backup_config

    # 处理配置文件，默认不重置机器码
    generate_new_config

    # 执行主程序文件修改
    log_info "正在执行主程序文件修改..."

    # 使用子shell执行修改，避免错误导致整个脚本退出
    (
        if modify_cursor_app_files; then
            log_info "主程序文件修改成功！"
        else
            log_warn "主程序文件修改失败，但配置文件修改可能已成功"
            log_warn "如果重启后 Cursor 仍然提示设备被禁用，请重新运行此脚本"
        fi
    )

    # 恢复错误处理
    set -e

    show_file_tree
    show_follow_info

    # 直接执行禁用自动更新
    disable_auto_update

    log_info "请重启 Cursor 以应用新的配置"

    # 显示最后的提示信息
    show_follow_info

    # 提供修复选项（移到最后）
    echo
    log_warn "Cursor 修复选项"

    # 使用新的菜单选择函数
    select_menu_option "请使用上下箭头选择，按Enter确认:" "忽略 - 不执行修复操作|修复模式 - 恢复原始的 Cursor 安装" 0
    fix_choice=$?

    # 记录日志以便调试
    echo "[INPUT_DEBUG] 修复选项选择: $fix_choice" >> "$LOG_FILE"

    # 确保脚本不会因为输入问题而终止
    set +e

    # 处理用户选择 - 索引1对应"修复模式"选项
    if [ "$fix_choice" = "1" ]; then
        log_info "您选择了修复模式"
        # 使用子shell执行清理，避免错误导致整个脚本退出
        (
            if clean_cursor_app; then
                log_info "Cursor 已恢复到原始状态"
                log_info "如果您需要应用ID修改，请重新运行此脚本"
            else
                log_warn "未能找到备份，无法自动恢复"
                log_warn "建议重新安装 Cursor"
            fi
        )
    else
        log_info "已跳过修复操作"
    fi

    # 恢复错误处理
    set -e

    # 记录脚本完成信息
    log_info "脚本执行完成"
    echo "========== Cursor ID 修改工具日志结束 $(date) ==========" >> "$LOG_FILE"

    # 显示日志文件位置
    echo
    log_info "详细日志已保存到: $LOG_FILE"
    echo "如遇问题请将此日志文件提供给开发者以协助排查"
    echo

    # 添加修复"应用已损坏"选项
    echo
    log_warn "应用修复选项"

    # 使用新的菜单选择函数
    select_menu_option "请使用上下箭头选择，按Enter确认:" "忽略 - 不执行修复操作|修复"应用已损坏"问题 - 解决macOS提示应用已损坏无法打开的问题" 0
    damaged_choice=$?

    echo "[INPUT_DEBUG] 应用修复选项选择: $damaged_choice" >> "$LOG_FILE"

    set +e

    # 处理用户选择 - 索引1对应"修复应用已损坏"选项
    if [ "$damaged_choice" = "1" ]; then
        log_info "您选择了修复"应用已损坏"问题"
        (
            if fix_damaged_app; then
                log_info "修复"应用已损坏"问题完成"
            else
                log_warn "修复"应用已损坏"问题失败"
            fi
        )
    else
        log_info "已跳过应用修复操作"
    fi

    set -e
}

# 执行主函数
main
