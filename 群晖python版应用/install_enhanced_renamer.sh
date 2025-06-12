#!/bin/bash
# -*- coding: utf-8 -*-
# 智能影视文件重命名工具 - 增强版安装脚本
# 作者: OpenHands AI
# 版本: 2.0.0
# 描述: 自动安装和配置增强版智能影视文件重命名工具

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_highlight() {
    echo -e "${PURPLE}[HIGHLIGHT]${NC} $1"
}

print_step() {
    echo -e "${CYAN}[STEP]${NC} $1"
}

# 检测操作系统
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if grep -q "synology" /proc/version 2>/dev/null; then
            OS="synology"
        else
            OS="linux"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    elif [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]]; then
        OS="windows"
    else
        OS="unknown"
    fi
    
    print_info "检测到操作系统: $OS"
}

# 检查Python环境
check_python() {
    print_step "检查Python环境..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
        print_success "找到Python3: $PYTHON_VERSION"
    elif command -v python &> /dev/null; then
        PYTHON_VERSION=$(python --version 2>&1 | cut -d' ' -f2)
        if [[ $PYTHON_VERSION == 3.* ]]; then
            PYTHON_CMD="python"
            print_success "找到Python: $PYTHON_VERSION"
        else
            print_error "需要Python 3.6或更高版本，当前版本: $PYTHON_VERSION"
            exit 1
        fi
    else
        print_error "未找到Python，请先安装Python 3.6或更高版本"
        exit 1
    fi
    
    # 检查Python版本是否满足要求
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
    
    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 6 ]); then
        print_error "需要Python 3.6或更高版本，当前版本: $PYTHON_VERSION"
        exit 1
    fi
}

# 检查网络连接
check_network() {
    print_step "检查网络连接..."
    
    # 测试TMDb连接
    if curl -s --connect-timeout 5 "https://api.themoviedb.org/3" > /dev/null 2>&1; then
        print_success "TMDb API连接正常"
        TMDB_AVAILABLE=true
    else
        print_warning "TMDb API连接失败，可能影响元数据获取功能"
        TMDB_AVAILABLE=false
    fi
    
    # 测试豆瓣连接
    if curl -s --connect-timeout 5 "https://movie.douban.com" > /dev/null 2>&1; then
        print_success "豆瓣连接正常"
        DOUBAN_AVAILABLE=true
    else
        print_warning "豆瓣连接失败，可能影响中文元数据获取"
        DOUBAN_AVAILABLE=false
    fi
    
    if [ "$TMDB_AVAILABLE" = false ] && [ "$DOUBAN_AVAILABLE" = false ]; then
        print_warning "网络连接可能存在问题，API功能可能无法正常使用"
        read -p "是否继续安装？(y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "安装已取消"
            exit 0
        fi
    fi
}

# 创建安装目录
create_install_dir() {
    print_step "创建安装目录..."
    
    case $OS in
        "synology")
            INSTALL_DIR="/volume1/python_apps/enhanced_video_renamer"
            ;;
        "linux"|"macos")
            INSTALL_DIR="$HOME/enhanced_video_renamer"
            ;;
        "windows")
            INSTALL_DIR="$HOME/enhanced_video_renamer"
            ;;
        *)
            INSTALL_DIR="./enhanced_video_renamer"
            ;;
    esac
    
    if [ -d "$INSTALL_DIR" ]; then
        print_warning "安装目录已存在: $INSTALL_DIR"
        read -p "是否覆盖现有安装？(y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "安装已取消"
            exit 0
        fi
        rm -rf "$INSTALL_DIR"
    fi
    
    mkdir -p "$INSTALL_DIR"
    print_success "创建安装目录: $INSTALL_DIR"
}

