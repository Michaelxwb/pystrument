#!/usr/bin/env python3
"""
测试AI分析功能
"""
import os
import sys
import uuid
from pathlib import Path
import asyncio
from datetime import datetime

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

from app.tasks.ai_analysis import analyze_performance_task


def create_test_performance_data():
    """创建测试性能数据"""
    return {
        "trace_id": f"trace_{uuid.uuid4().hex[:12]}",
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


def test_ai_analysis():
    """测试AI分析功能"""
    print("创建测试性能数据...")
    test_data = create_test_performance_data()
    print(f"测试数据ID: {test_data['trace_id']}")
    
    # 保存测试数据到数据库
    import asyncio
    from app.utils.database import init_database, get_database
    
    async def save_test_data():
        await init_database()
        db = get_database()
        collection = db.performance_records
        await collection.insert_one(test_data)
        print("测试数据已保存到数据库")
        return test_data['trace_id']
    
    trace_id = asyncio.run(save_test_data())
    
    # 触发AI分析任务
    print("触发AI分析任务...")
    try:
        result = analyze_performance_task.delay(
            trace_id,
            "aliyun_qianwen",
            "normal"
        )
        print(f"任务已提交，任务ID: {result.id}")
        print("等待任务完成...")
        task_result = result.get(timeout=60)
        print("任务完成，结果:")
        print(task_result)
    except Exception as e:
        print(f"任务执行失败: {str(e)}")


if __name__ == "__main__":
    test_ai_analysis()