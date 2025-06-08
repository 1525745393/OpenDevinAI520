"""
API测试工具
"""

import json
import time
import requests
from pathlib import Path
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse
from src.utils.logger import setup_logger

class ApiTester:
    """API测试工具类"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化API测试工具
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.logger = setup_logger("ApiTester")
        self.session = requests.Session()
        self.test_results = []
    
    def get_description(self) -> str:
        """获取工具描述"""
        return "API测试工具 - 支持HTTP API接口测试和性能分析"
    
    def execute(self, action: str, args: List[str]) -> Optional[str]:
        """
        执行工具操作
        
        Args:
            action: 操作名称
            args: 参数列表
            
        Returns:
            Optional[str]: 执行结果
        """
        if action == "test":
            return self._test_api(args)
        elif action == "batch_test":
            return self._batch_test(args)
        elif action == "load_test":
            return self._load_test(args)
        elif action == "monitor":
            return self._monitor_api(args)
        elif action == "report":
            return self._generate_report(args)
        elif action == "help":
            return self._show_help()
        else:
            return f"未知操作: {action}"
    
    def _test_api(self, args: List[str]) -> str:
        """
        测试单个API
        
        Args:
            args: 参数列表 [url, method, data]
            
        Returns:
            str: 测试结果
        """
        if not args:
            return "请指定API URL"
        
        url = args[0]
        method = args[1].upper() if len(args) > 1 else "GET"
        data = args[2] if len(args) > 2 else None
        
        try:
            # 解析数据
            request_data = None
            headers = {"Content-Type": "application/json"}
            
            if data:
                try:
                    request_data = json.loads(data)
                except json.JSONDecodeError:
                    # 如果不是JSON，作为表单数据处理
                    request_data = data
                    headers = {"Content-Type": "application/x-www-form-urlencoded"}
            
            # 发送请求
            start_time = time.time()
            response = self.session.request(
                method=method,
                url=url,
                json=request_data if headers["Content-Type"] == "application/json" else None,
                data=request_data if headers["Content-Type"] != "application/json" else None,
                headers=headers,
                timeout=30
            )
            end_time = time.time()
            
            # 记录测试结果
            result = {
                "url": url,
                "method": method,
                "status_code": response.status_code,
                "response_time": round((end_time - start_time) * 1000, 2),
                "content_length": len(response.content),
                "headers": dict(response.headers),
                "success": 200 <= response.status_code < 300
            }
            
            self.test_results.append(result)
            
            # 格式化输出
            status_emoji = "✅" if result["success"] else "❌"
            return f"""
{status_emoji} API测试结果:
URL: {url}
方法: {method}
状态码: {response.status_code}
响应时间: {result['response_time']}ms
内容长度: {result['content_length']} bytes
成功: {'是' if result['success'] else '否'}
"""
        
        except requests.exceptions.RequestException as e:
            error_result = {
                "url": url,
                "method": method,
                "error": str(e),
                "success": False
            }
            self.test_results.append(error_result)
            return f"❌ API测试失败: {e}"
        
        except Exception as e:
            return f"❌ 测试过程出错: {e}"
    
    def _batch_test(self, args: List[str]) -> str:
        """
        批量测试API
        
        Args:
            args: 参数列表 [config_file]
            
        Returns:
            str: 批量测试结果
        """
        if not args:
            return "请指定测试配置文件"
        
        config_file = Path(args[0])
        if not config_file.exists():
            return f"配置文件不存在: {config_file}"
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                test_config = json.load(f)
            
            total_tests = len(test_config.get("tests", []))
            passed_tests = 0
            failed_tests = 0
            
            for test_case in test_config.get("tests", []):
                try:
                    url = test_case["url"]
                    method = test_case.get("method", "GET")
                    data = test_case.get("data")
                    expected_status = test_case.get("expected_status", 200)
                    
                    # 执行测试
                    start_time = time.time()
                    response = self.session.request(
                        method=method,
                        url=url,
                        json=data,
                        timeout=30
                    )
                    end_time = time.time()
                    
                    # 验证结果
                    success = response.status_code == expected_status
                    if success:
                        passed_tests += 1
                    else:
                        failed_tests += 1
                    
                    # 记录结果
                    result = {
                        "name": test_case.get("name", url),
                        "url": url,
                        "method": method,
                        "status_code": response.status_code,
                        "expected_status": expected_status,
                        "response_time": round((end_time - start_time) * 1000, 2),
                        "success": success
                    }
                    self.test_results.append(result)
                    
                    status_emoji = "✅" if success else "❌"
                    self.logger.info(f"{status_emoji} {result['name']}: {response.status_code} ({result['response_time']}ms)")
                
                except Exception as e:
                    failed_tests += 1
                    self.logger.error(f"❌ 测试失败 {test_case.get('name', 'Unknown')}: {e}")
            
            return f"""