# 复制文件
copy_files() {
    print_step "复制程序文件..."
    
    # 检查必需文件
    required_files=(
        "video_renamer.py"
        "video_renamer_enhanced.py"
        "video_renamer_enhanced_demo.py"
        "API_SETUP_GUIDE.md"
        "VIDEO_RENAMER_README.md"
    )
    
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            print_error "缺少必需文件: $file"
            exit 1
        fi
    done
    
    # 复制主程序文件
    cp video_renamer.py "$INSTALL_DIR/"
    cp video_renamer_enhanced.py "$INSTALL_DIR/"
    cp video_renamer_enhanced_demo.py "$INSTALL_DIR/"
    
    # 复制文档文件
    cp API_SETUP_GUIDE.md "$INSTALL_DIR/"
    cp VIDEO_RENAMER_README.md "$INSTALL_DIR/"
    
    # 复制其他文件（如果存在）
    [ -f "README.md" ] && cp README.md "$INSTALL_DIR/"
    [ -f "INSTALL.md" ] && cp INSTALL.md "$INSTALL_DIR/"
    
    # 设置执行权限
    chmod +x "$INSTALL_DIR/video_renamer.py"
    chmod +x "$INSTALL_DIR/video_renamer_enhanced.py"
    chmod +x "$INSTALL_DIR/video_renamer_enhanced_demo.py"
    
    print_success "程序文件复制完成"
}

# 创建启动脚本
create_launcher() {
    print_step "创建启动脚本..."
    
    # 创建基础版启动脚本
    cat > "$INSTALL_DIR/start_basic_renamer.sh" << EOF
#!/bin/bash
# 智能影视文件重命名工具 - 基础版启动脚本

cd "\$(dirname "\$0")"
$PYTHON_CMD video_renamer.py
EOF
    
    # 创建增强版启动脚本
    cat > "$INSTALL_DIR/start_enhanced_renamer.sh" << EOF
#!/bin/bash
# 智能影视文件重命名工具 - 增强版启动脚本

cd "\$(dirname "\$0")"
$PYTHON_CMD video_renamer_enhanced.py
EOF
    
    # 创建演示脚本
    cat > "$INSTALL_DIR/start_enhanced_demo.sh" << EOF
#!/bin/bash
# 智能影视文件重命名工具 - 增强版演示脚本

cd "\$(dirname "\$0")"
$PYTHON_CMD video_renamer_enhanced_demo.py
EOF
    
    # 创建API配置助手脚本
    cat > "$INSTALL_DIR/setup_api.sh" << EOF
#!/bin/bash
# API配置助手脚本

echo "🔧 API配置助手"
echo "=============="
echo
echo "1. TMDb API配置:"
echo "   访问: https://www.themoviedb.org/settings/api"
echo "   注册账户并获取API密钥"
echo
echo "2. 启动增强版工具:"
echo "   ./start_enhanced_renamer.sh"
echo
echo "3. 在程序中配置API:"
echo "   选择菜单: 4 -> 1 -> 输入API密钥"
echo
echo "4. 测试API连接:"
echo "   选择菜单: 5"
echo
read -p "按回车键继续..."
./start_enhanced_renamer.sh
EOF
    
    chmod +x "$INSTALL_DIR/start_basic_renamer.sh"
    chmod +x "$INSTALL_DIR/start_enhanced_renamer.sh"
    chmod +x "$INSTALL_DIR/start_enhanced_demo.sh"
    chmod +x "$INSTALL_DIR/setup_api.sh"
    
    print_success "启动脚本创建完成"
}

# 创建配置目录
create_config_dirs() {
    print_step "创建配置目录..."
    
    # 创建元数据目录
    mkdir -p "$INSTALL_DIR/metadata"
    mkdir -p "$INSTALL_DIR/metadata/posters"
    mkdir -p "$INSTALL_DIR/logs"
    
    # 创建示例配置文件
    cat > "$INSTALL_DIR/api_config_example.json" << 'EOF'
{
  "api_settings": {
    "tmdb": {
      "enabled": true,
      "api_key": "your_tmdb_api_key_here",
      "language": "zh-CN",
      "region": "CN"
    },
    "douban": {
      "enabled": true
    },
    "general": {
      "timeout": 10,
      "retry_count": 3,
      "rate_limit_delay": 1.0,
      "cache_enabled": true,
      "cache_expire_days": 7
    }
  },
  "metadata_settings": {
    "fetch_metadata": true,
    "generate_nfo": true,
    "download_posters": true,
    "download_fanart": true,
    "prefer_chinese_title": true,
    "fallback_to_original": true,
    "metadata_priority": ["tmdb", "douban"],
    "poster_size": "w500",
    "fanart_size": "w1280"
  }
}
EOF
    
    print_success "配置目录创建完成"
}

