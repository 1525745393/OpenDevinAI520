#!/bin/bash

# OpenDevinAI520 启动脚本
# 作者: OpenDevinAI520 团队
# 版本: v1.2.0

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_message() {
    echo -e "${2}${1}${NC}"
}

# 打印标题
print_title() {
    echo -e "\n${CYAN}================================${NC}"
    echo -e "${CYAN}  $1${NC}"
    echo -e "${CYAN}================================${NC}\n"
}

# 检查命令是否存在
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 检查Python版本
check_python() {
    if command_exists python3; then
        PYTHON_CMD="python3"
    elif command_exists python; then
        PYTHON_CMD="python"
    else
        print_message "❌ 错误: 未找到Python。请安装Python 3.8+。" $RED
        exit 1
    fi

    # 检查Python版本
    PYTHON_VERSION=$($PYTHON_CMD -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    REQUIRED_VERSION="3.8"
    
    if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
        print_message "❌ 错误: Python版本过低。当前版本: $PYTHON_VERSION，要求: $REQUIRED_VERSION+" $RED
        exit 1
    fi
    
    print_message "✅ Python版本检查通过: $PYTHON_VERSION" $GREEN
}

# 安装依赖
install_dependencies() {
    print_title "安装依赖"
    
    if [ ! -f "requirements.txt" ]; then
        print_message "❌ 错误: 未找到requirements.txt文件。" $RED
        exit 1
    fi
    
    print_message "📦 正在安装Python依赖..." $YELLOW
    $PYTHON_CMD -m pip install --upgrade pip
    $PYTHON_CMD -m pip install -r requirements.txt
    
    print_message "✅ 依赖安装完成" $GREEN
}

# 创建必要目录
create_directories() {
    print_title "创建工作目录"
    
    DIRS=("logs" "uploads" "downloads" "temp" "backups")
    
    for dir in "${DIRS[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            print_message "📁 创建目录: $dir" $BLUE
        fi
    done
    
    print_message "✅ 目录创建完成" $GREEN
}

# 检查配置文件
check_config() {
    print_title "检查配置"
    
    if [ ! -f "config/config.yaml" ]; then
        print_message "⚠️  警告: 未找到配置文件，将使用默认配置。" $YELLOW
    else
        print_message "✅ 配置文件检查通过" $GREEN
    fi
    
    # 创建.env文件（如果不存在）
    if [ ! -f ".env" ]; then
        cat > .env << EOF
# OpenDevinAI520 环境配置
LOG_LEVEL=INFO
WORK_DIR=./workspace
API_TIMEOUT=30
API_RETRIES=3
WEB_HOST=0.0.0.0
WEB_PORT=5000
WEB_DEBUG=False
EOF
        print_message "📝 创建默认.env配置文件" $BLUE
    fi
}

# 运行测试
run_tests() {
    print_title "运行测试"
    
    if [ -d "tests" ] && command_exists pytest; then
        print_message "🧪 正在运行测试..." $YELLOW
        $PYTHON_CMD -m pytest tests/ -v
        print_message "✅ 测试完成" $GREEN
    else
        print_message "⚠️  跳过测试（未找到pytest或tests目录）" $YELLOW
    fi
}

# 启动应用
start_application() {
    print_title "启动应用"
    
    MODE=${1:-"interactive"}
    
    case $MODE in
        "web")
            print_message "🌐 启动Web界面模式..." $CYAN
            print_message "📍 访问地址: http://localhost:5000" $BLUE
            $PYTHON_CMD web/app.py
            ;;
        "cli")
            print_message "💻 启动命令行模式..." $CYAN
            $PYTHON_CMD src/main.py --list-tools
            ;;
        "both")
            print_message "🚀 启动双模式..." $CYAN
            print_message "💻 命令行工具列表:" $BLUE
            $PYTHON_CMD src/main.py --list-tools
            echo ""
            print_message "🌐 启动Web界面..." $BLUE
            print_message "📍 访问地址: http://localhost:5000" $BLUE
            $PYTHON_CMD web/app.py &
            WEB_PID=$!
            echo ""
            print_message "🎯 进入交互模式..." $BLUE
            $PYTHON_CMD src/main.py
            kill $WEB_PID 2>/dev/null || true
            ;;
        "interactive"|*)
            print_message "🎯 启动交互模式..." $CYAN
            $PYTHON_CMD src/main.py
            ;;
    esac
}

