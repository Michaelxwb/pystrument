#!/usr/bin/env python3
"""
调试环境变量替换
"""
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

print("环境变量:")
print(f"ALIYUN_QIANWEN_API_KEY: {os.getenv('ALIYUN_QIANWEN_API_KEY')}")

# 模拟配置文件中的headers
headers = {
    "Authorization": "${ALIYUN_QIANWEN_API_KEY}",
    "Content-Type": "application/json"
}

print("\n原始headers:")
for name, value in headers.items():
    print(f"  {name}: {value}")

# 处理环境变量替换
processed_headers = {}
for header_name, header_value in headers.items():
    if isinstance(header_value, str) and header_value.startswith("${") and header_value.endswith("}"):
        env_var_name = header_value[2:-1]
        actual_value = os.getenv(env_var_name, header_value)
        processed_headers[header_name] = actual_value
        print(f"  替换 {env_var_name} -> {actual_value}")
    else:
        processed_headers[header_name] = header_value

print("\n处理后的headers:")
for name, value in processed_headers.items():
    print(f"  {name}: {value}")