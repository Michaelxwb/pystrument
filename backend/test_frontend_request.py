#!/usr/bin/env python3
"""
测试前端请求AI分析接口
"""
import os
import sys
from pathlib import Path
import requests
import json

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 创建测试性能数据（如果不存在）
from app.utils.database import init_database, get_database
import asyncio
from datetime import datetime
import uuid

async def create_test_data():
    """创建测试性能数据"""
    await init_database()
    db = get_database()
    
    # 检查是否已存在测试数据
    test_record = await db.performance_records.find_one({"trace_id": "trace_1ae3e17df20d4c15"})
    if not test_record:
        # 创建测试数据
        test_data = {
            "trace_id": "trace_1ae3e17df20d4c15",
            "project_key": "test_project",
            "request_info": {
                "path": "/api/test",
                "method": "GET",
                "headers": {},
                "query_params": {},
                "body": ""
            },
            "response_info": {
                "status_code": 200,
                "headers": {},
                "body": "OK"
            },
            "performance_metrics": {
                "total_duration": 0.456,
                "cpu_time": 0.123,
                "memory_usage": {
                    "peak_memory": 45.6,
                    "avg_memory": 32.1
                },
                "io_wait_time": 0.333,
                "network_time": 0.123
            },
            "function_calls": [
                {
                    "call_id": f"call_{uuid.uuid4().hex[:8]}",
                    "function_name": "database_query",
                    "file_path": "/app/models/user.py",
                    "line_number": 45,
                    "duration": 0.321,
                    "depth": 1,
                    "arguments": {},
                    "return_value": None
                },
                {
                    "call_id": f"call_{uuid.uuid4().hex[:8]}",
                    "function_name": "process_data",
                    "file_path": "/app/services/data_processor.py",
                    "line_number": 123,
                    "duration": 0.123,
                    "depth": 1,
                    "arguments": {},
                    "return_value": None
                }
            ],
            "environment": {
                "framework_version": "FastAPI 0.68.0",
                "python_version": "3.9.6",
                "server_info": "uvicorn"
            },
            "timestamp": datetime.utcnow()
        }
        
        await db.performance_records.insert_one(test_data)
        print("已创建测试性能数据")
    else:
        print("测试性能数据已存在")

def test_frontend_request():
    """测试前端请求"""
    # 首先确保有测试数据
    asyncio.run(create_test_data())
    
    # 模拟前端请求
    url = "http://localhost:8000/api/v1/analysis/analyze/trace_1ae3e17df20d4c15"
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json;charset=UTF-8",
    }
    data = {
        "ai_service": "default",
        "priority": "normal"
    }
    
    print(f"发送请求到: {url}")
    print(f"请求数据: {json.dumps(data, indent=2)}")
    
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"任务ID: {result.get('data', {}).get('task_id')}")
            print(f"分析ID: {result.get('data', {}).get('analysis_id')}")
            return result.get('data', {}).get('task_id')
        else:
            print(f"请求失败: {response.status_code}")
            return None
    except Exception as e:
        print(f"请求异常: {str(e)}")
        return None

if __name__ == "__main__":
    test_frontend_request()