# 创建桌面快捷方式 (仅限Linux和macOS)
create_desktop_shortcut() {
    if [[ "$OS" == "linux" ]] && command -v desktop-file-install &> /dev/null; then
        print_step "创建桌面快捷方式..."
        
        # 基础版快捷方式
        cat > "$HOME/.local/share/applications/video-renamer-basic.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=智能影视重命名工具 (基础版)
Comment=跨平台影视文件智能重命名工具
Exec=$INSTALL_DIR/start_basic_renamer.sh
Icon=video-x-generic
Terminal=true
Categories=AudioVideo;Video;
EOF
        
        # 增强版快捷方式
        cat > "$HOME/.local/share/applications/video-renamer-enhanced.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=智能影视重命名工具 (增强版)
Comment=集成API的智能影视文件重命名工具
Exec=$INSTALL_DIR/start_enhanced_renamer.sh
Icon=video-x-generic
Terminal=true
Categories=AudioVideo;Video;
EOF
        
        print_success "桌面快捷方式创建完成"
    fi
}

# 群晖专用设置
setup_synology() {
    if [[ "$OS" == "synology" ]]; then
        print_step "配置群晖专用设置..."
        
        # 创建Video Station目录链接
        if [ -d "/volume1/video" ]; then
            ln -sf "/volume1/video" "$INSTALL_DIR/video_station"
            print_success "创建Video Station目录链接"
        fi
        
        # 创建群晖任务计划脚本
        cat > "$INSTALL_DIR/synology_task.sh" << EOF
#!/bin/bash
# 群晖任务计划脚本
# 用于定期自动重命名新增的视频文件

RENAMER_DIR="$INSTALL_DIR"
VIDEO_DIR="/volume1/video"
LOG_FILE="\$RENAMER_DIR/logs/auto_rename.log"

echo "\$(date): 开始自动重命名任务" >> "\$LOG_FILE"

# 检查新增文件并重命名
cd "\$RENAMER_DIR"
$PYTHON_CMD video_renamer_enhanced.py --auto-mode --directory "\$VIDEO_DIR" >> "\$LOG_FILE" 2>&1

echo "\$(date): 自动重命名任务完成" >> "\$LOG_FILE"
EOF
        
        chmod +x "$INSTALL_DIR/synology_task.sh"
        
        # 设置权限
        chown -R admin:users "$INSTALL_DIR" 2>/dev/null || true
        
        print_success "群晖设置完成"
        print_info "可在控制面板 -> 任务计划中添加定期执行脚本: $INSTALL_DIR/synology_task.sh"
    fi
}

# 运行初始化
run_initialization() {
    print_step "运行初始化..."
    
    cd "$INSTALL_DIR"
    
    # 运行基础版程序生成配置文件
    echo "6" | timeout 10 $PYTHON_CMD video_renamer.py > /dev/null 2>&1 || true
    
    # 运行增强版程序生成配置文件
    echo "8" | timeout 10 $PYTHON_CMD video_renamer_enhanced.py > /dev/null 2>&1 || true
    
    if [ -f "video_renamer_config.json" ]; then
        print_success "基础版配置文件初始化完成"
    fi
    
    if [ -f "video_renamer_enhanced_config.json" ]; then
        print_success "增强版配置文件初始化完成"
    fi
}

# 显示API配置指南
show_api_guide() {
    print_highlight "📖 API配置指南"
    echo "=================================================================="
    echo
    echo "🌐 TMDb API配置 (推荐):"
    echo "   1. 访问: https://www.themoviedb.org/settings/api"
    echo "   2. 注册免费账户"
    echo "   3. 申请API密钥"
    echo "   4. 在程序中配置: 菜单 4 -> 1 -> 输入密钥"
    echo
    echo "🎭 豆瓣API配置:"
    echo "   1. 无需注册，直接启用"
    echo "   2. 在程序中启用: 菜单 4 -> 2"
    echo "   3. 注意访问频率限制"
    echo
    echo "🔧 配置建议:"
    echo "   • 同时启用TMDb和豆瓣API获得最佳效果"
    echo "   • TMDb提供国际数据，豆瓣提供中文数据"
    echo "   • 首次使用建议先测试API连接"
    echo
    echo "=================================================================="
}

