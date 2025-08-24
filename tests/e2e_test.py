#!/usr/bin/env python3
"""
端到端集成测试脚本
"""
import asyncio
import aiohttp
import time
import sys
import json
from typing import Dict, Any
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class E2ETestRunner:
    """端到端测试运行器"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
        self.test_project_key = None
        
    async def __aenter__(self):
        """异步上下文管理器入口"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if self.session:
            await self.session.close()
    
    async def test_health_check(self) -> bool:
        """测试健康检查接口"""
        logger.info("测试健康检查接口...")
        try:
            async with self.session.get(f"{self.base_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("code") == 0:
                        logger.info("✓ 健康检查通过")
                        return True
        except Exception as e:
            logger.error(f"✗ 健康检查失败: {e}")
        return False
    
    async def test_create_project(self) -> bool:
        """测试创建项目"""
        logger.info("测试创建项目...")
        
        project_data = {
            "name": "E2E测试项目",
            "description": "端到端测试项目",
            "framework": "flask",
            "base_url": "http://test.example.com",
            "sampling_rate": 50.0,
            "enable_ai_analysis": True
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/api/v1/projects",
                json=project_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("code") == 0:
                        self.test_project_key = data["data"]["project_key"]
                        logger.info(f"✓ 项目创建成功，项目键: {self.test_project_key}")
                        return True
                    else:
                        logger.error(f"✗ 项目创建失败: {data.get('msg')}")
                else:
                    logger.error(f"✗ 项目创建失败: HTTP {response.status}")
        except Exception as e:
            logger.error(f"✗ 项目创建异常: {e}")
        return False
    
    async def test_get_projects(self) -> bool:
        """测试获取项目列表"""
        logger.info("测试获取项目列表...")
        
        try:
            async with self.session.get(f"{self.base_url}/api/v1/projects") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("code") == 0:
                        projects = data["data"]["projects"]
                        logger.info(f"✓ 项目列表获取成功，共 {len(projects)} 个项目")
                        return True
                    else:
                        logger.error(f"✗ 项目列表获取失败: {data.get('msg')}")
                else:
                    logger.error(f"✗ 项目列表获取失败: HTTP {response.status}")
        except Exception as e:
            logger.error(f"✗ 项目列表获取异常: {e}")
        return False
    
    async def test_submit_performance_data(self) -> str:
        """测试提交性能数据"""
        logger.info("测试提交性能数据...")
        
        if not self.test_project_key:
            logger.error("✗ 没有可用的测试项目")
            return None
        
        # 构造性能数据
        performance_data = {
            "trace_id": f"e2e_test_trace_{int(time.time())}",
            "project_key": self.test_project_key,
            "timestamp": time.time(),
            "request_info": {
                "method": "GET",
                "path": "/api/test-endpoint",
                "headers": {"User-Agent": "E2E-Test-Client"},
                "remote_ip": "127.0.0.1",
                "query_params": {"test": "true"}
            },
            "response_info": {
                "status_code": 200,
                "response_size": 1024,
                "content_type": "application/json"
            },
            "performance_metrics": {
                "total_duration": 0.25,  # 250ms
                "cpu_time": 0.15,
                "memory_usage": {
                    "start_memory": 100,
                    "peak_memory": 150
                }
            },
            "function_calls": [
                {
                    "id": "call_1",
                    "function_name": "test_handler",
                    "file_path": "/app/handlers/test.py",
                    "line_number": 25,
                    "duration": 0.2,
                    "depth": 0
                },
                {
                    "id": "call_2",
                    "function_name": "database_query",
                    "file_path": "/app/db/queries.py",
                    "line_number": 45,
                    "duration": 0.15,
                    "depth": 1
                },
                {
                    "id": "call_3",
                    "function_name": "process_data",
                    "file_path": "/app/utils/processor.py",
                    "line_number": 12,
                    "duration": 0.08,
                    "depth": 1
                }
            ],
            "environment": {
                "python_version": "3.9.6",
                "framework_version": "Flask 2.0.1",
                "platform": "Linux-5.4.0",
                "hostname": "e2e-test-host"
            }
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/api/v1/performance/collect",
                json=performance_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("code") == 0:
                        record_id = data["data"]["record_id"]
                        logger.info(f"✓ 性能数据提交成功，记录ID: {record_id}")
                        return record_id
                    else:
                        logger.error(f"✗ 性能数据提交失败: {data.get('msg')}")
                else:
                    logger.error(f"✗ 性能数据提交失败: HTTP {response.status}")
        except Exception as e:
            logger.error(f"✗ 性能数据提交异常: {e}")
        return None
    
    async def test_query_performance_data(self) -> bool:
        """测试查询性能数据"""
        logger.info("测试查询性能数据...")
        
        if not self.test_project_key:
            logger.error("✗ 没有可用的测试项目")
            return False
        
        try:
            params = {
                "project_key": self.test_project_key,
                "page": 1,
                "size": 10
            }
            
            async with self.session.get(
                f"{self.base_url}/api/v1/performance/records",
                params=params
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("code") == 0:
                        records = data["data"]["records"]
                        logger.info(f"✓ 性能数据查询成功，共 {len(records)} 条记录")
                        return True
                    else:
                        logger.error(f"✗ 性能数据查询失败: {data.get('msg')}")
                else:
                    logger.error(f"✗ 性能数据查询失败: HTTP {response.status}")
        except Exception as e:
            logger.error(f"✗ 性能数据查询异常: {e}")
        return False
    
    async def test_trigger_ai_analysis(self, performance_record_id: str) -> str:
        """测试触发AI分析"""
        logger.info("测试触发AI分析...")
        
        if not performance_record_id:
            logger.error("✗ 没有可用的性能记录ID")
            return None
        
        analysis_request = {
            "ai_service": "default",
            "priority": "normal"
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/api/v1/analysis/analyze/{performance_record_id}",
                json=analysis_request
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("code") == 0:
                        task_id = data["data"]["task_id"]
                        logger.info(f"✓ AI分析触发成功，任务ID: {task_id}")
                        return task_id
                    else:
                        logger.error(f"✗ AI分析触发失败: {data.get('msg')}")
                else:
                    logger.error(f"✗ AI分析触发失败: HTTP {response.status}")
        except Exception as e:
            logger.error(f"✗ AI分析触发异常: {e}")
        return None
    
    async def test_check_analysis_status(self, task_id: str) -> bool:
        """测试检查分析状态"""
        logger.info("测试检查分析状态...")
        
        if not task_id:
            logger.error("✗ 没有可用的任务ID")
            return False
        
        max_attempts = 10
        for attempt in range(max_attempts):
            try:
                async with self.session.get(
                    f"{self.base_url}/api/v1/analysis/task-status/{task_id}"
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("code") == 0:
                            status = data["data"]["status"]
                            logger.info(f"分析状态: {status}")
                            
                            if status == "SUCCESS":
                                logger.info("✓ AI分析完成")
                                return True
                            elif status == "FAILURE":
                                logger.error("✗ AI分析失败")
                                return False
                            else:
                                # 等待继续检查
                                await asyncio.sleep(2)
                                continue
                        else:
                            logger.error(f"✗ 状态检查失败: {data.get('msg')}")
                            return False
                    else:
                        logger.error(f"✗ 状态检查失败: HTTP {response.status}")
                        return False
            except Exception as e:
                logger.error(f"✗ 状态检查异常: {e}")
                return False
        
        logger.warning("⚠ AI分析超时")
        return False
    
    async def test_get_ai_services(self) -> bool:
        """测试获取AI服务列表"""
        logger.info("测试获取AI服务列表...")
        
        try:
            async with self.session.get(f"{self.base_url}/api/v1/analysis/config/ai-services") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("code") == 0:
                        services = data["data"]
                        logger.info(f"✓ AI服务列表获取成功，共 {len(services)} 个服务")
                        return True
                    else:
                        logger.error(f"✗ AI服务列表获取失败: {data.get('msg')}")
                else:
                    logger.error(f"✗ AI服务列表获取失败: HTTP {response.status}")
        except Exception as e:
            logger.error(f"✗ AI服务列表获取异常: {e}")
        return False
    
    async def cleanup_test_data(self) -> bool:
        """清理测试数据"""
        logger.info("清理测试数据...")
        
        if not self.test_project_key:
            return True
        
        try:
            async with self.session.delete(f"{self.base_url}/api/v1/projects/{self.test_project_key}") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("code") == 0:
                        logger.info("✓ 测试数据清理成功")
                        return True
                    else:
                        logger.error(f"✗ 测试数据清理失败: {data.get('msg')}")
                else:
                    logger.error(f"✗ 测试数据清理失败: HTTP {response.status}")
        except Exception as e:
            logger.error(f"✗ 测试数据清理异常: {e}")
        return False
    
    async def run_all_tests(self) -> Dict[str, bool]:
        """运行所有测试"""
        logger.info("开始端到端测试...")
        
        results = {}
        
        # 1. 健康检查
        results["health_check"] = await self.test_health_check()
        
        # 2. 项目管理测试
        results["create_project"] = await self.test_create_project()
        results["get_projects"] = await self.test_get_projects()
        
        # 3. 性能数据测试
        performance_record_id = await self.test_submit_performance_data()
        results["submit_performance"] = performance_record_id is not None
        results["query_performance"] = await self.test_query_performance_data()
        
        # 4. AI分析测试
        results["get_ai_services"] = await self.test_get_ai_services()
        
        if performance_record_id:
            task_id = await self.test_trigger_ai_analysis(performance_record_id)
            results["trigger_analysis"] = task_id is not None
            
            if task_id:
                results["check_analysis_status"] = await self.test_check_analysis_status(task_id)
            else:
                results["check_analysis_status"] = False
        else:
            results["trigger_analysis"] = False
            results["check_analysis_status"] = False
        
        # 5. 清理测试数据
        results["cleanup"] = await self.cleanup_test_data()
        
        # 输出测试结果
        logger.info("\n" + "="*50)
        logger.info("端到端测试结果:")
        logger.info("="*50)
        
        passed = 0
        total = len(results)
        
        for test_name, result in results.items():
            status = "✓ PASS" if result else "✗ FAIL"
            logger.info(f"{test_name:20s} {status}")
            if result:
                passed += 1
        
        logger.info("="*50)
        logger.info(f"测试总结: {passed}/{total} 通过")
        
        if passed == total:
            logger.info("🎉 所有测试通过！")
        else:
            logger.warning("⚠ 部分测试失败")
        
        return results


async def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="性能分析平台端到端测试")
    parser.add_argument("--url", default="http://localhost:8000", help="API服务地址")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        async with E2ETestRunner(args.url) as runner:
            results = await runner.run_all_tests()
            
            # 返回适当的退出码
            if all(results.values()):
                sys.exit(0)
            else:
                sys.exit(1)
    
    except KeyboardInterrupt:
        logger.info("测试被用户中断")
        sys.exit(130)
    except Exception as e:
        logger.error(f"测试运行异常: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())