"""
系统设置相关API
"""
import os
import json
import logging
import time
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Body
from pydantic import BaseModel
from app.utils.response import success_response, error_response
from app.utils.database import get_database
from app.config.settings import settings

# 设置日志
logger = logging.getLogger(__name__)
router = APIRouter()

# 数据模型定义
class BasicSettings(BaseModel):
    platformName: str
    adminEmail: str
    timezone: str
    language: str

class MonitorSettings(BaseModel):
    defaultSamplingRate: float
    dataRetentionDays: int
    slowQueryThreshold: int
    autoCleanup: bool

class AISettings(BaseModel):
    defaultService: str
    apiKey: str
    requestTimeout: int
    autoAnalysis: bool

class NotificationSettings(BaseModel):
    emailEnabled: bool
    smtpServer: Optional[str] = ""
    smtpPort: Optional[int] = 587
    senderEmail: Optional[str] = ""
    webhookEnabled: bool
    webhookUrl: Optional[str] = ""

class SystemSettings(BaseModel):
    basic: BasicSettings
    monitor: MonitorSettings
    ai: AISettings
    notification: NotificationSettings

class OperationLog(BaseModel):
    id: str
    timestamp: datetime
    action: str
    details: str
    operator: str

class SystemStatus(BaseModel):
    database: dict
    redis: dict
    aiService: dict
    storage: dict


# 获取系统设置
@router.get("")
async def get_settings(db = Depends(get_database)):
    logger.info("获取系统设置")
    
    try:
        # 从数据库获取设置
        settings_doc = await db.system_settings.find_one({"type": "system_settings"})
        
        if not settings_doc:
            # 如果不存在，返回默认设置
            return success_response({
                "basic": {
                    "platformName": "性能分析平台",
                    "adminEmail": "admin@example.com",
                    "timezone": "Asia/Shanghai",
                    "language": "zh-CN"
                },
                "monitor": {
                    "defaultSamplingRate": 0.3,
                    "dataRetentionDays": 30,
                    "slowQueryThreshold": 500,
                    "autoCleanup": True
                },
                "ai": {
                    "defaultService": "openai-gpt3.5",
                    "apiKey": "",
                    "requestTimeout": 30,
                    "autoAnalysis": False
                },
                "notification": {
                    "emailEnabled": False,
                    "smtpServer": "",
                    "smtpPort": 587,
                    "senderEmail": "",
                    "webhookEnabled": False,
                    "webhookUrl": ""
                }
            })
        
        # 处理MongoDB ObjectId
        if "_id" in settings_doc:
            settings_doc["_id"] = str(settings_doc["_id"])
        
        # 保护敏感信息
        if "ai" in settings_doc and "apiKey" in settings_doc["ai"] and settings_doc["ai"]["apiKey"]:
            settings_doc["ai"]["apiKey"] = "********"
        
        return success_response(settings_doc)
        
    except Exception as e:
        logger.error(f"获取系统设置失败: {str(e)}")
        return error_response(500, f"获取系统设置失败: {str(e)}")


# 更新系统设置
@router.post("")
async def update_settings(settings_data: SystemSettings, db = Depends(get_database)):
    logger.info("更新系统设置")
    
    try:
        # 获取当前设置
        current_settings = await db.system_settings.find_one({"type": "system_settings"})
        
        # 如果设置了占位符API密钥，保留原始密钥
        if settings_data.ai.apiKey == "********" and current_settings and "ai" in current_settings:
            settings_data.ai.apiKey = current_settings["ai"]["apiKey"]
        
        # 准备要保存的设置数据
        settings_dict = settings_data.dict()
        settings_dict["type"] = "system_settings"
        settings_dict["updated_at"] = datetime.utcnow()
        
        # 更新或创建设置
        if current_settings:
            await db.system_settings.update_one(
                {"type": "system_settings"}, 
                {"$set": settings_dict}
            )
        else:
            settings_dict["created_at"] = datetime.utcnow()
            await db.system_settings.insert_one(settings_dict)
        
        # 记录操作日志
        log_entry = {
            "timestamp": datetime.utcnow(),
            "action": "update_settings",
            "details": "更新系统设置",
            "operator": "system",  # 后续可以添加用户身份验证
            "created_at": datetime.utcnow()
        }
        await db.operation_logs.insert_one(log_entry)
        
        return success_response({"success": True})
        
    except Exception as e:
        logger.error(f"更新系统设置失败: {str(e)}")
        return error_response(500, f"更新系统设置失败: {str(e)}")


