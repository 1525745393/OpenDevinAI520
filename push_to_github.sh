#!/bin/bash

# OpenDevinAI520 GitHub推送脚本
# 用于将本地代码推送到已创建的GitHub仓库

set -e

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                OpenDevinAI520 GitHub推送                     ║"
echo "║                                                              ║"
echo "║              将本地代码推送到GitHub仓库                        ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# 获取GitHub用户名
if [ -z "$1" ]; then
    echo -e "${YELLOW}请提供您的GitHub用户名:${NC}"
    read -p "GitHub用户名: " GITHUB_USERNAME
else
    GITHUB_USERNAME=$1
fi

if [ -z "$GITHUB_USERNAME" ]; then
    echo -e "${RED}错误: 必须提供GitHub用户名${NC}"
    exit 1
fi

REPO_URL="https://github.com/${GITHUB_USERNAME}/OpenDevinAI520.git"

echo -e "${BLUE}准备推送到: $REPO_URL${NC}"

# 检查是否在正确的目录
if [ ! -f "README.md" ] || [ ! -d "src" ]; then
    echo -e "${RED}错误: 请在OpenDevinAI520项目根目录运行此脚本${NC}"
    exit 1
fi

# 检查Git状态
echo -e "${BLUE}检查Git状态...${NC}"
if ! git status &>/dev/null; then
    echo -e "${RED}错误: 当前目录不是Git仓库${NC}"
    exit 1
fi

# 检查是否有未提交的更改
if ! git diff-index --quiet HEAD --; then
    echo -e "${YELLOW}检测到未提交的更改，正在提交...${NC}"
    git add .
    git commit -m "最终更新: 准备推送到GitHub"
fi

# 检查远程仓库
if git remote get-url origin &>/dev/null; then
    CURRENT_ORIGIN=$(git remote get-url origin)
    echo -e "${YELLOW}当前远程仓库: $CURRENT_ORIGIN${NC}"
    
    if [ "$CURRENT_ORIGIN" != "$REPO_URL" ]; then
        echo -e "${YELLOW}更新远程仓库地址...${NC}"
        git remote remove origin
        git remote add origin $REPO_URL
    fi
else
    echo -e "${BLUE}添加远程仓库...${NC}"
    git remote add origin $REPO_URL
fi

# 推送代码
echo -e "${BLUE}推送代码到GitHub...${NC}"
echo "目标仓库: $REPO_URL"
echo "分支: main"

if git push -u origin main; then
    echo -e "${GREEN}✅ 代码推送成功！${NC}"
    echo ""
    echo "🎉 OpenDevinAI520项目已成功推送到GitHub！"
    echo ""
    echo "📍 仓库地址: https://github.com/${GITHUB_USERNAME}/OpenDevinAI520"
    echo "📚 文档地址: https://${GITHUB_USERNAME}.github.io/OpenDevinAI520/ (稍后可用)"
    echo ""
    echo "下一步:"
    echo "1. 访问仓库页面查看代码"
    echo "2. 等待GitHub Actions构建文档"
    echo "3. 在Settings > Pages中启用GitHub Pages"
    echo "4. 创建第一个Release版本"
    echo ""
    echo -e "${GREEN}🌟 项目部署完成！人人为我，我为人人！${NC}"
else
    echo -e "${RED}❌ 推送失败${NC}"
    echo ""
    echo "可能的原因:"
    echo "1. 仓库不存在 - 请先在GitHub创建仓库"
    echo "2. 权限不足 - 检查仓库访问权限"
    echo "3. 网络问题 - 检查网络连接"
    echo ""
    echo "解决方案:"
    echo "1. 确保已在GitHub创建名为 'OpenDevinAI520' 的仓库"
    echo "2. 检查仓库是否为公开或您有写入权限"
    echo "3. 尝试使用SSH地址推送"
    echo ""
    echo "手动推送命令:"
    echo "git remote add origin $REPO_URL"
    echo "git push -u origin main"
    exit 1
fi