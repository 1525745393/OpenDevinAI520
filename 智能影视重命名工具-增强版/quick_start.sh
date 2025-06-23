#!/bin/bash
# -*- coding: utf-8 -*-
# 智能影视重命名工具 - 增强版快速开始脚本
# 作者: OpenHands AI
# 版本: 2.0.0

set -e

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_header() {
    echo -e "${BLUE}"
    echo "=================================================================="
    echo "🎬 智能影视重命名工具 - 增强版"
    echo "   版本: 2.0.0"
    echo "   作者: OpenHands AI"
    echo "   功能: API集成、元数据获取、NFO生成、海报下载"
    echo "=================================================================="
    echo -e "${NC}"
}

print_menu() {
    echo -e "${GREEN}请选择操作:${NC}"
    echo "1. 🚀 运行增强版重命名工具"
    echo "2. 🎮 运行功能演示程序"
    echo "3. 🔧 运行自动安装脚本"
    echo "4. 📖 查看API配置指南"
    echo "5. 📚 查看完整文档"
    echo "6. ❓ 显示帮助信息"
    echo "7. 🚪 退出"
    echo
}

check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_VERSION=$(python --version 2>&1 | cut -d' ' -f2)
        if [[ $PYTHON_VERSION == 3.* ]]; then
            PYTHON_CMD="python"
        else
            echo -e "${RED}❌ 需要Python 3.6或更高版本${NC}"
            exit 1
        fi
    else
        echo -e "${RED}❌ 未找到Python，请先安装Python 3.6或更高版本${NC}"
        exit 1
    fi
}

check_dependencies() {
    echo -e "${BLUE}🔍 检查依赖文件...${NC}"
    
    required_files=("video_renamer_enhanced.py" "video_renamer.py")
    missing_files=()
    
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            missing_files+=("$file")
        fi
    done
    
    if [ ${#missing_files[@]} -ne 0 ]; then
        echo -e "${RED}❌ 缺少必需文件:${NC}"
        for file in "${missing_files[@]}"; do
            echo "   - $file"
        done
        echo -e "${YELLOW}💡 请确保所有文件都在当前目录中${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ 依赖文件检查通过${NC}"
}

run_enhanced_renamer() {
    echo -e "${BLUE}🚀 启动增强版重命名工具...${NC}"
    echo
    $PYTHON_CMD video_renamer_enhanced.py
}

run_demo() {
    echo -e "${BLUE}🎮 启动功能演示程序...${NC}"
    echo
    if [ -f "video_renamer_enhanced_demo.py" ]; then
        $PYTHON_CMD video_renamer_enhanced_demo.py
    else
        echo -e "${YELLOW}⚠️  演示程序文件不存在${NC}"
        echo "请确保 video_renamer_enhanced_demo.py 文件在当前目录中"
    fi
}

run_installer() {
    echo -e "${BLUE}🔧 运行自动安装脚本...${NC}"
    echo
    if [ -f "install_enhanced_renamer.sh" ]; then
        chmod +x install_enhanced_renamer.sh
        ./install_enhanced_renamer.sh
    else
        echo -e "${YELLOW}⚠️  安装脚本文件不存在${NC}"
        echo "请确保 install_enhanced_renamer.sh 文件在当前目录中"
    fi
}

show_api_guide() {
    echo -e "${BLUE}📖 API配置指南${NC}"
    echo
    if [ -f "API_SETUP_GUIDE.md" ]; then
        if command -v less &> /dev/null; then
            less API_SETUP_GUIDE.md
        elif command -v more &> /dev/null; then
            more API_SETUP_GUIDE.md
        else
            cat API_SETUP_GUIDE.md
        fi
    else
        echo -e "${YELLOW}⚠️  API配置指南文件不存在${NC}"
        echo "请确保 API_SETUP_GUIDE.md 文件在当前目录中"
        echo
        echo -e "${GREEN}快速配置提示:${NC}"
        echo "1. TMDb API: 访问 https://www.themoviedb.org/settings/api"
        echo "2. 注册账户并获取免费API密钥"
        echo "3. 在程序中配置: 菜单 4 → 1 → 输入密钥"
        echo "4. 启用豆瓣API: 菜单 4 → 2"
    fi
}

show_documentation() {
    echo -e "${BLUE}📚 查看完整文档${NC}"
    echo
    if [ -f "ENHANCED_README.md" ]; then
        if command -v less &> /dev/null; then
            less ENHANCED_README.md
        elif command -v more &> /dev/null; then
            more ENHANCED_README.md
        else
            cat ENHANCED_README.md
        fi
    else
        echo -e "${YELLOW}⚠️  完整文档文件不存在${NC}"
        echo "请确保 ENHANCED_README.md 文件在当前目录中"
    fi
}

show_help() {
    echo -e "${BLUE}❓ 帮助信息${NC}"
    echo
    echo -e "${GREEN}🎯 增强版主要功能:${NC}"
    echo "   • TMDb API集成 - 获取国际影视数据"
    echo "   • 豆瓣API集成 - 获取中文影视数据"
    echo "   • NFO文件生成 - 支持媒体中心"
    echo "   • 海报自动下载 - 完整媒体库体验"
    echo "   • 智能匹配算法 - 自动选择最佳结果"
    echo "   • 元数据缓存 - 避免重复API调用"
    echo
    echo -e "${GREEN}🔧 使用流程:${NC}"
    echo "   1. 配置API密钥（TMDb推荐，豆瓣可选）"
    echo "   2. 运行程序并选择要处理的目录"
    echo "   3. 预览重命名结果"
    echo "   4. 确认后执行重命名"
    echo "   5. 享受完整的元数据体验"
    echo
    echo -e "${GREEN}📁 文件说明:${NC}"
    echo "   • video_renamer_enhanced.py - 主程序"
    echo "   • video_renamer_enhanced_demo.py - 演示程序"
    echo "   • API_SETUP_GUIDE.md - API配置指南"
    echo "   • ENHANCED_README.md - 完整文档"
    echo "   • install_enhanced_renamer.sh - 安装脚本"
    echo
    echo -e "${GREEN}🆘 故障排除:${NC}"
    echo "   • API连接失败: 检查网络和API密钥"
    echo "   • 元数据不准确: 确保文件名包含年份"
    echo "   • 权限问题: 确保有目录写入权限"
    echo "   • 查看日志: logs/video_renamer.log"
    echo
    echo -e "${YELLOW}💡 建议首次使用时先运行演示程序熟悉功能${NC}"
}

main() {
    print_header
    
    # 检查Python环境
    check_python
    
    # 检查依赖文件
    check_dependencies
    
    while true; do
        echo
        print_menu
        read -p "请输入选择 (1-7): " choice
        
        case $choice in
            1)
                run_enhanced_renamer
                ;;
            2)
                run_demo
                ;;
            3)
                run_installer
                ;;
            4)
                show_api_guide
                ;;
            5)
                show_documentation
                ;;
            6)
                show_help
                ;;
            7)
                echo -e "${GREEN}👋 再见！${NC}"
                exit 0
                ;;
            *)
                echo -e "${RED}❌ 无效选择，请输入 1-7${NC}"
                ;;
        esac
        
        echo
        read -p "按回车键继续..." -r
    done
}

# 运行主函数
main "$@"