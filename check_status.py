#!/usr/bin/env python3
"""
OpenDevinAI520 项目状态检查脚本
检查项目完整性、工具可用性和系统状态
"""

import os
import sys
import subprocess
import importlib.util
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()

def check_python_version():
    """检查Python版本"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        return True, f"{version.major}.{version.minor}.{version.micro}"
    return False, f"{version.major}.{version.minor}.{version.micro}"

def check_dependencies():
    """检查依赖包"""
    required_packages = [
        'requests', 'click', 'rich', 'pydantic', 'black', 'flake8',
        'pytest', 'mkdocs', 'python-dotenv', 'colorama', 'tqdm',
        'pandas', 'openpyxl', 'PyYAML', 'lxml', 'autopep8'
    ]
    
    missing = []
    installed = []
    
    for package in required_packages:
        try:
            importlib.import_module(package.replace('-', '_'))
            installed.append(package)
        except ImportError:
            missing.append(package)
    
    return installed, missing

def check_tools():
    """检查工具模块"""
    tools_dir = Path("src/tools")
    if not tools_dir.exists():
        return [], ["工具目录不存在"]
    
    expected_tools = [
        "code_formatter.py",
        "file_processor.py", 
        "api_tester.py",
        "media_renamer.py",
        "data_converter.py",
        "env_configurator.py",
        "log_analyzer.py"
    ]
    
    available = []
    missing = []
    
    for tool in expected_tools:
        tool_path = tools_dir / tool
        if tool_path.exists():
            available.append(tool.replace('.py', ''))
        else:
            missing.append(tool.replace('.py', ''))
    
    return available, missing

def check_directories():
    """检查必要目录"""
    required_dirs = [
        "src", "src/tools", "src/utils", "docs", "tests", 
        "examples", "config", ".github", ".github/workflows"
    ]
    
    existing = []
    missing = []
    
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            existing.append(dir_path)
        else:
            missing.append(dir_path)
    
    return existing, missing

def check_files():
    """检查重要文件"""
    required_files = [
        "README.md", "LICENSE", "requirements.txt", "start.sh",
        "src/main.py", "config/config.yaml", "mkdocs.yml",
        ".github/workflows/ci.yml", "CONTRIBUTING.md", "COMMUNITY.md"
    ]
    
    existing = []
    missing = []
    
    for file_path in required_files:
        if Path(file_path).exists():
            existing.append(file_path)
        else:
            missing.append(file_path)
    
    return existing, missing

def check_git_status():
    """检查Git状态"""
    try:
        # 检查是否是Git仓库
        result = subprocess.run(['git', 'status'], 
                              capture_output=True, text=True, cwd='.')
        if result.returncode != 0:
            return False, "不是Git仓库"
        
        # 检查远程仓库
        result = subprocess.run(['git', 'remote', '-v'], 
                              capture_output=True, text=True, cwd='.')
        if 'origin' in result.stdout:
            return True, "Git仓库正常，已配置远程仓库"
        else:
            return True, "Git仓库正常，未配置远程仓库"
            
    except FileNotFoundError:
        return False, "Git未安装"
    except Exception as e:
        return False, f"Git检查失败: {str(e)}"

def run_tool_test():
    """运行工具测试"""
    try:
        result = subprocess.run([sys.executable, 'src/main.py', '--list-tools'], 
                              capture_output=True, text=True, cwd='.')
        if result.returncode == 0:
            return True, "主程序运行正常"
        else:
            return False, f"主程序运行失败: {result.stderr}"
    except Exception as e:
        return False, f"测试失败: {str(e)}"

def main():
    """主函数"""
    console.print(Panel.fit(
        "[bold cyan]🚀 OpenDevinAI520 项目状态检查[/bold cyan]",
        box=box.DOUBLE
    ))
    
    # 检查Python版本
    python_ok, python_version = check_python_version()
    console.print(f"\n[bold]🐍 Python版本:[/bold] {python_version}", end="")
    if python_ok:
        console.print(" [green]✅[/green]")
    else:
        console.print(" [red]❌ (需要3.8+)[/red]")
    
    # 检查依赖
    installed_deps, missing_deps = check_dependencies()
    console.print(f"\n[bold]📦 依赖包:[/bold] {len(installed_deps)}/{len(installed_deps) + len(missing_deps)} 已安装", end="")
    if not missing_deps:
        console.print(" [green]✅[/green]")
    else:
        console.print(" [yellow]⚠️[/yellow]")
        console.print(f"   缺失: {', '.join(missing_deps)}")
    
    # 检查工具
    available_tools, missing_tools = check_tools()
    console.print(f"\n[bold]🛠️ 工具模块:[/bold] {len(available_tools)}/7 可用", end="")
    if not missing_tools:
        console.print(" [green]✅[/green]")
    else:
        console.print(" [red]❌[/red]")
        console.print(f"   缺失: {', '.join(missing_tools)}")
    
    # 检查目录
    existing_dirs, missing_dirs = check_directories()
    console.print(f"\n[bold]📁 目录结构:[/bold] {len(existing_dirs)}/{len(existing_dirs) + len(missing_dirs)} 存在", end="")
    if not missing_dirs:
        console.print(" [green]✅[/green]")
    else:
        console.print(" [yellow]⚠️[/yellow]")
        console.print(f"   缺失: {', '.join(missing_dirs)}")
    
    # 检查文件
    existing_files, missing_files = check_files()
    console.print(f"\n[bold]📄 重要文件:[/bold] {len(existing_files)}/{len(existing_files) + len(missing_files)} 存在", end="")
    if not missing_files:
        console.print(" [green]✅[/green]")
    else:
        console.print(" [yellow]⚠️[/yellow]")
        console.print(f"   缺失: {', '.join(missing_files)}")
    
    # 检查Git状态
    git_ok, git_msg = check_git_status()
    console.print(f"\n[bold]🔧 Git状态:[/bold] {git_msg}", end="")
    if git_ok:
        console.print(" [green]✅[/green]")
    else:
        console.print(" [red]❌[/red]")
    
    # 运行工具测试
    test_ok, test_msg = run_tool_test()
    console.print(f"\n[bold]🧪 功能测试:[/bold] {test_msg}", end="")
    if test_ok:
        console.print(" [green]✅[/green]")
    else:
        console.print(" [red]❌[/red]")
    
    # 生成详细报告
    console.print("\n" + "="*60)
    console.print("[bold cyan]📊 详细状态报告[/bold cyan]")
    
    # 工具状态表
    if available_tools:
        table = Table(title="🛠️ 可用工具", box=box.ROUNDED)
        table.add_column("工具名称", style="cyan")
        table.add_column("状态", style="green")
        
        tool_names = {
            "code_formatter": "代码格式化工具",
            "file_processor": "文件批量处理工具", 
            "api_tester": "API测试工具",
            "media_renamer": "媒体文件重命名工具",
            "data_converter": "数据转换工具",
            "env_configurator": "环境配置工具",
            "log_analyzer": "日志分析工具"
        }
        
        for tool in available_tools:
            name = tool_names.get(tool, tool)
            table.add_row(name, "✅ 可用")
        
        console.print(table)
    
    # 总体状态
    total_checks = 7
    passed_checks = sum([
        python_ok,
        not missing_deps,
        not missing_tools,
        not missing_dirs,
        not missing_files,
        git_ok,
        test_ok
    ])
    
    console.print(f"\n[bold]📈 总体状态:[/bold] {passed_checks}/{total_checks} 检查通过")
    
    if passed_checks == total_checks:
        console.print(Panel(
            "[bold green]🎉 项目状态完美！所有检查都通过了。\n"
            "您可以开始使用 OpenDevinAI520 了！[/bold green]",
            title="✅ 状态良好",
            box=box.DOUBLE
        ))
    elif passed_checks >= 5:
        console.print(Panel(
            "[bold yellow]⚠️ 项目基本可用，但有一些小问题需要解决。\n"
            "请查看上述检查结果并修复相关问题。[/bold yellow]",
            title="⚠️ 需要注意",
            box=box.DOUBLE
        ))
    else:
        console.print(Panel(
            "[bold red]❌ 项目存在严重问题，可能无法正常运行。\n"
            "请仔细检查并修复上述问题后再试。[/bold red]",
            title="❌ 需要修复",
            box=box.DOUBLE
        ))
    
    # 提供建议
    console.print("\n[bold cyan]💡 建议操作:[/bold cyan]")
    if missing_deps:
        console.print("• 运行 [cyan]pip install -r requirements.txt[/cyan] 安装缺失依赖")
    if missing_dirs:
        console.print("• 运行 [cyan]./start.sh[/cyan] 自动创建缺失目录")
    if not test_ok:
        console.print("• 检查 [cyan]src/main.py[/cyan] 文件是否存在问题")
    
    console.print("\n[bold]🚀 快速启动:[/bold]")
    console.print("• 交互模式: [cyan]./start.sh[/cyan]")
    console.print("• Web模式: [cyan]./start.sh web[/cyan]")
    console.print("• 查看帮助: [cyan]./start.sh --help[/cyan]")

if __name__ == "__main__":
    main()