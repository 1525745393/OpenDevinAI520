#!/bin/bash

# GitHub仓库创建脚本
# 需要有repo权限的GitHub token

set -e

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🚀 OpenDevinAI520 GitHub仓库创建脚本${NC}"
echo "=============================================="

# 检查GitHub token
if [ -z "$GITHUB_TOKEN" ]; then
    echo -e "${RED}错误: 未设置GITHUB_TOKEN环境变量${NC}"
    echo "请设置您的GitHub Personal Access Token:"
    echo "export GITHUB_TOKEN=your_token_here"
    echo ""
    echo "Token需要以下权限:"
    echo "- repo (完整仓库权限)"
    echo "- workflow (GitHub Actions权限)"
    exit 1
fi

# 检查token权限
echo -e "${BLUE}检查GitHub token权限...${NC}"
SCOPES=$(curl -s -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user | grep -o '"x-oauth-scopes": "[^"]*"' | cut -d'"' -f4)
echo "当前权限: $SCOPES"

if [[ ! "$SCOPES" == *"repo"* ]]; then
    echo -e "${YELLOW}警告: Token可能缺少repo权限，创建可能失败${NC}"
fi

# 获取用户信息
echo -e "${BLUE}获取GitHub用户信息...${NC}"
USER_INFO=$(curl -s -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user)
USERNAME=$(echo $USER_INFO | grep -o '"login": "[^"]*"' | cut -d'"' -f4)
echo "用户名: $USERNAME"

# 创建仓库
echo -e "${BLUE}创建GitHub仓库...${NC}"
REPO_DATA='{
  "name": "OpenDevinAI520",
  "description": "实用工具开发平台 - 自用人人为我我为人人，致力于创建高效便民的开发工具集",
  "private": false,
  "has_issues": true,
  "has_projects": true,
  "has_wiki": true,
  "has_downloads": true,
  "auto_init": false,
  "license_template": "mit",
  "homepage": "https://'$USERNAME'.github.io/OpenDevinAI520/",
  "topics": ["python", "tools", "utilities", "cli", "web", "automation", "development"]
}'

RESPONSE=$(curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/user/repos \
  -d "$REPO_DATA")

# 检查创建结果
if echo "$RESPONSE" | grep -q '"clone_url"'; then
    CLONE_URL=$(echo $RESPONSE | grep -o '"clone_url": "[^"]*"' | cut -d'"' -f4)
    HTML_URL=$(echo $RESPONSE | grep -o '"html_url": "[^"]*"' | cut -d'"' -f4)
    
    echo -e "${GREEN}✅ 仓库创建成功！${NC}"
    echo "仓库地址: $HTML_URL"
    echo "克隆地址: $CLONE_URL"
    
    # 添加远程仓库并推送
    echo -e "${BLUE}推送代码到GitHub...${NC}"
    
    # 检查是否已有远程仓库
    if git remote get-url origin &>/dev/null; then
        echo "移除现有的origin远程仓库..."
        git remote remove origin
    fi
    
    # 添加新的远程仓库
    git remote add origin $CLONE_URL
    
    # 推送代码
    echo "推送main分支..."
    git push -u origin main
    
    echo -e "${GREEN}✅ 代码推送成功！${NC}"
    echo ""
    echo "🎉 仓库已创建并上传完成！"
    echo "📍 访问地址: $HTML_URL"
    echo "📚 文档地址: https://$USERNAME.github.io/OpenDevinAI520/ (稍后可用)"
    echo ""
    echo "下一步:"
    echo "1. 访问仓库页面查看代码"
    echo "2. 等待GitHub Actions构建文档"
    echo "3. 在Settings > Pages中启用GitHub Pages"
    echo "4. 邀请贡献者参与项目"
    
else
    echo -e "${RED}❌ 仓库创建失败${NC}"
    echo "错误信息:"
    echo "$RESPONSE" | grep -o '"message": "[^"]*"' | cut -d'"' -f4
    echo ""
    echo "可能的原因:"
    echo "1. Token权限不足 (需要repo权限)"
    echo "2. 仓库名已存在"
    echo "3. API限制"
    echo ""
    echo "请检查token权限或手动创建仓库"
    exit 1
fi

# 启用GitHub Pages (如果支持)
echo -e "${BLUE}配置GitHub Pages...${NC}"
PAGES_DATA='{
  "source": {
    "branch": "gh-pages",
    "path": "/"
  }
}'

PAGES_RESPONSE=$(curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/$USERNAME/OpenDevinAI520/pages \
  -d "$PAGES_DATA")

if echo "$PAGES_RESPONSE" | grep -q '"html_url"'; then
    PAGES_URL=$(echo $PAGES_RESPONSE | grep -o '"html_url": "[^"]*"' | cut -d'"' -f4)
    echo -e "${GREEN}✅ GitHub Pages配置成功${NC}"
    echo "文档地址: $PAGES_URL"
else
    echo -e "${YELLOW}⚠️  GitHub Pages需要手动配置${NC}"
    echo "请在仓库Settings > Pages中手动启用"
fi

echo ""
echo -e "${GREEN}🎊 OpenDevinAI520项目部署完成！${NC}"
echo -e "${BLUE}人人为我，我为人人 - 让我们一起构建更好的开发工具生态！${NC}"