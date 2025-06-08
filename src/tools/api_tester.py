#!/usr/bin/env python3
"""
API测试工具
快速测试和调试API接口
"""

import json
import time
import requests
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

class APITester:
    """API测试器"""
    
    def __init__(self, base_url: str = "", timeout: int = 30):
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()
        self.test_results = []
        self.headers = {}
    
    def set_headers(self, headers: Dict[str, str]):
        """设置请求头"""
        self.headers.update(headers)
        self.session.headers.update(headers)
    
    def set_auth(self, auth_type: str, **kwargs):
        """设置认证"""
        if auth_type.lower() == 'bearer':
            token = kwargs.get('token')
            self.set_headers({'Authorization': f'Bearer {token}'})
        elif auth_type.lower() == 'basic':
            username = kwargs.get('username')
            password = kwargs.get('password')
            self.session.auth = (username, password)
        elif auth_type.lower() == 'apikey':
            key = kwargs.get('key')
            header_name = kwargs.get('header', 'X-API-Key')
            self.set_headers({header_name: key})
    
    def test_endpoint(self, method: str, endpoint: str, 
                     data: Optional[Dict] = None, 
                     params: Optional[Dict] = None,
                     headers: Optional[Dict] = None,
                     expected_status: int = 200,
                     test_name: str = None) -> Dict[str, Any]:
        """测试单个API端点"""
        
        url = urljoin(self.base_url, endpoint) if self.base_url else endpoint
        test_name = test_name or f"{method.upper()} {endpoint}"
        
        # 合并请求头
        request_headers = self.headers.copy()
        if headers:
            request_headers.update(headers)
        
        start_time = time.time()
        
        try:
            response = self.session.request(
                method=method.upper(),
                url=url,
                json=data if method.upper() in ['POST', 'PUT', 'PATCH'] else None,
                params=params,
                headers=request_headers,
                timeout=self.timeout
            )
            
            end_time = time.time()
            response_time = round((end_time - start_time) * 1000, 2)  # 毫秒
            
            # 尝试解析JSON响应
            try:
                response_json = response.json()
            except json.JSONDecodeError:
                response_json = None
            
            # 判断测试是否通过
            status_match = response.status_code == expected_status
            
            result = {
                'test_name': test_name,
                'method': method.upper(),
                'url': url,
                'status_code': response.status_code,
                'expected_status': expected_status,
                'status_match': status_match,
                'response_time': response_time,
                'response_headers': dict(response.headers),
                'response_json': response_json,
                'response_text': response.text if not response_json else None,
                'request_data': data,
                'request_params': params,
                'request_headers': request_headers,
                'success': status_match and response.status_code < 400
            }
            
            self.test_results.append(result)
            return result
            
        except requests.exceptions.RequestException as e:
            end_time = time.time()
            response_time = round((end_time - start_time) * 1000, 2)
            
            result = {
                'test_name': test_name,
                'method': method.upper(),
                'url': url,
                'status_code': None,
                'expected_status': expected_status,
                'status_match': False,
                'response_time': response_time,
                'error': str(e),
                'request_data': data,
                'request_params': params,
                'request_headers': request_headers,
                'success': False
            }
            
            self.test_results.append(result)
            return result
    
    def batch_test(self, test_cases: List[Dict]) -> List[Dict]:
        """批量测试API"""
        results = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("执行API测试...", total=len(test_cases))
            
            for test_case in test_cases:
                progress.update(task, description=f"测试: {test_case.get('name', 'Unknown')}")
                
                result = self.test_endpoint(
                    method=test_case['method'],
                    endpoint=test_case['endpoint'],
                    data=test_case.get('data'),
                    params=test_case.get('params'),
                    headers=test_case.get('headers'),
                    expected_status=test_case.get('expected_status', 200),
                    test_name=test_case.get('name')
                )
                
                results.append(result)
                progress.advance(task)
        
        return results
    
    def load_test_suite(self, file_path: str) -> List[Dict]:
        """从JSON文件加载测试套件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            console.print(f"❌ 加载测试套件失败: {e}", style="red")
            return []
    
    def save_results(self, file_path: str):
        """保存测试结果到文件"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.test_results, f, indent=2, ensure_ascii=False)
            console.print(f"✅ 测试结果已保存到: {file_path}")
        except Exception as e:
            console.print(f"❌ 保存结果失败: {e}", style="red")
    
    def print_result(self, result: Dict):
        """打印单个测试结果"""
        status_style = "green" if result['success'] else "red"
        status_icon = "✅" if result['success'] else "❌"
        
        # 创建结果面板
        title = f"{status_icon} {result['test_name']}"
        
        content = []
        content.append(f"[bold]请求:[/bold] {result['method']} {result['url']}")
        
        if result.get('status_code'):
            content.append(f"[bold]状态码:[/bold] {result['status_code']} (期望: {result['expected_status']})")
        
        content.append(f"[bold]响应时间:[/bold] {result['response_time']}ms")
        
        if result.get('error'):
            content.append(f"[bold red]错误:[/bold red] {result['error']}")
        
        panel = Panel(
            "\n".join(content),
            title=title,
            border_style=status_style,
            padding=(1, 2)
        )
        
        console.print(panel)
        
        # 显示响应内容
        if result.get('response_json'):
            console.print("\n📄 [bold]JSON响应:[/bold]")
            json_str = json.dumps(result['response_json'], indent=2, ensure_ascii=False)
            syntax = Syntax(json_str, "json", theme="monokai", line_numbers=True)
            console.print(syntax)
        elif result.get('response_text'):
            console.print("\n📄 [bold]响应内容:[/bold]")
            console.print(result['response_text'][:500] + "..." if len(result['response_text']) > 500 else result['response_text'])
    
    def print_summary(self):
        """打印测试摘要"""
        if not self.test_results:
            console.print("📋 没有测试结果")
            return
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r['success'])
        failed_tests = total_tests - passed_tests
        
        avg_response_time = sum(r['response_time'] for r in self.test_results) / total_tests
        
        # 创建摘要表格
        table = Table(title="🧪 API测试摘要")
        table.add_column("指标", style="cyan")
        table.add_column("值", style="green")
        
        table.add_row("总测试数", str(total_tests))
        table.add_row("通过", str(passed_tests))
        table.add_row("失败", str(failed_tests))
        table.add_row("成功率", f"{(passed_tests/total_tests)*100:.1f}%")
        table.add_row("平均响应时间", f"{avg_response_time:.2f}ms")
        
        console.print(table)
        
        # 显示失败的测试
        if failed_tests > 0:
            console.print("\n❌ [bold red]失败的测试:[/bold red]")
            for result in self.test_results:
                if not result['success']:
                    error_msg = result.get('error', f"状态码: {result.get('status_code', 'Unknown')}")
                    console.print(f"  • {result['test_name']}: {error_msg}")
    
    def generate_report(self) -> str:
        """生成HTML测试报告"""
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>API测试报告</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .header { background: #f0f0f0; padding: 20px; border-radius: 5px; }
                .test-case { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
                .success { border-left: 5px solid #4CAF50; }
                .failure { border-left: 5px solid #f44336; }
                .json { background: #f5f5f5; padding: 10px; border-radius: 3px; overflow-x: auto; }
                pre { margin: 0; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🧪 API测试报告</h1>
                <p>生成时间: {timestamp}</p>
                <p>总测试数: {total} | 通过: {passed} | 失败: {failed}</p>
            </div>
            
            {test_cases}
        </body>
        </html>
        """
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r['success'])
        failed_tests = total_tests - passed_tests
        
        test_cases_html = ""
        for result in self.test_results:
            status_class = "success" if result['success'] else "failure"
            status_icon = "✅" if result['success'] else "❌"
            
            response_content = ""
            if result.get('response_json'):
                json_str = json.dumps(result['response_json'], indent=2, ensure_ascii=False)
                response_content = f'<div class="json"><pre>{json_str}</pre></div>'
            elif result.get('response_text'):
                response_content = f'<div class="json"><pre>{result["response_text"][:1000]}</pre></div>'
            
            test_cases_html += f"""
            <div class="test-case {status_class}">
                <h3>{status_icon} {result['test_name']}</h3>
                <p><strong>请求:</strong> {result['method']} {result['url']}</p>
                <p><strong>状态码:</strong> {result.get('status_code', 'N/A')} (期望: {result['expected_status']})</p>
                <p><strong>响应时间:</strong> {result['response_time']}ms</p>
                {f"<p><strong>错误:</strong> {result['error']}</p>" if result.get('error') else ""}
                {response_content}
            </div>
            """
        
        return html_template.format(
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            total=total_tests,
            passed=passed_tests,
            failed=failed_tests,
            test_cases=test_cases_html
        )


def main():
    """主函数 - 命令行接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="API测试工具")
    parser.add_argument('--base-url', help='API基础URL')
    parser.add_argument('--timeout', type=int, default=30, help='请求超时时间(秒)')
    parser.add_argument('--auth-type', choices=['bearer', 'basic', 'apikey'], help='认证类型')
    parser.add_argument('--token', help='Bearer token')
    parser.add_argument('--username', help='用户名(Basic认证)')
    parser.add_argument('--password', help='密码(Basic认证)')
    parser.add_argument('--api-key', help='API密钥')
    parser.add_argument('--header-name', default='X-API-Key', help='API密钥头名称')
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 单个测试命令
    test_parser = subparsers.add_parser('test', help='测试单个API端点')
    test_parser.add_argument('method', help='HTTP方法')
    test_parser.add_argument('endpoint', help='API端点')
    test_parser.add_argument('--data', help='请求数据(JSON字符串)')
    test_parser.add_argument('--params', help='查询参数(JSON字符串)')
    test_parser.add_argument('--expected-status', type=int, default=200, help='期望状态码')
    
    # 批量测试命令
    batch_parser = subparsers.add_parser('batch', help='批量测试API')
    batch_parser.add_argument('test_file', help='测试套件JSON文件')
    batch_parser.add_argument('--output', help='结果输出文件')
    batch_parser.add_argument('--report', help='生成HTML报告文件')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # 创建API测试器
    tester = APITester(base_url=args.base_url or "", timeout=args.timeout)
    
    # 设置认证
    if args.auth_type == 'bearer' and args.token:
        tester.set_auth('bearer', token=args.token)
    elif args.auth_type == 'basic' and args.username and args.password:
        tester.set_auth('basic', username=args.username, password=args.password)
    elif args.auth_type == 'apikey' and args.api_key:
        tester.set_auth('apikey', key=args.api_key, header=args.header_name)
    
    try:
        if args.command == 'test':
            # 解析请求数据
            data = json.loads(args.data) if args.data else None
            params = json.loads(args.params) if args.params else None
            
            console.print(f"🧪 测试API端点: {args.method.upper()} {args.endpoint}")
            
            result = tester.test_endpoint(
                method=args.method,
                endpoint=args.endpoint,
                data=data,
                params=params,
                expected_status=args.expected_status
            )
            
            tester.print_result(result)
        
        elif args.command == 'batch':
            console.print(f"🧪 批量测试API: {args.test_file}")
            
            test_cases = tester.load_test_suite(args.test_file)
            if not test_cases:
                return 1
            
            results = tester.batch_test(test_cases)
            
            # 显示摘要
            tester.print_summary()
            
            # 保存结果
            if args.output:
                tester.save_results(args.output)
            
            # 生成HTML报告
            if args.report:
                html_report = tester.generate_report()
                with open(args.report, 'w', encoding='utf-8') as f:
                    f.write(html_report)
                console.print(f"📊 HTML报告已生成: {args.report}")
        
        return 0
    
    except Exception as e:
        console.print(f"❌ 执行失败: {e}", style="red")
        return 1


if __name__ == "__main__":
    exit(main())