# 显示帮助信息
show_help() {
    cat << EOF
🚀 OpenDevinAI520 启动脚本

用法: $0 [选项] [模式]

模式:
  interactive  交互模式（默认）
  cli          命令行模式（显示工具列表）
  web          Web界面模式
  both         双模式（CLI + Web）

选项:
  --help, -h   显示此帮助信息
  --no-deps    跳过依赖安装
  --no-test    跳过测试运行
  --version    显示版本信息

示例:
  $0                    # 交互模式
  $0 web               # Web界面模式
  $0 cli               # 命令行模式
  $0 both              # 双模式
  $0 --no-deps web     # 跳过依赖安装，启动Web模式

更多信息:
  📚 文档: ./docs/
  🐛 问题: https://github.com/1525745393/OpenDevinAI520/issues
  💬 讨论: https://github.com/1525745393/OpenDevinAI520/discussions

EOF
}

# 显示版本信息
show_version() {
    cat << EOF
OpenDevinAI520 v1.2.0
实用工具开发平台

构建信息:
  Python: $($PYTHON_CMD --version)
  平台: $(uname -s)
  架构: $(uname -m)

项目地址: https://github.com/1525745393/OpenDevinAI520
许可证: MIT License
EOF
}

# 主函数
main() {
    # 解析参数
    SKIP_DEPS=false
    SKIP_TESTS=false
    MODE="interactive"
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --help|-h)
                show_help
                exit 0
                ;;
            --version)
                show_version
                exit 0
                ;;
            --no-deps)
                SKIP_DEPS=true
                shift
                ;;
            --no-test)
                SKIP_TESTS=true
                shift
                ;;
            web|cli|both|interactive)
                MODE=$1
                shift
                ;;
            *)
                print_message "❌ 未知参数: $1" $RED
                show_help
                exit 1
                ;;
        esac
    done
    
    # 显示欢迎信息
    clear
    cat << "EOF"
 ██████╗ ██████╗ ███████╗███╗   ██╗██████╗ ███████╗██╗   ██╗██╗███╗   ██╗ █████╗ ██╗███████╗██████╗  ██████╗ 
██╔═══██╗██╔══██╗██╔════╝████╗  ██║██╔══██╗██╔════╝██║   ██║██║████╗  ██║██╔══██╗██║██╔════╝╚════██╗██╔═████╗
██║   ██║██████╔╝█████╗  ██╔██╗ ██║██║  ██║█████╗  ██║   ██║██║██╔██╗ ██║███████║██║███████╗ █████╔╝██║██╔██║
██║   ██║██╔═══╝ ██╔══╝  ██║╚██╗██║██║  ██║██╔══╝  ╚██╗ ██╔╝██║██║╚██╗██║██╔══██║██║╚════██║██╔═══╝ ████╔╝██║
╚██████╔╝██║     ███████╗██║ ╚████║██████╔╝███████╗ ╚████╔╝ ██║██║ ╚████║██║  ██║██║███████║███████╗╚██████╔╝
 ╚═════╝ ╚═╝     ╚══════╝╚═╝  ╚═══╝╚═════╝ ╚══════╝  ╚═══╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝╚══════╝╚══════╝ ╚═════╝ 
EOF
    
    print_message "\n🚀 实用工具开发平台 - 人人为我，我为人人" $CYAN
    print_message "版本: v1.2.0 | 模式: $MODE\n" $BLUE
    
    # 执行启动流程
    check_python
    
    if [ "$SKIP_DEPS" = false ]; then
        install_dependencies
    fi
    
    create_directories
    check_config
    
    if [ "$SKIP_TESTS" = false ]; then
        run_tests
    fi
    
    start_application $MODE
}

# 错误处理
trap 'print_message "\n❌ 启动过程中发生错误，请检查上述输出。" $RED; exit 1' ERR

# 运行主函数
main "$@"