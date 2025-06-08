#!/bin/bash

# OpenDevinAI520 快速启动脚本
# 用于快速启动应用，无需完整部署流程

set -e

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    OpenDevinAI520                            ║"
echo "║                  实用工具开发平台                              ║"
echo "║                                                              ║"
echo "║              人人为我，我为人人                                ║"
echo "║          让我们一起构建更好的开发工具生态！                      ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}警告: 未找到Python3，尝试使用python...${NC}"
    if ! command -v python &> /dev/null; then
        echo "错误: 未找到Python，请先安装Python 3.8+"
        exit 1
    fi
    PYTHON_CMD="python"
else
    PYTHON_CMD="python3"
fi

# 检查依赖
echo -e "${BLUE}检查依赖...${NC}"
if [ ! -f "requirements.txt" ]; then
    echo "错误: 未找到requirements.txt文件"
    exit 1
fi

# 尝试导入关键模块
$PYTHON_CMD -c "import sys; sys.path.insert(0, '.'); from src.main import main" 2>/dev/null || {
    echo -e "${YELLOW}检测到缺少依赖，正在安装...${NC}"
    $PYTHON_CMD -m pip install -r requirements.txt
}

# 创建必要目录
mkdir -p logs uploads downloads temp

# 解析启动模式
MODE=${1:-cli}

case $MODE in
    "cli"|"command"|"cmd")
        echo -e "${GREEN}🚀 启动命令行模式...${NC}"
        $PYTHON_CMD src/main.py
        ;;
    "web"|"server"|"http")
        echo -e "${GREEN}🌐 启动Web模式...${NC}"
        echo -e "${BLUE}访问地址: http://localhost:12000${NC}"
        $PYTHON_CMD web/app.py
        ;;
    "both"|"all")
        echo -e "${GREEN}🚀 同时启动CLI和Web模式...${NC}"
        echo -e "${BLUE}Web访问地址: http://localhost:12000${NC}"
        # 后台启动Web服务器
        $PYTHON_CMD web/app.py &
        WEB_PID=$!
        echo "Web服务器PID: $WEB_PID"
        
        # 启动CLI
        $PYTHON_CMD src/main.py
        
        # 清理后台进程
        kill $WEB_PID 2>/dev/null || true
        ;;
    "help"|"-h"|"--help")
        echo "OpenDevinAI520 快速启动脚本"
        echo ""
        echo "用法: $0 [模式]"
        echo ""
        echo "模式:"
        echo "  cli, command, cmd    启动命令行模式 (默认)"
        echo "  web, server, http    启动Web模式"
        echo "  both, all           同时启动CLI和Web模式"
        echo "  help, -h, --help    显示此帮助信息"
        echo ""
        echo "示例:"
        echo "  $0              # 命令行模式"
        echo "  $0 web          # Web模式"
        echo "  $0 both         # 同时启动"
        ;;
    *)
        echo "错误: 未知模式 '$MODE'"
        echo "使用 '$0 help' 查看帮助信息"
        exit 1
        ;;
esac