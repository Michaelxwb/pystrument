"""
项目管理API路由
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from datetime import datetime
import uuid

from app.middleware.response import success_response, error_response, ErrorCode
from app.models.project import Project, ProjectCreate, ProjectUpdate
from app.services.project_service import ProjectService

router = APIRouter()


@router.post("/", summary="创建项目")
async def create_project(project_data: ProjectCreate):
    """创建新项目"""
    try:
        service = ProjectService()
        
        # 检查项目名称是否已存在
        existing_project = await service.get_project_by_name(project_data.name)
        if existing_project:
            return error_response(
                ErrorCode.PROJECT_NAME_EXISTS,
                "项目名称已存在"
            )
        
        # 创建项目
        project = await service.create_project(project_data)
        
        return success_response(
            data={
                "project_key": project.project_key,
                "name": project.name,
                "description": project.description,
                "framework": project.framework,
                "status": project.status,
                "created_at": project.created_at.isoformat()
            },
            msg="项目创建成功"
        )
        
    except Exception as e:
        return error_response(
            ErrorCode.SYSTEM_ERROR,
            f"创建项目失败: {str(e)}"
        )


@router.get("/", summary="获取项目列表")
async def get_projects(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
    status: Optional[str] = Query(None, description="项目状态"),
    framework: Optional[str] = Query(None, description="技术框架")
):
    """获取项目列表"""
    try:
        service = ProjectService()
        
        # 构建查询条件
        filters = {}
        if status:
            filters["status"] = status
        if framework:
            filters["framework"] = framework
        
        # 获取项目列表
        projects, total = await service.get_projects(
            page=page,
            size=size,
            filters=filters
        )
        
        return success_response(
            data={
                "projects": [
                    {
                        "project_key": p.project_key,
                        "name": p.name,
                        "description": p.description,
                        "framework": p.framework,
                        "status": p.status,
                        "created_at": p.created_at.isoformat(),
                        "last_activity": p.last_activity.isoformat() if p.last_activity else None
                    }
                    for p in projects
                ],
                "total": total,
                "page": page,
                "size": size,
                "pages": (total + size - 1) // size
            }
        )
        
    except Exception as e:
        return error_response(
            ErrorCode.SYSTEM_ERROR,
            f"获取项目列表失败: {str(e)}"
        )


@router.get("/{project_key}", summary="获取项目详情")
async def get_project(project_key: str):
    """获取项目详情"""
    try:
        service = ProjectService()
        project = await service.get_project_by_key(project_key)
        
        if not project:
            return error_response(
                ErrorCode.PROJECT_NOT_FOUND,
                "项目不存在"
            )
        
        return success_response(
            data={
                "project_key": project.project_key,
                "name": project.name,
                "description": project.description,
                "framework": project.framework,
                "status": project.status,
                "config": project.config,
                "created_at": project.created_at.isoformat(),
                "updated_at": project.updated_at.isoformat(),
                "last_activity": project.last_activity.isoformat() if project.last_activity else None
            }
        )
        
    except Exception as e:
        return error_response(
            ErrorCode.SYSTEM_ERROR,
            f"获取项目详情失败: {str(e)}"
        )


@router.put("/{project_key}", summary="更新项目")
async def update_project(project_key: str, project_data: ProjectUpdate):
    """更新项目信息"""
    try:
        service = ProjectService()
        
        # 检查项目是否存在
        existing_project = await service.get_project_by_key(project_key)
        if not existing_project:
            return error_response(
                ErrorCode.PROJECT_NOT_FOUND,
                "项目不存在"
            )
        
        # 如果要更新名称，检查新名称是否已被其他项目使用
        if project_data.name and project_data.name != existing_project.name:
            name_conflict = await service.get_project_by_name(project_data.name)
            if name_conflict and name_conflict.project_key != project_key:
                return error_response(
                    ErrorCode.PROJECT_NAME_EXISTS,
                    "项目名称已被其他项目使用"
                )
        
        # 更新项目
        updated_project = await service.update_project(project_key, project_data)
        
        return success_response(
            data={
                "project_key": updated_project.project_key,
                "name": updated_project.name,
                "description": updated_project.description,
                "framework": updated_project.framework,
                "status": updated_project.status,
                "config": updated_project.config,
                "updated_at": updated_project.updated_at.isoformat()
            },
            msg="项目更新成功"
        )
        
    except Exception as e:
        return error_response(
            ErrorCode.SYSTEM_ERROR,
            f"更新项目失败: {str(e)}"
        )


@router.delete("/{project_key}", summary="删除项目")
async def delete_project(project_key: str):
    """删除项目（软删除）"""
    try:
        service = ProjectService()
        
        # 检查项目是否存在
        existing_project = await service.get_project_by_key(project_key)
        if not existing_project:
            return error_response(
                ErrorCode.PROJECT_NOT_FOUND,
                "项目不存在"
            )
        
        # 执行软删除（将状态改为archived）
        await service.archive_project(project_key)
        
        return success_response(msg="项目已归档")
        
    except Exception as e:
        return error_response(
            ErrorCode.SYSTEM_ERROR,
            f"删除项目失败: {str(e)}"
        )


@router.get("/{project_key}/stats", summary="获取项目统计信息")
async def get_project_stats(project_key: str):
    """获取项目统计信息"""
    try:
        service = ProjectService()
        
        # 检查项目是否存在
        project = await service.get_project_by_key(project_key)
        if not project:
            return error_response(
                ErrorCode.PROJECT_NOT_FOUND,
                "项目不存在"
            )
        
        # 获取统计信息
        stats = await service.get_project_stats(project_key)
        
        return success_response(data=stats)
        
    except Exception as e:
        return error_response(
            ErrorCode.SYSTEM_ERROR,
            f"获取项目统计失败: {str(e)}"
        )