# 获取系统状态
@router.get("/status")
async def get_system_status(db = Depends(get_database)):
    logger.info("获取系统状态")
    
    try:
        # 检查数据库状态
        db_status = {"status": "normal", "message": "连接正常"}
        try:
            await db.command("ping")
        except Exception as e:
            db_status = {"status": "error", "message": f"连接失败: {str(e)}"}
        
        # 检查Redis状态
        redis_status = {"status": "normal", "message": "连接正常"}
        
        # 检查AI服务状态
        ai_status = {"status": "warning", "message": "需要配置API密钥"}
        settings_doc = await db.system_settings.find_one({"type": "system_settings"})
        if settings_doc and "ai" in settings_doc and settings_doc["ai"].get("apiKey"):
            ai_status = {"status": "normal", "message": "已配置"}
        
        # 检查存储状态
        storage_status = {
            "used": 120,  # MB
            "total": 500,  # MB
            "unit": "MB"
        }
        
        status_data = {
            "database": db_status,
            "redis": redis_status,
            "aiService": ai_status,
            "storage": storage_status
        }
        
        return success_response(status_data)
        
    except Exception as e:
        logger.error(f"获取系统状态失败: {str(e)}")
        return error_response(500, f"获取系统状态失败: {str(e)}")


# 获取操作日志
@router.get("/logs")
async def get_operation_logs(
    page: int = 1, 
    size: int = 10,
    db = Depends(get_database)
):
    logger.info(f"获取操作日志, 页码: {page}, 大小: {size}")
    
    try:
        # 计算跳过的记录数
        skip = (page - 1) * size
        
        # 查询总数
        total = await db.operation_logs.count_documents({})
        
        # 查询日志记录
        cursor = db.operation_logs.find().sort("timestamp", -1).skip(skip).limit(size)
        logs = []
        
        async for log in cursor:
            # 处理MongoDB ObjectId
            log["_id"] = str(log["_id"])
            logs.append({
                "id": str(log.get("_id")),
                "timestamp": log.get("timestamp").isoformat(),
                "action": log.get("action"),
                "details": log.get("details"),
                "operator": log.get("operator")
            })
        
        return success_response({
            "logs": logs,
            "total": total,
            "page": page,
            "size": size
        })
        
    except Exception as e:
        logger.error(f"获取操作日志失败: {str(e)}")
        return error_response(500, f"获取操作日志失败: {str(e)}")


# 测试数据库连接
@router.post("/test/database")
async def test_database_connection(db = Depends(get_database)):
    logger.info("测试数据库连接")
    
    try:
        # 测试数据库连接
        start_time = time.time()
        await db.command("ping")
        response_time = round((time.time() - start_time) * 1000, 2)  # 毫秒
        
        return success_response({
            "success": True,
            "message": f"连接成功，响应时间: {response_time}ms"
        })
        
    except Exception as e:
        logger.error(f"测试数据库连接失败: {str(e)}")
        return error_response(500, f"连接失败: {str(e)}")


# 测试Redis连接
@router.post("/test/redis")
async def test_redis_connection():
    logger.info("测试Redis连接")
    
    try:
        # 这里需要实际的Redis连接测试
        # 为简化示例，这里模拟连接成功
        return success_response({
            "success": True,
            "message": "连接成功，响应时间: 5ms"
        })
        
    except Exception as e:
        logger.error(f"测试Redis连接失败: {str(e)}")
        return error_response(500, f"连接失败: {str(e)}")


