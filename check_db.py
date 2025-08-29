import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def check_analysis_records():
    # 使用正确的MongoDB连接字符串
    mongodb_url = "mongodb://admin:admin123@127.0.0.1:27017/?authSource=admin"
    
    # 连接到MongoDB
    client = AsyncIOMotorClient(mongodb_url)
    db = client.pystrument
    
    # 检查分析记录集合
    collection = db.ai_analysis_results
    count = await collection.count_documents({})
    print(f"分析记录总数: {count}")
    
    # 获取一个示例记录
    record = await collection.find_one()
    if record:
        print("示例记录:")
        print(record)
    else:
        print("没有找到分析记录")
    
    # 检查特定ID的记录
    specific_id = "analysis_trace_1ae3e17df20d4c15_1756413803"
    specific_record = await collection.find_one({"analysis_id": specific_id})
    if specific_record:
        print(f"找到特定记录 {specific_id}:")
        print(specific_record)
    else:
        print(f"没有找到特定记录 {specific_id}")

if __name__ == "__main__":
    asyncio.run(check_analysis_records())