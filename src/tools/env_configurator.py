#!/usr/bin/env python3
"""
开发环境配置工具
快速配置各种开发环境：Python, Node.js, Docker, Git等
"""

import os
import json
import subprocess
import platform
import argparse
from pathlib import Path
from typing import Dict, List, Optional
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

console = Console()


class EnvironmentConfigurator:
    """开发环境配置工具"""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.configured_items = []
        self.errors = []
        self.operations_log = []
    
    def check_command_exists(self, command: str) -> bool:
        """检查命令是否存在"""
        try:
            subprocess.run([command, '--version'], 
                         capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def run_command(self, command: str, shell: bool = True) -> Dict:
        """执行命令"""
        try:
            result = subprocess.run(
                command, shell=shell, capture_output=True, 
                text=True, timeout=300
            )
            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': '命令执行超时',
                'returncode': -1
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'returncode': -1
            }
    
    def setup_python_env(self, project_dir: str, python_version: str = "3.9") -> bool:
        """配置Python开发环境"""
        try:
            project_path = Path(project_dir)
            project_path.mkdir(parents=True, exist_ok=True)
            
            console.print(f"🐍 配置Python环境: {project_dir}")
            
            # 检查Python是否安装
            if not self.check_command_exists('python3'):
                console.print("❌ Python3 未安装")
                return False
            
            # 创建虚拟环境
            venv_path = project_path / 'venv'
            if not venv_path.exists():
                console.print("📦 创建虚拟环境...")
                result = self.run_command(f'python3 -m venv {venv_path}')
                if not result['success']:
                    console.print(f"❌ 创建虚拟环境失败: {result.get('stderr', '')}")
                    return False
            
            # 创建requirements.txt
            requirements_file = project_path / 'requirements.txt'
            if not requirements_file.exists():
                default_requirements = [
                    "# 基础依赖",
                    "requests>=2.25.0",
                    "rich>=10.0.0",
                    "",
                    "# 开发依赖",
                    "pytest>=6.0.0",
                    "black>=21.0.0",
                    "flake8>=3.8.0",
                    "mypy>=0.800",
                ]
                requirements_file.write_text('\n'.join(default_requirements))
                console.print("📝 创建 requirements.txt")
            
            # 创建.gitignore
            gitignore_file = project_path / '.gitignore'
            if not gitignore_file.exists():
                python_gitignore = [
                    "# Python",
                    "__pycache__/",
                    "*.py[cod]",
                    "*$py.class",
                    "*.so",
                    ".Python",
                    "build/",
                    "develop-eggs/",
                    "dist/",
                    "downloads/",
                    "eggs/",
                    ".eggs/",
                    "lib/",
                    "lib64/",
                    "parts/",
                    "sdist/",
                    "var/",
                    "wheels/",
                    "*.egg-info/",
                    ".installed.cfg",
                    "*.egg",
                    "",
                    "# Virtual Environment",
                    "venv/",
                    "env/",
                    "ENV/",
                    "",
                    "# IDE",
                    ".vscode/",
                    ".idea/",
                    "*.swp",
                    "*.swo",
                    "*~",
                    "",
                    "# OS",
                    ".DS_Store",
                    "Thumbs.db",
                ]
                gitignore_file.write_text('\n'.join(python_gitignore))
                console.print("📝 创建 .gitignore")
            
            # 创建pyproject.toml
            pyproject_file = project_path / 'pyproject.toml'
            if not pyproject_file.exists():
                pyproject_content = '''[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "my-project"
version = "0.1.0"
description = "A Python project"
authors = [{name = "Developer", email = "dev@example.com"}]
license = {text = "MIT"}
readme = "README.md"
requires-python = ">=3.8"
dependencies = []

[project.optional-dependencies]
dev = [
    "pytest>=6.0.0",
    "black>=21.0.0",
    "flake8>=3.8.0",
    "mypy>=0.800",
]

[tool.black]
line-length = 88
target-version = ['py38']

[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
'''
                pyproject_file.write_text(pyproject_content)
                console.print("📝 创建 pyproject.toml")
            
            # 创建基本项目结构
            src_dir = project_path / 'src'
            tests_dir = project_path / 'tests'
            docs_dir = project_path / 'docs'
            
            for dir_path in [src_dir, tests_dir, docs_dir]:
                dir_path.mkdir(exist_ok=True)
                init_file = dir_path / '__init__.py'
                if dir_path in [src_dir, tests_dir] and not init_file.exists():
                    init_file.touch()
            
            # 创建README.md
            readme_file = project_path / 'README.md'
            if not readme_file.exists():
                readme_content = f'''# {project_path.name}

## 项目描述

这是一个Python项目。

## 安装

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/Mac
# 或
venv\\Scripts\\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

## 使用

```python
# 示例代码
print("Hello, World!")
```

## 开发

```bash
# 安装开发依赖
pip install -e .[dev]

# 运行测试
pytest

# 代码格式化
black src/

# 代码检查
flake8 src/
mypy src/
```

## 许可证

MIT License
'''
                readme_file.write_text(readme_content)
                console.print("📝 创建 README.md")
            
            self.configured_items.append(f"Python环境: {project_dir}")
            self.operations_log.append(f"配置Python环境: {project_dir}")
            console.print("✅ Python环境配置完成")
            return True
            
        except Exception as e:
            error_msg = f"配置Python环境失败: {str(e)}"
            self.errors.append(error_msg)
            console.print(f"❌ {error_msg}")
            return False
    
    def setup_nodejs_env(self, project_dir: str) -> bool:
        """配置Node.js开发环境"""
        try:
            project_path = Path(project_dir)
            project_path.mkdir(parents=True, exist_ok=True)
            
            console.print(f"🟢 配置Node.js环境: {project_dir}")
            
            # 检查Node.js是否安装
            if not self.check_command_exists('node'):
                console.print("❌ Node.js 未安装")
                return False
            
            # 初始化package.json
            package_json = project_path / 'package.json'
            if not package_json.exists():
                console.print("📦 初始化 package.json...")
                
                package_data = {
                    "name": project_path.name.lower().replace(' ', '-'),
                    "version": "1.0.0",
                    "description": "A Node.js project",
                    "main": "index.js",
                    "scripts": {
                        "start": "node index.js",
                        "dev": "nodemon index.js",
                        "test": "jest",
                        "lint": "eslint .",
                        "format": "prettier --write ."
                    },
                    "keywords": [],
                    "author": "",
                    "license": "MIT",
                    "devDependencies": {
                        "nodemon": "^2.0.0",
                        "jest": "^27.0.0",
                        "eslint": "^8.0.0",
                        "prettier": "^2.0.0"
                    }
                }
                
                with open(package_json, 'w') as f:
                    json.dump(package_data, f, indent=2)
                console.print("📝 创建 package.json")
            
            # 创建.gitignore
            gitignore_file = project_path / '.gitignore'
            if not gitignore_file.exists():
                nodejs_gitignore = [
                    "# Dependencies",
                    "node_modules/",
                    "npm-debug.log*",
                    "yarn-debug.log*",
                    "yarn-error.log*",
                    "",
                    "# Runtime data",
                    "pids",
                    "*.pid",
                    "*.seed",
                    "*.pid.lock",
                    "",
                    "# Coverage directory used by tools like istanbul",
                    "coverage/",
                    "",
                    "# Build output",
                    "dist/",
                    "build/",
                    "",
                    "# Environment variables",
                    ".env",
                    ".env.local",
                    ".env.development.local",
                    ".env.test.local",
                    ".env.production.local",
                    "",
                    "# IDE",
                    ".vscode/",
                    ".idea/",
                    "",
                    "# OS",
                    ".DS_Store",
                    "Thumbs.db",
                ]
                gitignore_file.write_text('\n'.join(nodejs_gitignore))
                console.print("📝 创建 .gitignore")
            
            # 创建基本文件
            index_file = project_path / 'index.js'
            if not index_file.exists():
                index_content = '''console.log('Hello, Node.js!');

// 示例Express服务器
// const express = require('express');
// const app = express();
// const port = 3000;

// app.get('/', (req, res) => {
//   res.send('Hello World!');
// });

// app.listen(port, () => {
//   console.log(`Server running at http://localhost:${port}`);
// });
'''
                index_file.write_text(index_content)
                console.print("📝 创建 index.js")
            
            # 创建ESLint配置
            eslint_file = project_path / '.eslintrc.json'
            if not eslint_file.exists():
                eslint_config = {
                    "env": {
                        "browser": True,
                        "es2021": True,
                        "node": True
                    },
                    "extends": ["eslint:recommended"],
                    "parserOptions": {
                        "ecmaVersion": 12,
                        "sourceType": "module"
                    },
                    "rules": {
                        "indent": ["error", 2],
                        "linebreak-style": ["error", "unix"],
                        "quotes": ["error", "single"],
                        "semi": ["error", "always"]
                    }
                }
                
                with open(eslint_file, 'w') as f:
                    json.dump(eslint_config, f, indent=2)
                console.print("📝 创建 .eslintrc.json")
            
            # 创建Prettier配置
            prettier_file = project_path / '.prettierrc'
            if not prettier_file.exists():
                prettier_config = {
                    "semi": True,
                    "trailingComma": "es5",
                    "singleQuote": True,
                    "printWidth": 80,
                    "tabWidth": 2
                }
                
                with open(prettier_file, 'w') as f:
                    json.dump(prettier_config, f, indent=2)
                console.print("📝 创建 .prettierrc")
            
            # 创建README.md
            readme_file = project_path / 'README.md'
            if not readme_file.exists():
                readme_content = f'''# {project_path.name}

## 项目描述

这是一个Node.js项目。

## 安装

```bash
# 安装依赖
npm install

# 或使用yarn
yarn install
```

## 使用

```bash
# 启动项目
npm start

# 开发模式
npm run dev

# 运行测试
npm test

# 代码检查
npm run lint

# 代码格式化
npm run format
```

## 项目结构

```
{project_path.name}/
├── index.js          # 主入口文件
├── package.json      # 项目配置
├── .eslintrc.json    # ESLint配置
├── .prettierrc       # Prettier配置
├── .gitignore        # Git忽略文件
└── README.md         # 项目说明
```

## 许可证

MIT License
'''
                readme_file.write_text(readme_content)
                console.print("📝 创建 README.md")
            
            self.configured_items.append(f"Node.js环境: {project_dir}")
            self.operations_log.append(f"配置Node.js环境: {project_dir}")
            console.print("✅ Node.js环境配置完成")
            return True
            
        except Exception as e:
            error_msg = f"配置Node.js环境失败: {str(e)}"
            self.errors.append(error_msg)
            console.print(f"❌ {error_msg}")
            return False
    
    def setup_git_config(self, name: str = None, email: str = None) -> bool:
        """配置Git"""
        try:
            console.print("🔧 配置Git...")
            
            # 检查Git是否安装
            if not self.check_command_exists('git'):
                console.print("❌ Git 未安装")
                return False
            
            # 获取用户信息
            if not name:
                name = Prompt.ask("请输入您的姓名", default="Developer")
            if not email:
                email = Prompt.ask("请输入您的邮箱", default="dev@example.com")
            
            # 配置用户信息
            commands = [
                f'git config --global user.name "{name}"',
                f'git config --global user.email "{email}"',
                'git config --global init.defaultBranch main',
                'git config --global core.autocrlf input',
                'git config --global core.editor "code --wait"',
                'git config --global pull.rebase false',
            ]
            
            for cmd in commands:
                result = self.run_command(cmd)
                if not result['success']:
                    console.print(f"⚠️ 命令执行失败: {cmd}")
            
            # 创建全局.gitignore
            global_gitignore = Path.home() / '.gitignore_global'
            if not global_gitignore.exists():
                gitignore_content = [
                    "# OS generated files",
                    ".DS_Store",
                    ".DS_Store?",
                    "._*",
                    ".Spotlight-V100",
                    ".Trashes",
                    "ehthumbs.db",
                    "Thumbs.db",
                    "",
                    "# IDE files",
                    ".vscode/",
                    ".idea/",
                    "*.swp",
                    "*.swo",
                    "*~",
                    "",
                    "# Temporary files",
                    "*.tmp",
                    "*.temp",
                    "*.log",
                ]
                global_gitignore.write_text('\n'.join(gitignore_content))
                
                # 配置全局gitignore
                self.run_command(f'git config --global core.excludesfile {global_gitignore}')
                console.print("📝 创建全局 .gitignore")
            
            self.configured_items.append("Git配置")
            self.operations_log.append(f"配置Git: {name} <{email}>")
            console.print("✅ Git配置完成")
            return True
            
        except Exception as e:
            error_msg = f"配置Git失败: {str(e)}"
            self.errors.append(error_msg)
            console.print(f"❌ {error_msg}")
            return False
    
    def setup_docker_env(self, project_dir: str, app_type: str = "python") -> bool:
        """配置Docker环境"""
        try:
            project_path = Path(project_dir)
            project_path.mkdir(parents=True, exist_ok=True)
            
            console.print(f"🐳 配置Docker环境: {project_dir}")
            
            # 创建Dockerfile
            dockerfile = project_path / 'Dockerfile'
            if not dockerfile.exists():
                if app_type == "python":
                    dockerfile_content = '''FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["python", "app.py"]
'''
                elif app_type == "nodejs":
                    dockerfile_content = '''FROM node:16-alpine

WORKDIR /app

# 复制package文件
COPY package*.json ./

# 安装依赖
RUN npm ci --only=production

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 3000

# 创建非root用户
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nextjs -u 1001

USER nextjs

# 启动命令
CMD ["npm", "start"]
'''
                else:
                    dockerfile_content = '''FROM alpine:latest

WORKDIR /app

# 安装基础工具
RUN apk add --no-cache \\
    curl \\
    wget

# 复制应用文件
COPY . .

# 启动命令
CMD ["sh"]
'''
                
                dockerfile.write_text(dockerfile_content)
                console.print("📝 创建 Dockerfile")
            
            # 创建.dockerignore
            dockerignore = project_path / '.dockerignore'
            if not dockerignore.exists():
                dockerignore_content = [
                    "node_modules",
                    "npm-debug.log",
                    "Dockerfile*",
                    "docker-compose*",
                    ".dockerignore",
                    ".git",
                    ".gitignore",
                    "README.md",
                    ".env",
                    ".nyc_output",
                    "coverage",
                    ".nyc_output",
                    "__pycache__",
                    "*.pyc",
                    "*.pyo",
                    "*.pyd",
                    ".Python",
                    "env",
                    "venv",
                    ".venv",
                    "pip-log.txt",
                    "pip-delete-this-directory.txt",
                    ".tox",
                    ".coverage",
                    ".coverage.*",
                    ".cache",
                    "nosetests.xml",
                    "coverage.xml",
                    "*.cover",
                    "*.log",
                    ".DS_Store",
                    ".vscode",
                    ".idea",
                ]
                dockerignore.write_text('\n'.join(dockerignore_content))
                console.print("📝 创建 .dockerignore")
            
            # 创建docker-compose.yml
            compose_file = project_path / 'docker-compose.yml'
            if not compose_file.exists():
                if app_type == "python":
                    compose_content = '''version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - .:/app
    environment:
      - PYTHONPATH=/app
      - FLASK_ENV=development
    depends_on:
      - db
      - redis

  db:
    image: postgres:13
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
'''
                elif app_type == "nodejs":
                    compose_content = '''version: '3.8'

services:
  app:
    build: .
    ports:
      - "3000:3000"
    volumes:
      - .:/app
      - /app/node_modules
    environment:
      - NODE_ENV=development
    depends_on:
      - db
      - redis

  db:
    image: mongo:4.4
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: password
    volumes:
      - mongo_data:/data/db
    ports:
      - "27017:27017"

  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"

volumes:
  mongo_data:
'''
                else:
                    compose_content = '''version: '3.8'

services:
  app:
    build: .
    ports:
      - "8080:8080"
    volumes:
      - .:/app

volumes:
  app_data:
'''
                
                compose_file.write_text(compose_content)
                console.print("📝 创建 docker-compose.yml")
            
            self.configured_items.append(f"Docker环境: {project_dir}")
            self.operations_log.append(f"配置Docker环境: {project_dir} ({app_type})")
            console.print("✅ Docker环境配置完成")
            return True
            
        except Exception as e:
            error_msg = f"配置Docker环境失败: {str(e)}"
            self.errors.append(error_msg)
            console.print(f"❌ {error_msg}")
            return False
    
    def check_system_requirements(self) -> Dict:
        """检查系统要求"""
        requirements = {
            'python3': self.check_command_exists('python3'),
            'node': self.check_command_exists('node'),
            'npm': self.check_command_exists('npm'),
            'git': self.check_command_exists('git'),
            'docker': self.check_command_exists('docker'),
            'docker-compose': self.check_command_exists('docker-compose'),
        }
        
        return requirements
    
    def display_system_info(self):
        """显示系统信息"""
        console.print("🖥️ 系统信息:")
        console.print(f"  操作系统: {platform.system()} {platform.release()}")
        console.print(f"  架构: {platform.machine()}")
        console.print(f"  Python版本: {platform.python_version()}")
        
        console.print("\n📋 工具检查:")
        requirements = self.check_system_requirements()
        
        table = Table()
        table.add_column("工具", style="cyan")
        table.add_column("状态", style="magenta")
        
        for tool, available in requirements.items():
            status = "✅ 已安装" if available else "❌ 未安装"
            table.add_row(tool, status)
        
        console.print(table)
    
    def get_report(self) -> Dict:
        """获取配置报告"""
        return {
            'configured_items': self.configured_items,
            'errors': self.errors,
            'operations_log': self.operations_log,
            'total_configured': len(self.configured_items),
            'total_errors': len(self.errors)
        }
    
    def display_report(self):
        """显示配置报告"""
        report = self.get_report()
        
        # 创建统计表格
        table = Table(title="📊 环境配置报告")
        table.add_column("项目", style="cyan")
        table.add_column("数量", style="magenta")
        
        table.add_row("配置成功", str(report['total_configured']))
        table.add_row("配置失败", str(report['total_errors']))
        table.add_row("总操作数", str(len(report['operations_log'])))
        
        console.print(table)
        
        # 显示配置项目
        if report['configured_items']:
            console.print("\n✅ 已配置项目:")
            for item in report['configured_items']:
                console.print(f"  • {item}")
        
        # 显示错误
        if report['errors']:
            console.print("\n❌ 错误信息:")
            for error in report['errors']:
                console.print(f"  • {error}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="开发环境配置工具")
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 系统信息命令
    info_parser = subparsers.add_parser('info', help='显示系统信息')
    
    # Python环境配置
    python_parser = subparsers.add_parser('python', help='配置Python环境')
    python_parser.add_argument('project_dir', help='项目目录')
    python_parser.add_argument('--version', default='3.9', help='Python版本')
    
    # Node.js环境配置
    nodejs_parser = subparsers.add_parser('nodejs', help='配置Node.js环境')
    nodejs_parser.add_argument('project_dir', help='项目目录')
    
    # Git配置
    git_parser = subparsers.add_parser('git', help='配置Git')
    git_parser.add_argument('--name', help='用户名')
    git_parser.add_argument('--email', help='邮箱')
    
    # Docker配置
    docker_parser = subparsers.add_parser('docker', help='配置Docker环境')
    docker_parser.add_argument('project_dir', help='项目目录')
    docker_parser.add_argument('--type', choices=['python', 'nodejs', 'generic'], 
                              default='python', help='应用类型')
    
    # 完整配置
    full_parser = subparsers.add_parser('full', help='完整环境配置')
    full_parser.add_argument('project_dir', help='项目目录')
    full_parser.add_argument('--type', choices=['python', 'nodejs'], 
                            default='python', help='项目类型')
    full_parser.add_argument('--git-name', help='Git用户名')
    full_parser.add_argument('--git-email', help='Git邮箱')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    configurator = EnvironmentConfigurator()
    
    try:
        if args.command == 'info':
            configurator.display_system_info()
        
        elif args.command == 'python':
            configurator.setup_python_env(args.project_dir, args.version)
        
        elif args.command == 'nodejs':
            configurator.setup_nodejs_env(args.project_dir)
        
        elif args.command == 'git':
            configurator.setup_git_config(args.name, args.email)
        
        elif args.command == 'docker':
            configurator.setup_docker_env(args.project_dir, args.type)
        
        elif args.command == 'full':
            console.print(f"🚀 完整环境配置: {args.project_dir}")
            
            # 配置Git（如果提供了参数）
            if args.git_name or args.git_email:
                configurator.setup_git_config(args.git_name, args.git_email)
            
            # 配置项目环境
            if args.type == 'python':
                configurator.setup_python_env(args.project_dir)
            elif args.type == 'nodejs':
                configurator.setup_nodejs_env(args.project_dir)
            
            # 配置Docker
            configurator.setup_docker_env(args.project_dir, args.type)
            
            console.print("🎉 完整环境配置完成！")
        
        # 显示报告
        if args.command != 'info':
            configurator.display_report()
        
    except KeyboardInterrupt:
        console.print("\n⚠️ 操作被用户取消")
    except Exception as e:
        console.print(f"\n❌ 执行失败: {str(e)}")


if __name__ == "__main__":
    main()