📊 批量测试完成:
总测试数: {total_tests}
通过: {passed_tests}
失败: {failed_tests}
成功率: {(passed_tests/total_tests*100):.1f}%
"""
        
        except Exception as e:
            return f"❌ 批量测试失败: {e}"
    
    def _load_test(self, args: List[str]) -> str:
        """
        负载测试
        
        Args:
            args: 参数列表 [url, concurrent_users, duration]
            
        Returns:
            str: 负载测试结果
        """
        if len(args) < 3:
            return "参数不足。用法: load_test <url> <并发用户数> <持续时间(秒)>"
        
        url = args[0]
        concurrent_users = int(args[1])
        duration = int(args[2])
        
        try:
            import threading
            import queue
            
            results_queue = queue.Queue()
            start_time = time.time()
            
            def worker():
                """工作线程"""
                while time.time() - start_time < duration:
                    try:
                        request_start = time.time()
                        response = self.session.get(url, timeout=10)
                        request_end = time.time()
                        
                        results_queue.put({
                            "status_code": response.status_code,
                            "response_time": (request_end - request_start) * 1000,
                            "success": 200 <= response.status_code < 300
                        })
                    except Exception as e:
                        results_queue.put({
                            "error": str(e),
                            "success": False
                        })
                    
                    time.sleep(0.1)  # 避免过于频繁的请求
            
            # 启动工作线程
            threads = []
            for _ in range(concurrent_users):
                thread = threading.Thread(target=worker)
                thread.start()
                threads.append(thread)
            
            # 等待测试完成
            for thread in threads:
                thread.join()
            
            # 收集结果
            results = []
            while not results_queue.empty():
                results.append(results_queue.get())
            
            # 统计分析
            total_requests = len(results)
            successful_requests = sum(1 for r in results if r.get("success", False))
            failed_requests = total_requests - successful_requests
            
            response_times = [r["response_time"] for r in results if "response_time" in r]
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            min_response_time = min(response_times) if response_times else 0
            max_response_time = max(response_times) if response_times else 0
            
            rps = total_requests / duration  # 每秒请求数
            
            return f"""
🚀 负载测试结果:
URL: {url}
并发用户: {concurrent_users}
测试时长: {duration}秒
总请求数: {total_requests}
成功请求: {successful_requests}
失败请求: {failed_requests}
成功率: {(successful_requests/total_requests*100):.1f}%
平均响应时间: {avg_response_time:.2f}ms
最小响应时间: {min_response_time:.2f}ms
最大响应时间: {max_response_time:.2f}ms
每秒请求数: {rps:.2f} RPS
"""
        
        except Exception as e:
            return f"❌ 负载测试失败: {e}"
    
    def _monitor_api(self, args: List[str]) -> str:
        """
        监控API
        
        Args:
            args: 参数列表 [url, interval, count]
            
        Returns:
            str: 监控结果
        """
        if not args:
            return "请指定要监控的API URL"
        
        url = args[0]
        interval = int(args[1]) if len(args) > 1 else 60  # 默认60秒间隔
        count = int(args[2]) if len(args) > 2 else 10     # 默认监控10次
        
        try:
            monitor_results = []
            
            for i in range(count):
                try:
                    start_time = time.time()
                    response = self.session.get(url, timeout=30)
                    end_time = time.time()
                    
                    result = {
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "status_code": response.status_code,
                        "response_time": round((end_time - start_time) * 1000, 2),
                        "success": 200 <= response.status_code < 300
                    }
                    
                    monitor_results.append(result)
                    
                    status_emoji = "✅" if result["success"] else "❌"
                    self.logger.info(f"{status_emoji} [{result['timestamp']}] {url}: {result['status_code']} ({result['response_time']}ms)")
                    
                    if i < count - 1:  # 最后一次不需要等待
                        time.sleep(interval)
                
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    self.logger.error(f"❌ 监控请求失败: {e}")
            
            # 生成监控报告
            successful_checks = sum(1 for r in monitor_results if r["success"])
            avg_response_time = sum(r["response_time"] for r in monitor_results) / len(monitor_results)
            uptime = (successful_checks / len(monitor_results)) * 100
            
            return f"""
📈 API监控报告:
URL: {url}
监控次数: {len(monitor_results)}
成功次数: {successful_checks}
可用性: {uptime:.1f}%
平均响应时间: {avg_response_time:.2f}ms
"""
        
        except Exception as e:
            return f"❌ API监控失败: {e}"
    
    def _generate_report(self, args: List[str]) -> str:
        """
        生成测试报告
        
        Args:
            args: 参数列表 [output_file]
            
        Returns:
            str: 报告生成结果
        """
        if not self.test_results:
            return "没有测试结果可生成报告"
        
        output_file = args[0] if args else "api_test_report.json"
        
        try:
            report = {
                "summary": {
                    "total_tests": len(self.test_results),
                    "successful_tests": sum(1 for r in self.test_results if r.get("success", False)),
                    "failed_tests": sum(1 for r in self.test_results if not r.get("success", False)),
                    "generated_at": time.strftime("%Y-%m-%d %H:%M:%S")
                },
                "results": self.test_results
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            return f"✅ 测试报告已生成: {output_file}"
        
        except Exception as e:
            return f"❌ 生成报告失败: {e}"
    
    def _show_help(self) -> str:
        """显示帮助信息"""
        return """
API测试工具帮助:

操作:
  test <url> [method] [data]           - 测试单个API
  batch_test <config_file>             - 批量测试API
  load_test <url> <users> <duration>   - 负载测试
  monitor <url> [interval] [count]     - 监控API
  report [output_file]                 - 生成测试报告
  help                                 - 显示此帮助信息

示例:
  api_tester test https://api.example.com/users
  api_tester test https://api.example.com/login POST '{"username":"test","password":"123"}'
  api_tester batch_test tests.json
  api_tester load_test https://api.example.com 10 60
  api_tester monitor https://api.example.com 30 20

批量测试配置文件格式 (JSON):
{
  "tests": [
    {
      "name": "获取用户列表",
      "url": "https://api.example.com/users",
      "method": "GET",
      "expected_status": 200
    },
    {
      "name": "创建用户",
      "url": "https://api.example.com/users",
      "method": "POST",
      "data": {"name": "test", "email": "test@example.com"},
      "expected_status": 201
    }
  ]
}
"""