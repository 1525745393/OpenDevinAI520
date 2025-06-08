#!/bin/bash

# OpenDevinAI520 部署脚本
# 用于快速部署和启动项目

set -e

echo "🚀 OpenDevinAI520 部署脚本"
echo "=========================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查Python版本
check_python() {
    log_info "检查Python版本..."
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        log_success "Python版本: $PYTHON_VERSION"
        
        # 检查版本是否满足要求 (3.8+)
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
            log_success "Python版本满足要求 (3.8+)"
        else
            log_error "Python版本过低，需要3.8或更高版本"
            exit 1
        fi
    else
        log_error "未找到Python3，请先安装Python"
        exit 1
    fi
}

# 检查pip
check_pip() {
    log_info "检查pip..."
    if command -v pip3 &> /dev/null; then
        log_success "pip3 已安装"
    elif command -v pip &> /dev/null; then
        log_success "pip 已安装"
    else
        log_error "未找到pip，请先安装pip"
        exit 1
    fi
}

# 创建虚拟环境
create_venv() {
    log_info "创建虚拟环境..."
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        log_success "虚拟环境创建成功"
    else
        log_warning "虚拟环境已存在，跳过创建"
    fi
}

# 激活虚拟环境
activate_venv() {
    log_info "激活虚拟环境..."
    source venv/bin/activate
    log_success "虚拟环境已激活"
}

# 安装依赖
install_dependencies() {
    log_info "安装Python依赖..."
    pip install --upgrade pip
    pip install -r requirements.txt
    log_success "Python依赖安装完成"
    
    # 检查是否需要安装Node.js依赖
    if [ -f "package.json" ] && command -v npm &> /dev/null; then
        log_info "安装Node.js依赖..."
        npm install
        log_success "Node.js依赖安装完成"
    else
        log_warning "跳过Node.js依赖安装 (npm未找到或package.json不存在)"
    fi
}

# 创建必要目录
create_directories() {
    log_info "创建必要目录..."
    mkdir -p logs
    mkdir -p uploads
    mkdir -p downloads
    mkdir -p temp
    log_success "目录创建完成"
}

# 运行测试
run_tests() {
    if [ "$1" = "--skip-tests" ]; then
        log_warning "跳过测试"
        return
    fi
    
    log_info "运行测试..."
    if command -v pytest &> /dev/null; then
        pytest tests/ -v
        log_success "测试通过"
    else
        log_warning "pytest未安装，跳过测试"
    fi
}

# 启动应用
start_app() {
    local mode=$1
    
    case $mode in
        "cli")
            log_info "启动命令行模式..."
            python src/main.py
            ;;
        "web")
            log_info "启动Web模式..."
            python web/app.py
            ;;
        "both")
            log_info "同时启动CLI和Web模式..."
            # 在后台启动Web服务器
            python web/app.py &
            WEB_PID=$!
            echo "Web服务器PID: $WEB_PID"
            
            # 启动CLI
            python src/main.py
            
            # 清理后台进程
            kill $WEB_PID 2>/dev/null || true
            ;;
        *)
            log_error "未知启动模式: $mode"
            echo "可用模式: cli, web, both"
            exit 1
            ;;
    esac
}

# 显示帮助信息
show_help() {
    echo "OpenDevinAI520 部署脚本"
    echo ""
    echo "用法: $0 [选项] [模式]"
    echo ""
    echo "选项:"
    echo "  --help          显示此帮助信息"
    echo "  --skip-tests    跳过测试"
    echo "  --dev           开发模式 (启用调试)"
    echo ""
    echo "模式:"
    echo "  cli             启动命令行模式 (默认)"
    echo "  web             启动Web模式"
    echo "  both            同时启动CLI和Web模式"
    echo ""
    echo "示例:"
    echo "  $0              # 默认CLI模式"
    echo "  $0 web          # Web模式"
    echo "  $0 --skip-tests cli  # 跳过测试的CLI模式"
}

# 主函数
main() {
    local skip_tests=false
    local dev_mode=false
    local start_mode="cli"
    
    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --help)
                show_help
                exit 0
                ;;
            --skip-tests)
                skip_tests=true
                shift
                ;;
            --dev)
                dev_mode=true
                shift
                ;;
            cli|web|both)
                start_mode=$1
                shift
                ;;
            *)
                log_error "未知参数: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # 设置开发模式环境变量
    if [ "$dev_mode" = true ]; then
        export OPENDEVINAI520_DEBUG=true
        export OPENDEVINAI520_LOG_LEVEL=DEBUG
        log_info "开发模式已启用"
    fi
    
    echo "🎯 开始部署 OpenDevinAI520..."
    echo ""
    
    # 执行部署步骤
    check_python
    check_pip
    create_venv
    activate_venv
    install_dependencies
    create_directories
    
    if [ "$skip_tests" = false ]; then
        run_tests
    else
        run_tests --skip-tests
    fi
    
    echo ""
    log_success "🎉 部署完成！"
    echo ""
    
    # 启动应用
    start_app $start_mode
}

# 错误处理
trap 'log_error "部署过程中发生错误，退出代码: $?"' ERR

# 运行主函数
main "$@"