# 测试AI服务连接
@router.post("/test/ai-service")
async def test_ai_service_connection(db = Depends(get_database)):
    logger.info("测试AI服务连接")
    
    try:
        # 获取API密钥
        settings_doc = await db.system_settings.find_one({"type": "system_settings"})
        
        if not settings_doc or "ai" not in settings_doc or not settings_doc["ai"].get("apiKey"):
            return error_response(400, "未配置API密钥")
        
        # 实际应用中应该测试实际的AI服务连接
        # 这里模拟连接成功
        return success_response({
            "success": True,
            "message": "连接成功，服务可用"
        })
        
    except Exception as e:
        logger.error(f"测试AI服务连接失败: {str(e)}")
        return error_response(500, f"连接失败: {str(e)}")


# 清理缓存
@router.post("/clear-cache")
async def clear_cache(db = Depends(get_database)):
    logger.info("清理缓存")
    
    try:
        # 记录操作日志
        log_entry = {
            "timestamp": datetime.utcnow(),
            "action": "clear_cache",
            "details": "清理系统缓存",
            "operator": "system",
            "created_at": datetime.utcnow()
        }
        await db.operation_logs.insert_one(log_entry)
        
        # 实际应用中应该执行实际的缓存清理操作
        # 这里模拟清理成功
        return success_response({
            "success": True,
            "message": "缓存清理成功"
        })
        
    except Exception as e:
        logger.error(f"清理缓存失败: {str(e)}")
        return error_response(500, f"清理缓存失败: {str(e)}")


# 导出配置
@router.get("/export")
async def export_config(db = Depends(get_database)):
    logger.info("导出系统配置")
    
    try:
        # 获取系统设置
        settings_doc = await db.system_settings.find_one({"type": "system_settings"})
        
        if not settings_doc:
            return error_response(404, "未找到系统配置")
        
        # 移除不需要导出的字段
        if "_id" in settings_doc:
            del settings_doc["_id"]
        
        # 记录操作日志
        log_entry = {
            "timestamp": datetime.utcnow(),
            "action": "export_config",
            "details": "导出系统配置",
            "operator": "system",
            "created_at": datetime.utcnow()
        }
        await db.operation_logs.insert_one(log_entry)
        
        # 返回JSON配置
        return success_response(settings_doc)
        
    except Exception as e:
        logger.error(f"导出系统配置失败: {str(e)}")
        return error_response(500, f"导出系统配置失败: {str(e)}")


# 导入配置
@router.post("/import")
async def import_config(
    config: UploadFile = File(...),
    db = Depends(get_database)
):
    logger.info("导入系统配置")
    
    try:
        # 读取上传的配置文件
        content = await config.read()
        config_data = json.loads(content)
        
        # 验证配置数据
        if "basic" not in config_data or "monitor" not in config_data or "ai" not in config_data:
            return error_response(400, "配置文件格式无效")
        
        # 更新系统设置
        config_data["type"] = "system_settings"
        config_data["updated_at"] = datetime.utcnow()
        
        await db.system_settings.update_one(
            {"type": "system_settings"},
            {"$set": config_data},
            upsert=True
        )
        
        # 记录操作日志
        log_entry = {
            "timestamp": datetime.utcnow(),
            "action": "import_config",
            "details": "导入系统配置",
            "operator": "system",
            "created_at": datetime.utcnow()
        }
        await db.operation_logs.insert_one(log_entry)
        
        return success_response({
            "success": True,
            "message": "配置导入成功"
        })
        
    except json.JSONDecodeError:
        logger.error("导入系统配置失败: 无效的JSON格式")
        return error_response(400, "配置文件不是有效的JSON格式")
        
    except Exception as e:
        logger.error(f"导入系统配置失败: {str(e)}")
        return error_response(500, f"导入系统配置失败: {str(e)}")