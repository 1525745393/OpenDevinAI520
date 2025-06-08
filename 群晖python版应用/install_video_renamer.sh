#!/bin/bash
# -*- coding: utf-8 -*-
# 智能影视文件重命名工具 - 安装脚本
# 作者: OpenHands AI
# 版本: 1.0.0
# 描述: 自动安装和配置智能影视文件重命名工具

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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
    print_info "检查Python环境..."
    
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
}

# 创建安装目录
create_install_dir() {
    print_info "创建安装目录..."
    
    case $OS in
        "synology")
            INSTALL_DIR="/volume1/python_apps/video_renamer"
            ;;
        "linux"|"macos")
            INSTALL_DIR="$HOME/video_renamer"
            ;;
        "windows")
            INSTALL_DIR="$HOME/video_renamer"
            ;;
        *)
            INSTALL_DIR="./video_renamer"
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
    print_info "复制程序文件..."
    
    # 复制主程序文件
    cp video_renamer.py "$INSTALL_DIR/"
    cp video_renamer_demo.py "$INSTALL_DIR/"
    cp VIDEO_RENAMER_README.md "$INSTALL_DIR/"
    
    # 设置执行权限
    chmod +x "$INSTALL_DIR/video_renamer.py"
    chmod +x "$INSTALL_DIR/video_renamer_demo.py"
    
    print_success "程序文件复制完成"
}

# 创建启动脚本
create_launcher() {
    print_info "创建启动脚本..."
    
    # 创建启动脚本
    cat > "$INSTALL_DIR/start_video_renamer.sh" << EOF
#!/bin/bash
# 智能影视文件重命名工具启动脚本

cd "\$(dirname "\$0")"
$PYTHON_CMD video_renamer.py
EOF
    
    # 创建演示脚本
    cat > "$INSTALL_DIR/start_demo.sh" << EOF
#!/bin/bash
# 智能影视文件重命名工具演示脚本

cd "\$(dirname "\$0")"
$PYTHON_CMD video_renamer_demo.py
EOF
    
    chmod +x "$INSTALL_DIR/start_video_renamer.sh"
    chmod +x "$INSTALL_DIR/start_demo.sh"
    
    print_success "启动脚本创建完成"
}

# 创建桌面快捷方式 (仅限Linux和macOS)
create_desktop_shortcut() {
    if [[ "$OS" == "linux" ]] && command -v desktop-file-install &> /dev/null; then
        print_info "创建桌面快捷方式..."
        
        cat > "$HOME/.local/share/applications/video-renamer.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=智能影视文件重命名工具
Comment=跨平台影视文件智能重命名工具
Exec=$INSTALL_DIR/start_video_renamer.sh
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
        print_info "配置群晖专用设置..."
        
        # 创建Video Station目录链接
        if [ -d "/volume1/video" ]; then
            ln -sf "/volume1/video" "$INSTALL_DIR/video_station"
            print_success "创建Video Station目录链接"
        fi
        
        # 设置权限
        chown -R admin:users "$INSTALL_DIR" 2>/dev/null || true
        
        print_info "群晖设置完成"
    fi
}

# 运行初始化
run_initialization() {
    print_info "运行初始化..."
    
    cd "$INSTALL_DIR"
    
    # 运行程序生成配置文件
    echo "6" | $PYTHON_CMD video_renamer.py > /dev/null 2>&1 || true
    
    if [ -f "video_renamer_config.json" ]; then
        print_success "配置文件初始化完成"
    else
        print_warning "配置文件初始化可能失败，请手动运行程序"
    fi
}

# 显示安装完成信息
show_completion_info() {
    echo
    echo "=================================================================="
    print_success "🎉 智能影视文件重命名工具安装完成！"
    echo "=================================================================="
    echo
    print_info "📁 安装位置: $INSTALL_DIR"
    print_info "💻 操作系统: $OS"
    print_info "🐍 Python版本: $PYTHON_VERSION"
    echo
    print_info "🚀 启动方式:"
    echo "   方式1: cd $INSTALL_DIR && ./start_video_renamer.sh"
    echo "   方式2: cd $INSTALL_DIR && $PYTHON_CMD video_renamer.py"
    echo
    print_info "🎬 演示程序:"
    echo "   cd $INSTALL_DIR && ./start_demo.sh"
    echo
    print_info "📖 使用说明:"
    echo "   查看文件: $INSTALL_DIR/VIDEO_RENAMER_README.md"
    echo
    
    case $OS in
        "synology")
            print_info "🏠 群晖用户提示:"
            echo "   • 可通过SSH连接运行程序"
            echo "   • 支持Video Station目录结构"
            echo "   • 建议先使用预览模式测试"
            ;;
        "linux")
            if [ -f "$HOME/.local/share/applications/video-renamer.desktop" ]; then
                print_info "🖥️ 桌面快捷方式已创建"
            fi
            ;;
        "macos")
            print_info "🍎 macOS用户提示:"
            echo "   • 可通过终端运行程序"
            echo "   • 支持拖拽文件夹操作"
            ;;
    esac
    
    echo
    print_info "💡 使用建议:"
    echo "   1. 首次使用建议运行演示程序熟悉功能"
    echo "   2. 重要文件建议先备份"
    echo "   3. 使用预览模式确认重命名结果"
    echo "   4. 可自定义配置文件中的模板和规则"
    echo
    echo "=================================================================="
    
    # 询问是否立即运行
    read -p "是否立即运行程序？(y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cd "$INSTALL_DIR"
        $PYTHON_CMD video_renamer.py
    fi
}

# 主安装流程
main() {
    echo "🎬 智能影视文件重命名工具 - 自动安装脚本"
    echo "   作者: OpenHands AI"
    echo "   版本: 1.0.0"
    echo
    
    # 检查是否在正确的目录
    if [ ! -f "video_renamer.py" ]; then
        print_error "请在包含video_renamer.py的目录中运行此脚本"
        exit 1
    fi
    
    # 执行安装步骤
    detect_os
    check_python
    create_install_dir
    copy_files
    create_launcher
    create_desktop_shortcut
    setup_synology
    run_initialization
    show_completion_info
}

# 错误处理
trap 'print_error "安装过程中发生错误，请检查错误信息"; exit 1' ERR

# 运行主函数
main "$@"