# 显示安装完成信息
show_completion_info() {
    echo
    echo "=================================================================="
    print_success "🎉 智能影视文件重命名工具 - 增强版安装完成！"
    echo "=================================================================="
    echo
    print_info "📁 安装位置: $INSTALL_DIR"
    print_info "💻 操作系统: $OS"
    print_info "🐍 Python版本: $PYTHON_VERSION"
    print_info "🌐 网络状态: TMDb:${TMDB_AVAILABLE:-未知} | 豆瓣:${DOUBAN_AVAILABLE:-未知}"
    echo
    print_highlight "🚀 启动方式:"
    echo "   基础版: cd $INSTALL_DIR && ./start_basic_renamer.sh"
    echo "   增强版: cd $INSTALL_DIR && ./start_enhanced_renamer.sh"
    echo "   演示版: cd $INSTALL_DIR && ./start_enhanced_demo.sh"
    echo "   API配置: cd $INSTALL_DIR && ./setup_api.sh"
    echo
    print_highlight "📖 文档说明:"
    echo "   API配置指南: $INSTALL_DIR/API_SETUP_GUIDE.md"
    echo "   使用说明: $INSTALL_DIR/VIDEO_RENAMER_README.md"
    echo "   配置示例: $INSTALL_DIR/api_config_example.json"
    echo
    print_highlight "🆕 增强版新功能:"
    echo "   • TMDb API集成 - 获取国际影视数据"
    echo "   • 豆瓣API集成 - 获取中文影视数据"
    echo "   • NFO文件生成 - 支持媒体中心"
    echo "   • 海报自动下载 - 完整媒体库体验"
    echo "   • 智能元数据匹配 - 自动选择最佳结果"
    echo "   • 元数据缓存 - 避免重复API调用"
    echo
    
    case $OS in
        "synology")
            print_highlight "🏠 群晖用户提示:"
            echo "   • 可通过SSH连接运行程序"
            echo "   • 支持Video Station目录结构"
            echo "   • 可设置任务计划自动处理新文件"
            echo "   • 任务脚本: $INSTALL_DIR/synology_task.sh"
            ;;
        "linux")
            if [ -f "$HOME/.local/share/applications/video-renamer-enhanced.desktop" ]; then
                print_highlight "🖥️ 桌面快捷方式已创建"
            fi
            ;;
        "macos")
            print_highlight "🍎 macOS用户提示:"
            echo "   • 可通过终端运行程序"
            echo "   • 支持拖拽文件夹操作"
            ;;
    esac
    
    echo
    print_highlight "💡 使用建议:"
    echo "   1. 首次使用建议运行演示程序熟悉功能"
    echo "   2. 配置API密钥以获得最佳重命名效果"
    echo "   3. 重要文件建议先备份"
    echo "   4. 使用预览模式确认重命名结果"
    echo "   5. 网络不稳定时可禁用API功能"
    echo
    echo "=================================================================="
    
    # 显示API配置指南
    show_api_guide()
    
    # 询问是否立即配置API
    read -p "是否立即配置API？(y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cd "$INSTALL_DIR"
        ./setup_api.sh
    else
        # 询问是否运行演示
        read -p "是否运行演示程序？(y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            cd "$INSTALL_DIR"
            $PYTHON_CMD video_renamer_enhanced_demo.py
        fi
    fi
}

# 主安装流程
main() {
    echo "🎬 智能影视文件重命名工具 - 增强版自动安装脚本"
    echo "   作者: OpenHands AI"
    echo "   版本: 2.0.0"
    echo "   功能: API集成、元数据获取、NFO生成、海报下载"
    echo
    
    # 检查是否在正确的目录
    if [ ! -f "video_renamer_enhanced.py" ]; then
        print_error "请在包含video_renamer_enhanced.py的目录中运行此脚本"
        exit 1
    fi
    
    # 执行安装步骤
    detect_os
    check_python
    check_network
    create_install_dir
    copy_files
    create_launcher
    create_config_dirs
    create_desktop_shortcut
    setup_synology
    run_initialization
    show_completion_info
}

# 错误处理
trap 'print_error "安装过程中发生错误，请检查错误信息"; exit 1' ERR

# 运行主函数
main "$@"