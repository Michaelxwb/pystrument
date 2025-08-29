#!/usr/bin/env python3
"""
简单测试AI分析功能
"""
import os
import sys
from pathlib import Path
import time

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

from app.tasks.ai_analysis import analyze_performance_task


def simple_test():
    """简单测试"""
    print("提交测试任务...")
    try:
        result = analyze_performance_task.delay(
            "trace_be1d58705118",  # 使用之前创建的测试数据ID
            "aliyun_qianwen",
            "normal"
        )
        print(f"任务已提交，任务ID: {result.id}")
        
        # 等待几秒钟让任务完成
        time.sleep(15)
        
        # 检查任务状态
        print(f"任务状态: {result.state}")
        if result.ready():
            print("任务已完成")
            print("任务结果:", result.result)
        else:
            print("任务仍在运行中...")
            
    except Exception as e:
        print(f"任务提交失败: {str(e)}")


if __name__ == "__main__":
    simple_test()